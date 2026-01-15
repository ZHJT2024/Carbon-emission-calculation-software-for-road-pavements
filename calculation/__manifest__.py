# -*- coding: utf-8 -*-
{
    'name': "Shared Calculation Module",

    'summary': """
       Shared calculation utilities
       """,

    'description': """
          Shared calculation utilities
    """,
    'sequence': 320,

    'author': "Wei Zhou",
    'website': "",

 
    'category': 'Base Application',
    'version': '0.1',
    'license': 'LGPL-3',


    'depends': ['base','web'],

    'data': [
        'views/calculation_model.xml',
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
