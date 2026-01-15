# Addons Module Docs (English)

This repository contains 4 Odoo Addons: `carbon`, `calculation`, `smslogin`, and `access_control`. They implement a carbon-accounting prototype (entities + formulas + results + reports), configurable calculation logic, SMS-based verification/login (with Alibaba Cloud Captcha), and frontend access control.

> Note: This document is generated from the actual code and manifests (`__manifest__.py`) in this repo.

---

## 1. Runtime & Common Conventions

- **Framework**: Odoo (standard addon structure with `models/`, `views/`, `security/`, manifests, etc.)
- **REST framework**: `smslogin` and `carbon` expose APIs via `odoo.addons.base_rest.controllers.main.RestController`, so you need the `base_rest` stack (and its component dependencies).
  - `smslogin/controllers/controllers.py`: `_root_path = '/api/sms/v2/'`
  - `carbon/controllers/controllers.py`: `_root_path = '/api/carbon/v2/'`
- **Role model**: multiple modules use `security.role` and `res.users.security_role_ids`. Also, `access_control/views/security_role_extend.xml` inherits `security_user_roles.security_role_view_form`, so you typically need a `security_user_roles`-like addon providing the role model + view.

---

## 2. carbon: Carbon Accounting (Prototype + Entities + Formulas + Results + Reports)

### 2.1 Purpose

`carbon` provides a runnable carbon-accounting prototype:

- Project + scheme modeling
- Inventory libraries and emission-factor entities
- Two computation modes:
  - `rough`: screening-level / scheme comparison
  - `fine`: detailed accounting per stage/category
- Persisted results (per stage, and per category)
- Reports (QWeb + PDF download with charts)

Manifest: `carbon/__manifest__.py`

### 2.2 REST API & Report Download

Controller: `carbon/controllers/controllers.py`

- Root path: `/api/carbon/v2/`
- Collection: `carbon.project.services`
- Report download:
  - `GET /download_report?id=<id>&mode=<rough|fine|rough_compare|fine_compare>`
  - Internally calls Odoo report rendering (`report_routes`) and returns a PDF

Service: `carbon/services/model_services.py`

Endpoints (selected; full list is in the file):

- User:
  - `GET|PUT /users/info`
  - `GET /users/roles`
  - `GET|POST|PUT|DELETE /users/childs`
- Projects:
  - `GET|POST|PUT|DELETE /users/projects`
  - `PUT|DELETE /users/projects/<project_id>/schemes`
  - `GET|POST /users/projects/<id>/result`
  - `GET /users/projects/<id>` project details (inventory + stages + schemes + submitted data)
  - `GET /users/projects/ranking` (top 5)
  - `GET /users/projects/overview` (grouped by city)
- Inventories:
  - `GET|POST|PUT|DELETE /users/inventories`
  - `GET|POST|PUT|DELETE /users/inventories/details`
- Base data:
  - `GET /units`, `GET /stages`, `GET /stages/<id>/links`, `GET /stages/<id>/inventories`
  - `GET /layers`, `GET /compositions`, `GET /layers/<id>/compositions` (inventory-aware options)
  - `GET /citys`, `GET /geojson`

### 2.3 Core Entities (Partial)

Projects & schemes:

- `carbon.project` (`carbon/models/carbon_project.py`)
  - `mode`, `stage_ids`, `fine_stage_ids`, `inventory_id`, `scheme_ids`
  - `active_scheme_id` prefers completed `fine`, otherwise completed+selected `rough`
- `carbon.project.scheme` (`carbon/models/carbon_project_scheme.py`)
  - `data` as JSON text
  - `calc_rough()` and `calc_fine(...)`
- `carbon.project.result` (`carbon/models/carbon_project_result.py`)
  - metrics: `res_all`, `res_area`, `res_year`, `res_area_year`
  - `category_result` as JSON

Stages & process steps:

- `carbon.stage` (`carbon/models/carbon_stage.py`) with `sequence` and `code`
- `carbon.link` (`carbon/models/carbon_link.py`) with `sequence` and `stage_id`

Structural layers:

- `structural.layer` (`carbon/models/structural_layer.py`)
- `structural.layer.composition` (`carbon/models/structural_layer_composition.py`) includes `code`, `type`, and `columns` configuration

Inventory library:

- `life.cycle.inventory` (`carbon/models/life_cycle_inventory.py`)
- `life.cycle.inventory.type` (`carbon/models/life_cycle_inventory_type.py`) binds to `carbon.link` and allowed units
- `material.life.cycle.inventory` (`carbon/models/material_life_cycle_inventory.py`)
- `carbon.life.cycle.inventory` (`carbon/models/carbon_life_cycle_inventory.py`)

Geo/admin regions:

- `res.country.state.city.district` (`carbon/models/res_country_state_city_district.py`)
  - `district_import` fetches geojson from `https://geo.datav.aliyun.com/areas_v2/bound/<code>.json`

### 2.4 Computation Logic (As Implemented)

1) `rough` (scheme comparison / screening-level)

- Entry: `carbon.project.scheme.calc_rough()`
- Formulas:
  - functions imported from `carbon/tests/fun.py` (e.g., `calc_LQ_A1`, `calc_JC_A2`, `calc_D2`, ...)
- Inputs:
  - `scheme.data` JSON (`LayerData`, `wyData`, ...)
  - emission factors selected from `material.life.cycle.inventory` etc. by `inventory_id` and `composition_id`
- Output:
  - writes `carbon.project.result` per stage
  - writes `category_result` JSON (aggregated categories)

2) `fine` (detailed accounting)

- Entry: `carbon.project.scheme.calc_fine(stage_id, scheme_id, scheme_data, project)`
- Core:
  - base term: `factor_number * number`
  - if category is `A2` and `distance` is present: multiply by `distance`
  - if `link_id` is provided: derives categories like `A1/A2/.../D2` from `stage.code + link.sequence`
  - special handling for stage code `C`: computes and adds `"Traffic delay"`
- Output:
  - persists stage metrics and `category_result` into `carbon.project.result`

### 2.5 Reports & Charts

- QWeb report templates: `carbon/reports/*.xml`
- Report builders: `carbon/models/project_report.py`
  - generates pie/bar charts with `matplotlib`/`numpy`
  - uses Chinese font `carbon/static/fonts/simhei.ttf`
  - writes images to `carbon/static/src/images/` (names include scheme id + timestamp)
  - `/download_report` wraps the Odoo report engine and returns a PDF

---

## 3. calculation: Configurable Calculation Logic (Dynamic Execution)

### 3.1 Purpose

`calculation` stores executable code snippets in Odoo and provides an execution entrypoint. It can be used to externalize carbon formulas per category/stage so formulas can be updated without a deployment.

Manifest: `calculation/__manifest__.py`

### 3.2 Model & Execution

Model: `calculation.model` (`calculation/models/calculation_model.py`)

- Fields:
  - `name`: lookup key for the calculation record
  - `params`: parameter placeholder/name (string)
  - `code`: code snippet (string)
- Execution:
  - `start_run(self, name, **params)` looks up by `name` and runs:
    - `exec(m.code.replace(m.params, params.get(m.params)))`

UI: `calculation/views/calculation_model.xml`

- A `RUN` button triggers `start_run`

---

## 4. smslogin: SMS Verification + Login (Alibaba Cloud Captcha)

### 4.1 Purpose

`smslogin` provides frontend-facing auth APIs:

- Send SMS verification codes (after Alibaba Cloud Captcha 2.0 validation)
- Register (creates `res.users`, binds default roles, binds default data)
- Login via password or SMS verification code, with optional session concurrency limits
- Change password

Manifest: `smslogin/__manifest__.py`

### 4.2 REST API Entry

Controller: `smslogin/controllers/controllers.py`

- Root path: `/api/sms/v2/`
- Collection: `sms.services`

Service: `smslogin/services/model_services.py`

Endpoints (as implemented):

- `POST /api/sms/v2/sendsms` (`auth='public'`)
- `POST /api/sms/v2/register` (`auth='public'`)
- `POST /api/sms/v2/prelogin` (`auth='public'`)
- `POST /api/sms/v2/login` (`auth='public'`)
- `POST /api/sms/v2/password` (`auth='user'`)

Datamodels: `smslogin/datamodels/datamodels.py`

### 4.3 Key Models

- `verify.code` (`smslogin/models/verify_code.py`)
  - 5-minute expiry via `com_is_expired`
  - `check_verify_code(verifycode, phone)` marks the code used when valid
- `login.record` (`smslogin/models/login_record.py`) stores `sid`, method, IP, timestamp
- `captcha.record` (`smslogin/models/captcha_record.py`) exists but is marked deprecated; the current API flow does not persist Captcha tokens here

### 4.4 Required Configuration (ir.config_parameter)

As read by `smslogin/services/model_services.py`:

- `ACCESS_KEY_ID` / `ACCESS_KEY_SECRET`: used to sign Alibaba Cloud Captcha requests
- `sms.config`: SMS gateway config (JSON string)
  - the code does `replace('%', code).replace('$', phone)` then `json.loads`
  - expected keys: `active_platform`, and platform config `{url, params}`
- `max.session`: max concurrent sessions per user (default 1)
  - login code scans `http.root.session_store.path` for `werkzeug_*.sess` and deletes extra session files

---

## 5. access_control: Frontend Page/Button Access Control

### 5.1 Purpose

`access_control` manages frontend permissions for:

- **Pages/routes** (by route `path`)
- **Buttons** inside a route (by button `domId`, with a configurable `state`)
- **Navigation entries** (menu visibility/availability)

Manifest: `access_control/__manifest__.py`

### 5.2 Data Model (Key Odoo Models)

Route and button definitions:

- `access.route` (`access_control/models/access_route.py`)
  - `name`, `path`, `pid/children` (tree routing)
  - `buttons`: one2many to `access.route.button`
- `access.route.button` (`access_control/models/access_route_button.py`)
  - `domId`: frontend DOM identifier
  - `name`: display label
  - `route_id`: parent route
- `access.navigation` (`access_control/models/access_navigation.py`)
  - `name`, `route_id` (and `path` via related field)
  - `sequence` with uniqueness check on change

Role → permission mapping:

- `role.access.route` (`access_control/models/role_access_route.py`)
  - `role_id` → `security.role`
  - `route_id` → `access.route`
  - `buttons`: one2many to `role.access.route.button`
- `role.access.route.button` (`access_control/models/role_access_route_button.py`)
  - `role_route_id` → `role.access.route`
  - `button_id` → `access.route.button`
  - `state`: button state exposed to the frontend
- `role.access.navigation` (`access_control/models/role_access_navigation.py`)
  - `role_id` → `security.role`
  - `navigation_id` → `access.navigation`
  - `available`: if false, the web API returns `disabled: true`

Role extension:

- `SecurityRoleExtend` (`access_control/models/extend.py`) extends `security.role`
  - `get_role_access()` / `get_role_access_by_web()`: routes + buttons
  - `get_role_navigation_access()` / `get_role_navigation_access_by_web()`: navigation entries
  - `configure_routing_permissions()` / `configure_navigation_permissions()`: returns `ir.actions.client` for the config panels

### 5.3 Backend UI & Config Panels

Assets and menus: `access_control/views/menu.xml`

- Injects JS into `web.assets_backend`:
  - `access_control/static/src/js/operate_access.js`
  - `access_control/static/src/js/operate_navigation_access.js`
- Defines `ir.actions.client`:
  - `tag = operate_access`: route/button configuration panel
  - `tag = operate_navigation_access`: navigation configuration panel
- Adds menu entries under **Access Control**

QWeb templates: `access_control/static/src/xml/template.xml`

- `operate_access_template`: per-role route list, button state config, add/delete routes
- `operate_navigation_access_template`: per-role navigation config, add/delete navigation

Role form buttons: `access_control/views/security_role_extend.xml`

- Adds two buttons on `security.role`:
  - `Configure Route Permissions`
  - `Configure Navigation Permissions`

### 5.4 HTTP API (Frontend Consumption & Sync)

Controller: `access_control/controllers/main.py`

1) Fetch navigation permissions for the current user:

- `GET /api/get_user_navigations` (`auth='user'`)
- Returns a dict keyed by role id with `navigations[{path,name,disabled?}]`

2) Fetch route + button permissions for the current user:

- `GET /api/get_user_routes` (`auth='user'`)
- Returns a dict keyed by role id with `routes[{id,pid,path,buttons[{domId,name,state}]}]`

3) Sync frontend routes into Odoo:

- `POST /api/routes` (`type='json'`, `auth='user'`)
- Key behavior:
  - **Deletes and rebuilds** `access.route` and `role.access.route` (via `search([]).unlink()`)
  - Recursively creates route tree, and creates buttons from `route.meta.buttons`
- Expected route fields (based on code):
  - `path`, `name`
  - `meta.buttons`: array of dicts written into `access.route.button` (commonly `domId`, `name`, etc.)

### 5.5 Recommended Workflow

1. Frontend publishes the route list (including button metadata), then calls `POST /api/routes`
2. Configure `access.navigation` items in Odoo (bind a navigation entry to a route, set `sequence`)
3. For each `security.role`, grant:
   - allowed routes + button states (via “Control Panel” or role form buttons)
   - allowed navigation items (`available` controls `disabled`)
4. Frontend calls:
   - `GET /api/get_user_routes` to enforce page/button access
   - `GET /api/get_user_navigations` to render/disable menus

---

## 6. Inter-module Relationships (Current Code)

- `smslogin` registration assigns `security_role_ids` by referencing `carbon` role xmlids.
- `access_control` exports permission data keyed by `security.role`; `carbon` defines several roles in `carbon/views/security_role_data.xml`.
- `calculation` is not directly referenced by `carbon` yet, but it is suitable for externalizing/updating carbon formulas dynamically.

---

## 7. Quick Code Entry Index

- `carbon`: `carbon/controllers/controllers.py`, `carbon/services/model_services.py`, `carbon/models/carbon_project_scheme.py`, `carbon/tests/fun.py`, `carbon/models/project_report.py`, `carbon/reports/*.xml`
- `calculation`: `calculation/models/calculation_model.py`
- `smslogin`: `smslogin/controllers/controllers.py`, `smslogin/services/model_services.py`, `smslogin/models/*.py`, `smslogin/datamodels/datamodels.py`
- `access_control`: `access_control/controllers/main.py`, `access_control/models/extend.py`, `access_control/static/src/js/*`, `access_control/static/src/xml/template.xml`

---

## 8. License

This project is licensed under `LGPL-3.0-or-later`. See `LICENSE`.
