"""
glpi_config.py
==============
Extends res.config.settings with all GLPI connection parameters.
All values persist via ir.config_parameter (system parameters).

Includes an action_test_connection method that opens a real GLPI session,
calls getMyProfiles, and closes the session — giving instant feedback
without running a full sync.
"""

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from ..services.glpi_client import GLPIClient, GLPIApiError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # ── Connection ────────────────────────────────────────────────────
    glpi_base_url = fields.Char(
        string='GLPI Base URL',
        help='Base URL of your GLPI server, e.g. http://glpi.example.com\n'
             'Do NOT append /apirest.php — this is added automatically.',
        config_parameter='glpi_asset_sync.base_url',
    )
    glpi_app_token = fields.Char(
        string='App Token',
        help='Application token from GLPI: Setup ▶ General ▶ API ▶ Add application token.\n'
             'Required for every API call.',
        config_parameter='glpi_asset_sync.app_token',
    )
    glpi_user_token = fields.Char(
        string='User API Token',
        help='Preferred authentication method. No password is sent over the wire.\n'
             'Generate in GLPI: user profile ▶ Remote access keys ▶ Regenerate.',
        config_parameter='glpi_asset_sync.user_token',
    )
    glpi_username = fields.Char(
        string='Username',
        help='HTTP Basic auth username. Used only when User API Token is blank.',
        config_parameter='glpi_asset_sync.username',
    )
    glpi_password = fields.Char(
        string='Password',
        help='HTTP Basic auth password. Used only when User API Token is blank.',
        config_parameter='glpi_asset_sync.password',
    )
    glpi_verify_ssl = fields.Boolean(
        string='Verify SSL Certificate',
        default=True,
        help='Keep enabled in production. Disable only for self-signed certificates '
             'in isolated staging environments.',
        config_parameter='glpi_asset_sync.verify_ssl',
    )

    # ── Sync scope ────────────────────────────────────────────────────
    glpi_entity_id = fields.Integer(
        string='GLPI Entity ID',
        default=0,
        help='Set to 0 to sync from the root entity.\n'
             'Enter a positive integer to restrict sync to one specific entity.',
        config_parameter='glpi_asset_sync.entity_id',
    )
    glpi_entity_recursive = fields.Boolean(
        string='Include Sub-entities',
        default=False,
        help='When enabled, passes is_recursive=1 to changeActiveEntities '
             'so child entities are included.',
        config_parameter='glpi_asset_sync.entity_recursive',
    )
    glpi_batch_size = fields.Integer(
        string='Batch Size',
        default=200,
        help='Number of Computer records fetched per API request. '
             'Maximum allowed by GLPI is 200.',
        config_parameter='glpi_asset_sync.batch_size',
    )

    # ── Test connection button ────────────────────────────────────────

    def action_test_glpi_connection(self):
        """
        Verify connectivity without running a full sync.
        Opens a real GLPI session, calls getMyProfiles, and closes the session.
        """
        base_url = self.glpi_base_url
        if not base_url:
            raise UserError(_('Please enter a GLPI Base URL before testing.'))

        client = GLPIClient(
            base_url=base_url,
            app_token=self.glpi_app_token,
            user_token=self.glpi_user_token,
            username=self.glpi_username,
            password=self.glpi_password,
            verify_ssl=self.glpi_verify_ssl,
        )
        try:
            client.test_connection()
        except GLPIApiError as exc:
            raise UserError(
                _('GLPI connection test failed:\n%s') % str(exc)
            ) from exc

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Connection Successful'),
                'message': _('Odoo can reach your GLPI server and authenticate successfully.'),
                'type': 'success',
                'sticky': False,
            },
        }
