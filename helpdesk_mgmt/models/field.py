from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    # ✅ NEW Many2many
    asset_ids = fields.Many2many(
        "asset.management",
        "ticket_asset_rel",
        "ticket_id",
        "asset_id",
        string="Assets"
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee",
        compute="_compute_employee",
        store=True
    )

    @api.depends('user_id')
    def _compute_employee(self):
        for rec in self:
            rec.employee_id = rec.user_id.employee_id

    # @api.onchange('user_id')
    # def _onchange_user_id(self):
    #     if self.user_id:
    #         assets = self.env['asset.management'].search([
    #             ('transfer_ids.transfer_employee_id.user_id', '=', self.user_id.id)
    #         ])
    #         self.asset_ids = [(6, 0, assets.ids)]


class Employee(models.Model):
    _inherit = 'hr.employee'

    ticket_ids = fields.One2many(
        'helpdesk.ticket',
        'employee_id',
        string="Tickets"
    )

    ticket_count = fields.Integer(
        compute="_compute_ticket_count"
    )

    def _compute_ticket_count(self):
        for rec in self:
            rec.ticket_count = len(rec.ticket_ids)

    def action_view_tickets(self):
        self.ensure_one()
        return {
            'name': 'Tickets',
            'type': 'ir.actions.act_window',
            'res_model': 'helpdesk.ticket',
            'view_mode': 'list,form',
            'domain': [('employee_id', '=', self.id)],
            'context': {'default_employee_id': self.id}
        }
class AssetManagement(models.Model):
    _inherit = "asset.management"

    ticket_ids = fields.Many2many(
        "helpdesk.ticket",
        "ticket_asset_rel",   # SAME relation table
        "asset_id",
        "ticket_id",
        string="Tickets"
    )
    current_employee_id = fields.Many2one(
        'hr.employee',
        compute='_compute_current_employee',
        store=True
    )

    @api.depends('transfer_ids')
    def _compute_current_employee(self):
        for rec in self:
            if rec.transfer_ids:
                latest = max(rec.transfer_ids, key=lambda x: x.id)
                rec.current_employee_id = latest.transfer_employee_id
            else:
                rec.current_employee_id = False

    ticket_count = fields.Integer(
        compute="_compute_ticket_count"
    )

    def _compute_ticket_count(self):
        for rec in self:
            rec.ticket_count = len(rec.ticket_ids)

    def action_view_tickets(self):
        self.ensure_one()
        return {
            'name': 'Tickets',
            'type': 'ir.actions.act_window',
            'res_model': 'helpdesk.ticket',
            'view_mode': 'list,form',
            'domain': [('asset_ids', 'in', self.id)],
            'context': {'default_asset_ids': [(6, 0, [self.id])]}
        }