from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from datetime import date, timedelta
import calendar


class EmployeeProjectExpenses(models.Model):
    _name = 'employee.project.expenses'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin', 'avatar.mixin']

    date = fields.Date(required=True)
    name = fields.Char(required=True)
    employee_sheet_id = fields.Many2one('employee.project.timesheet', "Employee Sheet", )
    project_id = fields.Many2one('project.project', required=True)
    employee_id = fields.Many2one('hr.employee', default=lambda self: self.env.user.employee_id.id, required=True)
    move_id = fields.Many2one('account.move')
    amount = fields.Float(required=True)
    company_id = fields.Many2one('res.company', readonly=True,
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  help="Expenses Currency.", )
    bill_non = fields.Selection([('bill', 'billable'), ('non', 'Nonbillable')], default='non', required=True)

    def create_invoice_from_expenses(self):
        print("---------------------------------------------------------------")
        for rec in self:
            if rec.bill_non == 'non' or rec.move_id:
                print("continue")
                continue
            else:
                rec.move_id = rec.employee_sheet_id.invoice_id
            print("expenses - >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.")


class HrDepartment(models.Model):
    _inherit = "hr.department"

    related_service_id = fields.Many2one('product.product', string="Service", domain="[('type','=','service')]")


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    related_service_id = fields.Many2one('product.product', string="Service",
                                         related="employee_id.service_id", store=True)
    employee_sheet_id = fields.Many2one('employee.project.timesheet', "Employee Sheet")
    bill_non = fields.Selection([('bill', 'billable'), ('non', 'Nonbillable')], default='non', string="B/N",
                                required=True)
    time_type = fields.Selection(
        [('regular', 'Regular Hours'),
         ('overtime', 'Overtime'),
         ('weekend', 'Weekend Overtime'),
         ('timeoff', 'Paid Time Off'),
         ('un_paid', 'UnPaid Time Off'),
         ('holiday', 'Holiday Overtime')], string="Type",
        default='regular', required=True)

    invoice_id = fields.Many2one('account.move', string='Invoice Timesheet', readonly=True, copy=False)

    @api.onchange('time_type', 'bill_non')
    def check_bill_and_type(self):
        if self.time_type and self.time_type == 'un_paid' and self.bill_non and self.bill_non == 'bill':
            raise ValidationError('UnPaid timeoff must be non billable')

    @api.constrains()
    def constrain_bill_non_type(self):
        for rec in self:
            if rec.time_type and rec.time_type == 'un_paid' and rec.bill_non and rec.bill_non == 'bill':
                raise ValidationError('UnPaid timeoff must be non billable')

    def create_invoice_from_attendance(self):
        print("==========-Start-=============")
        for rec in self:
            print(rec)
            if rec.bill_non == 'non' or rec.unit_amount == 0 or rec.invoice_id or rec.time_type not in ['regular',
                                                                                                        'overtime',
                                                                                                        'weekend',
                                                                                                        'holiday']:
                print("continue")
                continue
            today = datetime.today()
            quotation = self.env['sale.order'].search(
                [('project_id', '=', rec.project_id.id), ('to_invoice_from', '<=', rec.date),
                 ('to_invoice_to', '>=', rec.date)])
            print(quotation)
            quotation_line = quotation.order_line.filtered_domain(
                ['|', ('product_id', '=', rec.related_service_id.id), ('employee_ids', 'in', [rec.employee_id.id])])
            service_id = quotation_line.product_id
            if not quotation_line:
                raise ValidationError('There is no quotation within this period ')
            if len(quotation_line) > 1:
                raise ValidationError('Quotation Service must be only one')
            price_unit = quotation_line.price_unit
            price_overtime = 0
            week_day = rec.date.weekday()
            invoice_time_tpye = rec.time_type
            if invoice_time_tpye == 'overtime':
                invoice_time_tpye = 'regular'
            price_overtime = price_unit * quotation.monday_saturday_overtime if invoice_time_tpye == 'overtime' else price_unit * quotation.sunday_holiday_overtime
            discount = quotation_line.discount
            # sunday_holiday_price_overtime = price_unit * quotation.sunday_holiday_overtime

            week_number = rec.date.isocalendar()[1]
            start = rec.date - timedelta(days=rec.date.weekday())
            end = start + timedelta(days=6)
            print("week_number,start,end")
            print(week_number, start, end)
            start_month = calendar.month_abbr[int(start.strftime("%m"))]
            end_month = calendar.month_abbr[int(end.strftime("%m"))]
            inv_name_msg = {
                'regular': "Regular working hours (Week#{}/{}) Mon, {}. {} - Sun, {}. {}".format(week_number,
                                                                                                 start.strftime("%Y"),
                                                                                                 start.strftime("%d"),
                                                                                                 start_month,
                                                                                                 end.strftime("%d"),
                                                                                                 end_month ),
                'overtime': "Overtime working hours (Week#{}/{}) Mon, {}. {} - Sun, {}. {}".format(week_number,
                                                                                                   start.strftime("%Y"),
                                                                                                   start.strftime("%d"),
                                                                                                   start_month,
                                                                                                   end.strftime("%d"),
                                                                                                   end_month),
                'holiday': "Holiday working hours (Week#{}/{}) Mon, {}. {} - Sun, {}. {}".format(week_number,
                                                                                                 start.strftime("%Y"),
                                                                                                 start.strftime("%d"),
                                                                                                 start_month,
                                                                                                 end.strftime("%d"),
                                                                                                 end_month ),
                'weekend': "WeekEnd working hours (Week#{}/{}) Mon, {}. {} - Sun, {}. {}".format(week_number,
                                                                                                 start.strftime("%Y"),
                                                                                                 start.strftime("%d"),
                                                                                                 start_month,
                                                                                                 end.strftime("%d"),
                                                                                                 end_month )}
            invoice = self.env['account.move'].search([('state', '=', 'draft'), ('project_id', '=', rec.project_id.id),
                                                       ('service_id', '=', quotation_line.product_id.id)])
            print("rec.id - ",rec.id)
            if invoice:
                print("If Invoice", rec.id)
                rec.invoice_id = invoice.id
                invoice_line = self.env['account.move.line'].search(
                    [('move_id', '=', invoice.id), ('week_number', '=', week_number),
                     ('time_type', '=', invoice_time_tpye)])
                total_quantity = rec.unit_amount
                overtime_quantity = 0
                overtime_invoice_line = self.env['account.move.line']
                print(invoice_line, " invoice_line",invoice_time_tpye)
                if invoice_line:
                    print("if Invoice Line For -------------------------------{}".format(rec.id))
                    quant = invoice_line.quantity + rec.unit_amount
                    print(quant, invoice_line.quantity ,rec.unit_amount)
                    print("quant before 50",quant,invoice_time_tpye)
                    if quant > 50 and invoice_time_tpye == 'regular':
                        print("quant after 50",quant)
                        total_quantity = 50
                        overtime_quantity = quant - 50
                        print(overtime_quantity,"overtime_quantityovertime_quantity")
                        overtime_invoice_line = invoice.invoice_line_ids.filtered(
                            lambda x: x.time_type == 'overtime')
                        print("overtime_invoice_line in check ine",overtime_invoice_line,overtime_invoice_line.quantity)
                    else:
                        total_quantity = quant
                    print("total_quantity",total_quantity,'overtime_quantity',overtime_quantity)
                    print(overtime_invoice_line, overtime_quantity, invoice_line)
                    if overtime_invoice_line and overtime_quantity:
                        qty = overtime_invoice_line['quantity']
                        print(qty,overtime_invoice_line.quantity + overtime_quantity)
                        print({
                            'quantity': overtime_invoice_line.quantity + overtime_quantity,
                            'price_unit': price_overtime})
                        print(overtime_invoice_line.id)
                        print("i will write overtime here")
                        invoice.write({'invoice_line_ids': [(1, overtime_invoice_line.id, {
                            'quantity': overtime_invoice_line.quantity + overtime_quantity,
                            'price_unit': price_overtime,
                        })]})
                    elif overtime_quantity and not overtime_invoice_line:
                        val = {
                            'product_id': quotation_line.product_id.id,
                            'name': inv_name_msg['overtime'],
                            'account_id': quotation_line.product_id.property_account_income_id.id,
                            'quantity': overtime_quantity,
                            'discount': discount,
                            'price_unit': price_unit * 1.25,
                            'week_number': week_number,
                            'time_type': 'overtime',
                        }
                        print("invoice line overtime",invoice_line)
                        invoice['invoice_line_ids'] = [(0, None, val)]
                        invoice._recompute_dynamic_lines(recompute_all_taxes=False)
                    print(invoice_line,'invoice_line')
                    print("i will write bas here")
                    print(invoice_line)
                    write_out= invoice.write({'invoice_line_ids': [(1, invoice_line.id, {
                        'quantity': total_quantity,
                        'price_unit': price_unit if invoice_time_tpye == 'regular' else price_overtime,
                    })]})
                    print("write done", total_quantity,write_out)
                    # print(invoice_line,'write done',invoice_line.quantity)
                    print(invoice.invoice_line_ids,invoice.invoice_line_ids.mapped('quantity'))

                else:
                    print("If Not")
                    val = {
                        'product_id': quotation_line.product_id.id,
                        'quantity': total_quantity,
                        'name': inv_name_msg[invoice_time_tpye],
                        'account_id': quotation_line.product_id.property_account_income_id.id,
                        'discount': discount,
                        'price_unit': price_unit if invoice_time_tpye == 'regular' else price_overtime,
                        'week_number': week_number,
                        'time_type': invoice_time_tpye,
                        'move_id': invoice.id,

                    }
                    print(rec.unit_amount)
                    print(val)
                    print("invoice")
                    invoice['invoice_line_ids'] = [(0, None, val)]
                    print(invoice['invoice_line_ids'])
                    invoice._recompute_dynamic_lines(recompute_all_taxes=False)
                    print("========================-----------------------=================================")
                    print("Invoice line created")
                    invoice_line = self.env['account.move.line'].search(
                        [('move_id', '=', invoice.id), ('week_number', '=', week_number),
                         ('time_type', '=', invoice_time_tpye)])
                    print(invoice_line.quantity)
                    val = {
                        'product_id': quotation_line.product_id.id,
                        'quantity': total_quantity + 0,
                        'name': inv_name_msg[invoice_time_tpye],
                        'account_id': quotation_line.product_id.property_account_income_id.id,
                        'discount': discount,
                        'price_unit': price_unit if invoice_time_tpye == 'regular' else price_overtime,
                        'week_number': week_number,
                        'time_type': invoice_time_tpye,
                        'move_id':invoice.id,

                    }
                    print(val)
                    invoice.write({'invoice_line_ids': [(1, invoice_line.id, val)]})
                    # print("after",invoice_line.quantity)
                    print(rec.unit_amount)
                    print(val)
                    print("invoice")
                    # invoice['invoice_line_ids'] = [(0, None, val)]
                    print(invoice['invoice_line_ids'])
                    invoice._recompute_dynamic_lines(recompute_all_taxes=False)
            else:
                create_values = {
                    'product_id': quotation_line.product_id.id,
                    'quantity': rec.unit_amount,
                    'name': inv_name_msg[invoice_time_tpye],
                    'account_id': quotation_line.product_id.property_account_income_id.id,
                    'discount': discount,
                    'price_unit': price_unit if invoice_time_tpye == 'regular' else price_overtime,
                    'week_number': week_number,
                    'time_type': invoice_time_tpye,
                    'move_id': invoice.id
                }
                invoice = self.env['account.move'].with_context(check_move_validity=False).create(
                    {
                        'move_type': 'out_invoice',
                        'date': today,
                        'invoice_date': today,
                        'partner_id': rec.project_id.partner_id.id,
                        'currency_id': quotation.currency_id.id,
                        'project_id': rec.project_id.id,
                        'per_diem': quotation.per_diem,
                        'employee_id': quotation_line.employee_ids[0],
                        'service_id': quotation_line.product_id.id,
                        'invoice_line_ids': [
                            (0, None, create_values)]
                    })
                print(invoice)
                # invoice._recompute_dynamic_lines(recompute_all_taxes=False, recompute_tax_base_amount=False)
                rec.invoice_id = invoice.id


class EmployeeProjectTimeSheet(models.Model):
    _name = 'employee.project.timesheet'



    @api.model
    def _default_user(self):
        if self.employee_id.user_id:
            user = self.employee_id.user_id
        else:
            user = self.env.user
            employee = self.env.user.employee_id
        return self.env.context.get('user_id', user.id)\

    @api.model
    def _default_employee(self):
        if self.user_id:
            employee = self.user_id.employee_id
        else:
            employee = self.env.user.employee_id
        return self.env.context.get('employee_id',employee)


    name = fields.Char(required=False)
    active = fields.Boolean(default=True)
    project_id = fields.Many2many('project.project', required=False)
    employee_id = fields.Many2one('hr.employee', required=False,default=_default_employee,readonly=True)
    date_from = fields.Date(required=False, compute='get_date_from_date_to_from_schedule', store=True)
    date_to = fields.Date(required=False, compute='get_date_from_date_to_from_schedule', store=True)
    work_schedule_id = fields.Many2one('work.schedule', domain="[('employee_ids','in',employee_id)]", required=True)
    note = fields.Text()
    company_id = fields.Many2one('res.company', readonly=True,
                                 default=lambda self: self.env.company)
    timesheet_line_ids = fields.One2many('account.analytic.line', 'employee_sheet_id')
    expenses_line_ids = fields.One2many('employee.project.expenses', 'employee_sheet_id')
    hr_expense_line_ids = fields.One2many('hr.expense', 'employee_sheet_id', string='Expenses')
    state = fields.Selection([('draft', 'Draft'), ('submit', 'Submitted'), ('invoiced', 'Invoiced')], default='draft')
    regular_hours = fields.Float(compute='compute_timesheet_hours')
    overtime_hours = fields.Float(compute='compute_timesheet_hours')
    weekend_hours = fields.Float(compute='compute_timesheet_hours')
    holidays_hours = fields.Float(compute='compute_timesheet_hours')
    timeoff_hours = fields.Float(compute='compute_timesheet_hours')
    invoice_id = fields.Many2one('account.move', string='Invoice Timesheet', store=True,
                                 compute='get_invoice_move_id_from_timesheet', )

    user_id = fields.Many2one('res.users', string='User', default=_default_user,readonly=True)

    @api.depends('work_schedule_id')
    def get_date_from_date_to_from_schedule(self):
        for rec in self:
            if rec.work_schedule_id:
                rec.date_from = rec.work_schedule_id.date_from
                rec.date_to = rec.work_schedule_id.date_to

    @api.depends('timesheet_line_ids.invoice_id')
    def get_invoice_move_id_from_timesheet(self):
        for rec in self:
            for line in rec.timesheet_line_ids:
                if line.invoice_id:
                    rec.invoice_id = line.invoice_id

    def rest_timesheet_to_draft(self):
        if self.state == 'submit':
            self.state = 'draft'

    def submit_employee_timesheet(self):
        total_hours = self.regular_hours + self.timeoff_hours
        total_overtime = self.overtime_hours + self.holidays_hours + self.weekend_hours
        if total_hours <= 40:
            if total_overtime > 0:
                raise ValidationError('you cant submit overtime')
        elif total_hours > 40:
            raise ValidationError('you cant submit regular + timeoff hours more > 40')
        self.state = 'submit'

    @api.depends('timesheet_line_ids', 'timesheet_line_ids.time_type')
    def compute_timesheet_hours(self):
        for rec in self:
            regular = 0
            overtime = 0
            weekend = 0
            holidays = 0
            timeoff_hours = 0
            for line in rec.timesheet_line_ids:
                if line.time_type == 'regular':
                    regular += line.unit_amount
                elif line.time_type == 'overtime':
                    overtime += line.unit_amount
                elif line.time_type == 'weekend':
                    weekend += line.unit_amount
                elif line.time_type == 'holidays':
                    holidays += line.unit_amount
                elif line.time_type == 'timeoff':
                    timeoff_hours += line.unit_amount
            rec.regular_hours = regular
            rec.overtime_hours = overtime
            rec.weekend_hours = weekend
            rec.holidays_hours = holidays
            rec.timeoff_hours = timeoff_hours

    @api.constrains('timesheet_line_ids', 'date_from', 'date_to', 'user_id')
    def check_date_and_time(self):
        for rec in self:
            for line in rec.timesheet_line_ids:
                if line.date < rec.date_from or line.date > rec.date_to:
                    raise ValidationError('Timesheet Line Date Must be with in date from and date to')
                if line.user_id != rec.user_id:
                    raise ValidationError('Timesheet Lines User Must Be the same')

    @api.onchange('work_schedule_id')
    def get_date_from_and_date_to(self):
        if self.work_schedule_id:
            self.date_from = self.work_schedule_id.date_from
            self.date_to = self.work_schedule_id.date_to


    # onchange if not employee not allow add aline or constains all line have the same employee and not empty

    @api.onchange('employee_id')
    def check_employee_id(self):
        current_date = fields.date.today()
        print("current_date")
        print(current_date)
        if self.employee_id.user_id:
            self.user_id = self.employee_id.user_id.id
        schedule = self.env['work.schedule'].search([])
        if self.timesheet_line_ids and not self.employee_id:
            raise ValidationError("Employee is not set")

    def action_create_invoice_for_expenses(self, move_id):
        if not move_id:
            raise ValidationError('there is not invoice')
        for line in self.expenses_line_ids:
            if line.bill_non == 'bill':
                line.move_id = move_id
        for line in self.hr_expense_line_ids:
            if line.bill_non == 'bill':
                line.move_id = move_id

    def create_invoice_timesheet(self):
        for line_sheet in self.timesheet_line_ids:
            if line_sheet.bill_non == 'bill':
                partner_id = line_sheet.project_id.partner_id
                if not partner_id:
                    raise ValidationError('project {} must have a customer'.format(line_sheet.project_id.name))
                invoice_id = self.env['account.move'].search(
                    [('partner_id', '=', partner_id.id), ('state', '=', 'draft')])
                if not invoice_id:
                    invoices = self.env['account.move'].create([
                        {
                            'move_type': 'out_invoice',
                            'partner_id': partner_id.id,
                            'invoice_date': fields.datetime.today(),
                            'invoice_line_ids': [(0, 0,
                                                  {'name': line_sheet.task_id.name, 'quantity': line_sheet.unit_amount,
                                                   'price_unit': 1000.0})],
                        }])
                else:
                    invoices = self.env['account.move'].write([
                        {
                            'invoice_line_ids': [(0, 0,
                                                  {'name': line_sheet.task_id.name, 'quantity': line_sheet.unit_amount,
                                                   'price_unit': 1000.0})],
                        }])
        self.action_create_invoice_for_expenses(invoices.id)
