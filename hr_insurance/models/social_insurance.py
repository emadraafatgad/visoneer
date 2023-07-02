from odoo import models, fields, api, exceptions, _
from odoo.exceptions import Warning, ValidationError
from datetime import datetime as dt
from odoo.fields import Date, Datetime
from dateutil.relativedelta import relativedelta


class EmployeeInsuranceExtra(models.Model):
    _name = 'emp.insurance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'min_insurance_salary'

    active = fields.Boolean(string='Active')
    min_insurance_salary = fields.Float(string='Minimum Insurance salary')
    max_insurance_salary = fields.Float(string='Maximum Insurance salary')
    company_percentage = fields.Float(string='Company Percentage')
    employee_percentage = fields.Float(string='Employee Percentage')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id)

    tot_company_percentage = fields.Float()
    tot_emp_percentage = fields.Float()
    tot_age_company_percentage = fields.Float()
    tot_age_emp_percentage = fields.Float()
    # tot_company_percentage = fields.Float(compute='calc_total_insurance')
    # tot_emp_percentage = fields.Float(compute='calc_total_insurance')
    # tot_age_company_percentage = fields.Float(compute='calc_total_insurance')
    # tot_age_emp_percentage = fields.Float(compute='calc_total_insurance')
    is_over_age = fields.Boolean(string='Over the age')
    over_age = fields.Float(string='Over age')
    over_age_company_percentage = fields.Float(string='Over Age Company Percentage')
    over_age_employee_percentage = fields.Float(string='Over Age Employee Percentage')

    insurances_type_per = fields.One2many('insurances.percentage', 'conf_inverse', string='Certified Social Insurance')
    insurances_over_age = fields.One2many('insurances.age', 'over_age_inverse', string='Over Age Social Insurance')

    _sql_constraints = [
        (
            'unique_active',
            'unique (active)',
            'You can not activate more than one record at the same time',
        )
    ]

    @api.depends('insurances_type_per', 'insurances_over_age', 'over_age_employee_percentage',
                 'over_age_company_percentage', 'employee_percentage', 'company_percentage')
    def calc_total_insurance(self):
        for rec in self:
            print(rec)
            # if len(rec.insurances_type_per) >1 :
            #     print("rec.insurances_type_per")
            #     print(rec.insurances_type_per)
            #     for line in rec.insurances_type_per:
            #         rec.tot_company_percentage += line.co_percentage
            #         rec.tot_emp_percentage += line.employee_percentage
            #     if (rec.tot_emp_percentage > rec.employee_percentage) or (
            #             rec.tot_company_percentage > rec.company_percentage):
            #         raise ValidationError(
            #             _('total employee percentage or total company percentage should not exceed company percentage and employee percentage '))
            #
            #     if rec.is_over_age == True:
            #         for line in rec.insurances_over_age:
            #             rec.tot_age_company_percentage += line.co_percentage
            #             rec.tot_age_emp_percentage += line.employee_percentage
            #         if (rec.tot_age_emp_percentage > rec.over_age_employee_percentage) or (
            #                 rec.tot_age_company_percentage > rec.over_age_company_percentage):
            #             raise ValidationError(
            #                 _('total employee percentage or total company percentage should not exceed company percentage and employee percentage '))

    # state = fields.Selection([
    #     ('submit', "Submitted"),
    #     ('confirmed', "Confirmed"),
    #     ('approve', "Approved"),
    #
    # ], default='submit')
    #
    #
    # def action_confirm(self):
    #     self.state = 'confirmed'

    #
    # def action_approve(self):
    #     self.state = 'approve'

    #
    # def action_submit(self):
    #     self.state = 'submit'

    #
    # @api.depends('date_start', 'leaving_date')
    # def _duration_of_years(self):
    #     for rec in self:
    #         if rec.date_start and rec.leaving_date:
    #             init_date = dt.strptime(str(rec.date_start), '%Y-%m-%d')
    #             end_date = dt.strptime(str(rec.leaving_date), '%Y-%m-%d')
    #             # rec.total_working_years = str((end_date - init_date).days)
    #             asd = str(relativedelta(end_date, init_date))
    #             mm = asd.split('(')
    #             ww = mm[1]
    #             qq = ('(' + ww)
    #             rec.total_working_years = (qq)

    #
    # @api.depends('system_time', 'leaving_date')
    # def _duration_of_notice(self):
    #     for rec in self:
    #         if rec.leaving_date:
    #             fmt = '%Y-%m-%d'
    #             d1 = rec.system_time
    #             d2 = rec.leaving_date
    #             # days_between_dates = str((d2 - d1).days)
    #             # self.notice_period = str(int((int(days_between_dates))))
    #             asd = str(relativedelta(d2, d1))
    #             mm = asd.split('(')
    #             ww = mm[1]
    #             qq = ('(' + ww)
    #             rec.notice_period = (qq)


class InsurancesConfigTypes(models.Model):
    _name = 'insurances.percentage'
    _rec_name = 'insurances_type'

    # insurances_type = fields.Selection([
    #     ('old_disability_death', "Old/Disability/Death"),
    #     ('reward', "Reward"),
    #     ('work_injury', "Work Injury"),
    #     ('disease', "Disease"),
    #     ('unemployment', "Unemployment"),
    # ], string='Insurances Type')
    insurances_type = fields.Selection([
        ('old_disability_death', "الشيخوخة والعجز والوفاة"),
        ('reward', "المكافأة"),
        ('work_injury', "إصابة العمل"),
        ('disease', "المرض"),
        ('unemployment', "البطالة"),
    ], string='Insurances Type')

    co_percentage = fields.Float(string='Company Percentage %')
    employee_percentage = fields.Float(string='Employee Percentage %')

    conf_inverse = fields.Many2one('emp.insurance')


class OverAgeInsurancesConfigTypes(models.Model):
    _name = 'insurances.age'
    _rec_name = 'insurances_type'

    # insurances_type = fields.Selection([
    #     ('old_disability_death', "Old/Disability/Death"),
    #     ('reward', "Reward"),
    #     ('work_injury', "Work Injury"),
    #     ('disease', "Disease"),
    #     ('unemployment', "Unemployment"),
    # ], string='Insurances Type')
    insurances_type = fields.Selection([
        ('old_disability_death', "الشيخوخة والعجز والوفاة"),
        ('reward', "المكافأة"),
        ('work_injury', "إصابة العمل"),
        ('disease', "المرض"),
        ('unemployment', "البطالة"),
    ], string='Insurances Type')

    co_percentage = fields.Float(string='Company Percentage %')
    employee_percentage = fields.Float(string='Employee Percentage %')

    over_age_inverse = fields.Many2one('emp.insurance')


class HrJobInheritTawzeef(models.Model):
    _inherit = 'hr.job'

    insurance_job_title = fields.Char(string='المسمي الوظيفي باللغة العربية')


class InsurancePayslipInheritTawzeef(models.Model):
    _inherit = 'hr.payslip'

    emp_percentage_insurance = fields.Float(string='Insurance Employee Percentage',
                                            related='contract_id.employee_percentage')
    company_percentage_insurance = fields.Float(string='Insurance Company Percentage',
                                                related='contract_id.company_percentage')
