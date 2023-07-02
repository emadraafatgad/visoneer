from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError, ValidationError

class HrContractSalaryStopExtraInherit(models.Model):
    _inherit = "hr.contract"

    salary_stop = fields.Boolean(string="Salary Stop")
    salary_stop_date_from = fields.Date(string="From Date")
    salary_stop_date_to = fields.Date(string="To Date")

    #
    # def action_payslip_done(self):
    #     if self.contract_id.salary_stop == True:
    #         raise ValidationError("Employee Salary has been stopped!!")
    #     if not self.env.context.get('without_compute_sheet'):
    #         self.compute_sheet()
    #     return self.write({'state': 'done'})


