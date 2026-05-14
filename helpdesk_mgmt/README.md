# Helpdesk Management

![Version](https://img.shields.io/badge/version-1.0-blue)
![Category](https://img.shields.io/badge/category-After-Sales-green)
![License](https://img.shields.io/badge/license-AGPL-3-orange)
![Type](https://img.shields.io/badge/type-Application-purple)

| | |
|---|---|
| **Name** | Helpdesk Management |
| **Version** | 1.0 |
| **Category** | After-Sales |
| **Author** | AdaptiveCity, Tecnativa, ForgeFlow, C2i Change 2 Improve, Domatix, Factor Libre, SDi Soluciones, Odoo Community Association (OCA) |
| **License** | AGPL-3 |
| **Application** | Yes |
| **Website** | https://github.com/OCA/helpdesk |

## Description

Helpdesk

## Functionality

### Models & Fields

#### Extends `helpdesk.ticket, hr.employee, asset.management`

**File:** `models/field.py`

**Inherits:** `helpdesk.ticket`, `hr.employee`, `asset.management`

**Fields:**

| Field | Type |
|-------|------|
| `asset_ids` | `Many2many` |
| `employee_id` | `Many2one` |
| `ticket_ids` | `One2many` |
| `ticket_count` | `Integer` |
| `current_employee_id` | `Many2one` |

**Key Methods:**

- `_compute_employee()` — Computed field
- `_onchange_user_id()` — Onchange handler
- `_compute_ticket_count()` — Computed field
- `action_view_tickets()` — Action/workflow method
- `_compute_current_employee()` — Computed field
- `_compute_ticket_count()` — Computed field
- `action_view_tickets()` — Action/workflow method

#### `helpdesk.ticket` — Helpdesk Ticket

**File:** `models/helpdesk_ticket.py`

**Inherits:** `mail.thread.cc`, `mail.activity.mixin`, `portal.mixin`, `mail.tracking.duration.mixin`

**Fields:**

| Field | Type |
|-------|------|
| `number` | `Char` |
| `name` | `Char` |
| `description` | `Html` |
| `user_id` | `Many2one` |
| `user_ids` | `Many2many` |
| `stage_id` | `Many2one` |
| `partner_id` | `Many2one` |
| `commercial_partner_id` | `Many2one` |
| `partner_name` | `Char` |
| `partner_email` | `Char` |
| `last_stage_update` | `Datetime` |
| `assigned_date` | `Datetime` |
| `closed_date` | `Datetime` |
| `closed` | `Boolean` |
| `unattended` | `Boolean` |
| `tag_ids` | `Many2many` |
| `company_id` | `Many2one` |
| `channel_id` | `Many2one` |
| `category_id` | `Many2one` |
| `team_id` | `Many2one` |
| `priority` | `Selection` |
| `attachment_ids` | `One2many` |
| `color` | `Integer` |
| `kanban_state` | `Selection` |
| `sequence` | `Integer` |
| `active` | `Boolean` |
| `duplicate_id` | `Many2one` |
| `duplicate_ids` | `One2many` |
| `duplicate_count` | `Integer` |
| `duplicate_tracking_enabled` | `Boolean` |

**Key Methods:**

- `_compute_stage_id()` — Computed field
- `_compute_user_id()` — Computed field
- `_compute_team_id()` — Computed field
- `_compute_duplicate_count()` — Computed field
- `action_open_duplicate_wizard()` — Action/workflow method
- `action_view_duplicates()` — Action/workflow method
- `_compute_display_name()` — Computed field
- `_onchange_partner_id()` — Onchange handler
- `create()` — Overridden ORM method
- `write()` — Overridden ORM method
- `action_duplicate_tickets()` — Action/workflow method
- `_compute_access_url()` — Computed field

#### `helpdesk.ticket.category` — Helpdesk Ticket Category

**File:** `models/helpdesk_ticket_category.py`

**Fields:**

| Field | Type |
|-------|------|
| `sequence` | `Integer` |
| `active` | `Boolean` |
| `name` | `Char` |
| `company_id` | `Many2one` |
| `parent_id` | `Many2one` |
| `child_id` | `One2many` |
| `parent_path` | `Char` |
| `complete_name` | `Char` |
| `show_in_portal` | `Boolean` |

**Key Methods:**

- `_compute_complete_name()` — Computed field

#### `helpdesk.ticket.channel` — Helpdesk Ticket Channel

**File:** `models/helpdesk_ticket_channel.py`

**Fields:**

| Field | Type |
|-------|------|
| `sequence` | `Integer` |
| `name` | `Char` |
| `active` | `Boolean` |
| `company_id` | `Many2one` |

#### `helpdesk.ticket.stage` — Helpdesk Ticket Stage

**File:** `models/helpdesk_ticket_stage.py`

**Fields:**

| Field | Type |
|-------|------|
| `name` | `Char` |
| `description` | `Html` |
| `sequence` | `Integer` |
| `active` | `Boolean` |
| `unattended` | `Boolean` |
| `closed` | `Boolean` |
| `close_from_portal` | `Boolean` |
| `mail_template_id` | `Many2one` |
| `fold` | `Boolean` |
| `company_id` | `Many2one` |
| `team_ids` | `Many2many` |

**Key Methods:**

- `_onchange_closed()` — Onchange handler

#### `helpdesk.ticket.tag` — Helpdesk Ticket Tag

**File:** `models/helpdesk_ticket_tag.py`

**Fields:**

| Field | Type |
|-------|------|
| `sequence` | `Integer` |
| `name` | `Char` |
| `color` | `Integer` |
| `active` | `Boolean` |
| `company_id` | `Many2one` |

#### `helpdesk.ticket.team` — Helpdesk Ticket Team

**File:** `models/helpdesk_ticket_team.py`

**Inherits:** `mail.thread`, `mail.alias.mixin`

**Fields:**

| Field | Type |
|-------|------|
| `sequence` | `Integer` |
| `name` | `Char` |
| `user_ids` | `Many2many` |
| `active` | `Boolean` |
| `category_ids` | `Many2many` |
| `company_id` | `Many2one` |
| `user_id` | `Many2one` |
| `alias_id` | `Many2one` |
| `color` | `Integer` |
| `ticket_ids` | `One2many` |
| `todo_ticket_count` | `Integer` |
| `todo_ticket_count_unassigned` | `Integer` |
| `todo_ticket_count_unattended` | `Integer` |
| `todo_ticket_count_high_priority` | `Integer` |
| `show_in_portal` | `Boolean` |
| `parent_id` | `Many2one` |
| `complete_name` | `Char` |
| `parent_path` | `Char` |

**Key Methods:**

- `_compute_complete_name()` — Computed field
- `_get_applicable_stages()`
- `_compute_todo_tickets()` — Computed field

#### Extends `ir.http`

**File:** `models/ir_http.py`

**Inherits:** `ir.http`

**Key Methods:**

- `_get_translation_frontend_modules_name()`

#### `helpdesk.ticket.stage`

**File:** `models/res_company.py`

**Inherits:** `res.company`

**Fields:**

| Field | Type |
|-------|------|
| `helpdesk_mgmt_portal_select_team` | `Boolean` |
| `helpdesk_mgmt_portal_team_id_required` | `Boolean` |
| `helpdesk_mgmt_portal_category_id_required` | `Boolean` |
| `helpdesk_mgmt_duplicate_tracking` | `Boolean` |
| `helpdesk_mgmt_duplicate_ticket_stage_id` | `Many2one` |
| `helpdesk_mgmt_ticket_auto_assign` | `Boolean` |

#### Extends `res.config.settings`

**File:** `models/res_config_settings.py`

**Inherits:** `res.config.settings`

**Fields:**

| Field | Type |
|-------|------|
| `helpdesk_mgmt_portal_select_team` | `Boolean` |
| `helpdesk_mgmt_portal_team_id_required` | `Boolean` |
| `helpdesk_mgmt_portal_category_id_required` | `Boolean` |
| `helpdesk_mgmt_duplicate_tracking` | `Boolean` |
| `helpdesk_mgmt_duplicate_ticket_stage_id` | `Many2one` |
| `helpdesk_mgmt_ticket_auto_assign` | `Boolean` |

#### `helpdesk.ticket`

**File:** `models/res_partner.py`

**Inherits:** `res.partner`

**Fields:**

| Field | Type |
|-------|------|
| `helpdesk_ticket_ids` | `One2many` |
| `helpdesk_ticket_count` | `Integer` |
| `helpdesk_ticket_active_count` | `Integer` |
| `helpdesk_ticket_count_string` | `Char` |

**Key Methods:**

- `_compute_helpdesk_ticket_count()` — Computed field
- `action_view_helpdesk_tickets()` — Action/workflow method

#### `helpdesk.ticket.team`

**File:** `models/res_users.py`

**Inherits:** `res.users`

**Fields:**

| Field | Type |
|-------|------|
| `helpdesk_team_ids` | `Many2many` |

#### `helpdesk.ticket.duplicate.wizard` — helpdesk Ticket Duplicate Wizard

**File:** `wizards/helpdesk_ticket_duplicate_wizard.py`

**Fields:**

| Field | Type |
|-------|------|
| `ticket_id` | `Many2one` |
| `duplicate_of_id` | `Many2one` |
| `target_stage_id` | `Many2one` |

**Key Methods:**

- `action_confirm()` — Action/workflow method

### Views & UI

**Form Views:** `helpdesk_ticket_category_views.xml`, `helpdesk_ticket_channel_views.xml`, `helpdesk_ticket_menu.xml`, `helpdesk_ticket_stage_views.xml`, `helpdesk_ticket_tag_views.xml`, `helpdesk_ticket_team_views.xml`, `helpdesk_ticket_templates.xml`, `helpdesk_ticket_views.xml`, `res_config_settings_views.xml`

**List/Tree Views:** `helpdesk_ticket_category_views.xml`, `helpdesk_ticket_channel_views.xml`, `helpdesk_ticket_stage_views.xml`, `helpdesk_ticket_tag_views.xml`, `helpdesk_ticket_team_views.xml`, `helpdesk_ticket_views.xml`

**Kanban Views:** `helpdesk_dashboard_views.xml`, `helpdesk_ticket_team_views.xml`, `helpdesk_ticket_views.xml`

**Search Views:** `helpdesk_ticket_category_views.xml`, `helpdesk_ticket_channel_views.xml`, `helpdesk_ticket_stage_views.xml`, `helpdesk_ticket_tag_views.xml`, `helpdesk_ticket_team_views.xml`, `helpdesk_ticket_views.xml`

**Menus:** `helpdesk_ticket_menu.xml`

**Website/Portal Templates:**

- `portal.portal_breadcrumbs` (`helpdesk_ticket_templates.xml`)
- `portal_ticket_new_button` (`helpdesk_ticket_templates.xml`)
- `portal.portal_docs_entry` (`helpdesk_ticket_templates.xml`)
- `portal.portal_my_home` (`helpdesk_ticket_templates.xml`)
- `portal.portal_searchbar` (`helpdesk_ticket_templates.xml`)
- `portal_my_tickets` (`helpdesk_ticket_templates.xml`)
- `portal_ticket_list` (`helpdesk_ticket_templates.xml`)
- `portal.portal_sidebar` (`helpdesk_ticket_templates.xml`)
- `portal_create_ticket` (`helpdesk_ticket_templates.xml`)

### Security

**Security Groups:**

- User: Personal tickets
- User: Team tickets
- User
- Helpdesk Manager
- User: Personal tickets
- User: Team tickets
- User
- Helpdesk Manager

**Access Rights:** 21 model access rules defined

| Model |
|-------|
| `helpdesk.ticket.manager` |
| `helpdesk.ticket.user` |
| `helpdesk.ticket.user.personal` |
| `helpdesk.ticket.portal` |
| `helpdesk.ticket.stage.manager` |
| `helpdesk.ticket.stage.user` |
| `helpdesk.ticket.stage.portal` |
| `helpdesk.ticket.stage.public` |
| `helpdesk.ticket.tag.manager` |
| `helpdesk.ticket.tag.user` |
| `helpdesk.ticket.team.manager` |
| `helpdesk.ticket.team.user` |
| `helpdesk.ticket.team.portal` |
| `helpdesk.ticket.channel.manager` |
| `helpdesk.ticket.channel.user` |
| `helpdesk.ticket.category.manager` |
| `helpdesk.ticket.category.user` |
| `helpdesk.ticket.category.portal` |
| `helpdesk.ticket.category.public` |
| ... +1 more |

**Record Rules:** `helpdesk_security.xml`

### Web Controllers & Routes

| Route | Controller |
|-------|------------|
| `/ticket/close` | `main.py` |
| `/new/ticket` | `main.py` |
| `/submitted/ticket` | `main.py` |
| `/my/tickets` | `myaccount.py` |
| `/my/tickets/page/<int:page>` | `myaccount.py` |
| `/my/ticket/<int:ticket_id>` | `myaccount.py` |

### Data & Automation

**Sequences:** `helpdesk_data.xml`

**Email Templates:** `helpdesk_data.xml`

### Frontend Assets

**JavaScript:**

- `static/tests/views/helpdesk_team_kanban_view.test.js`
- `static/src/js/new_ticket.esm.js`
- `static/src/views/helpdesk_dashboard/helpdesk_dashboard.esm.js`
- `static/src/views/helpdesk_dashboard/helpdesk_team_kanban_view.esm.js`

**XML Templates (Frontend):**

- `static/src/views/helpdesk_dashboard/helpdesk_dashboard.xml`
- `static/src/views/helpdesk_dashboard/helpdesk_team_kanban_view.xml`

## Dependencies

| Module | Type |
|--------|------|
| `mail` | Odoo Core |
| `portal` | Odoo Core |
| `asset_management` | Custom |

## File Structure

```
helpdesk_mgmt/
├── README.rst
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   ├── main.py
│   └── myaccount.py
├── data/
│   └── helpdesk_data.xml
├── demo/
│   └── helpdesk_demo.xml
├── i18n/
│   ├── ca.po
│   ├── ca_ES.po
│   ├── de.po
│   ├── es.po
│   ├── es_AR.po
│   ├── fr.po
│   ├── helpdesk_mgmt.pot
│   ├── hu.po
│   ├── it.po
│   ├── lv.po
│   ├── lv_LV.po
│   ├── nl.po
│   ├── nl_NL.po
│   ├── pl.po
│   ├── pt.po
│   ├── pt_BR.po
│   ├── ru.po
│   ├── sk.po
│   ├── sv.po
│   └── tr.po
├── migrations/
│   └── 18.0.1.7.0/
│       └── post-migration.py
├── models/
│   ├── __init__.py
│   ├── field.py
│   ├── helpdesk_ticket.py
│   ├── helpdesk_ticket_category.py
│   ├── helpdesk_ticket_channel.py
│   ├── helpdesk_ticket_stage.py
│   ├── helpdesk_ticket_tag.py
│   ├── helpdesk_ticket_team.py
│   ├── ir_http.py
│   ├── res_company.py
│   ├── res_config_settings.py
│   ├── res_partner.py
│   └── res_users.py
├── pyproject.toml
├── readme/
│   ├── CONFIGURE.md
│   ├── CONTRIBUTORS.md
│   ├── DESCRIPTION.md
│   ├── ROADMAP.md
│   └── USAGE.md
├── security/
│   ├── helpdesk_security.xml
│   └── ir.model.access.csv
├── static/
│   ├── description/
│   │   ├── Categories.PNG
│   │   ├── Channels.PNG
│   │   ├── Stage.PNG
│   │   ├── Tags.PNG
│   │   ├── Teams.PNG
│   │   ├── Tickets01.PNG
│   │   ├── Tickets02.PNG
│   │   ├── Tickets_Kanban.PNG
│   │   ├── icon.png
│   │   ├── icon.svg
│   │   └── index.html
│   ├── src/
│   │   ├── img/
│   │   ├── js/
│   │   └── views/
│   └── tests/
│       └── views/
├── tests/
│   ├── __init__.py
│   ├── common.py
│   ├── test_helpdesk_category_hierarchy.py
│   ├── test_helpdesk_fetchmail.py
│   ├── test_helpdesk_portal.py
│   ├── test_helpdesk_ticket.py
│   ├── test_helpdesk_ticket_team.py
│   ├── test_js.py
│   └── test_res_partner.py
├── views/
│   ├── field.xml
│   ├── helpdesk_dashboard_views.xml
│   ├── helpdesk_ticket_category_views.xml
│   ├── helpdesk_ticket_channel_views.xml
│   ├── helpdesk_ticket_menu.xml
│   ├── helpdesk_ticket_stage_views.xml
│   ├── helpdesk_ticket_tag_views.xml
│   ├── helpdesk_ticket_team_views.xml
│   ├── helpdesk_ticket_templates.xml
│   ├── helpdesk_ticket_views.xml
│   ├── res_config_settings_views.xml
│   └── res_partner_views.xml
└── wizards/
    ├── __init__.py
    ├── helpdesk_ticket_duplicate_wizard.py
    └── helpdesk_ticket_duplicate_wizard_views.xml
```

## Installation

This module is part of the **[odoo-asset-helpdesk-suite](https://github.com/tejas7287/odoo-asset-helpdesk-suite)** suite.

1. Place this module in your Odoo addons directory
2. Update the apps list: **Settings** → **Apps** → **Update Apps List**
3. Search for **"Helpdesk Management"** and click **Install**

## License

AGPL-3
