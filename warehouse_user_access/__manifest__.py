# -*- coding: utf-8 -*-

{
    'name': 'Warehouse user access',
    'version': '15.0.1',
    'category': '',
    "author": "Yazeed Khader ",
    "website": "yazeedkhdr@gmail.com",
    'summary': '',
    'description': """
    user can see only allowed warehouses and related transfers and reports in INVENTORY and Barcode app
    """,
    'depends': ['stock', 'account', 'base'],
    'data': [
        'security/security.xml',
        'views/add_filde.xml',
    ],
    'installable': True,
    'auto_install': False,
    'assets': {},
    'license': 'LGPL-3',
}
