# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccountPayment(models.TransientModel):
    _inherit ='account.payment.register'

    manual_currency_rate_active = fields.Boolean('Apply Manual Exchange')
    manual_currency_rate = fields.Float('Rate', digits=(12, 12), tracking=500)

class ReportCurrencyRate(models.AbstractModel):
    _name = 'report.module_name.report_name'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.payment.register'].browse(docids)
        report_data = []
        for doc in docs:
            report_data.append({
                'name': doc.name,
                'manual_currency_rate_active': doc.manual_currency_rate_active,
                'manual_currency_rate': doc.manual_currency_rate,
                'created_date': doc.create_date,
            })
        return {
            'doc_ids': docs.ids,
            'doc_model': 'account.payment.register',
            'docs': docs,
            'report_data': report_data,
        }
           change_date = fields.Datetime('Change Date', readonly=True, default=fields.Datetime.now)
          old_rate = fields.Float('Old Rate', digits=(12, 12), readonly=True)
          new_rate = fields.Float('New Rate', digits=(12, 12), readonly=True)