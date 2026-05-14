"""
models/glpi_sync_log.py
=======================
Audit log for every GLPI sync run.

One ``glpi.sync.log`` record is created at the start of each cron execution
or manual trigger. Individual record-level errors are appended to the
``exceptions`` field as a JSON array so the complete run is captured in one
place without interrupting the sync.

State machine
-------------
running → done      All records processed (errors may still exist on rows).
running → error     A fatal exception stopped the sync early.
"""

import json
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class GlpiSyncLog(models.Model):
    _name = 'glpi.sync.log'
    _description = 'GLPI Asset Sync Log'
    _order = 'sync_start desc'
    _rec_name = 'sync_start'

    # -----------------------------------------------------------------------
    # Fields
    # -----------------------------------------------------------------------

    sync_start = fields.Datetime(
        string='Started',
        required=True,
        default=fields.Datetime.now,
        readonly=True,
    )
    sync_end = fields.Datetime(string='Finished', readonly=True)
    state = fields.Selection(
        selection=[
            ('running', 'Running'),
            ('done', 'Done'),
            ('error', 'Error'),
        ],
        string='State',
        default='running',
        required=True,
        index=True,
        readonly=True,
    )
    fetched = fields.Integer(string='Fetched', default=0, readonly=True)
    created = fields.Integer(string='Created', default=0, readonly=True)
    updated = fields.Integer(string='Updated', default=0, readonly=True)
    skipped = fields.Integer(string='Skipped', default=0, readonly=True,
                             help='Records where no field changed (timestamp still updated).')
    error_count = fields.Integer(string='Errors', default=0, readonly=True)
    duration_seconds = fields.Float(
        string='Duration (s)',
        compute='_compute_duration',
        store=True,
        readonly=True,
    )
    error_message = fields.Text(
        string='Fatal Error',
        readonly=True,
        help='Populated when a fatal exception stops the sync.',
    )
    exceptions = fields.Text(
        string='Per-record Exceptions (JSON)',
        readonly=True,
        help='JSON array of {glpi_id, error} objects for non-fatal per-row errors.',
    )

    # -----------------------------------------------------------------------
    # Computed
    # -----------------------------------------------------------------------

    @api.depends('sync_start', 'sync_end')
    def _compute_duration(self):
        for rec in self:
            if rec.sync_start and rec.sync_end:
                rec.duration_seconds = (rec.sync_end - rec.sync_start).total_seconds()
            else:
                rec.duration_seconds = 0.0

    # -----------------------------------------------------------------------
    # Helpers used by the sync engine
    # -----------------------------------------------------------------------

    def add_exception(self, glpi_id, message: str):
        """
        Append a per-record error to ``exceptions`` and increment ``error_count``.

        Parameters
        ----------
        glpi_id : int | str
            GLPI ID of the failing record (or a batch descriptor like
            ``'batch@200'``).
        message : str
            Error message.
        """
        try:
            current = json.loads(self.exceptions or '[]')
        except (json.JSONDecodeError, TypeError):
            current = []
        current.append({'glpi_id': glpi_id, 'error': message})
        self.write({
            'exceptions': json.dumps(current, ensure_ascii=False),
            'error_count': self.error_count + 1,
        })
        _logger.warning('GLPI sync error — GLPI ID %s: %s', glpi_id, message)

    def finish(self, state: str = 'done', error_message: str = None):
        """
        Mark the sync run as complete.

        Parameters
        ----------
        state : str
            ``'done'`` or ``'error'``.
        error_message : str, optional
            Fatal error message (only set when ``state='error'``).
        """
        vals = {
            'sync_end': fields.Datetime.now(),
            'state': state,
        }
        if error_message:
            vals['error_message'] = error_message
        self.write(vals)
        _logger.info(
            'GLPI sync finished: state=%s fetched=%s created=%s updated=%s '
            'skipped=%s errors=%s duration=%.1fs',
            state,
            self.fetched,
            self.created,
            self.updated,
            self.skipped,
            self.error_count,
            self.duration_seconds,
        )