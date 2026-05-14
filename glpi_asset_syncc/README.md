# GLPI Asset Sync

![Version](https://img.shields.io/badge/version-19.0.1.0.0-blue)
![Category](https://img.shields.io/badge/category-Inventory%2FConfiguration-green)
![License](https://img.shields.io/badge/license-LGPL-3-orange)
![Type](https://img.shields.io/badge/type-Application-purple)

| | |
|---|---|
| **Name** | GLPI Asset Sync |
| **Version** | 19.0.1.0.0 |
| **Category** | Inventory/Configuration |
| **Author** | Your Organisation |
| **License** | LGPL-3 |
| **Application** | Yes |

## Description

Pull GLPI computer assets into Odoo via REST API with UUID upsert and audit log

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

## Functionality

### Models & Fields

#### Extends `res.config.settings`

**File:** `models/glpi_config.py`

**Inherits:** `res.config.settings`

**Fields:**

| Field | Type |
|-------|------|
| `glpi_base_url` | `Char` |
| `glpi_app_token` | `Char` |
| `glpi_user_token` | `Char` |
| `glpi_username` | `Char` |
| `glpi_password` | `Char` |
| `glpi_verify_ssl` | `Boolean` |
| `glpi_entity_id` | `Integer` |
| `glpi_entity_recursive` | `Boolean` |
| `glpi_batch_size` | `Integer` |

**Key Methods:**

- `action_test_glpi_connection()` — Action/workflow method

#### `glpi.sync.log` — GLPI Asset Sync Log

**File:** `models/glpi_sync_log.py`

**Fields:**

| Field | Type |
|-------|------|
| `sync_start` | `Datetime` |
| `sync_end` | `Datetime` |
| `state` | `Selection` |
| `triggered_by` | `Selection` |
| `fetched` | `Integer` |
| `created` | `Integer` |
| `updated` | `Integer` |
| `skipped` | `Integer` |
| `error_count` | `Integer` |
| `error_message` | `Text` |
| `exceptions` | `Text` |
| `duration_seconds` | `Float` |

**Key Methods:**

- `_compute_duration()` — Computed field

#### Extends `product.product`

**File:** `models/product_asset.py`

**Inherits:** `product.product`

**Fields:**

| Field | Type |
|-------|------|
| `x_glpi_id` | `Integer` |
| `x_glpi_itemtype` | `Char` |
| `x_glpi_uuid` | `Char` |
| `x_glpi_asset_tag` | `Char` |
| `x_glpi_serial` | `Char` |
| `x_glpi_manufacturer` | `Char` |
| `x_glpi_last_sync` | `Datetime` |
| `x_glpi_raw_json` | `Text` |

**Key Methods:**

- `action_sync_glpi_now()` — Action/workflow method

#### `glpi.field.map` — GLPI Computer Field Discovery

**File:** `wizard/glpi_field_map.py`

**Fields:**

| Field | Type |
|-------|------|
| `itemtype` | `Char` |
| `result_json` | `Text` |
| `result_table` | `Html` |
| `state` | `Selection` |

**Key Methods:**

- `_get_client()`
- `action_fetch_fields()` — Action/workflow method

### Views & UI

**Form Views:** `glpi_sync_log_views.xml`, `product_asset_views.xml`

**List/Tree Views:** `glpi_sync_log_views.xml`

**Menus:** `glpi_sync_log_views.xml`, `product_asset_views.xml`

### Security

**Access Rights:** 3 model access rules defined

| Model |
|-------|
| `glpi.sync.log admin` |
| `glpi.sync.log user` |
| `glpi.field.map admin` |

### Data & Automation

**Scheduled Actions (Cron):** `ir_cron_data.xml`

## Dependencies

| Module | Type |
|--------|------|
| `base` | Odoo Core |
| `product` | Odoo Core |
| `base_setup` | Odoo Core |

## File Structure

```
glpi_asset_syncc/
├── __init__.py
├── __manifest__.py
├── data/
│   └── ir_cron_data.xml
├── models/
│   ├── __init__.py
│   ├── glpi_config.py
│   ├── glpi_sync_log.py
│   └── product_asset.py
├── security/
│   └── ir.model.access.csv
├── services/
│   ├── __init__.py
│   └── glpi_client.py
├── views/
│   ├── glpi_sync_log_views.xml
│   ├── product_asset_views.xml
│   └── res_config_settings_views.xml
└── wizard/
    ├── __init__.py
    ├── glpi_field_map.py
    └── glpi_field_map_views.xml
```

## Installation

This module is part of the **[odoo-asset-helpdesk-suite](https://github.com/tejas7287/odoo-asset-helpdesk-suite)** suite.

1. Place this module in your Odoo addons directory
2. Update the apps list: **Settings** → **Apps** → **Update Apps List**
3. Search for **"GLPI Asset Sync"** and click **Install**

## License

LGPL-3
