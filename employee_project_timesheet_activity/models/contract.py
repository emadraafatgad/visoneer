from odoo import models, fields, api


class Contract(models.Model):
    _inherit = 'hr.contract'

    overtime_rate = fields.Float(required=True)
    weekend_rate = fields.Float(required=True)
    holidays_rate = fields.Float(required=True)
    overtime_amount = fields.Float(compute="compute_hour_rate_amount")
    weekend_amount = fields.Float(compute="compute_hour_rate_amount")
    holidays_amount = fields.Float(compute="compute_hour_rate_amount")
    overtime_global = fields.Float(required=True)
    weekend_global = fields.Float(required=True)
    holidays_global = fields.Float(required=True)

    @api.depends('wage','overtime_rate','weekend_rate','holidays_rate')
    def compute_hour_rate_amount(self):
        for rec in self:
            rec.overtime_amount = rec.overtime_rate * rec.wage / 160
            rec.weekend_amount = rec.weekend_rate * rec.wage / 160
            rec.holidays_amount = rec.holidays_rate * rec.wage / 160
