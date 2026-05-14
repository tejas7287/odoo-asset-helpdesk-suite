"""
glpi_field_map.py
=================
Transient wizard that calls listSearchOptions/Computer on the configured
GLPI server and displays the result as a formatted table in a popup dialog.

Use this once per GLPI environment to discover the integer field IDs for
UUID, Inventory Number, Serial Number, and Manufacturer — then configure
those IDs in forcedisplay when switching to the search API.

Accessible via:  GLPI Asset Sync ▶ Field Discovery
"""

import json
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from ..services.glpi_client import GLPIClient, GLPIApiError

_logger = logging.getLogger(__name__)


class GlpiFieldMap(models.TransientModel):
    _name = 'glpi.field.map'
    _description = 'GLPI Computer Field Discovery'

    itemtype = fields.Char(
        string='Item Type',
        default='Computer',
        required=True,
        help='GLPI item type to query. Usually "Computer".',
    )
    result_json = fields.Text(
        string='Raw JSON Result',
        readonly=True,
    )
    result_table = fields.Html(
        string='Field ID Table',
        readonly=True,
        sanitize=False,
    )
    state = fields.Selection(
        [('draft', 'Ready'), ('done', 'Results')],
        default='draft',
    )

    @api.model
    def _get_client(self):
        icp = self.env['ir.config_parameter'].sudo()
        base_url = icp.get_param('glpi_asset_sync.base_url')
        if not base_url:
            raise UserError(_('GLPI Base URL is not configured. Go to Settings ▶ GLPI Asset Sync.'))
        return GLPIClient(
            base_url=base_url,
            app_token=icp.get_param('glpi_asset_sync.app_token'),
            user_token=icp.get_param('glpi_asset_sync.user_token'),
            username=icp.get_param('glpi_asset_sync.username'),
            password=icp.get_param('glpi_asset_sync.password'),
            verify_ssl=(icp.get_param('glpi_asset_sync.verify_ssl', 'True') == 'True'),
        )

    def action_fetch_fields(self):
        """Call listSearchOptions and render results as an HTML table."""
        client = self._get_client()
        client.init_session()
        try:
            opts = client.list_search_options(self.itemtype or 'Computer')
        except GLPIApiError as exc:
            raise UserError(_('GLPI API error: %s') % str(exc)) from exc
        finally:
            client.kill_session()

        # Build a clean HTML table sorted by field ID
        rows_html = []
        for fid, meta in sorted(opts.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 9999):
            if not isinstance(meta, dict):
                continue
            name = meta.get('name', '')
            field = meta.get('field', '')
            table = meta.get('table', '')
            rows_html.append(
                f'<tr><td style="padding:4px 12px;font-family:monospace">{fid}</td>'
                f'<td style="padding:4px 12px">{name}</td>'
                f'<td style="padding:4px 12px;font-family:monospace">{field}</td>'
                f'<td style="padding:4px 12px;color:#888;font-size:0.85em">{table}</td></tr>'
            )

        table_html = (
            '<table style="border-collapse:collapse;width:100%">'
            '<thead><tr style="background:#f0f0f0;font-weight:bold">'
            '<th style="padding:6px 12px;text-align:left">Field ID</th>'
            '<th style="padding:6px 12px;text-align:left">Label</th>'
            '<th style="padding:6px 12px;text-align:left">DB Column</th>'
            '<th style="padding:6px 12px;text-align:left">DB Table</th>'
            '</tr></thead><tbody>'
            + ''.join(rows_html)
            + '</tbody></table>'
        )

        self.write({
            'result_json':  json.dumps(opts, indent=2, ensure_ascii=False),
            'result_table': table_html,
            'state':        'done',
        })

        # Re-open the same wizard to show results
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'glpi.field.map',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
