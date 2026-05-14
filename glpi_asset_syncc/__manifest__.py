{
    'name': 'GLPI Asset Sync',
    'version': '19.0.1.0.0',
    'summary': 'Pull GLPI computer assets into Odoo via REST API with UUID upsert and audit log',
    'description': """
GLPI Asset Sync
===============
One-way integration: GLPI REST API → Odoo product master.

What it does
------------
* Opens a GLPI REST session (initSession / App-Token + User-Token or Basic auth)
* Optionally restricts to one GLPI entity (changeActiveEntities)
* Pages through all Computer records in configurable batches (max 200/request)
* Upserts into product.product using a 3-key fallback:
    1. x_glpi_id        -- GLPI primary integer ID
    2. x_glpi_uuid      -- Motherboard UUID
    3. x_glpi_asset_tag -- Inventory number / other serial
* Writes a full audit log (glpi.sync.log) per run with per-record exceptions
* Exposes a "Sync Now" server action and a scheduled cron (inactive by default)
* Test Connection button on Settings page verifies credentials instantly
* Field Discovery wizard calls listSearchOptions/Computer and renders a table
  of field IDs — use these IDs in forcedisplay when switching to the search API

Fields added to product.product
---------------------------------
x_glpi_id           Upsert key 1 — GLPI primary ID
x_glpi_uuid         Upsert key 2 — Motherboard UUID
x_glpi_asset_tag    Upsert key 3 — Inventory number / other serial
x_glpi_serial       Hardware serial number
x_glpi_manufacturer Manufacturer name
x_glpi_itemtype     Usually "Computer"
x_glpi_last_sync    Timestamp of last successful sync
x_glpi_raw_json     Raw GLPI JSON payload (debug)
    """,
    'author': 'Your Organisation',
    'website': '',
    'license': 'LGPL-3',
    'category': 'Inventory/Configuration',
    'depends': ['base','product', 'base_setup'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/product_asset_views.xml',
        'views/glpi_sync_log_views.xml',
        'wizard/glpi_field_map_views.xml',
        'data/ir_cron_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
