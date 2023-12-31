# -*- coding: utf-8 -*-
{
    'name': "attendance_sheet",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '15.0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_attendance'],

    # always loaded
    'data': [
        'security/security_group.xml',
        'security/ir.model.access.csv',
        'data/cron.xml',
        'views/views.xml',
        'views/templates.xml',
        'report/attendance_sheet_report.xml',
        'views/hr_attendance_sheet_views.xml',
        'views/hr_attendance_views.xml',
        'views/hr_department_views.xml',
        'views/hr_employee_views.xml',
        'views/res_company.xml',
        'views/res_config_settings.xml',
        'data/mail_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3',
}
