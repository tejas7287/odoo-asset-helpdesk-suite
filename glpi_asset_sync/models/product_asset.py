"""
models/product_asset.py
=======================
Extends ``product.product`` with GLPI-specific tracking fields and the
complete sync engine.

Architecture
------------
* Pull-based: Odoo opens a GLPI session, reads all Computer records in
  configurable batches, upserts into Odoo, then closes the session.
* One-directional: GLPI → Odoo only.
* Two fetch strategies:

  1. **Collection API** (default): ``GET /apirest.php/Computer/``
     Returns all fields GLPI includes by default. Fast and simple.

  2. **Search API**: ``GET /apirest.php/search/Computer``
     Use when you need specific fields via ``forcedisplay`` (field IDs
     from ``listSearchOptions``). Required if the collection API omits
     the inventory number field in your GLPI version.

Upsert key priority
-------------------
1. ``x_glpi_id``       — GLPI primary integer ID (most reliable after first sync)
2. ``x_glpi_uuid``     — Motherboard UUID (strong but can change on hardware swap)
3. ``x_glpi_asset_tag`` — Inventory number / other serial (business-visible)

Changing the base model
-----------------------
If your asset master is ``maintenance.equipment``, ``account.asset``, or a
custom model, change ``_inherit`` below. The sync logic is model-agnostic.
"""

import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from ..services.glpi_client import GLPIClient, GLPIApiError

_logger = logging.getLogger(__name__)


class ProductAsset(models.Model):
    _inherit = 'product.product'

    # -----------------------------------------------------------------------
    # GLPI tracking fields (spec: x_glpi_id, x_glpi_uuid, x_glpi_asset_tag,
    #                              x_glpi_itemtype, x_glpi_last_sync)
    # -----------------------------------------------------------------------

    x_glpi_id = fields.Integer(
        string='GLPI ID',
        index=True,
        copy=False,
        help='GLPI primary key (integer). Used as upsert key 1.',
    )
    x_glpi_itemtype = fields.Char(
        string='GLPI Item Type',
        default='Computer',
        copy=False,
        help='GLPI itemtype — usually "Computer".',
    )
    x_glpi_uuid = fields.Char(
        string='GLPI UUID',
        index=True,
        copy=False,
        help=(
            'Motherboard UUID as reported by the GLPI inventory agent.\n'
            'Used as upsert key 2. Note: UUID may change after a hardware swap\n'
            'unless manually locked in GLPI.'
        ),
    )
    x_glpi_asset_tag = fields.Char(
        string='GLPI Asset Tag',
        index=True,
        copy=False,
        help=(
            'Inventory number (otherserial) from GLPI.\n'
            'Fallback: inventory_number, then serial.\n'
            'Used as upsert key 3.'
        ),
    )
    x_glpi_last_sync = fields.Datetime(
        string='Last GLPI Sync',
        copy=False,
        help='Timestamp of the last successful sync for this record.',
    )
    x_glpi_raw_json = fields.Text(
        string='GLPI Raw JSON',
        copy=False,
        help='Full GLPI Computer payload snapshot — for debugging / auditing.',
    )

    _sql_constraints = [
        (
            'glpi_uuid_unique',
            'unique(x_glpi_uuid)',
            'GLPI UUID must be unique. Two product records cannot share the same UUID.',
        ),
    ]

    # -----------------------------------------------------------------------
    # Configuration helpers
    # -----------------------------------------------------------------------

    @api.model
    def _glpi_param(self, key: str, default=None) -> str:
        """Read a GLPI sync setting from ir.config_parameter."""
        return (
            self.env['ir.config_parameter']
            .sudo()
            .get_param(f'glpi_asset_sync.{key}', default)
        )

    @api.model
    def _get_glpi_client(self) -> GLPIClient:
        """
        Build and return a configured :class:`GLPIClient`.

        Reads all connection parameters from ``ir.config_parameter``.

        Raises
        ------
        UserError
            If GLPI Base URL has not been configured.
        """
        base_url = self._glpi_param('base_url')
        if not base_url:
            raise UserError(
                _('GLPI Base URL is not configured.\n'
                  'Go to Settings > GLPI Asset Sync and save the connection details.')
            )
        return GLPIClient(
            base_url=base_url,
            app_token=self._glpi_param('app_token'),
            user_token=self._glpi_param('user_token'),
            username=self._glpi_param('username'),
            password=self._glpi_param('password'),
            verify_ssl=(self._glpi_param('verify_ssl', 'True') == 'True'),
        )

    # -----------------------------------------------------------------------
    # Public entry points
    # -----------------------------------------------------------------------

    @api.model
    def cron_sync_glpi_computers(self):
        """
        Cron entry point — called by the ``ir.cron`` scheduled action.

        Creates a ``glpi.sync.log`` record, runs the full sync, then
        finalises the log record with the outcome state.
        """
        log = self.env['glpi.sync.log'].create({})
        # Commit so the "Running" log is visible even if the sync crashes.
        self.env.cr.commit()
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
        Manual trigger — bound to the "Sync Now" server action on the
        Products list and form views.

        Returns a notification action for immediate UI feedback.
        """
        self.cron_sync_glpi_computers()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('GLPI Sync Complete'),
                'message': _(
                    'Asset synchronisation finished. '
                    'Check GLPI Sync Logs for details.'
                ),
                'type': 'success',
                'sticky': False,
            },
        }

    # -----------------------------------------------------------------------
    # Core sync engine
    # -----------------------------------------------------------------------

    @api.model
    def _run_sync(self, log):
        """
        Open a GLPI session, iterate all Computer records, upsert each into
        Odoo, then close the session.

        Parameters
        ----------
        log : glpi.sync.log
            Active log record. Updated incrementally during the sync.
        """
        client = self._get_glpi_client()
        client.init_session()

        try:
            # Optional: restrict scope to a specific entity
            entity_id = int(self._glpi_param('entity_id', 0) or 0)
            is_recursive = (
                1 if self._glpi_param('entity_recursive', 'False') == 'True' else 0
            )
            if entity_id:
                client.change_active_entity(entity_id, is_recursive)

            batch_size = min(int(self._glpi_param('batch_size', 200) or 200), 200)
            start = 0

            while True:
                # ── Fetch batch ────────────────────────────────────────────
                try:
                    rows = client.get_computers(
                        start=start, end=start + batch_size - 1
                    )
                except GLPIApiError as exc:
                    _logger.error(
                        'GLPI fetch error at offset %s: %s', start, exc
                    )
                    log.add_exception(f'batch@{start}', str(exc))
                    break

                if not rows:
                    break

                log.write({'fetched': log.fetched + len(rows)})

                # ── Upsert each row ────────────────────────────────────────
                for row in rows:
                    try:
                        result = self._upsert_from_glpi_row(row)
                        if result == 'created':
                            log.write({'created': log.created + 1})
                        elif result == 'updated':
                            log.write({'updated': log.updated + 1})
                        else:
                            log.write({'skipped': log.skipped + 1})
                    except Exception as exc:
                        log.add_exception(row.get('id', '?'), str(exc))

                if len(rows) < batch_size:
                    break
                start += batch_size

        finally:
            client.kill_session()

    # -----------------------------------------------------------------------
    # Upsert logic  (spec § 15–16: matching engine + create/update)
    # -----------------------------------------------------------------------

    @api.model
    def _upsert_from_glpi_row(self, row: dict) -> str:
        """
        Upsert a single GLPI Computer row into Odoo.

        Field mapping (collection API field names)
        ------------------------------------------
        GLPI field           Odoo field
        ``id``               ``x_glpi_id``
        ``uuid``             ``x_glpi_uuid``
        ``otherserial``      ``x_glpi_asset_tag``  (priority 1)
        ``inventory_number`` ``x_glpi_asset_tag``  (priority 2)
        ``serial``           ``x_glpi_asset_tag``  (priority 3 / fallback)
        ``name``             ``name``
        ``itemtype``         ``x_glpi_itemtype``

        If the collection API does not expose the fields you need, switch to
        ``search_computers`` with ``forcedisplay`` and override this method
        to read from numeric field-ID keys instead of named keys.

        Returns
        -------
        str
            ``'created'``, ``'updated'``, or ``'skipped'``.
        """
        glpi_id = row.get('id')

        # Sanitise UUID — GLPI sometimes returns empty strings
        uuid = (row.get('uuid') or '').strip() or None

        # Asset tag: try otherserial (inventory number), then serial
        asset_tag = (
            row.get('otherserial')
            or row.get('inventory_number')
            or row.get('serial')
            or ''
        ).strip() or None

        name = (row.get('name') or '').strip() or f'GLPI Asset {glpi_id}'

        # ── Match existing record (priority: GLPI ID > UUID > asset tag) ──
        record = self.browse()
        if glpi_id:
            record = self.search([('x_glpi_id', '=', glpi_id)], limit=1)
        if not record and uuid:
            record = self.search([('x_glpi_uuid', '=', uuid)], limit=1)
        if not record and asset_tag:
            record = self.search([('x_glpi_asset_tag', '=', asset_tag)], limit=1)

        # ── Build values dict ──────────────────────────────────────────────
        vals = {
            'name': name,
            'x_glpi_id': glpi_id,
            'x_glpi_itemtype': row.get('itemtype', 'Computer'),
            'x_glpi_uuid': uuid,
            'x_glpi_asset_tag': asset_tag,
            'x_glpi_last_sync': fields.Datetime.now(),
            'x_glpi_raw_json': str(row),
        }

        if record:
            # ── Check for meaningful changes (spec § 16: changed-field-only) ─
            compare_keys = {
                k for k in vals
                if k not in ('x_glpi_last_sync', 'x_glpi_raw_json')
            }
            changed = any(
                str(record[k]) != str(vals[k]) for k in compare_keys
            )
            if changed:
                record.write(vals)
                return 'updated'
            else:
                # Data unchanged — still refresh timestamp and raw snapshot
                record.write({
                    'x_glpi_last_sync': vals['x_glpi_last_sync'],
                    'x_glpi_raw_json': vals['x_glpi_raw_json'],
                })
                return 'skipped'
        else:
            # ── Create new record ──────────────────────────────────────────
            # type='consu' avoids stock moves being created for asset records
            vals.setdefault('type', 'consu')
            self.create(vals)
            return 'created'