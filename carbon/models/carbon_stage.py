# -*- coding: utf-8 -*-
from odoo import fields, api, models
from odoo.exceptions import UserError, ValidationError

class CarbonStage(models.Model):
    """
    Stage
    """
    _name = 'carbon.stage'
    _description = "Stage"
    _rec_name = 'name'
    _order = 'sequence'
    
    _sql_constraints = [('name_unique', 'unique(name)', 'Stage name must be unique.')]

  

    sequence = fields.Integer(string='Sequence')
    name = fields.Char(string='Stage name', required=True)
    code = fields.Char(string='Stage code')
   
    
