# -*- coding: utf-8 -*-
from odoo import fields, api, models
from odoo.exceptions import UserError, ValidationError

class CarbonLink(models.Model):
    """
    Process step
    """
    _name = 'carbon.link'
    _description = "Process Step"
    _rec_name = 'name'
    _order = 'sequence'
    
    sequence = fields.Integer(string='Sequence')
    name = fields.Char(string='Process step name', required=True)
    code = fields.Char(string='Process step code')
    stage_id = fields.Many2one('carbon.stage', string='Stage')
   
    
