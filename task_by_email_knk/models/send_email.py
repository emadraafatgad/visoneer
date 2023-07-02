# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).
from odoo import models, _, api


class Project(models.Model):
    _inherit = 'project.task'

    def send_task_by_email(self):
        compose_form = self.env.ref('mail.email_compose_message_wizard_form')
        return {
            'type': 'ir.actions.act_window',
            'name': _("Task By Email"),
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': {
                'default_res_model': 'mail.compose.message',
                'default_subject': self.name,
                'default_res_ids': self.user_ids.ids,
                'default_body': self.date_deadline,
                'default_body': self.description,
                'default_attachment_ids': self.attachment_ids.ids
            }
        }


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.model
    def default_get(self, fields):
        rec = super(MailComposer, self).default_get(fields)
        ctx = self.env.context
        if ctx.get('default_subject'):
            rec.update({'subject': ctx['default_subject']})
        return rec
