# Asset Management

![Version](https://img.shields.io/badge/version-1.0-blue)
![Category](https://img.shields.io/badge/category-Operations-green)
![License](https://img.shields.io/badge/license-LGPL-3-orange)
![Type](https://img.shields.io/badge/type-Application-purple)

| | |
|---|---|
| **Name** | Asset Management |
| **Version** | 1.0 |
| **Category** | Operations |
| **Author** | WebbyCrown Solutions |
| **License** | LGPL-3 |
| **Application** | Yes |
| **Website** | https://www.webbycrown.com |

## Description

Manage company assets, transfers, maintenance, and depreciation.

Streamline your asset lifecycle management with our comprehensive Odoo module. Track assets, automate depreciation, manage maintenance, and handle transfers effortlessly. Generate detailed reports, monitor warranties, and optimize asset utilization. User-friendly interface ensures easy adoption. Suitable for businesses of all sizes, this module empowers you to make informed decisions and maximize the value of your assets.

## Functionality

### Models & Fields

#### `asset.management` — Asset Management

**File:** `models/asset_management.py`

**Fields:**

| Field | Type |
|-------|------|
| `active` | `Boolean` |
| `name` | `Char` |
| `barcode` | `Char` |
| `product_id` | `Many2one` |
| `asset_type_id` | `Many2one` |
| `model_type` | `Selection` |
| `initial_stock` | `Integer` |
| `current_stock` | `Integer` |
| `active_transfers` | `Integer` |
| `depreciation_apply` | `Boolean` |
| `expired_warranty_date` | `Date` |
| `vendor_id` | `Many2one` |
| `invoice_date` | `Date` |
| `amount` | `Float` |
| `current_amount` | `Float` |
| `total_depreciation_amount` | `Float` |
| `total_maintenance_amount` | `Float` |
| `status` | `Selection` |
| `document_ids` | `Many2many` |
| `tag_ids` | `Many2many` |
| `transfer_ids` | `One2many` |
| `maintenance_ids` | `One2many` |
| `depreciation_ids` | `One2many` |
| `last_depreciation_date` | `Date` |
| `transfer_count` | `Integer` |
| `maintenance_count` | `Integer` |
| `depreciation_count` | `Integer` |
| `invoice_id` | `Many2one` |
| `months_left` | `Integer` |
| `assigned_user` | `Char` |
| `assign_by` | `Char` |
| `remaining_warranty` | `Char` |
| `warranty_status` | `Char` |
| `color` | `Integer` |
| `asset_id` | `Many2one` |
| `transfer_employee_id` | `Many2one` |
| `assign_date` | `Date` |
| `return_date` | `Date` |
| `transfer_code` | `Char` |
| `stock_qty` | `Integer` |
| `maintenance_vendor_id` | `Many2one` |
| `maintenance_status` | `Selection` |
| `maintenance_amount` | `Float` |
| `file_name` | `Char` |
| `document` | `Binary` |
| `depreciation_amount` | `Float` |
| `entry_date` | `Date` |
| `notes` | `Text` |
| `created_by` | `Many2one` |
| `depreciation_frequency` | `Selection` |
| `depreciation_method` | `Selection` |
| `depreciation_rate` | `Float` |
| `depreciation_start_delay` | `Integer` |
| `depreciation_basis` | `Selection` |
| `maximum_depreciation_entries` | `Integer` |

**Key Methods:**

- `_compute_active_transfers()` — Computed field
- `_compute_current_stock()` — Computed field
- `_compute_months_left()` — Computed field
- `_compute_assigned_user()` — Computed field
- `_compute_all_count()` — Computed field
- `_compute_current_amount()` — Computed field
- `_compute_total_depreciation_amount()` — Computed field
- `_compute_total_maintenance_amount()` — Computed field
- `create()` — Overridden ORM method
- `action_open_label_layout()` — Action/workflow method
- `create()` — Overridden ORM method
- `create()` — Overridden ORM method

#### Extends `res.partner, hr.employee, hr.work.location`

**File:** `models/res_partner.py`

**Inherits:** `res.partner`, `hr.employee`, `hr.work.location`

**Fields:**

| Field | Type |
|-------|------|
| `is_asset_vendor` | `Boolean` |
| `asset_count` | `Integer` |
| `employee_count` | `Integer` |

**Key Methods:**

- `create()` — Overridden ORM method
- `write()` — Overridden ORM method
- `_get_current_assets()`
- `_compute_asset_count()` — Computed field
- `action_view_assets()` — Action/workflow method
- `_get_location_assets()`
- `_compute_counts()` — Computed field
- `action_view_employees()` — Action/workflow method
- `action_view_assets()` — Action/workflow method

#### `asset.stock.movement.report` — Asset Stock Movement Analysis

**File:** `models/stock_movement_report.py`

**Fields:**

| Field | Type |
|-------|------|
| `asset_id` | `Many2one` |
| `asset_name` | `Char` |
| `employee_id` | `Many2one` |
| `date` | `Date` |
| `movement_type` | `Selection` |
| `user_id` | `Many2one` |

#### `asset.vendor` — Asset Vendor

**File:** `models/vendors.py`

**Fields:**

| Field | Type |
|-------|------|
| `name` | `Char` |
| `address` | `Char` |
| `location` | `Char` |
| `seller` | `Char` |
| `contact_phone` | `Char` |
| `contact_email` | `Char` |
| `additional_services` | `Boolean` |
| `repair_service` | `Boolean` |
| `maintenance_service` | `Boolean` |

#### `asset.label.layout` — Choose the sheet layout to print the asset labels

**File:** `wizard/asset_label_wizard.py`

**Fields:**

| Field | Type |
|-------|------|
| `print_format` | `Selection` |
| `custom_quantity` | `Integer` |
| `asset_ids` | `Many2many` |
| `custom_columns` | `Integer` |
| `custom_rows` | `Integer` |
| `show_price` | `Boolean` |
| `red_band_color` | `Char` |
| `rows` | `Integer` |
| `columns` | `Integer` |

**Key Methods:**

- `_compute_dimensions()` — Computed field

### Views & UI

**Form Views:** `asset_vendor_views.xml`, `asset_views.xml`

**List/Tree Views:** `asset_vendor_views.xml`, `asset_views.xml`, `stock_movement_report_views.xml`

**Kanban Views:** `asset_views.xml`

**Search Views:** `asset_views.xml`, `stock_movement_report_views.xml`

**Menus:** `asset_report.xml`, `asset_vendor_views.xml`, `asset_views.xml`, `stock_movement_report_views.xml`

### Security

**Security Groups:**

- User
- Administrator
- User
- Administrator
- Administrator
- User
- Administrator
- User
- Administrator
- User

**Access Rights:** 16 model access rules defined

| Model |
|-------|
| `asset.management` |
| `asset.transfer.entry.user` |
| `asset.transfer.entry.assets.user` |
| `asset.maintenance.entry.user` |
| `asset.maintenance.entry.assets.user` |
| `asset.depreciation.entry.user` |
| `asset.depreciation.entry.assets.user` |
| `asset.vendor` |
| `asset.vendor.assets.user` |
| `asset.type.user` |
| `asset.tag.user` |
| `asset.tag.admin` |
| `asset.tag.system` |
| `asset.stock.movement.report.user` |
| `asset.stock.movement.report.admin` |
| `asset.label.layout` |

**Record Rules:** `security.xml`

### Data & Automation

**Sequences:** `sequence.xml`

**Scheduled Actions (Cron):** `sequence.xml`

**Other Data:** `demo_data.xml`

### Reports

- `asset_label_report.xml`
- `asset_label_templates.xml`
- `asset_template_templates.xml`

### Frontend Assets

**SCSS:**

- `static/src/scss/report_label_sheet.scss`

## Dependencies

| Module | Type |
|--------|------|
| `base` | Odoo Core |
| `product` | Odoo Core |
| `hr` | Odoo Core |
| `account` | Odoo Core |

## File Structure

```
asset_management/
├── __init__.py
├── __manifest__.py
├── data/
│   ├── demo_data.xml
│   ├── demo_summary.md
│   └── sequence.xml
├── doc/
│   └── index.rst
├── i18n/
│   ├── README.md
│   ├── ar.po
│   ├── de.po
│   ├── es.po
│   ├── es_ES.po
│   ├── fr.po
│   ├── it.po
│   ├── nl.po
│   ├── pt.po
│   ├── tr.po
│   └── update_translations.py
├── models/
│   ├── __init__.py
│   ├── asset_management.py
│   ├── res_partner.py
│   ├── stock_movement_report.py
│   └── vendors.py
├── report/
│   ├── __init__.py
│   ├── asset_label_report.py
│   ├── asset_label_report.xml
│   ├── asset_label_templates.xml
│   └── asset_template_templates.xml
├── security/
│   ├── ir.model.access.csv
│   └── security.xml
├── static/
│   ├── description/
│   │   ├── advance_hr.png
│   │   ├── advance_project_app.png
│   │   ├── button.png
│   │   ├── formate_screenshot.gif
│   │   ├── formate_screenshot_.png
│   │   ├── formate_screenshot_1.png
│   │   ├── formate_screenshot_2.png
│   │   ├── formate_screenshot_3.png
│   │   ├── formate_screenshot_4.png
│   │   ├── formate_screenshot_5.png
│   │   ├── formate_screenshot_6.png
│   │   ├── formate_screenshot_7.png
│   │   ├── formate_screenshot_8.png
│   │   ├── formate_screenshot_9.png
│   │   ├── icon.png
│   │   ├── index.html
│   │   ├── info-icon-1.png
│   │   ├── info-icon-2.png
│   │   ├── info-icon-3.png
│   │   ├── info-icon-4.png
│   │   ├── logo.png
│   │   ├── main_screenshot.png
│   │   ├── play.png
│   │   └── profilt_loss_app.png
│   └── src/
│       └── scss/
├── views/
│   ├── asset_report.xml
│   ├── asset_vendor_views.xml
│   ├── asset_views.xml
│   ├── res_partner.xml
│   └── stock_movement_report_views.xml
└── wizard/
    ├── __init__.py
    ├── asset_label_wizard.py
    └── asset_label_wizard_view.xml
```

## Installation

This module is part of the **[odoo-asset-helpdesk-suite](https://github.com/tejas7287/odoo-asset-helpdesk-suite)** suite.

1. Place this module in your Odoo addons directory
2. Update the apps list: **Settings** → **Apps** → **Update Apps List**
3. Search for **"Asset Management"** and click **Install**

## License

LGPL-3
