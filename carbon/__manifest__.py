# -*- coding: utf-8 -*-
{
    'name': "Carbon Accounting Module",

    'summary': """
       Carbon accounting module
       """,

    'description': """
         Carbon accounting module
    """,
    'sequence': 300,

    'author': "Wei Zhou",
    'website': "",

    'category': 'Base Application',
    'version': '0.1',
    'license': 'LGPL-3',


    'depends': ['base','web'],

 
    'data': [
        'reports/report_fine.xml',
        'reports/report_fine_compare.xml',
        'reports/report_rough.xml',
        'reports/report_rough_compare.xml',
        'views/res_country_state_city_district.xml',
        'views/res_country_state_city.xml',
        'views/res_country_state_extend.xml',
        'views/structural_layer.xml',
        'views/structural_layer_composition.xml',
        'views/life_cycle_inventory.xml',
        'views/life_cycle_inventory_type.xml',
        'views/material_life_cycle_inventory.xml',
        'views/mechanical_life_cycle_inventory.xml',
        'views/mixing_life_cycle_inventory.xml',
        'views/maintenance_life_cycle_inventory.xml',
        'views/carbon_life_cycle_inventory.xml',
        'views/carbon_project.xml',
        'views/carbon_project_scheme.xml',
        'views/carbon_project_result.xml',
        'views/carbon_unit.xml',
        'views/carbon_stage.xml',
        'views/carbon_link.xml',
        'views/res_users.xml',
        'views/security_role_data.xml',
        'views/menu.xml',
        'views/carbon_crons.xml',
        'views/res_groups_data.xml',
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
