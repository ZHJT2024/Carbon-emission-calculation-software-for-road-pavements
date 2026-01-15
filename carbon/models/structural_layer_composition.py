# -*- coding: utf-8 -*-
from odoo import fields, api, models
from odoo.exceptions import UserError, ValidationError

class StructuralLayerComposition(models.Model):
    """
    Structural layer component
    """
    _name = 'structural.layer.composition'
    _description = "Structural Layer Component"
    _rec_name = 'name'
    _order = 'sequence'

  
    sequence = fields.Integer(string='Sequence')
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code pattern', required=True)
    unit = fields.Char(string='Unit')
    type = fields.Selection(
            selection=[
                ('checkbox', 'Multiple choice'),
                ('radio', 'Single choice'),
                ('fill', 'Free text')
            ], required=True, string='Type',
            default='checkbox')
    columns = fields.Text('Column configuration for multi-select table')
    max_length = fields.Integer('Maximum number of selections')
    layer_ids = fields.Many2many('structural.layer', 'structural_layer_composition_layer','composition_id','layer_id', string="Structural layers", copy=False)


    def name_get(self):
        result = []
        for c in self:
            result.append((c.id, (f"{c.name}({', '.join(c.layer_ids.mapped('name'))})")))
        return result
    
