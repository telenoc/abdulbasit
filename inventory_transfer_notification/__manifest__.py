# -*- coding: utf-8 -*-
{
    'name': "Inventory Transfer Notification",

    'summary': """
         Make this module for the inventory transfer notification  """,

    'description': """
        Make this module for the inventory transfer notification. In this module we create two field
         one is User Notification in this we have select the user and the other field Message we can type the message. 
    """,

    'author': "Abdul Basit",
    'website': "http://telenoc.org",


    'category': 'Customize',
    'version': '0.1',


    'depends': ['base', 'stock', 'sale', 'account_accountant'],


    'data': [
        'views/inventory_notification.xml',
    ],

}
