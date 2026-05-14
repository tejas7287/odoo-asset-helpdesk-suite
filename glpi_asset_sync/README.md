# glpi_asset_sync – Odoo 19 Module

Pull GLPI Computer assets into the Odoo product master via the GLPI REST API.

---

## Quick-start

### 1 · Install

Copy the `glpi_asset_sync` folder into your Odoo addons path, then:

```bash
./odoo-bin -u glpi_asset_sync -d <your_db>
```

Or use the Apps menu: enable developer mode → search **GLPI Asset Sync** → Install.

---

### 2 · Configure GLPI

In GLPI:

1. **Enable the API**  
   *Setup ▶ General ▶ API* → Enable REST API = Yes → Save.

2. **Create an Application token**  
   *Setup ▶ General ▶ API ▶ Add application token* → note the value.

3. **Create (or find) a User API token**  
   Log in as the sync user → *Preferences ▶ Remote access keys* → Generate.  
   This user must have read access to Computers in the target entity.

4. (Optional) Restrict API access by IP in the same API settings page.

---

### 3 · Configure Odoo

*Settings ▶ GLPI Asset Sync*

| Field | Example |
|---|---|
| GLPI Base URL | `https://glpi.example.com` |
| App Token | `AbCdEf123...` |
| User API Token | `XyZwWv456...` (preferred over username/password) |
| Verify SSL | enabled (disable only for self-signed certs in staging) |
| GLPI Entity ID | `0` = root entity; enter a positive integer to restrict |
| Include Sub-entities | enable to pass `is_recursive=1` |
| Batch Size | `200` (GLPI maximum per request) |

---

### 4 · Test connection

Use the **Sync Now** server action (available in the Action menu on the
Products list view) or run the following in an Odoo shell:

```python
env['product.product'].cron_sync_glpi_computers()
```

Check *Inventory ▶ Configuration ▶ GLPI Sync Logs* for the result.

---

### 5 · Activate scheduled sync

Go to *Settings ▶ Technical ▶ Automation ▶ Scheduled Actions*, find
**GLPI: Sync Computer Assets**, set it to **Active**, and adjust the
interval (default: every 15 minutes).

---

## Field mapping

| GLPI field | Odoo field | Notes |
|---|---|---|
| `id` | `x_glpi_id` | Upsert key 1 (integer) |
| `uuid` | `x_glpi_uuid` | Upsert key 2; motherboard UUID |
| `otherserial` / `inventory_number` / `serial` | `x_glpi_asset_tag` | Upsert key 3 |
| `name` | `name` | Product name |
| `itemtype` | `x_glpi_itemtype` | Usually "Computer" |
| *(sync time)* | `x_glpi_last_sync` | Set by Odoo |
| *(full row)* | `x_glpi_raw_json` | Debug snapshot |

---

## Using the Search API instead of the Collection API

If the collection API (`/Computer/`) does not return the exact field names
you need, switch to the search API:

```python
# 1 – Discover field IDs for your GLPI version
client.init_session()
opts = client.list_search_options("Computer")
# Look for "uuid", "inventory number", "other serial number" in opts

# 2 – Fetch with explicit forcedisplay
results = client.search_computers(
    forcedisplay=[1, 2, 65, 160],  # replace with IDs from step 1
)
# results["data"] contains the rows
```

Then update `_upsert_from_glpi_row` to reference the numeric field IDs
returned by the search API instead of named keys.

---

## Restarting after a failure

1. Check *GLPI Sync Logs* for the error message.
2. If the session was not closed (GLPI shows an active session), either wait
   for the GLPI session timeout or close it manually in GLPI.
3. Fix the root cause (connectivity, credentials, GLPI downtime).
4. Trigger **Sync Now** or wait for the next cron run.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `GLPI Base URL is not configured` | Settings not saved | Save settings in Odoo |
| `HTTP 401` | Wrong token or App-Token missing | Check App-Token and User Token |
| `HTTP 400 ERROR_RANGE_EXCEED_TOTAL` | Normal – last page reached | Handled automatically; not a bug |
| Duplicate UUID constraint error | Two GLPI records with same UUID | Clean GLPI data; check UUID lock setting |
| Records created as wrong type | `type='consu'` default | Override `vals.setdefault('type', ...)` in `_upsert_from_glpi_row` |
| SSL error | Self-signed certificate | Disable *Verify SSL* in settings (staging only) |

---

## Module structure

```
glpi_asset_sync/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── glpi_config.py        # res.config.settings extension
│   ├── product_asset.py      # GLPI fields + sync engine
│   └── glpi_sync_log.py      # Audit log model
├── services/
│   ├── __init__.py
│   └── glpi_client.py        # GLPI REST API client
├── data/
│   └── ir_cron_data.xml      # Scheduled action + server action
├── security/
│   └── ir.model.access.csv
└── views/
    ├── res_config_settings_views.xml
    └── product_asset_views.xml
```
