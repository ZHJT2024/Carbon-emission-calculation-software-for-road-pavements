# -*- coding: utf-8 -*-
{
    'name': "Access Control Module",

    'summary': """
       Access control module
       """,

    'description': """
         Access control module
    """,
    'sequence': 200,

    'author': "Wei Zhou",
    'website': "",

    'category': 'Bim Construction',
    'version': '0.1',
    'license': 'LGPL-3',


    'depends': ['base'],

 
    'data': [
        'views/access_navigation.xml',
        'views/access_route.xml',
        'views/access_route_button.xml',
        'views/role_access_navigation.xml',
        'views/role_access_route.xml',
        'views/role_access_route_button.xml',
        'views/menu.xml',
        'views/security_role_extend.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        ],
    'demo': [
        # 'demo/demo.xml',
    ],
    'qweb': [
        "static/src/xml/template.xml",
    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
