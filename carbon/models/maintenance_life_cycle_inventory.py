# -*- coding: utf-8 -*-
from odoo import fields, api, models
from odoo.exceptions import UserError, ValidationError

class MaintenanceLifeCycleInventory(models.Model):
    """
    Maintenance life cycle inventory
    """
    _name = 'maintenance.life.cycle.inventory'
    _description = "Maintenance Life Cycle Inventory"
    _rec_name = 'name'

  

    name = fields.Char(string='Distress type', required=True)
    code = fields.Char(string='Code', compute='com_code')
    remark = fields.Char(string='Remarks', required=True)
    carbon_factor = fields.Char(string='Emission factor', required=True)
    unit_id = fields.Many2one('carbon.unit', 'Unit', ondelete='restrict', required=True)
    type_id = fields.Many2one('life.cycle.inventory.type', 'Type', ondelete='cascade')
    inventory_id = fields.Many2one('life.cycle.inventory', 'Inventory', ondelete='cascade')


    def com_code(self):
        for record in self:
            record.code = f'F-BH-{record.id}'
    
