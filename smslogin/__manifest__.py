# -*- coding: utf-8 -*-
{
    'name': "SMS Login Module",

    'summary': """
       SMS-based login module
       """,

    'description': """
         SMS-based login module
    """,
    'sequence': 310,

    'author': "Wei Zhou",
    'website': "",


    'category': 'Base Application',
    'version': '0.1',
    'license': 'LGPL-3',

 
    'depends': ['base','web'],


    'data': [
        'views/login_record.xml',
        'views/captcha_record.xml',
        'views/verify_code.xml',
        'views/menu.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        ],

    'demo': [
        # 'demo/demo.xml',
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,

}
