# -*- coding: utf-8 -*-
from odoo import fields, api, models
from odoo.exceptions import UserError, ValidationError

class LifeCycleInventoryType(models.Model):
    """
    Life cycle inventory type
    """
    _name = 'life.cycle.inventory.type'
    _description = "Life Cycle Inventory Type"
    _rec_name = 'name'

  
    name = fields.Char(string='Name', required=True)
    category = fields.Selection(selection=[
        ('material', 'Material'),
        ('ys_mechanical', 'Transport machinery'),
        ('mixing', 'Mixing'),
        ('sg_mechanical', 'Construction machinery'),
        ('cc_mechanical', 'Demolition machinery'),
        ('maintenance', 'Maintenance'),
        ('carbon', 'Carbon sink')
    ], string='Unit type (Deprecated)', required=True, default='material')
    link_id = fields.Many2one('carbon.link', 'Process step', ondelete='cascade')
    unit_ids = fields.Many2many('carbon.unit', 'inventory_type_unit','type_id','unit_id', string="Units", required=True)
    
