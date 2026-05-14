"""
models/glpi_config.py
=====================
Extends ``res.config.settings`` to expose all GLPI connection and sync
parameters in the Settings UI under **Settings > GLPI Asset Sync**.

All values are stored as ``ir.config_parameter`` (system parameters) so they
survive module upgrades and are readable without a transient record.

Parameters
----------
Connection
    base_url, app_token, user_token, username, password, verify_ssl

Sync scope
    entity_id, entity_recursive, batch_size
"""

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # -----------------------------------------------------------------------
    # Connection
    # -----------------------------------------------------------------------

    glpi_base_url = fields.Char(
        string='GLPI Base URL',
        config_parameter='glpi_asset_sync.base_url',
        help=(
            'Root URL of the GLPI server.\n'
            'Example: https://glpi.example.com\n'
            'Do NOT include /apirest.php or a trailing slash.'
        ),
    )
    glpi_app_token = fields.Char(
        string='App Token',
        config_parameter='glpi_asset_sync.app_token',
        help=(
            'GLPI Application token — required on every API request.\n'
            'Create in GLPI > Setup > General > API > Add application token.'
        ),
    )
    glpi_user_token = fields.Char(
        string='User API Token',
        config_parameter='glpi_asset_sync.user_token',
        help=(
            'Preferred authentication method.\n'
            'Generate in GLPI user profile > Remote access keys.\n'
            'Leave blank to fall back to username / password.'
        ),
    )
    glpi_username = fields.Char(
        string='Username',
        config_parameter='glpi_asset_sync.username',
        help='GLPI username. Used only when User API Token is blank.',
    )
    glpi_password = fields.Char(
        string='Password',
        config_parameter='glpi_asset_sync.password',
        help='GLPI password. Used only when User API Token is blank.',
    )
    glpi_verify_ssl = fields.Boolean(
        string='Verify SSL Certificate',
        default=True,
        config_parameter='glpi_asset_sync.verify_ssl',
        help=(
            'Validate the server TLS certificate.\n'
            'Disable ONLY for self-signed certificates in staging environments.'
        ),
    )

    # -----------------------------------------------------------------------
    # Sync scope
    # -----------------------------------------------------------------------

    glpi_entity_id = fields.Integer(
        string='GLPI Entity ID',
        default=0,
        config_parameter='glpi_asset_sync.entity_id',
        help=(
            'Restrict sync to a specific GLPI entity.\n'
            '0 = root entity (syncs everything the API user can see).\n'
            'Positive integer = restrict to that entity only.'
        ),
    )
    glpi_entity_recursive = fields.Boolean(
        string='Include Sub-entities',
        default=False,
        config_parameter='glpi_asset_sync.entity_recursive',
        help=(
            'When an Entity ID is set, also include all child entities.\n'
            'Passes is_recursive=1 to the GLPI changeActiveEntities call.'
        ),
    )
    glpi_batch_size = fields.Integer(
        string='Batch Size',
        default=200,
        config_parameter='glpi_asset_sync.batch_size',
        help=(
            'Number of Computer records fetched per API request.\n'
            'Maximum allowed by GLPI is 200. Lower this if you see timeouts.'
        ),
    )