{
    'name': 'GLPI Asset Sync',
    'version': '19.0.1.0.0',
    'summary': 'Pull GLPI computer assets into Odoo via REST API',
    'description': """
GLPI Asset Sync
===============
One-directional, pull-based integration that reads GLPI Computer assets via
the GLPI REST API and upserts them into the Odoo product master.

API flow
--------
initSession → (changeActiveEntities) → Computer/ batches → killSession

Upsert key priority
-------------------
1. x_glpi_id       GLPI primary integer ID
2. x_glpi_uuid     Motherboard UUID reported by inventory agent
3. x_glpi_asset_tag Inventory number / other serial

Features
--------
* Session-based auth: user_token (preferred) or HTTP Basic fallback
* App-Token header on every request
* Entity scoping with optional recursive flag
* Configurable batch size (max 200, GLPI limit)
* listSearchOptions discovery + /search/Computer forcedisplay support
* Full audit log per run (fetched / created / updated / skipped / errors)
* Scheduled cron (inactive by default — activate after configuring)
* Manual "Sync Now" server action bound to Products list and form
* Settings page under Settings > GLPI Asset Sync
    """,
    'author': 'Your Organisation',
    'website': '',
    'license': 'LGPL-3',
    'category': 'Inventory/Configuration',
    'depends': ['product', 'base_setup'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/product_asset_views.xml',
        'data/ir_cron_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}