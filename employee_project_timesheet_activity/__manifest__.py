{
    "name": "Project Timesheet Activity",
    "summary": "Project Timesheet Activity For Visioneering",
    "author": "Emad $ Adham ",
    "category": "Timesheet",
    "version": "0.0.9",
    "license": "AGPL-3",
    "depends": ['hr_timesheet', 'account','project', 'branch', 'hr_payroll_community','hr_expense'],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        'views/working_schedule.xml',
        'views/invoice_config.xml',
        'views/contract_rate.xml',
        'views/sale_order.xml',
        'views/expenses_menu.xml',
        "views/project_timesheet_activity_configuration.xml",
        "views/inherit_project_task.xml",
        "views/project_employee_timesheet.xml",
        "views/account_move.xml",
        'views/payslip_timesheet.xml',
        "views/rules.xml",
        "reports/report_invoice.xml",
    ],
    "application": True,
    "development_status": "Beta",
    "installable": True,
    "support": "emad.raafat1555@gmail.com",
    "summary": "his module adds a new field 'Activity' in timesheet line. User can analyze the time spent in different type of activities. This analysis helps in better planning.",
    'images': ['images/timesheetontask.png'
               ],
}
