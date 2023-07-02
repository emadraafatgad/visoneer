# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrDepartment(models.Model):
    _inherit = "hr.department"

    attendance_admin = fields.Many2one(
        "hr.employee",
        string="Attendance Admin",
        help="""In addition to the employees manager, this person can
        administer attendances for all employees in the department.""",
    )
