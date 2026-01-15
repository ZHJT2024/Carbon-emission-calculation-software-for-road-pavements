# -*- coding: utf-8 -*-
from odoo import fields, api, models
from odoo.exceptions import UserError, ValidationError

class MechanicalLifeCycleInventory(models.Model):
    """
    Mixing life cycle inventory
    """
    _name = 'mixing.life.cycle.inventory'
    _description = "Mixing Life Cycle Inventory"
    _rec_name = 'name'

  

    name = fields.Char(string='Name', required=True)

    fuel_category = fields.Char(string='Fuel category', required=True)
    fuel_value = fields.Char(string='Fuel calorific value', required=True)
    fuel_unit = fields.Selection(
        selection=[
            ('mjkg', 'MJ/kg'),
            ('mjm3', 'MJ/m³'),
            ('mjkwh', 'MJ/kWh')
        ],
        default='mjkg', required=True, string='Calorific value unit')
    fuel_rate = fields.Char(string='Heat exchange rate', required=True)

    code = fields.Char(string='Code', compute='com_code')
    carbon_factor = fields.Char(string='Emission factor', required=True)
    type_id = fields.Many2one('life.cycle.inventory.type', 'Type', ondelete='cascade')
    unit_id = fields.Many2one('carbon.unit', 'Unit', ondelete='restrict', required=True)
    inventory_id = fields.Many2one('life.cycle.inventory', 'Inventory', ondelete='cascade')


    def com_code(self):
        for record in self:
            record.code = f'F-MX-{record.id}'
    
