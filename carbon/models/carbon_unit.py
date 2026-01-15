# -*- coding: utf-8 -*-
from odoo import fields, api, models
from odoo.exceptions import UserError, ValidationError

class CarbonUnit(models.Model):
    """
    Unit
    """
    _name = 'carbon.unit'
    _description = "Unit"
    _rec_name = 'name'
    
    _sql_constraints = [('name_unique', 'unique(name)', 'Unit name must be unique.')]

  
    name = fields.Char(string='Unit', required=True)
    type = fields.Selection(
        selection=[
            ('material', 'Material'),
            ('mechanical', 'Mechanical'),
            ('mixing', 'Mixing'),
            ('maintenance', 'Maintenance')
        ],
        default='material', required=False, string='Type (Deprecated)')
   
    
