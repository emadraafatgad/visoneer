{
    'name': 'Social Insurance',
    'version': '1.0',
    'category': '',
    'sequence': 14,
    'author': '',
    'company': '',
    'license': 'LGPL-3',
    'website': '',
    'summary': '',
    'depends': ['base','hr_payroll_community','report_xlsx'],
    'data': [

           'security/contact.xml',
           'security/ir.model.access.csv',
           'views/social_insurance.xml',
           'views/employee_contract.xml',
           # 'views/insurance_report.xml',

            ],
    'demo': [],
    'images': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
