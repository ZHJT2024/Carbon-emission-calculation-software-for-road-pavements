# -*- coding: utf-8 -*-
from odoo import fields, api, models
from odoo.exceptions import UserError, ValidationError

class StructuralLayer(models.Model):
    """
    Structural layer
    """
    _name = 'structural.layer'
    _description = "Structural Layer"
    _rec_name = 'name'

  

    name = fields.Char(string='Name', required=True)
    is_active = fields.Boolean('Active',default=False)
    composition_ids = fields.Many2many('structural.layer.composition', 'structural_layer_composition_layer','layer_id','composition_id', string="Components", copy=False)
    
