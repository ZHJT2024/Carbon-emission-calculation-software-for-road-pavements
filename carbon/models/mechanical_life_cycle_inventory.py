# -*- coding: utf-8 -*-
from odoo import fields, api, models
from odoo.exceptions import UserError, ValidationError

class MechanicalLifeCycleInventory(models.Model):
    """
    Mechanical life cycle inventory
    """
    _name = 'mechanical.life.cycle.inventory'
    _description = "Mechanical Life Cycle Inventory"
    _rec_name = 'name'

  

    name = fields.Char(string='Machine name', required=True)
    code = fields.Char(string='Code', compute='com_code')
    carbon_factor = fields.Char(string='Emission factor', required=True)
    type_id = fields.Many2one('life.cycle.inventory.type', 'Type', ondelete='cascade')
    unit_id = fields.Many2one('carbon.unit', 'Unit', ondelete='restrict', required=True)
    inventory_id = fields.Many2one('life.cycle.inventory', 'Inventory', ondelete='cascade')


    def com_code(self):
        for record in self:
            record.code = f'F-JX-{record.id}'
    
