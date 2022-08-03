# -*- coding: utf-8 -*-
{
    'name': "Parent Partner",
    'summary': """
        Make A Field on Partner Form and Show Under The Address Type""",
    'description': """
        Make A Field on Partner Form and Show Under The Address Type
    """,
    'author': "Viltco",
    'website': "http://www.viltco.com",
    'category': 'contacts',
    'version': '15.0.0.0',
    'depends': ['base', 'web','contacts', 'account','account_reports'],
    'data': [
        'security/ir.model.access.csv',
        'views/parent_partner_views.xml',
        'wizard/partner_ledger.xml',
        'reports/report.xml',
        'reports/report_partner_ledger.xml',


    ],
    'assets': {
        'web.assets_backend': ['parent_partner/static/src/js/account_reports.js']
    },
    'license': 'LGPL-3',
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': False
}
