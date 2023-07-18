from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError, ValidationError

class WorkingDays(models.Model):
    _name = 'working.days'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    user = fields.Many2one('res.users',related='name.user_id')


    name = fields.Many2one('hr.employee',string='Employee')
    dept = fields.Many2one('hr.department', string='Department', related='name.department_id')
    emp_id = fields.Char(string='Identification No', related='name.identification_id')
    mobile = fields.Char(string='Mobile',)
    company_id = fields.Many2one('res.company', readonly=True, default=lambda self: self.env.user.company_id)
    internal_number = fields.Char(string="Internal Employee Number", related='name.internal_number')
    employee_number = fields.Char(string="Employee Number", readonly=False, related='name.employee_number')
    date = fields.Date('Withholding Date', default=fields.Date.today())
    # salary = fields.Float('Salary', compute='cal_emp_contract_salary')
    attendance_days = fields.Integer('Attendance Days')
    employee_contract = fields.Many2one('hr.contract', string='Contract', compute='cal_emp_contract_salary')


    @api.depends('name')
    def cal_emp_contract_salary(self):
        for rec in self:
            print("=========-----------------------===================")
            rec.employee_contract = False
            if rec.name:
                asd = self.env['hr.contract'].search([('employee_id', '=', rec.name.id), ('state', '=', 'open')],
                                                     limit=1)
                if asd:
                    rec.employee_contract = asd.id
                # else:/
                print("=----------------------------------------")