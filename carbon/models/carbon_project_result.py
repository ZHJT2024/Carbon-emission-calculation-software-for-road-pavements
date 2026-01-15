# -*- coding: utf-8 -*-
from odoo import fields, api, models
from odoo.exceptions import UserError, ValidationError

class CarbonProjectResult(models.Model):
    """
    Computation result
    """
    _name = 'carbon.project.result'
    _description = "Computation Result"
    # _rec_name = 'name'

    project_id = fields.Many2one('carbon.project', 'Project', ondelete='cascade')
    scheme_id = fields.Many2one('carbon.project.scheme', 'Scheme', required=True, ondelete='cascade')
    stage_id = fields.Many2one('carbon.stage', string='Stage', required=True)
    res_all = fields.Char(string='Total GHG emissions')
    res_area = fields.Char(string='Emission intensity per unit area')
    res_year = fields.Char(string='Average annual emission intensity')
    res_area_year = fields.Char(string='Average annual emission intensity per unit area')
    category_result = fields.Text(string='Category-level results')








