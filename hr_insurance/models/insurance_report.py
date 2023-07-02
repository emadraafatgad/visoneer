from odoo import models, fields, api, exceptions, _
import datetime,calendar
# from odoo.tools import dateutil
from datetime import date, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT




class WizInsuranceContract(models.TransientModel):
    _name = "insurance.wiz"

    emp_ids = fields.Many2many('hr.employee',string='Employees',context = {'active_test': False})
    archived_employees = fields.Boolean('Archived Employees')
    time_range = fields.Selection([
        ('current_month', "الشهر الحالى"),
        ('previous_month', "الشهر السابق"),
        ('current_quarter', "الربع السنوى الحالى"),
        ('previous_quarter', "الربع السنوى السابق"),
        ('previous_year', "السنه السابقة"),
        ('date', "تاريخ"),
    ], string='Time range',default='current_month')
    date_from = fields.Date('From Date')
    date_to = fields.Date('To Date')
    date_in = fields.Date('To Date')
    date_from_range = fields.Date('From Date range',default=fields.Date.today(),readonly=True)
    date_to_rang = fields.Date('To Date range',default=fields.Date.today(),readonly=True)


    @api.onchange('time_range')
    def _compute_date_amount(self):
        for rec in self:

                if rec.time_range =='current_month':
                    date = fields.Date.today()
                    f1 = datetime.datetime(date.year, date.month, 1)
                    l1 = datetime.datetime(date.year, date.month, calendar.mdays[date.month])
                    print(f1,l1)
                    rec.date_from_range = dateutil.parser.parse(str(f1)).date()
                    rec.date_to_rang = dateutil.parser.parse(str(l1)).date()
                # print('hiiiiii')
                # planned = (datetime.datetime.strptime(str(rec.date_from_range), '%Y-%m-%d') + datetime.timedelta(
                #     days=1)).strftime('%Y-%m-%d')
                # planned2 = (datetime.datetime.strptime(str(rec.date_to_rang), '%Y-%m-%d') + datetime.timedelta(
                #     days=3)).strftime('%Y-%m-%d')
                # print(planned,planned2)
                elif rec.time_range == 'previous_month':
                    date = fields.Date.today()
                    last_day_of_prev_month = date.today().replace(day=1) - timedelta(days=1)

                    start_day_of_prev_month = date.today().replace(day=1) - timedelta(days=last_day_of_prev_month.day)
                    print(last_day_of_prev_month,start_day_of_prev_month)
                    rec.date_from_range = start_day_of_prev_month
                    rec.date_to_rang = last_day_of_prev_month
                elif rec.time_range == 'previous_year':
                    date = fields.Date.today()
                    rec.date_from_range = datetime.date(date.today().year-1, 1, 1)
                    rec.date_to_rang = datetime.date(date.today().year-1, 12, 31)
                elif rec.time_range == 'current_quarter':
                    # current_date = datetime.now()
                    date = fields.Date.today()
                    date = datetime.datetime.strptime(str(date), DEFAULT_SERVER_DATE_FORMAT)
                    month = date.month
                    year = date.year
                    day = date.day
                    print(month,year,day)
                    if month==1 or month==2 or month==3 :
                        rec.date_from_range =str(year)+'-1-1'
                        rec.date_to_rang = str(year)+'-3-31'
                    elif month==4 or month==5 or month==6 :
                        rec.date_from_range =str(year)+'-4-1'
                        rec.date_to_rang = str(year)+'-6-30'
                    elif month==7 or month==8 or month==9 :
                        rec.date_from_range =str(year)+'-7-1'
                        rec.date_to_rang = str(year)+'-9-30'
                    elif month==10 or month==11 or month==12 :
                        rec.date_from_range =str(year)+'-10-1'
                        rec.date_to_rang = str(year)+'-12-31'
                    # currquarter = (date.month - 1) / 3 + 1
                    # rec.date_from_range = datetime.date(date.year, int(3 * currquarter - 2), 1)
                    # rec.date_to_rang = datetime.date(date.year,int(3 * currquarter + 1), 1) + timedelta(days=-1)
                elif rec.time_range == 'previous_quarter':
                    # current_date = datetime.now()
                    date = fields.Date.today()
                    date = datetime.datetime.strptime(str(date), DEFAULT_SERVER_DATE_FORMAT)
                    month = date.month
                    year = date.year
                    day = date.day
                    print(month,year,day)
                    if month==4 or month==5 or month==6 :
                        rec.date_from_range =str(year)+'-1-1'
                        rec.date_to_rang = str(year)+'-3-31'
                    elif month==7 or month==8 or month==9 :
                        rec.date_from_range =str(year)+'-4-1'
                        rec.date_to_rang = str(year)+'-6-30'
                    elif month==10 or month==11 or month==12 :
                        rec.date_from_range =str(year)+'-7-1'
                        rec.date_to_rang = str(year)+'-9-30'
                    elif month==1 or month==2 or month==3 :
                        rec.date_from_range =str(year-1)+'-10-1'
                        rec.date_to_rang = str(year-1)+'-12-31'


    def download_excel(self):
        return self.env.ref('hr_insurance.insurance_report_all').report_action(self)

    @api.onchange('time_range','date_from','date_to','date_from_range','date_to_rang')
    def cal_periods_insurance(self):
        for rec in self:
            if rec.emp_ids:
                if rec.time_range :
                    if rec.time_range =='date':
                        if rec.date_to and rec.date_from:
                            for line in rec.emp_ids:
                                list_emp=[]
                                list_company = []
                                contract = self.env['hr.contract'].search([('employee_id', '=', line.id),('state','=', 'open')],limit=1)
                                if contract:
                                    if contract.insurance_table:
                                        for record in contract.insurance_table:
                                            if (record.date >=rec.date_from)and(record.date <=rec.date_to):
                                                list_emp.append(record.emp_amount)
                                                list_company.append(record.company_amount)
                                        print(sum(list_emp))
                                        print(sum(list_company))
                                        sum_emp =sum(list_emp)
                                        sum_company = sum(list_company)
                                        line.employee_period=(sum_emp)
                                        line.company_period = (sum_company)
                    else:
                        if rec.date_from_range and rec.date_to_rang:
                            for line in rec.emp_ids:
                                list_emp = []
                                list_company = []
                                contract = self.env['hr.contract'].search(
                                    [('employee_id', '=', line.id), ('state', '=', 'open')], limit=1)
                                if contract:
                                    if contract.insurance_table:
                                        for record in contract.insurance_table:
                                            if (record.date >= rec.date_from_range) and (record.date <= rec.date_to_rang):
                                                list_emp.append(record.emp_amount)
                                                list_company.append(record.company_amount)
                                        print(sum(list_emp))
                                        print(sum(list_company))
                                        sum_emp = sum(list_emp)
                                        sum_company = sum(list_company)
                                        line.employee_period = (sum_emp)
                                        line.company_period = (sum_company)


class PartnerXlsx(models.AbstractModel):
    _name = 'report.hr_insurance.insurance_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet("Insurance Report")
        format = workbook.add_format({'bold': False, 'align': 'center'})
        style = workbook.add_format({'bold': True, 'align': 'center'})
        sheet.write(0, 0, "Name",style)
        sheet.write(0, 1, "Name In Arabic",style)
        sheet.write(0, 2, "Company",style)
        sheet.write(0, 3, "Mobile Phone",style)
        sheet.write(0, 4, "Employee Number",style)
        sheet.write(0, 5, "Internal Number",style)
        sheet.write(0, 6, "Job",style)
        sheet.write(0, 7, "Identification ID",style)
        sheet.write(0, 8, "Birthday",style)
        sheet.write(0, 9, "Hiring Date",style)
        sheet.write(0, 10, "Contract End Date",style)
        sheet.write(0, 11, "Form Registration Date",style)
        sheet.write(0, 12, "Social Insurances",style)
        sheet.write(0, 13, "Insurance Number",style)
        sheet.write(0, 14, "Register Method",style)
        sheet.write(0, 15, "Insurance Status",style)
        sheet.write(0, 16, "Company Percentage", style)
        sheet.write(0, 17, "Employee Percentage", style)
        sheet.write(0, 18, "Employee Period", style)
        sheet.write(0, 19, "Company Period", style)
        line_number = 1
        length = len(partners.emp_ids)
        # print(length)
        #
        # if partners.time_range=='date':
        for line in partners.emp_ids:
            #     if length > 0:
                sheet.write(line_number, 0, line.name , format)
                sheet.write(line_number, 1, line.name_in_arabic, format)
                sheet.write(line_number, 2, line.company_id.name, format)
                sheet.write(line_number, 3, line.mobile_phone, format)
                sheet.write(line_number, 4, line.employee_number, format)
                sheet.write(line_number, 5, line.internal_number, format)
                sheet.write(line_number, 6, line.job_id.name, format)
                sheet.write(line_number, 7, line.identification_id, format)
                sheet.write(line_number, 8, str(line.birthday), format)
                sheet.write(line_number, 9,str(line.hiring_date), format)
                sheet.write(line_number, 10, str(line.contract_end_date), format)
                sheet.write(line_number, 11, str(line.form_registration_date), format)
                sheet.write(line_number, 12, str(line.social_insurances), format)
                sheet.write(line_number, 13, line.insurance_number, format)
                sheet.write(line_number, 14, str(line.register_method), format)
                sheet.write(line_number, 15, str(line.insurance_status), format)
                sheet.write(line_number, 16, str(line.company_percentage), format)
                sheet.write(line_number, 17, str(line.employee_percentage), format)
                sheet.write(line_number, 18, str(line.employee_period), format)
                sheet.write(line_number, 19, str(line.company_period), format)

                line_number += 1
                length -= 1
            # sheet.write(line_number, 0, line.footer_collection, format)
