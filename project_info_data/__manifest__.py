# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Project - Info - Data",
    "version": "15.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainer": "Camptocamp",
    "license": "AGPL-3",
    "category": "Project",
    "complexity": "easy",
    "depends": ["base", "branch", "project", "hr", "base_address_city"],
    "website": "https://github.com/OCA/project",
    "data": [
        'views/employee_branch.xml',
        'views/project_info.xml',
    ],
    "installable": True,
    "auto_install": False,
}
