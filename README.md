# Odoo Asset Management & Helpdesk Suite

Complete asset lifecycle and IT service management for Odoo — from asset tracking and depreciation through helpdesk ticketing, IT requisitions, and GLPI integration.

## Workflow & Dependency Diagram

```
┌─────────────────────────┐
│    asset_management      │
│    (Asset Management)    │
│    Track, depreciate,    │
│    maintain, transfer    │
└───────────┬─────────────┘
            │ depends
            ▼
┌─────────────────────────┐
│     helpdesk_mgmt        │
│     (Helpdesk Mgmt)      │
│     Tickets, teams,      │
│     SLA, portal          │
└─────────────────────────┘

┌─────────────────────────┐  ┌──────────────────────────┐
│  it_asset_requisition    │  │   glpi_asset_sync        │
│  (IT Asset Requisition)  │  │   (GLPI Asset Sync v1)   │
│  Website form → RFQ      │  │   Pull GLPI computers    │
│  with approvals          │  │   into Odoo products     │
└─────────────────────────┘  └──────────────────────────┘

                             ┌──────────────────────────┐
                             │   glpi_asset_syncc        │
                             │   (GLPI Asset Sync v2)    │
                             │   Enhanced: UUID upsert,  │
                             │   audit log, field map    │
                             └──────────────────────────┘
```

## Modules Included

| # | Module | Name | Description |
|---|--------|------|-------------|
| 1 | `asset_management/` | Asset Management | Manage company assets, transfers, maintenance, and depreciation with detailed reports. |
| 2 | `helpdesk_mgmt/` | Helpdesk Management | Helpdesk ticket management with teams, stages, categories, and customer portal. |
| 3 | `it_asset_requisition/` | IT Asset Requisition | Website IT asset requisition form with approval workflow and RFQ creation. |
| 4 | `glpi_asset_sync/` | GLPI Asset Sync | Pull GLPI computer assets into Odoo via REST API. |
| 5 | `glpi_asset_syncc/` | GLPI Asset Sync v2 | Enhanced GLPI sync with UUID upsert, audit logging, and field discovery wizard. |

## Installation Order

1. `asset_management` — Core asset management
2. `helpdesk_mgmt` — Depends on `asset_management`
3. `it_asset_requisition` — Independent IT asset flow
4. `glpi_asset_sync` or `glpi_asset_syncc` — Choose one (v2 recommended)

## Setup

```bash
git clone https://github.com/tejas7287/odoo-asset-helpdesk-suite.git

# Add to odoo.conf
addons_path = /path/to/odoo/addons,/path/to/odoo-asset-helpdesk-suite
```

## License

LGPL-3 / AGPL-3 — See individual module manifests for specific licensing.
