# -*- coding: utf-8 -*-
from odoo import models, fields,api


class resCountryExtend(models.Model):
    '''
    Country extension
    '''
    _inherit = 'res.country'
    
    geo_json = fields.Text('geo json')

class resCountryStateExtend(models.Model):
    '''
    State/province extension
    '''
    _inherit = 'res.country.state'
    
    city_ids = fields.One2many('res.country.state.city','state_id',string='Cities')
    geo_json = fields.Text('geo json')







