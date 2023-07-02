{
    'name': 'HR Taxes',
    'version': '1.0',
    'category': '',
    'sequence': 14,
    'author': '',
    'company': '',
    'license': 'LGPL-3',
    'website': '',
    'summary': '',
    'depends': ['base','hr_payroll_community','hr_insurance'],
    'data': [

           'security/contact.xml',
           'security/rules.xml',
           'security/ir.model.access.csv',
           'views/tax.xml',
           'views/tax_part.xml',
           'views/contract.xml',
           'views/working_days.xml',

            ],
    'demo': [],
    'images': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
