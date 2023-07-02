from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    project_id = fields.Many2one('project.project')

    travel_rate = fields.Float(required=True, )
    monday_saturday_overtime = fields.Float(required=True, )
    sunday_holiday_overtime = fields.Float(required=True, )
    per_diem = fields.Float(required=True, )
    to_invoice_from = fields.Date(tracking=True, )
    to_invoice_to = fields.Date(tracking=True, )
    date_from = fields.Date(tracking=True, )
    date_to = fields.Date(tracking=True, )

    # service_id = fields.Many2one('product.product',  domain="[('type','=','service')]", store=True)

    @api.model
    def default_get(self, fields):
        rec = super(SaleOrder, self).default_get(fields)
        overtime_defaults = self.env['invoice.config.overtime'].search([], limit=1)
        if overtime_defaults and len(overtime_defaults) == 1:
            overtime = overtime_defaults[0]
            rec['travel_rate'] = overtime.travel_rate
            rec['monday_saturday_overtime'] = overtime.monday_saturday_overtime
            rec['sunday_holiday_overtime'] = overtime.sunday_holiday_overtime
            rec['per_diem'] = overtime.per_diem
        return rec


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    employee_ids = fields.Many2many('hr.employee')
