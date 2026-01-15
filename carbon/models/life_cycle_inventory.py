# -*- coding: utf-8 -*-
from odoo import fields, api, models
from odoo.exceptions import UserError, ValidationError

class LifeCycleInventory(models.Model):
    """
    Life cycle inventory
    """
    _name = 'life.cycle.inventory'
    _description = "Life Cycle Inventory"
    _rec_name = 'name'

  

    is_active = fields.Boolean(string='Active')
    name = fields.Char(string='Inventory name', required=True)
    remark = fields.Char(string='Remarks')
    user_id = fields.Many2one('res.users', string='Account', required=True)
