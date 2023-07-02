from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import datetime


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    payslip_id = fields.Many2one('hr.payslip')


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    attendance_sheet_line_ids = fields.One2many('hr.attendance', 'payslip_id')

    actual_worked_hours = fields.Float(compute='compute_actual_worked_hours', store=True)
    working_hours = fields.Float(compute='compute_actual_worked_hours', store=True)
    deduction_hours = fields.Float(compute='compute_actual_worked_hours', store=True)
    hour_amount = fields.Float(compute='compute_actual_hours_amount', store=True)
    deduction_amount = fields.Float(compute='compute_actual_hours_amount', store=True)

    @api.depends('working_hours','contract_id')
    def compute_actual_hours_amount(self):
        for rec in self:
            if rec.working_hours:
                rec.hour_amount = rec.contract_id.wage / rec.working_hours
                if rec.deduction_hours:
                    rec.deduction_amount = rec.deduction_hours * rec.hour_amount

    @api.depends('attendance_sheet_line_ids','worked_days_line_ids', 'attendance_sheet_line_ids.worked_hours')
    def compute_actual_worked_hours(self):
        for rec in self:
            actual_worked_hours = 0
            for line in rec.attendance_sheet_line_ids:
                actual_worked_hours += line.worked_hours
            rec.actual_worked_hours = actual_worked_hours
            for line in rec.worked_days_line_ids:
                if line.code == 'WORK100':
                    rec.working_hours = line.number_of_hours
            deduction_hours = rec.working_hours - actual_worked_hours

            rec.deduction_hours = deduction_hours if deduction_hours > 0 else 0
    def get_employee_attendance_sheets(self):
        for payslip in self:

            datetime_from = datetime.combine(payslip.date_from, datetime.min.time())
            datetime_to = datetime.combine(payslip.date_to, datetime.max.time())
            print(datetime_from)
            print(datetime_to)
            attendance_ids = self.env['hr.attendance'].search(
                [('employee_id', '=', payslip.employee_id.id), ('check_in', '>=', datetime_from),
                 ('check_in', '<=', datetime_to)])
            print(attendance_ids)
            for attend in attendance_ids:
                attend.write({'payslip_id': payslip.id})
            payslip.compute_actual_worked_hours()
