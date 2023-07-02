from odoo import fields, models, api, _


class InvoicingConfigurationOverTime(models.Model):
    _name = 'invoice.config.overtime'

    travel_rate = fields.Float(required=True, )
    monday_saturday_overtime = fields.Float(required=True, )
    sunday_holiday_overtime = fields.Float(required=True, )
    peer_deem = fields.Float( )
    per_diem = fields.Float(required=True, )
    company_id = fields.Many2one(
        'res.company', string='Company', change_default=True, required=False,
        default=lambda self: self.env.company,
    )
    state = fields.Selection([('draft', 'Draft'), ('running', 'Running'), ('closed', 'Closed')])

    def running_overtime(self):
        self.state = 'running'

    def lock_overtime(self):
        self.state = 'closed'

