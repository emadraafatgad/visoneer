# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models , fields, api


class Project(models.Model):
    _inherit = "project.project"

    branch_id = fields.Many2one('res.branch')
    country_id = fields.Many2one('res.country')
    state_id = fields.Many2one('res.country.state',domain="[('country_id', '=', country_id)]")
    city_id = fields.Many2one('res.city', 'City',domain="[('country_id', '=', country_id)]")
