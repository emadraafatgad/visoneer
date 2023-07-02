from odoo import fields, models, api
from datetime import datetime
from dateutil.relativedelta import relativedelta


class WorkSchedule(models.Model):
    _name = 'work.schedule'

    name = fields.Char(required=True)
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    active = fields.Boolean(default=True)
    employee_ids = fields.Many2many('hr.employee', required=True)
    company_id = fields.Many2one('res.company', readonly=True,
                                 default=lambda self: self.env.company)
    month = fields.Selection([])
    type = fields.Selection([('local', 'Local'), ('global', 'Global')], string="Local/Global", required=True,
                            default='local')

    def force_active_new_period(self):
        all_schedules = self.env['work.schedule'].search([('active', '=', True)])
        for line in all_schedules:
            line.active = False
        self.active = True

    def name_get(self):
        result = []
        for schedule in self:
            name = schedule.name + ' [ ' + schedule.type + ' ] '
            result.append((schedule.id, name))
        return result


class Employee(models.Model):
    _inherit = 'hr.employee'

    working_schedule = fields.Many2one('work.schedule')
    service_id = fields.Many2one('product.product', domain="[('type','=','service')]", string="Current Service",
                                 tracking=True)
