"""
glpi_sync_log.py
================
Audit log — one record per cron execution or manual "Sync Now" trigger.

Per-record errors are captured in the exceptions field (JSON array) so a
single run record shows everything: total fetched, created, updated,
skipped, errors, and the full exception list.
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

    sync_start = fields.Datetime(
        string='Started', required=True, default=fields.Datetime.now, readonly=True)
    sync_end = fields.Datetime(string='Finished', readonly=True)
    state = fields.Selection(
        [('running', 'Running'), ('done', 'Done'), ('error', 'Error')],
        default='running', required=True, index=True, readonly=True,
    )
    triggered_by = fields.Selection(
        [('cron', 'Scheduled'), ('manual', 'Manual')],
        string='Triggered By', default='cron', readonly=True,
    )

    # counters
    fetched = fields.Integer(string='Fetched', default=0, readonly=True)
    created = fields.Integer(string='Created', default=0, readonly=True)
    updated = fields.Integer(string='Updated', default=0, readonly=True)
    skipped = fields.Integer(string='Skipped', default=0, readonly=True)
    error_count = fields.Integer(string='Errors', default=0, readonly=True)

    # error details
    error_message = fields.Text(string='Fatal Error', readonly=True)
    exceptions = fields.Text(
        string='Per-record Exceptions',
        help='JSON array — [{glpi_id, error}] for non-fatal per-record errors.',
        readonly=True,
    )

    duration_seconds = fields.Float(
        string='Duration (s)', compute='_compute_duration', store=True)

    @api.depends('sync_start', 'sync_end')
    def _compute_duration(self):
        for rec in self:
            if rec.sync_start and rec.sync_end:
                rec.duration_seconds = (rec.sync_end - rec.sync_start).total_seconds()
            else:
                rec.duration_seconds = 0.0

    # ------------------------------------------------------------------
    # Helpers called by the sync engine
    # ------------------------------------------------------------------

    def add_exception(self, glpi_id, message):
        """Append one per-record error and increment the error counter."""
        try:
            current = json.loads(self.exceptions or '[]')
        except (json.JSONDecodeError, TypeError):
            current = []
        current.append({'glpi_id': glpi_id, 'error': str(message)})
        self.write({
            'exceptions': json.dumps(current, ensure_ascii=False),
            'error_count': self.error_count + 1,
        })
        _logger.warning('GLPI sync error — GLPI ID %s: %s', glpi_id, message)

    def finish(self, state='done', error_message=None, counts=None):
        """
        Mark the run as complete.

        Args:
            state: 'done' | 'error'
            error_message: optional fatal error string
            counts: optional dict with keys created, updated, skipped, fetched
        """
        vals = {'sync_end': fields.Datetime.now(), 'state': state}
        if error_message:
            vals['error_message'] = error_message
        if counts:
            vals.update({k: v for k, v in counts.items()
                         if k in ('fetched', 'created', 'updated', 'skipped')})
        self.write(vals)
