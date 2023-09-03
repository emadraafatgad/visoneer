from odoo import fields, models, api
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    payslip_id = fields.Many2one('hr.payslip')

    # work_schedule_id = fields.Many2one('work.schedule', related='employee_id.work_schedule_id', required=False)
    # work_schedule_id = fields.Many2one('work.schedule', related='employee_id.work_schedule_id', required=False)


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    timesheet_line_ids = fields.One2many('account.analytic.line', 'payslip_id')

    regular_hours = fields.Float(compute='compute_timesheet_hours', store=True)
    paid_off_hours = fields.Float(compute='compute_timesheet_hours', string='Paid Time Off', store=True)
    unpaid_off_hours = fields.Float(compute='compute_timesheet_hours', string="UnPaid Time Off", store=True)
    public_holidays_hours = fields.Float(compute='compute_timesheet_hours', string="Public Holidays", store=True)
    overtime_hours = fields.Float(compute='compute_timesheet_hours', store=True)
    weekend_hours = fields.Float(compute='compute_timesheet_hours', store=True)
    holidays_hours = fields.Float(compute='compute_timesheet_hours', store=True)
    overtime_global = fields.Float(compute='compute_timesheet_hours', store=True)
    weekend_global = fields.Float(compute='compute_timesheet_hours', store=True)
    holidays_global = fields.Float(compute='compute_timesheet_hours', store=True)

    @api.depends('timesheet_line_ids', 'timesheet_line_ids.time_type')
    def compute_timesheet_hours(self):
        for rec in self:
            regular = 0
            timeoff = 0
            unpaid_timeoff = 0
            holiday_off = 0
            overtime = 0
            weekend = 0
            holidays = 0
            global_overtime = 0
            global_weekend = 0
            global_holidays = 0

            for line in rec.timesheet_line_ids:
                print('type', line)
                print(line.employee_sheet_id.work_schedule_id.type, ' -- -- ', line.time_type)
                if line.time_type == 'regular':
                    regular += line.unit_amount
                if line.time_type == 'un_paid':
                    unpaid_timeoff += line.unit_amount
                if line.time_type == 'timeoff':
                    timeoff += line.unit_amount
                if line.time_type == 'public':
                    holiday_off += line.unit_amount
                elif line.employee_sheet_id.work_schedule_id.type == 'local' and line.time_type == 'overtime':
                    overtime += line.unit_amount
                elif line.employee_sheet_id.work_schedule_id.type == 'local' and line.time_type == 'weekend':
                    weekend += line.unit_amount
                elif line.employee_sheet_id.work_schedule_id.type == 'local' and line.time_type == 'holiday':
                    holidays += line.unit_amount
                elif line.employee_sheet_id.work_schedule_id.type == 'global' and line.time_type == 'overtime':
                    global_overtime += line.unit_amount
                elif line.employee_sheet_id.work_schedule_id.type == 'global' and line.time_type == 'weekend':
                    global_weekend += line.unit_amount
                elif line.employee_sheet_id.work_schedule_id.type == 'global' and line.time_type == 'holiday':
                    global_holidays += line.unit_amount
            rec.regular_hours = regular
            rec.overtime_hours = overtime
            rec.weekend_hours = weekend
            rec.holidays_hours = holidays
            rec.regular_hours = regular
            rec.overtime_global = global_overtime
            rec.weekend_global = global_weekend
            rec.holidays_global = global_holidays

    def get_attendance_sheets(self):
        for payslip in self:
            if not payslip.employee_id.user_id.id:
                raise ValidationError('Employee Must have related User')
            timesheet_ids = self.env['account.analytic.line'].search(
                [('user_id', '=', payslip.employee_id.user_id.id), ('date', '>=', payslip.date_from),
                 ('date', '<=', payslip.date_to)])
            print(timesheet_ids)
            for sheet in timesheet_ids:
                sheet.write({'payslip_id': payslip.id})
            payslip.compute_timesheet_hours()
