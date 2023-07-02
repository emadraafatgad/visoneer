# -*- coding: utf-8 -*-
{
    'name': "employee attendance sheet",

    'summary': """
        emad""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.emad.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '15.0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_attendance','hr_payroll_community'],

    # always loaded
    'data': [
        # 'security/security_group.xml',
        # 'security/ir.model.access.csv',
        'views/payslip.xml',
    ],
    # only loaded in demonstration mode
    'license': 'LGPL-3',
}
