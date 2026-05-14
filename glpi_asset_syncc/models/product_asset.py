"""
product_asset.py
================
Extends product.product with GLPI-specific fields and the full sync engine.

Upsert key priority
-------------------
1. x_glpi_id        GLPI primary integer ID — most reliable after first sync
2. x_glpi_uuid      Motherboard UUID — strong but can change after hardware swap
3. x_glpi_asset_tag Inventory number / other serial — business-visible identifier

Sync flow (GLPI → Odoo, one-directional)
-----------------------------------------
cron_sync_glpi_computers()
  └─ _run_sync(log)
       ├─ init_session()
       ├─ change_active_entity()     [if entity_id configured]
       └─ loop: get_computers(batch)
            └─ _upsert_from_glpi_row(row)
                 ├─ search existing record (3-key fallback)
                 ├─ write() if changed, or update timestamps only if skipped
                 └─ create() with type='consu' for new records

Bulk counter pattern
--------------------
Counters (created/updated/skipped) are accumulated locally in a dict and
written to the log in one write() per batch, not once per row, to avoid
excessive DB round-trips on large imports.

Switching the asset model
--------------------------
Change _inherit to 'maintenance.equipment', 'account.asset', or any custom
model. The sync logic itself does not change — only adjust the field mapping
in _upsert_from_glpi_row() to match the target model's column names.
"""

import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from ..services.glpi_client import GLPIClient, GLPIApiError

_logger = logging.getLogger(__name__)


class ProductAsset(models.Model):
    _inherit = 'product.product'

    # ------------------------------------------------------------------
    # GLPI tracking fields
    # ------------------------------------------------------------------

    x_glpi_id = fields.Integer(
        string='GLPI ID',
        index=True,
        copy=False,
        help='Primary key in GLPI. Used as upsert key 1.',
    )
    x_glpi_itemtype = fields.Char(
        string='GLPI Item Type',
        default='Computer',
        copy=False,
        help='GLPI item class — usually "Computer".',
    )
    x_glpi_uuid = fields.Char(
        string='GLPI UUID',
        index=True,
        copy=False,
        help='Motherboard UUID reported by the GLPI inventory agent. Upsert key 2.',
    )
    x_glpi_asset_tag = fields.Char(
        string='Asset Tag / Inventory No.',
        index=True,
        copy=False,
        help='GLPI inventory number (otherserial). Upsert key 3.',
    )
    x_glpi_serial = fields.Char(
        string='Serial Number',
        index=True,
        copy=False,
        help='Hardware serial number from GLPI.',
    )
    x_glpi_manufacturer = fields.Char(
        string='Manufacturer',
        copy=False,
        help='Manufacturer name resolved from GLPI manufacturers_id.',
    )
    x_glpi_last_sync = fields.Datetime(
        string='Last GLPI Sync',
        copy=False,
        help='Timestamp of the last successful sync for this record.',
    )
    x_glpi_raw_json = fields.Text(
        string='GLPI Raw JSON',
        copy=False,
        help='Full GLPI API payload snapshot — for debugging only.',
    )

    _sql_constraints = [
        (
            'glpi_uuid_unique',
            'unique(x_glpi_uuid)',
            'GLPI UUID must be unique across all asset records.',
        ),
    ]

    # ------------------------------------------------------------------
    # Settings helpers
    # ------------------------------------------------------------------

    @api.model
    def _glpi_param(self, key, default=None):
        """Read a glpi_asset_sync.* ir.config_parameter value."""
        return self.env['ir.config_parameter'].sudo().get_param(
            f'glpi_asset_sync.{key}', default
        )

    @api.model
    def _build_glpi_client(self):
        """Instantiate a GLPIClient from current system parameters."""
        base_url = self._glpi_param('base_url')
        if not base_url:
            raise UserError(
                _('GLPI Base URL is not configured. Go to Settings ▶ GLPI Asset Sync.')
            )
        return GLPIClient(
            base_url=base_url,
            app_token=self._glpi_param('app_token'),
            user_token=self._glpi_param('user_token'),
            username=self._glpi_param('username'),
            password=self._glpi_param('password'),
            verify_ssl=(self._glpi_param('verify_ssl', 'True') == 'True'),
        )

    # ------------------------------------------------------------------
    # Public entry points
    # ------------------------------------------------------------------

    @api.model
    def cron_sync_glpi_computers(self):
        """
        Entry point for ir.cron. Creates a log record, runs the sync,
        and finalises the log whether the sync succeeds or fails.
        """
        log = self.env['glpi.sync.log'].create({'triggered_by': 'cron'})
        self.env.cr.commit()   # persist log before the long-running sync
        try:
            self._run_sync(log)
        except Exception as exc:
            log.finish(state='error', error_message=str(exc))
            _logger.exception('GLPI sync fatal error: %s', exc)
            raise
        else:
            log.finish(state='error' if log.error_count else 'done')

    @api.model
    def action_sync_glpi_now(self):
        """
        Manual trigger — available as a server action bound to product.product.
        Returns a display_notification so the user sees an immediate result.
        """
        log = self.env['glpi.sync.log'].create({'triggered_by': 'manual'})
        self.env.cr.commit()
        try:
            self._run_sync(log)
        except Exception as exc:
            log.finish(state='error', error_message=str(exc))
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('GLPI Sync Failed'),
                    'message': str(exc),
                    'type': 'danger',
                    'sticky': True,
                },
            }
        else:
            log.finish(state='error' if log.error_count else 'done')
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('GLPI Sync Complete'),
                    'message': _(
                        'Fetched %(f)s · Created %(c)s · Updated %(u)s · '
                        'Skipped %(s)s · Errors %(e)s'
                    ) % {
                        'f': log.fetched, 'c': log.created,
                        'u': log.updated, 's': log.skipped, 'e': log.error_count,
                    },
                    'type': 'success' if not log.error_count else 'warning',
                    'sticky': False,
                },
            }

    # ------------------------------------------------------------------
    # Core sync engine
    # ------------------------------------------------------------------

    @api.model
    def _run_sync(self, log):
        """
        Open a GLPI session, page through all Computer records, and upsert
        each one into Odoo. Counters are written to the log per batch to
        minimise DB round-trips.
        """
        client = self._build_glpi_client()
        client.init_session()

        try:
            # Optional entity restriction
            entity_id = int(self._glpi_param('entity_id', 0) or 0)
            if entity_id:
                is_recursive = (
                    1 if self._glpi_param('entity_recursive', 'False') == 'True' else 0
                )
                client.change_active_entity(entity_id, is_recursive)
                _logger.info(
                    'GLPI sync: restricted to entity %s (recursive=%s)',
                    entity_id, is_recursive,
                )

            batch_size = min(int(self._glpi_param('batch_size', 200) or 200), 200)
            start = 0

            while True:
                # Fetch one page of computers
                try:
                    rows = client.get_computers(start=start, end=start + batch_size - 1)
                except GLPIApiError as exc:
                    _logger.error('GLPI fetch error at offset %s: %s', start, exc)
                    log.add_exception(f'batch@{start}', str(exc))
                    break

                if not rows:
                    break

                # Process the batch and accumulate local counters
                batch_counts = {'fetched': len(rows), 'created': 0, 'updated': 0, 'skipped': 0}

                for row in rows:
                    try:
                        result = self._upsert_from_glpi_row(row)
                        batch_counts[result] += 1
                    except Exception as exc:
                        log.add_exception(row.get('id', '?'), str(exc))

                # One write per batch instead of one per row
                log.write({
                    'fetched':  log.fetched  + batch_counts['fetched'],
                    'created':  log.created  + batch_counts['created'],
                    'updated':  log.updated  + batch_counts['updated'],
                    'skipped':  log.skipped  + batch_counts['skipped'],
                })
                self.env.cr.commit()   # flush progress after each batch

                _logger.info(
                    'GLPI sync progress: offset=%s fetched=%s created=%s updated=%s skipped=%s',
                    start, batch_counts['fetched'], batch_counts['created'],
                    batch_counts['updated'], batch_counts['skipped'],
                )

                if len(rows) < batch_size:
                    break
                start += batch_size

        finally:
            client.kill_session()

    # ------------------------------------------------------------------
    # Upsert logic
    # ------------------------------------------------------------------

    @api.model
    def _upsert_from_glpi_row(self, row):
        """
        Upsert a single GLPI Computer dict.

        Returns 'created', 'updated', or 'skipped'.

        Field mapping (collection API field names)
        -------------------------------------------
        GLPI field          Odoo field
        id                  x_glpi_id           (upsert key 1)
        uuid                x_glpi_uuid         (upsert key 2)
        otherserial         x_glpi_asset_tag    (upsert key 3, inventory no.)
        inventory_number    x_glpi_asset_tag    (fallback label in some versions)
        serial              x_glpi_serial
        manufacturer        x_glpi_manufacturer (resolved name, if present)
        manufacturers_id    x_glpi_manufacturer (raw int id, used as string fallback)
        name                name
        itemtype            x_glpi_itemtype

        Note: If the collection API does not return the exact field names you
        need, use client.search_computers(forcedisplay=[...]) with field IDs
        discovered via client.list_search_options('Computer').
        """
        glpi_id = row.get('id')

        # ── UUID / asset tag / serial ─────────────────────────────────
        def _clean(val):
            return (str(val).strip() if val else '') or None

        uuid = _clean(row.get('uuid'))
        asset_tag = _clean(
            row.get('otherserial') or row.get('inventory_number')
        )
        serial = _clean(row.get('serial'))
        manufacturer = _clean(
            row.get('manufacturer')                    # resolved name
            or row.get('manufacturers_id')             # raw int fallback
        )
        name = _clean(row.get('name')) or f'GLPI Asset {glpi_id}'

        # ── Find existing record — 3-key priority fallback ────────────
        record = self.browse()
        if glpi_id:
            record = self.search([('x_glpi_id', '=', glpi_id)], limit=1)
        if not record and uuid:
            record = self.search([('x_glpi_uuid', '=', uuid)], limit=1)
        if not record and asset_tag:
            record = self.search([('x_glpi_asset_tag', '=', asset_tag)], limit=1)

        # ── Values dict ───────────────────────────────────────────────
        vals = {
            'name':               name,
            'x_glpi_id':          glpi_id,
            'x_glpi_itemtype':    row.get('itemtype', 'Computer'),
            'x_glpi_uuid':        uuid,
            'x_glpi_asset_tag':   asset_tag,
            'x_glpi_serial':      serial,
            'x_glpi_manufacturer': manufacturer,
            'x_glpi_last_sync':   fields.Datetime.now(),
            'x_glpi_raw_json':    str(row),
        }

        # ── Upsert ────────────────────────────────────────────────────
        if record:
            # Compare only data fields — ignore last_sync and raw_json
            data_fields = {k: v for k, v in vals.items()
                           if k not in ('x_glpi_last_sync', 'x_glpi_raw_json')}
            changed = any(
                str(record[k]) != str(v) for k, v in data_fields.items()
            )
            if changed:
                record.write(vals)
                return 'updated'
            else:
                # Always refresh timestamp and raw snapshot even when skipped
                record.write({
                    'x_glpi_last_sync': vals['x_glpi_last_sync'],
                    'x_glpi_raw_json':  vals['x_glpi_raw_json'],
                })
                return 'skipped'
        else:
            # type='consu' prevents Odoo from creating stock moves for new records
            vals.setdefault('type', 'consu')
            self.create(vals)
            return 'created'
