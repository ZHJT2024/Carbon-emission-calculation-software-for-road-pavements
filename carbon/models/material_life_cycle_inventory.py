# -*- coding: utf-8 -*-
from odoo import fields, api, models
from odoo.exceptions import UserError, ValidationError

class MaterialLifeCycleInventory(models.Model):
    """
    Material life cycle inventory
    """
    _name = 'material.life.cycle.inventory'
    _description = "Material Life Cycle Inventory"
    _rec_name = 'name'

  

    name = fields.Char(string='Material name', required=True)
    carbon_factor = fields.Char(string='Emission factor', required=True)
    unit_id = fields.Many2one('carbon.unit', 'Unit', ondelete='restrict', required=True)
    type_id = fields.Many2one('life.cycle.inventory.type', 'Type', ondelete='cascade')
    stage_id = fields.Many2one('carbon.stage', 'Stage', ondelete='cascade')
    link_id = fields.Many2one('carbon.link', 'Process step')
    inventory_id = fields.Many2one('life.cycle.inventory', 'Inventory', ondelete='cascade' )
    composition_id = fields.Many2one('structural.layer.composition', 'Component')


    
    
