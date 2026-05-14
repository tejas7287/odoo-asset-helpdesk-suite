# IT Asset Requisition

![Version](https://img.shields.io/badge/version-1.1-blue)
![Category](https://img.shields.io/badge/category-Purchase-green)
![License](https://img.shields.io/badge/license-LGPL-3-orange)
![Type](https://img.shields.io/badge/type-Application-purple)

| | |
|---|---|
| **Name** | IT Asset Requisition |
| **Version** | 1.1 |
| **Category** | Purchase |
| **License** | LGPL-3 |
| **Application** | Yes |

## Description

Website IT Asset Requisition with RFQ Creation

## Functionality

### Models & Fields

#### `it.asset.requisition` — IT Asset Requisition

**File:** `models/it_asset_requisition.py`

**Fields:**

| Field | Type |
|-------|------|
| `name` | `Char` |
| `active` | `Boolean` |
| `state` | `Selection` |
| `color` | `Integer` |
| `emp_first_name` | `Char` |
| `emp_last_name` | `Char` |
| `emp_designation` | `Char` |
| `emp_department` | `Char` |
| `emp_office_site` | `Char` |
| `emp_code` | `Char` |
| `emp_location` | `Char` |
| `request_date` | `Date` |
| `manager_first_name` | `Char` |
| `manager_last_name` | `Char` |
| `manager_location` | `Char` |
| `manager_date` | `Date` |
| `manager_remarks` | `Text` |
| `email_approval` | `Boolean` |
| `hardware_product_id` | `Many2one` |
| `sim_product_id` | `Many2one` |
| `printer_product_id` | `Many2one` |
| `software_checkbox` | `Boolean` |
| `software_specify` | `Char` |
| `pda_checkbox` | `Boolean` |
| `pda_count` | `Integer` |
| `others_text` | `Text` |
| `justification_type` | `Selection` |
| `justification_text` | `Text` |
| `reqn_rcpt_date` | `Date` |
| `is_approved` | `Boolean` |
| `is_ordered` | `Boolean` |
| `is_dispatched` | `Boolean` |
| `po_num_text` | `Char` |
| `old_device_sn` | `Char` |
| `device_ageing` | `Char` |
| `make` | `Char` |
| `model_name` | `Char` |
| `ist_others` | `Char` |
| `ist_remark` | `Text` |
| `purchase_id` | `Many2one` |

**Key Methods:**

- `_compute_color()` — Computed field
- `_compute_status_booleans()` — Computed field
- `create()` — Overridden ORM method

#### Extends `it.asset.requisition, approval.request, hr.employee, product.template`

**File:** `models/it_asset_requisition_inherit.py`

**Inherits:** `it.asset.requisition`, `approval.request`, `hr.employee`, `product.template`

**Fields:**

| Field | Type |
|-------|------|
| `employee_id` | `Many2one` |
| `manager_id` | `Many2one` |
| `approval_request_id` | `Many2one` |
| `rfq_count` | `Integer` |
| `approval_count` | `Integer` |
| `it_requisition_id` | `Many2one` |
| `req_employee_id` | `Many2one` |
| `req_department` | `Char` |
| `req_designation` | `Char` |
| `req_manager_id` | `Many2one` |
| `req_hardware` | `Many2one` |
| `req_sim` | `Many2one` |
| `req_printer` | `Many2one` |
| `req_software_checkbox` | `Boolean` |
| `req_software_specify` | `Char` |
| `req_pda_checkbox` | `Boolean` |
| `req_pda_count` | `Integer` |
| `req_others_text` | `Text` |
| `req_justification_type` | `Selection` |
| `req_justification_text` | `Text` |
| `req_ist_remark` | `Text` |
| `req_manager_remarks` | `Text` |
| `emp_code` | `Char` |
| `asset_category` | `Selection` |

**Key Methods:**

- `_compute_counts()` — Computed field
- `_onchange_employee()` — Onchange handler
- `_onchange_manager()` — Onchange handler
- `action_open_rfq()` — Action/workflow method
- `_get_category()`
- `action_request_approval()` — Action/workflow method
- `action_open_approval()` — Action/workflow method
- `action_approve()` — Action/workflow method

#### Extends `purchase.order`

**File:** `models/purchase_order.py`

**Inherits:** `purchase.order`

**Fields:**

| Field | Type |
|-------|------|
| `it_asset_requisition_id` | `Many2one` |
| `emp_first_name` | `Char` |
| `emp_last_name` | `Char` |
| `emp_department` | `Char` |
| `emp_location` | `Char` |
| `manager_first_name` | `Char` |
| `manager_last_name` | `Char` |
| `manager_remarks` | `Text` |
| `justification_type` | `Selection` |
| `justification_text` | `Text` |
| `others_text` | `Text` |
| `needs_approval` | `Boolean` |

**Key Methods:**

- `button_confirm()` — Button handler

#### `it.user.access.form` — User Access Form

**File:** `models/user_access_form.py`

**Inherits:** `approval.request`, `hr.employee`, `project.task`

**Fields:**

| Field | Type |
|-------|------|
| `name` | `Char` |
| `active` | `Boolean` |
| `state` | `Selection` |
| `request_date` | `Date` |
| `employee_id` | `Many2one` |
| `first_name` | `Char` |
| `last_name` | `Char` |
| `department_location` | `Char` |
| `extension_no` | `Char` |
| `location_code` | `Char` |
| `location` | `Char` |
| `designation` | `Char` |
| `manager_id` | `Many2one` |
| `domain_account` | `Boolean` |
| `ehrms_access` | `Boolean` |
| `eiis_access` | `Boolean` |
| `elms_access` | `Boolean` |
| `md_sl_access` | `Boolean` |
| `hyperion_access` | `Boolean` |
| `sonar_access` | `Boolean` |
| `email_id_required` | `Boolean` |
| `email_id` | `Char` |
| `shared_drive_access` | `Boolean` |
| `drive_p` | `Boolean` |
| `drive_o` | `Boolean` |
| `drive_m` | `Boolean` |
| `drive_r` | `Boolean` |
| `drive_h` | `Boolean` |
| `drive_g` | `Boolean` |
| `drive_i` | `Boolean` |
| `internet_access` | `Boolean` |
| `lan_access` | `Boolean` |
| `wi_data_access` | `Boolean` |
| `guest_wifi_only` | `Boolean` |
| `user_id_text` | `Char` |
| `computer_name` | `Char` |
| `access_level` | `Char` |
| `policy_confirmed` | `Boolean` |
| `employee_signature` | `Char` |
| `department_head_name` | `Char` |
| `department_head_signature` | `Char` |
| `general_manager_name` | `Char` |
| `general_manager_signature` | `Char` |
| `ist_created_by` | `Char` |
| `ist_signature` | `Char` |
| `notes` | `Text` |
| `description` | `Html` |
| `project_id` | `Many2one` |
| `task_id` | `Many2one` |
| `approval_request_id` | `Many2one` |
| `approval_count` | `Integer` |
| `task_count` | `Integer` |
| `user_access_form_id` | `Many2one` |
| `user_access_form_count` | `Integer` |
| `user_access_employee_id` | `Many2one` |
| `user_access_project_id` | `Many2one` |
| `user_access_task_id` | `Many2one` |
| `user_access_description` | `Html` |
| `user_access_form_ids` | `One2many` |

**Key Methods:**

- `_compute_counts()` — Computed field
- `create()` — Overridden ORM method
- `write()` — Overridden ORM method
- `_onchange_employee_id()` — Onchange handler
- `_get_role_users()`
- `_get_or_create_employee_user()`
- `_get_user_access_category()`
- `_get_user_access_project()`
- `action_request_approval()` — Action/workflow method
- `action_admin_approve()` — Action/workflow method
- `_get_task_description()`
- `action_print_user_access_form()` — Action/workflow method
- `action_open_approval()` — Action/workflow method
- `action_open_task()` — Action/workflow method
- `_compute_user_access_form_count()` — Computed field
- `action_open_user_access_form()` — Action/workflow method
- `action_approve()` — Action/workflow method
- `_compute_user_access_form_count()` — Computed field
- `action_open_user_access_forms()` — Action/workflow method
- `_compute_user_access_form_count()` — Computed field
- `action_open_user_access_form()` — Action/workflow method

### Views & UI

**Form Views:** `it_asset_views.xml`, `user_access_form_views.xml`, `website_form.xml`

**List/Tree Views:** `it_asset_views.xml`, `user_access_form_views.xml`

**Menus:** `it_asset_views.xml`, `user_access_form_views.xml`

**Website/Portal Templates:**

- `asset_form` (`website_form.xml`)

### Security

**Security Groups:**

- Purchase Manager
- User Access Department Manager
- User Access General Manager

**Access Rights:** 2 model access rules defined

| Model |
|-------|
| `it.asset.requisition` |

### Web Controllers & Routes

| Route | Controller |
|-------|------------|
| `/it-asset/request` | `main.py` |
| `/it-asset/submit` | `main.py` |

### Data & Automation

**Sequences:** `ir_sequence.xml`

### Reports

- `user_access_form_report.xml`

## Dependencies

| Module | Type |
|--------|------|
| `base` | Odoo Core |
| `purchase` | Odoo Core |
| `website` | Odoo Core |
| `product` | Odoo Core |
| `hr` | Odoo Core |
| `approvals` | Odoo Core |
| `stock` | Odoo Core |
| `project` | Odoo Core |

## File Structure

```
it_asset_requisition/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── main.py
├── data/
│   └── ir_sequence.xml
├── hooks.py
├── migrations/
│   └── 1.1/
│       └── pre-migrate.py
├── models/
│   ├── __init__.py
│   ├── it_asset_requisition.py
│   ├── it_asset_requisition_inherit.py
│   ├── purchase_order.py
│   └── user_access_form.py
├── report/
│   └── user_access_form_report.xml
├── security/
│   ├── ir.model.access.csv
│   └── it_asset_security.xml
└── views/
    ├── it_asset_requisition_inherit_views.xml
    ├── it_asset_views.xml
    ├── purchase_order_views.xml
    ├── user_access_form_views.xml
    └── website_form.xml
```

## Installation

This module is part of the **[odoo-asset-helpdesk-suite](https://github.com/tejas7287/odoo-asset-helpdesk-suite)** suite.

1. Place this module in your Odoo addons directory
2. Update the apps list: **Settings** → **Apps** → **Update Apps List**
3. Search for **"IT Asset Requisition"** and click **Install**

## License

LGPL-3
