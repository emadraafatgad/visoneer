from odoo import fields, models


class WorkingRules(models.Model):
    _name = 'working.rules'

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    branch_id = fields.Many2one('res.branch')
    company_id = fields.Many2one('res.company')
    rate = fields.Float()
    invoice_rate = fields.Float()
