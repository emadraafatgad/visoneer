# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    "name" : "Manual Currency Exchange Rate",
    "version" : "15.0.0.2",
    'sequence': 1,
    "depends" : ['base','account'],
    "author": "Abdallah-Mohamed",
    'sequence': 1,
    "summary": "Apps apply manual currency rate on payment",
    "description": """Apps apply manual currency rate on payment""",
    "price": 0,    
    "currency": "EUR",
    'category': 'Accounting',
    "website" : "https://facebook.com/bodyx1994",
    "data" :[
             "views/customer_invoice.xml",
             "views/account_payment_view.xml",
             "views/currency_rate_report.xml",
    ],
    'qweb':[
    ],
    "auto_install": False,
    'application': True,
    "installable": True,
    "live_test_url": "",
	"images":[''],
    "license": "OPL-1",
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
