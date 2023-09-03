from odoo import fields, models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    week_number = fields.Char()
    time_type = fields.Selection(
        [('regular', 'Regular Hours'),
         ('overtime', 'Overtime'),
         ('weekend', 'Weekend Overtime'),
         ('timeoff', 'Paid Time Off'),
         ('holiday', 'Holiday Overtime')], string="Type",
        default='regular', required=True)


class HrExpenses(models.Model):
    _inherit = 'hr.expense'

    move_id = fields.Many2one('account.move')
    date = fields.Date(required=True)
    employee_sheet_id = fields.Many2one('employee.project.timesheet', "Employee Sheet", )
    amount = fields.Float(required=True)
    total_amount = fields.Monetary("Total In Currency", compute='_compute_amount', store=True,
                                   currency_field='currency_id', tracking=True, readonly=False)
    bill_non = fields.Selection([('bill', 'billable'), ('non', 'Nonbillable')], default='non', required=True)
    project_id = fields.Many2one('project.project', required=True)
    unit_amount = fields.Float("Unit Price", compute='_compute_from_product_id_company_id', store=True, required=False,
                               copy=True, states={'draft': [('readonly', False)], 'reported': [('readonly', False)],
                                                  'approved': [('readonly', False)], 'refused': [('readonly', False)]},
                               digits='Product Price')
    exchange_rate = fields.Float(default=1)
    move_currency = fields.Many2one('res.currency', related='move_id.currency_id')
    invoice_amount = fields.Monetary(compute='calc_invoice_amount_in_rate', currency_field='move_currency')
    expense_type = fields.Selection([('project', 'Project Expense'), ('travel', 'Travel'), ('other', 'Other Expense')],
                                    default='other')

    @api.depends('exchange_rate', 'total_amount')
    def calc_invoice_amount_in_rate(self):
        for rec in self:
            rec.invoice_amount = rec.amount / rec.exchange_rate

    @api.onchange('unit_amount', 'bill_non')
    def change_expense_amount_from_amount(self):
        if self.bill_non == 'non':
            total_amount = self.unit_amount
        else:
            total_amount = self.unit_amount * 1.1
        print("total_amount")
        print(total_amount)
        self.amount = total_amount

    def create_invoice_from_expenses(self):
        print("---------------------------------------------------------------")
        for rec in self:
            if rec.bill_non == 'non' or rec.move_id:
                print("continue")
                continue
            else:
                if rec.employee_sheet_id:
                    rec.move_id = rec.employee_sheet_id.invoice_id
                else:
                    employee_timesheet = self.env['employee.project.timesheet'].search(
                        [('date_from', '<=', rec.date), ('date_to', '>=', rec.date)])
                    print("employee_timesheet")
                    print(employee_timesheet)
                    rec.employee_sheet_id = employee_timesheet
                    rec.move_id = employee_timesheet.invoice_id
            print("expenses - >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.")


class AccountPer_diem(models.Model):
    _name = 'account.per.diem'

    date = fields.Date(required=True)
    employee_id = fields.Many2one('hr.employee', required=True)
    project_id = fields.Many2one('project.project', required=True)
    name = fields.Char('Description', required=True)
    quantity = fields.Integer(required=True)
    amount = fields.Float(required=True)
    total_amount = fields.Float(compute='calc_total_amount', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', help="Currency.", )
    move_id = fields.Many2one('account.move')
    company_id = fields.Many2one('res.company', readonly=True,
                                 default=lambda self: self.env.company)

    @api.depends('amount', 'quantity')
    def calc_total_amount(self):
        for rec in self:
            rec.total_amount = rec.amount * rec.quantity


class AccountMove(models.Model):
    _inherit = 'account.move'

    expenses_line_ids = fields.One2many('employee.project.expenses', 'move_id')
    hr_expense_line_ids = fields.One2many('hr.expense', 'move_id', string='Expenses')
    other_expense_ids = fields.One2many('account.per.diem', 'move_id', string='Other')
    project_id = fields.Many2one('project.project')
    service_id = fields.Many2one('product.product', domain="[('type','=','service')]", store=True)
    per_diem = fields.Float()
    employee_id = fields.Many2one('hr.employee')
    expense_move_id = fields.Many2one('account.move')

    def _get_account_move_line_values(self):
        move_line_values_by_expense = {}

    def action_post(self):
        self.create_expense_income_expense()
        return super(AccountMove, self).action_post()

    def create_expense_income_expense(self):
        for rec in self:
            self.ensure_one()
            journal = self.journal_id
            # account_date = date.today()
            move_values = {
                'journal_id': journal.id,
                'invoice_date': self.invoice_date,
                'date': self.invoice_date,
                'ref': self.name,
                'name': '/',
            }
            move = self.env['account.move'].create(move_values)

            move_line_values = []
            total = 0
            for line in rec.hr_expense_line_ids:
                move_line_src = {
                    'name': line.product_id.name,
                    'quantity': line.quantity,
                    'debit': 0,
                    'credit': line.total_amount,
                    'account_id': line.product_id.product_tmpl_id.get_product_accounts()['income'].id,
                    # 'analytic_account_id': overtime.analytic_account_id.id,
                    'partner_id': self.partner_id.id,
                }
                total += line.total_amount
                move_line_values.append(move_line_src)
            customer_move = move_line_src = {
                'name': self.project_id.name,
                'quantity': 1,
                'credit': 0,
                'debit': total,
                'account_id': self.partner_id.property_account_receivable_id.id,
                # 'analytic_account_id': overtime.analytic_account_id.id,
                'partner_id': self.partner_id.id,
            }
            move_line_values.append(customer_move)
            move.write({'line_ids': [(0, 0, line) for line in move_line_values]})
            self.write({'expense_move_id': move.id})
