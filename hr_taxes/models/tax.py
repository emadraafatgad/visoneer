from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError, ValidationError


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    taxable = fields.Boolean(string='بندالضريبه')
    has_tax = fields.Boolean(string='الوعاء الضريبي')


class TaxSegments(models.Model):
    _name = 'tax.segments'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name_slide'

    name_slide = fields.Selection([
        ('first_slide', "الشريحة اﻻولي"),
        ('second_slide', "الشريحة الثانية"),
        ('third_slide', "الشريحة الثالثة"),
        ('forth_slide', "الشريحة الرابعة"),
        ('fifth_slide', "الشريحة الخامسة"),
        ('sixth_slide', "الشريحة السادسة"),
        ('seventh_slide', "الشريحة السابعة"),
    ], default='first_slide', string='الشريحة')
    exemption_limit = fields.Float(string='حد الإعفاء')
    # slide_sums_ids = fields.One2many('slide.sums', 'tax_segments_id',
    #                                  string='مبالغ الشرائح')
    amount_from = fields.Integer('المبلغ من')
    to = fields.Integer('الي')
    tax_rate = fields.Float('نسبه الضريبه')
    discount_value = fields.Float('قيمه الخصم')
    difference = fields.Float('الفرق', compute='cal_difference_from_to')

    @api.depends('amount_from', 'to')
    def cal_difference_from_to(self):
        for rec in self:
            rec.difference = rec.to - rec.amount_from


class TaxSegmentsPart(models.Model):
    _name = 'tax.part'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'slide'

    slide = fields.Selection([
        ('first_slide', "الشريحة اﻻولي"),
        ('second_slide', "الشريحة الثانية"),
        ('third_slide', "الشريحة الثالثة"),
        ('forth_slide', "الشريحة الرابعة"),
        ('fifth_slide', "الشريحة الخامسة"),
        ('sixth_slide', "الشريحة السادسة"),
        ('seventh_slide', "الشريحة السابعة"),
    ], default='first_slide')
    # exemption_limit = fields.Float(string='حد الإعفاء')
    # slide_sums_ids = fields.One2many('slide.sums', 'tax_segments_id',
    #                                  string='مبالغ الشرائح')
    amount_from = fields.Integer('المبلغ من')
    to = fields.Integer('الي')
    # tax_rate = fields.Float('نسبه الضريبه')
    # discount_value = fields.Float('قيمه الخصم')
    # difference = fields.Float('الفرق', compute='cal_difference_from_to')

    #
    # @api.depends('amount_from', 'to')
    # def cal_difference_from_to(self):
    #     for rec in self:
    #         rec.difference = rec.to - rec.amount_from


class PayrollSalaryTaxesExtra(models.Model):
    _inherit = 'hr.payslip'

    all_lines_tax = fields.Float(string='Total Taxes',)
    sum_slides = fields.Float(string='SUM', )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'Waiting'),
        ('compute', 'Computed'),
        ('done', 'Done'),
        ('paid', 'Paid'),
        ('cancel', 'Rejected'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft',
        help="""* When the payslip is created the status is \'Draft\'
                    \n* If the payslip is under verification, the status is \'Waiting\'.
                    \n* If the payslip is confirmed then status is set to \'Done\'.
                    \n* When user cancel payslip the status is \'Rejected\'.""")

    # def compute_sheet(self):
    #     for payslip in self:
    #         payslip.cal_working_days()
    #         if payslip.contract_id.salary_stop == True:
    #             raise ValidationError("Employee Salary has been stopped!!")
    #         payslip.compute_all_taxes_lines()
    #         payslip.total_insurance_history()
    #         payslip.line_ids.rounding_amount_float()
    #         payslip.state = 'compute'
    #     return super(PayrollSalaryTaxesExtra, self).compute_sheet()

    def compute_sheet(self):
        for payslip in self:
            # payslip.cal_working_days()
            if payslip.contract_id.salary_stop == True:
                raise ValidationError("Employee Salary has been stopped!!")
            number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
            # delete old payslip lines
            payslip.line_ids.unlink()
            # set the list of contract for which the rules have to be applied
            # if we don't give the contract, then the rules to apply should be for all current contracts of the employee
            contract_ids = payslip.contract_id.ids or \
                           self.get_contract(payslip.employee_id, payslip.date_from, payslip.date_to)
            lines = [(0, 0, line) for line in self._get_payslip_lines(contract_ids, payslip.id)]
            payslip.write({'line_ids': lines, 'number': number})

            payslip.compute_all_taxes_lines()
            payslip.total_insurance_history()
            # payslip.line_ids.rounding_amount_float()
            # payslip.state = 'compute'

        return True

    # @api.depends('line_ids')
    def compute_all_taxes_lines(self):
        for record in self:
            record.all_lines_tax = 0
            for rec in record.line_ids:
                if rec.salary_rule_id.has_tax == True:
                    record.all_lines_tax += rec.amount
                    # print("line.amount",rec.amount)
                    # print(rec.amount)
            first_slide = self.env['tax.segments'].search([('name_slide', '=', 'first_slide')])
            second_slide = self.env['tax.segments'].search([('name_slide', '=', 'second_slide')])
            third_slide = self.env['tax.segments'].search([('name_slide', '=', 'third_slide')])
            forth_slide = self.env['tax.segments'].search([('name_slide', '=', 'forth_slide')])
            fifth_slide = self.env['tax.segments'].search([('name_slide', '=', 'fifth_slide')])
            sixth_slide = self.env['tax.segments'].search([('name_slide', '=', 'sixth_slide')])
            seventh_slide = self.env['tax.segments'].search([('name_slide', '=', 'seventh_slide')])
            # print(record.all_lines_tax)
            # print(record.all_lines_tax*12)
            # print(first_slide.exemption_limit)
            year_salary = record.all_lines_tax*12 - first_slide.exemption_limit
            # print("year_salary")
            # print(record.all_lines_tax)
            # print(year_salary)
            tax_amount = 0
            flag = False
            if year_salary > first_slide.difference:
                year_salary = year_salary - first_slide.difference
                tax_amount = tax_amount + first_slide.difference * first_slide.tax_rate/100
                print("1 - > ",year_salary,tax_amount)
            else:
                tax_amount = tax_amount + year_salary * first_slide.tax_rate / 100
                print("1 - < ", year_salary, tax_amount)
                flag = True
            if year_salary > second_slide.difference:
                year_salary = year_salary - second_slide.difference
                tax_amount = tax_amount + second_slide.difference*second_slide.tax_rate/100
                print("2 - > ", year_salary, tax_amount)
            elif not flag:
                tax_amount = tax_amount + year_salary * second_slide.tax_rate / 100
                print("2 - <>> ", year_salary, tax_amount)
                flag = True
            if year_salary > third_slide.difference:
                year_salary = year_salary - third_slide.difference
                tax_amount = tax_amount + third_slide.difference*third_slide.tax_rate/100
                print("3 - > ", year_salary, tax_amount)
            elif not flag:
                tax_amount = tax_amount + year_salary * third_slide.tax_rate / 100
                print("3 - <>> ", year_salary, tax_amount)
                flag = True
            if year_salary > forth_slide.difference:
                year_salary = year_salary - forth_slide.difference
                tax_amount = tax_amount + forth_slide.difference*forth_slide.tax_rate/100
                print("4 - > ", year_salary, tax_amount)

            elif not flag:
                tax_amount = tax_amount + year_salary * forth_slide.tax_rate / 100
                print("4 - <>> ", year_salary, tax_amount)
                flag = True
            if year_salary > fifth_slide.difference:
                year_salary = year_salary - fifth_slide.difference
                tax_amount = tax_amount + fifth_slide.difference*fifth_slide.tax_rate/100
                print("5 - > ", year_salary, tax_amount)
            elif not flag:
                tax_amount = tax_amount + year_salary * fifth_slide.tax_rate / 100
                print("5 - <>> ", year_salary, tax_amount)
                flag = True
            if year_salary > sixth_slide.difference:
                year_salary = year_salary - sixth_slide.difference
                tax_amount = tax_amount + sixth_slide.difference*sixth_slide.tax_rate/100
                print("6 - > ", year_salary, tax_amount)
            elif not flag:
                tax_amount = tax_amount + year_salary * sixth_slide.tax_rate / 100
                print("6 - <>> ", year_salary, tax_amount)
                flag = True
            if year_salary > seventh_slide.difference:
                year_salary = year_salary - seventh_slide.difference
                tax_amount = tax_amount + seventh_slide.difference*seventh_slide.tax_rate/100
                print("7 - > ", year_salary, tax_amount)
            elif not flag:
                tax_amount = tax_amount + year_salary * seventh_slide.tax_rate / 100
                print("7 - <>> ", year_salary, tax_amount)
            monthly_tax_amount = tax_amount / 12
            print("monthly_tax_amount")
            print(monthly_tax_amount)
            record.sum_slides = monthly_tax_amount
            for line in record.line_ids:
                if line.salary_rule_id.taxable == True:
                    print(line.name)
                    if line.amount == 0.0:
                        print('yes')
                        print(record.sum_slides)
                        line.write({'amount': record.sum_slides})
                        print(line.amount)
            for line in record.line_ids:
                if line.code == 'NET':
                    print("NET")
                    print(line.amount,monthly_tax_amount)
                    amount = line.amount
                    after_tax= amount - monthly_tax_amount
                    print(after_tax)
                    line.write({'amount': after_tax})





    # @api.depends('line_ids')
    # def compute_all_taxes_lines_ids(self):
    #     for record in self:
    #         for rec in record.line_ids:
    #             if rec.salary_rule_id.has_tax == True:
    #                 record.all_lines_tax += rec.amount
    #         first_slide = self.env['tax.segments'].search([('name_slide', '=', 'first_slide')])
    #         second_slide = self.env['tax.segments'].search([('name_slide', '=', 'second_slide')])
    #         third_slide = self.env['tax.segments'].search([('name_slide', '=', 'third_slide')])
    #         forth_slide = self.env['tax.segments'].search([('name_slide', '=', 'forth_slide')])
    #         fifth_slide = self.env['tax.segments'].search([('name_slide', '=', 'fifth_slide')])
    #         sixth_slide = self.env['tax.segments'].search([('name_slide', '=', 'sixth_slide')])
    #         seventh_slide = self.env['tax.segments'].search([('name_slide', '=', 'seventh_slide')])
    #         first_slide_part = self.env['tax.part'].search([('slide', '=', 'first_slide')])
    #         second_slide_part = self.env['tax.part'].search([('slide', '=', 'second_slide')])
    #         third_slide_part = self.env['tax.part'].search([('slide', '=', 'third_slide')])
    #         forth_slide_part = self.env['tax.part'].search([('slide', '=', 'forth_slide')])
    #         fifth_slide_part = self.env['tax.part'].search([('slide', '=', 'fifth_slide')])
    #         sixth_slide_part = self.env['tax.part'].search([('slide', '=', 'sixth_slide')])
    #         seventh_slide_part = self.env['tax.part'].search([('slide', '=', 'seventh_slide')])
    #         eximption = record.all_lines_tax - first_slide.exemption_limit
    #         if record.all_lines_tax > seventh_slide.to:
    #             after_deduct = record.all_lines_tax - first_slide.exemption_limit
    #             if after_deduct < second_slide_part.to:
    #                 if after_deduct < second_slide.to:
    #                     second_percentage_part = second_slide.to * (second_slide.tax_rate / 100)
    #                     total = second_percentage_part
    #                     print(second_percentage_part)
    #                     print(total)
    #                 else:
    #                     second_percentage_part = second_slide.to * (second_slide.tax_rate / 100)
    #                     after_deduct = after_deduct - second_slide.to
    #                     if after_deduct < third_slide.difference:
    #                         third_percentage_part = after_deduct * (third_slide.tax_rate / 100)
    #                         total = second_percentage_part + third_percentage_part
    #                     else:
    #                         third_percentage_part = third_slide.difference * (third_slide.tax_rate / 100)
    #                         after_deduct = after_deduct - third_slide.difference
    #                         if after_deduct < forth_slide.difference:
    #                             fourth_percentage_part = after_deduct * (forth_slide.tax_rate / 100)
    #                             total = second_percentage_part + third_percentage_part + fourth_percentage_part
    #                         else:
    #                             fourth_percentage_part = forth_slide.difference * (forth_slide.tax_rate / 100)
    #                             after_deduct = after_deduct - forth_slide.difference
    #                             if after_deduct < fifth_slide.difference:
    #                                 fifth_percentage_part = after_deduct * (fifth_slide.tax_rate / 100)
    #                                 total = second_percentage_part + third_percentage_part + fourth_percentage_part + fifth_percentage_part
    #                             else:
    #                                 fifth_percentage_part = fifth_slide.difference * (fifth_slide.tax_rate / 100)
    #                                 after_deduct = after_deduct - fifth_slide.difference
    #                                 if after_deduct < sixth_slide.difference:
    #                                     sixth_percentage_part = after_deduct * (sixth_slide.tax_rate / 100)
    #                                     total = second_percentage_part + third_percentage_part + fourth_percentage_part + fifth_percentage_part + sixth_percentage_part
    #                                 else:
    #                                     sixth_percentage_part = sixth_slide.difference * (sixth_slide.tax_rate / 100)
    #                                     after_deduct = after_deduct - sixth_slide.difference
    #                                     seventh_percentage_part = after_deduct * (seventh_slide.tax_rate / 100)
    #                                     total = second_percentage_part + third_percentage_part + fourth_percentage_part + fifth_percentage_part + sixth_percentage_part + seventh_percentage_part
    #             elif after_deduct < third_slide_part.to:
    #                 if after_deduct < third_slide.to:
    #                     third_percentage_part = third_slide.to * (third_slide.tax_rate / 100)
    #                     total = third_percentage_part
    #                 else:
    #                     third_percentage_part = third_slide.to * (third_slide.tax_rate / 100)
    #                     after_deduct = after_deduct - third_slide.to
    #
    #                     if after_deduct < forth_slide.difference:
    #                         fourth_percentage_part = after_deduct * (forth_slide.tax_rate / 100)
    #                         total = third_percentage_part + fourth_percentage_part
    #                     else:
    #                         fourth_percentage_part = forth_slide.difference * (forth_slide.tax_rate / 100)
    #                         after_deduct = after_deduct - forth_slide.difference
    #                         if after_deduct < fifth_slide.difference:
    #                             fifth_percentage_part = after_deduct * (fifth_slide.tax_rate / 100)
    #                             total = third_percentage_part + fourth_percentage_part + fifth_percentage_part
    #                         else:
    #                             fifth_percentage_part = fifth_slide.difference * (fifth_slide.tax_rate / 100)
    #                             after_deduct = after_deduct - fifth_slide.difference
    #                             if after_deduct < sixth_slide.difference:
    #                                 sixth_percentage_part = after_deduct * (sixth_slide.tax_rate / 100)
    #                                 total = third_percentage_part + fourth_percentage_part + fifth_percentage_part + sixth_percentage_part
    #                             else:
    #                                 sixth_percentage_part = sixth_slide.difference * (sixth_slide.tax_rate / 100)
    #                                 after_deduct = after_deduct - sixth_slide.difference
    #                                 seventh_percentage_part = after_deduct * (seventh_slide.tax_rate / 100)
    #                                 total = third_percentage_part + fourth_percentage_part + fifth_percentage_part + sixth_percentage_part + seventh_percentage_part
    #             elif after_deduct < forth_slide_part.to:
    #                 if after_deduct < forth_slide.to:
    #                     fourth_percentage_part = forth_slide.to * (forth_slide.tax_rate / 100)
    #                     total = fourth_percentage_part
    #                 else:
    #                     fourth_percentage_part = forth_slide.to * (forth_slide.tax_rate / 100)
    #                     after_deduct = after_deduct - forth_slide.to
    #                     if after_deduct < fifth_slide.difference:
    #                         fifth_percentage_part = after_deduct * (fifth_slide.tax_rate / 100)
    #                         total = fourth_percentage_part + fifth_percentage_part
    #                     else:
    #                         fifth_percentage_part = fifth_slide.difference * (fifth_slide.tax_rate / 100)
    #                         after_deduct = after_deduct - fifth_slide.difference
    #                         if after_deduct < sixth_slide.difference:
    #                             sixth_percentage_part = after_deduct * (sixth_slide.tax_rate / 100)
    #                             total = fourth_percentage_part + fifth_percentage_part + sixth_percentage_part
    #                         else:
    #                             sixth_percentage_part = sixth_slide.difference * (sixth_slide.tax_rate / 100)
    #                             after_deduct = after_deduct - sixth_slide.difference
    #                             seventh_percentage_part = after_deduct * (seventh_slide.tax_rate / 100)
    #                             total = fourth_percentage_part + fifth_percentage_part + sixth_percentage_part + seventh_percentage_part
    #             elif after_deduct < fifth_slide_part.to:
    #                 if after_deduct < fifth_slide.to:
    #                     fifth_percentage_part = fifth_slide.to * (fifth_slide.tax_rate / 100)
    #                     total = fifth_percentage_part
    #                 else:
    #                     fifth_percentage_part = fifth_slide.to * (fifth_slide.tax_rate / 100)
    #                     after_deduct = after_deduct - fifth_slide.to
    #                     if after_deduct < sixth_slide.difference:
    #                         sixth_percentage_part = after_deduct * (sixth_slide.tax_rate / 100)
    #                         total = fifth_percentage_part + sixth_percentage_part
    #                     else:
    #                         sixth_percentage_part = sixth_slide.difference * (sixth_slide.tax_rate / 100)
    #                         after_deduct = after_deduct - sixth_slide.difference
    #                         seventh_percentage_part = after_deduct * (seventh_slide.tax_rate / 100)
    #                         total = fifth_percentage_part + sixth_percentage_part + seventh_percentage_part
    #             elif after_deduct < sixth_slide_part.to:
    #                 if after_deduct < sixth_slide.to:
    #                     sixth_percentage_part = sixth_slide.to * (sixth_slide.tax_rate / 100)
    #                     total = sixth_percentage_part
    #                 else:
    #                     sixth_percentage_part = sixth_slide.to * (sixth_slide.tax_rate / 100)
    #                     after_deduct = after_deduct - sixth_slide.to
    #                     seventh_percentage_part = after_deduct * (seventh_slide.tax_rate / 100)
    #                     total = sixth_percentage_part + seventh_percentage_part
    #             else:
    #                 seventh_percentage_part = seventh_slide.to * (seventh_slide.tax_rate / 100)
    #                 total = seventh_percentage_part
    #         else:
    #             if eximption < first_slide.difference:
    #                 first_percentage = eximption * (first_slide.tax_rate / 100)
    #                 total = first_percentage
    #             else:
    #                 first_percentage = first_slide.difference * (first_slide.tax_rate / 100)
    #                 eximption = eximption - first_slide.difference
    #                 if eximption < second_slide.difference:
    #                     second_percentage = eximption * (second_slide.tax_rate / 100)
    #                     total = first_percentage + second_percentage
    #                 else:
    #                     second_percentage = second_slide.difference * (second_slide.tax_rate / 100)
    #                     eximption = eximption - second_slide.difference
    #                     if eximption < third_slide.difference:
    #                         third_percentage = eximption * (third_slide.tax_rate / 100)
    #                         total = first_percentage + second_percentage + third_percentage
    #                     else:
    #                         third_percentage = third_slide.difference * (third_slide.tax_rate / 100)
    #                         eximption = eximption - third_slide.difference
    #                         if eximption < forth_slide.difference:
    #                             fourth_percentage = eximption * (forth_slide.tax_rate / 100)
    #                             total = first_percentage + second_percentage + third_percentage + fourth_percentage
    #                         else:
    #                             fourth_percentage = forth_slide.difference * (forth_slide.tax_rate / 100)
    #                             eximption = eximption - forth_slide.difference
    #                             if eximption < fifth_slide.difference:
    #                                 fifth_percentage = eximption * (fifth_slide.tax_rate / 100)
    #                                 total = first_percentage + second_percentage + third_percentage + fourth_percentage + fifth_percentage
    #                             else:
    #                                 fifth_percentage = fifth_slide.difference * (fifth_slide.tax_rate / 100)
    #                                 eximption = eximption - fifth_slide.difference
    #                                 if eximption < sixth_slide.difference:
    #                                     sixth_percentage = eximption * (sixth_slide.tax_rate / 100)
    #                                     total = first_percentage + second_percentage + third_percentage + fourth_percentage + fifth_percentage + sixth_percentage
    #                                 else:
    #                                     sixth_percentage = sixth_slide.difference * (sixth_slide.tax_rate / 100)
    #                                     eximption = eximption - sixth_slide.difference
    #                                     seventh_percentage = eximption * (seventh_slide.tax_rate / 100)
    #                                     total = first_percentage + second_percentage + third_percentage + fourth_percentage + fifth_percentage + sixth_percentage + seventh_percentage
    #         print(total, 'final')
    #         record.sum_slides = total / 12
    #         for line in record.line_ids:
    #             if line.salary_rule_id.taxable == True:
    #                 print(line.name)
    #                 if line.amount == 0.0:
    #                     print('yes')
    #                     print(record.sum_slides)
    #                     line.write({'amount': record.sum_slides})
    #                     print(line.amount)

    # @api.depends('employee_id')
    def cal_working_days(self):
        list = []
        for rec in self:
            if rec.employee_id:
                working_days = self.env['working.days'].search(
                    [('name', '=', rec.employee_id.id), ('date', '<=', rec.date_to), ('date', '>=', rec.date_from)])
                if working_days:
                    print(working_days.attendance_days)
                list.append((0, 0, {
                    'name': 'working days',
                    'code': 'WD',
                    'number_of_days': working_days.attendance_days,
                    'contract_id': rec.contract_id.id,
                }))
                if rec.worked_days_line_ids:
                    rec.worked_days_line_ids.unlink()
                print(list)
                rec.worked_days_line_ids = list

    def total_insurance_history(self):
        list = []
        for rec in self:
            if rec.employee_id:
                history = self.env['hr.contract'].search(
                    [('employee_id', '=', rec.employee_id.id), ('state', '=', 'open')])

                if history:
                    history.write({
                        'insurance_table': [(0, 0, {
                            # 'date':  fields.Date.today(),
                            'date': rec.date_from,
                            'emp_amount': rec.emp_percentage_insurance,
                            'company_amount': rec.company_percentage_insurance,

                        })]
                    })
