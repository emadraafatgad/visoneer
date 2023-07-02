from odoo import models, fields, api, exceptions, _


class WizComputePayslip(models.TransientModel):
    _name = "compute.payslip"

    # name = fields.Text('Reject Reason')
    payslip = fields.Many2many('hr.payslip',domain=[('state','=','draft')])
    # domain = [('marked', '=', False), ('state', '=', 'done'), ('code_op', '=', 'incoming')]
    # dest_location = fields.Many2one('stock.location',string='Destination Location',domain=[('usage','=','internal')])
    @api.multi
    def confirm(self):
        for rec in self:
            for line in rec.payslip:
                line.compute_sheet()


class WizDonePayslip(models.TransientModel):
    _name = "done.payslip"

    # name = fields.Text('Reject Reason')
    payslip = fields.Many2many('hr.payslip',domain=[('state','=','compute')] )
    # domain = [('marked', '=', False), ('state', '=', 'done'), ('code_op', '=', 'incoming')]
    # dest_location = fields.Many2one('stock.location',string='Destination Location',domain=[('usage','=','internal')])
    @api.multi
    def confirm(self):
        for rec in self:
            for line in rec.payslip:
                line.action_payslip_done()

