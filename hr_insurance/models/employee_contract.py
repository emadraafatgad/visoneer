from odoo import models, fields, api, exceptions, _
from odoo.exceptions import Warning, ValidationError
import datetime
from dateutil.relativedelta import relativedelta


class ExtraContractInherit(models.Model):
    _inherit = 'hr.contract'

    date_of_birth = fields.Date(string='تاريخ ميلاد الموظف', compute='cal_contract_birth_from_emp', store=True)
    # current_emp_age = fields.Integer(string='عمر الموظف', compute='get_age_for_alloc_by_birth')
    current_emp_age = fields.Integer(string='عمر الموظف', )
    now_date = fields.Date(default=fields.Date.today())
    form_registration_date = fields.Date(string='تاريخ تسجيل الاستمارة')
    form_six_date = fields.Date(string='تاريخ استمارة 6')
    social_insurances = fields.Selection([
        ('insured', "مؤمن عليه"),
        ('not_insured', "غير مؤمن عليه"),
    ], string='التأمينات الاجتماعية', default='not_insured', related='employee_id.social_insurances', readonly=False)
    non_insurance_reason = fields.Char(string='سبب عدم التأمين')
    insurance_number = fields.Char(string='الرقم التأميني', related='employee_id.insurance_number', readonly=False)
    insurances_calculation = fields.Selection([
        ('insurance_salary', "الراتب التأميني"),
        ('modified_salary', "راتب معدل"),
    ], string='طريقة احتساب التأمينات', default='insurance_salary')
    register_method = fields.Selection([
        ('token', "Token"),
        ('office', "Office"),
    ], string='طريقة التسجيل', default='token', related='employee_id.register_method', readonly=False)
    insurance_status = fields.Selection([
        ('open', "Open"),
        ('paid', "Paid"),
    ], string='حالة التأمين', default='open')
    modified_salary = fields.Float(string='الراتب المعدل')
    company_percentage = fields.Float(string='نسبة الشركة', readonly=True, compute='calc_emp_co_percentage')
    employee_percentage = fields.Float(string='نسبة الموظف', readonly=True, compute='calc_emp_co_percentage')
    over_age = fields.Float(string='عمر فوق السن', compute='calc_emp_co_percentage')
    insurance_date_start = fields.Date('تاريخ بداية احتساب التأمينات', default=fields.Date.today, copy=True)

    total_insurance = fields.Float(string='Total Insurance', )
    total_insurance_company = fields.Float()
    # total_insurance = fields.Float(string='Total Insurance', compute='cal_total_insurance')
    # total_insurance_company = fields.Float(compute='cal_total_insurance')
    insurance_table = fields.One2many('insurance.monthly', 'inv_history')
    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure', compute='cal_all_struct')
    work_overtime = fields.Float()
    bounce = fields.Float()
    annual_raise = fields.Float()
    retroactive_raise = fields.Float()
    total_salary = fields.Float(compute='calculate_basic_salary', store=True, readonly=False)

    @api.depends('wage', 'work_overtime', 'bounce', 'annual_raise', 'retroactive_raise')
    def calculate_basic_salary(self):
        for rec in self:
            rec.total_salary = rec.wage + rec.work_overtime + rec.annual_raise + rec.bounce + rec.retroactive_raise

    @api.depends('social_insurances')
    def cal_all_struct(self):
        for rec in self:
            if rec.social_insurances == 'insured':
                asd = self.env['hr.payroll.structure'].search([('is_insured', '=', True)], limit=1)
                if asd:
                    rec.struct_id = asd.id
                else:
                    rec.struct_id = False
            elif rec.social_insurances == 'not_insured':
                asd = self.env['hr.payroll.structure'].search([('not_insured', '=', True)], limit=1)
                if asd:
                    rec.struct_id = asd.id
                else:
                    rec.struct_id = False
            else:
                rec.struct_id = False

    @api.depends('employee_id.birthday')
    def cal_contract_birth_from_emp(self):
        for rec in self:
            if rec.employee_id:
                print('heloo emp')
                if rec.employee_id.birthday:
                    print('hello birth')
                    print(rec.date_of_birth)
                    rec.date_of_birth = rec.employee_id.birthday
                    print(rec.date_of_birth)
                else:
                    print('no birth')
            else:
                print('no emp')

    @api.onchange('social_insurances', 'wage')
    def check_insuurance_range(self):
        asd = self.env['emp.insurance'].search([('active', '=', True)])
        for line in self:
            if line.social_insurances == 'insured':
                if line.wage:
                    if (line.wage < asd.min_insurance_salary):
                        raise ValidationError('Wage of this employee out of insurance range')
                    # (line.wage > asd.max_insurance_salary) or

    @api.depends('wage', 'modified_salary', 'insurances_calculation', 'over_age')
    def calc_emp_co_percentage(self):
        asd = self.env['emp.insurance'].search([('active', '=', True)])
        if asd:
            for rec in self:
                rec.over_age = asd.over_age
                if rec.current_emp_age <= rec.over_age:
                    if rec.insurances_calculation == 'insurance_salary':
                        rec.company_percentage = (asd.company_percentage / 100) * rec.wage
                        rec.employee_percentage = (asd.employee_percentage / 100) * rec.wage
                    elif rec.insurances_calculation == 'modified_salary':
                        rec.company_percentage = (asd.company_percentage / 100) * rec.modified_salary
                        rec.employee_percentage = (asd.employee_percentage / 100) * rec.modified_salary
                else:
                    if asd.is_over_age == True:
                        if rec.insurances_calculation == 'insurance_salary':
                            rec.company_percentage = (asd.over_age_company_percentage / 100) * rec.wage
                            rec.employee_percentage = (asd.over_age_employee_percentage / 100) * rec.wage
                        elif rec.insurances_calculation == 'modified_salary':
                            rec.company_percentage = (asd.over_age_company_percentage / 100) * rec.modified_salary
                            rec.employee_percentage = (asd.over_age_employee_percentage / 100) * rec.modified_salary
                    else:
                        raise ValidationError(
                            'there is no insurance configuration for over age employees please configur it and try again')
        else:
            raise ValidationError('there is no insurance configuration for employees please configur it and try again')

    @api.depends("date_of_birth", "now_date")
    def get_age_for_alloc_by_birth(self):
        for rec in self:
            if rec.now_date and rec.date_of_birth:
                fmt = '%Y-%m-%d'
                d1 = datetime.datetime.strptime(str(rec.now_date).strip(' \t\r\n').split(".")[0], fmt)
                d2 = datetime.datetime.strptime(str(rec.date_of_birth).strip(' \t\r\n').split(".")[0], fmt)
                years_between_dates = str((d1 - d2).days / 365)
                rec.current_emp_age = int(float(years_between_dates))
                print(years_between_dates)

    @api.depends('insurance_table')
    def cal_total_insurance(self):
        for line in self:
            if line.insurance_table:
                for rec in line.insurance_table:
                    line.total_insurance += rec.emp_amount
                    line.total_insurance_company += rec.company_amount

    @api.onchange('name', 'employee_id')
    def cal_name_from_emp_number(self):
        for rec in self:
            if rec.employee_id and rec.employee_id.hiring_date:
                rec.name = str(rec.employee_id.internal_number)
                rec.date_start = rec.employee_id.hiring_date
                rec.date_end = rec.date_start + relativedelta(years=1)
                rec.trial_date_end = rec.date_start + relativedelta(months=3)

    @api.onchange('name', 'state', 'form_registration_date', 'insurance_number', 'wage', 'company_percentage',
                  'employee_percentage', 'insurance_status',
                  'social_insurances', 'register_method')
    def move_employee_fields(self):
        for rec in self:
            if rec.state == 'open':
                check_emp = self.env['hr.employee'].search([('id', '=', rec.employee_id.id)])
                if check_emp:
                    check_emp.write(
                        {
                            'contract_end_date': rec.date_end,
                            'form_registration_date': rec.form_registration_date,
                            'social_insurances': rec.social_insurances,
                            'insurance_number': rec.insurance_number,
                            'register_method': rec.register_method,
                            'insurance_status': rec.insurance_status,
                            'company_percentage': rec.company_percentage,
                            'employee_percentage': rec.employee_percentage,
                        })


class InsuranceMonthlyRecords(models.Model):
    _name = 'insurance.monthly'

    date = fields.Date('Date')
    emp_amount = fields.Float('Employee Percentage')
    company_amount = fields.Float('Company Percentage')
    inv_history = fields.Many2one('hr.contract')


class HREmployee(models.Model):
    _inherit = 'hr.employee.public'

    hiring_date = fields.Date(string='Hiring Date', store=True, copy=True)
    hiring_date = fields.Date(string='Hiring Date', store=True, copy=True)
    internal_number = fields.Char(string="Tawzef Number")

    employee_number = fields.Char(string="Client Number", store=True)
    contract_end_date = fields.Date('Contract End Date')
    medic_exam = fields.Char()
    form_registration_date = fields.Date(string='تاريخ تسجيل الاستمارة', )
    social_insurances = fields.Selection([
        ('insured', "مؤمن عليه"),
        ('not_insured', "غير مؤمن عليه"),
    ], string='التأمينات الاجتماعية', default='not_insured')
    insurance_number = fields.Char(string='الرقم التأميني')
    register_method = fields.Selection([
        ('token', "Token"),
        ('office', "Office"),
    ], string='طريقة التسجيل', default='token')
    insurance_status = fields.Selection([
        ('open', "Open"),
        ('paid', "Paid"),
    ], string='حالة التأمين', default='open')

    company_percentage = fields.Float(string='نسبة الشركة', readonly=True)
    employee_percentage = fields.Float(string='نسبة الموظف', readonly=True)
    company_period = fields.Float(string='نسبة الشركة خلال الفترة', readonly=True, store=True)
    employee_period = fields.Float(string='نسبة الموظف خلال الفترة', readonly=True, store=True)
    working_schedule = fields.Many2one('work.schedule')
    service_id = fields.Many2one('product.product', domain="[('type','=','service')]", string="Current Service",
                                 tracking=True)
    branch_id = fields.Many2one('res.branch')

class HREmployeeContractInsurance(models.Model):
    _inherit = 'hr.employee'

    hiring_date = fields.Date(string='Hiring Date', store=True, copy=True)
    internal_number = fields.Char(string="Tawzef Number")

    employee_number = fields.Char(string="Client Number", store=True)
    contract_end_date = fields.Date('Contract End Date')
    medic_exam = fields.Char()
    form_registration_date = fields.Date(string='تاريخ تسجيل الاستمارة', )
    social_insurances = fields.Selection([
        ('insured', "مؤمن عليه"),
        ('not_insured', "غير مؤمن عليه"),
    ], string='التأمينات الاجتماعية', default='not_insured')
    insurance_number = fields.Char(string='الرقم التأميني')
    register_method = fields.Selection([
        ('token', "Token"),
        ('office', "Office"),
    ], string='طريقة التسجيل', default='token')
    insurance_status = fields.Selection([
        ('open', "Open"),
        ('paid', "Paid"),
    ], string='حالة التأمين', default='open')

    company_percentage = fields.Float(string='نسبة الشركة', readonly=True)
    employee_percentage = fields.Float(string='نسبة الموظف', readonly=True)
    company_period = fields.Float(string='نسبة الشركة خلال الفترة', readonly=True, store=True)
    employee_period = fields.Float(string='نسبة الموظف خلال الفترة', readonly=True, store=True)

    @api.onchange('name', 'insurance_number', 'social_insurances', 'register_method')
    def cal_emp_insurance_data_to_contract(self):
        for rec in self:
            print('hello everybody')
            print(self._origin.id)
            contr = self.env['hr.contract'].search([('state', '=', 'open'), ('employee_id', '=', self._origin.id)])
            if contr:
                contr.write(
                    {

                        'social_insurances': rec.social_insurances,
                        'insurance_number': rec.insurance_number,
                        'register_method': rec.register_method,
                        'name': rec.internal_number,

                    })
                # print('yes')
                # for line in contr:
                #     line.insurance_number = rec.insurance_number
                #     line.social_insurances = rec.social_insurances
                #     line.register_method = rec.register_method
                #     print(line.social_insurances,rec.social_insurances)
                #     print(line.insurance_number, rec.insurance_number)
                #     print(line.register_method, rec.register_method)
            else:
                print('nooo')


class HRPayrollContractInsurance(models.Model):
    _inherit = 'hr.payroll.structure'

    is_insured = fields.Boolean('مؤمن عليه')
    not_insured = fields.Boolean('غيرمؤمن عليه')
