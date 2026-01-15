# -*- coding: utf-8 -*-
from odoo import fields, api, models
from odoo.exceptions import UserError, ValidationError

class CarbonLifeCycleInventory(models.Model):
    """
    Carbon sink life cycle inventory
    """
    _name = 'carbon.life.cycle.inventory'
    _description = "Carbon Sink Life Cycle Inventory"
    _rec_name = 'name'

  

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', compute='com_code')
    carbon_factor = fields.Char(string='Emission factor', required=True)
    remark = fields.Char(string='Remarks')
    unit_id = fields.Many2one('carbon.unit', 'Unit', ondelete='restrict', required=True)
    material_id = fields.Many2one('material.life.cycle.inventory', 'Recycled material')
    type_id = fields.Many2one('life.cycle.inventory.type', 'Type', ondelete='cascade')
    inventory_id = fields.Many2one('life.cycle.inventory', 'Inventory', ondelete='cascade')


    def com_code(self):
        for record in self:
            record.code = f'F-TH-{record.id}'
    
