from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_asset_vendor = fields.Boolean(string="Asset Vendor")


    @api.model
    def create(self, vals):
        partner = super().create(vals)

        if vals.get('is_asset_vendor'):
            self._create_vendor(partner)

        return partner


    def write(self, vals):
        res = super().write(vals)

        for rec in self:
            if vals.get('is_asset_vendor') and rec.is_asset_vendor:
                self._create_vendor(rec)

        return res


    def _create_vendor(self, partner):

        # ✅ Company vs Individual logic
        company_name = partner.parent_id.name if partner.parent_id else partner.name
        contact_name = partner.name

        # ✅ Address
        full_address = partner._display_address().replace('\n', ', ')
        if not full_address.strip():
            full_address = company_name

        self.env['asset.vendor'].create({
            'name': company_name,          # Company Name
            'seller': contact_name,        # Person Name
            'contact_phone': partner.phone,
            'contact_email': partner.email,
            'address': full_address,
        })




class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    asset_count = fields.Integer(string="Assets", compute="_compute_asset_count")


    # ==============================
    # COMMON FUNCTION (LATEST OWNER)
    # ==============================
    def _get_current_assets(self):
        self.ensure_one()

        # ❌ REMOVE status filter
        transfers = self.env['asset.transfer.entry'].search(
            [],
            order='assign_date desc, id desc'
        )

        latest_asset_map = {}

        for transfer in transfers:
            asset = transfer.asset_id
            if not asset:
                continue

            # ✅ Take ONLY latest transfer per asset
            if asset.id not in latest_asset_map:
                latest_asset_map[asset.id] = transfer.transfer_employee_id.id

        return [
            asset_id
            for asset_id, emp_id in latest_asset_map.items()
            if emp_id == self.id
        ]


    # ==============================
    # COMPUTE COUNT
    # ==============================
    def _compute_asset_count(self):
        for rec in self:
            rec.asset_count = len(rec._get_current_assets())


    # ==============================
    # ACTION
    # ==============================
    def action_view_assets(self):
        self.ensure_one()

        asset_ids = self._get_current_assets()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Current Assets',
            'res_model': 'asset.management',
            'view_mode': 'list,form',
            'domain': [('id', 'in', asset_ids)],
        }




class HrWorkLocation(models.Model):
    _inherit = 'hr.work.location'

    employee_count = fields.Integer(compute="_compute_counts")
    asset_count = fields.Integer(compute="_compute_counts")


    # ==============================
    # COMMON LOGIC
    # ==============================
    def _get_location_assets(self):
        self.ensure_one()

        employees = self.env['hr.employee'].search([
            ('work_location_id', '=', self.id)
        ])

        if not employees:
            return []

        transfers = self.env['asset.transfer.entry'].search(
            [],
            order='assign_date desc, id desc'
        )

        latest_asset_map = {}

        for transfer in transfers:
            asset = transfer.asset_id
            if not asset:
                continue

            # latest per asset
            if asset.id not in latest_asset_map:
                latest_asset_map[asset.id] = transfer.transfer_employee_id.id

        # filter assets belonging to employees in this location
        employee_ids = employees.ids

        return [
            asset_id
            for asset_id, emp_id in latest_asset_map.items()
            if emp_id in employee_ids
        ]


    # ==============================
    # COMPUTE
    # ==============================
    def _compute_counts(self):
        for rec in self:
            employees = self.env['hr.employee'].search([
                ('work_location_id', '=', rec.id)
            ])

            rec.employee_count = len(employees)
            rec.asset_count = len(rec._get_location_assets())


    # ==============================
    # ACTIONS
    # ==============================
    def action_view_employees(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Employees',
            'res_model': 'hr.employee',
            'view_mode': 'list,form',
            'domain': [('work_location_id', '=', self.id)],
        }


    def action_view_assets(self):
        self.ensure_one()

        asset_ids = self._get_location_assets()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Assets',
            'res_model': 'asset.management',
            'view_mode': 'list,form',
            'domain': [('id', 'in', asset_ids)],
        }