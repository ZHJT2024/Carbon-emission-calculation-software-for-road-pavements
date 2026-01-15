# -*- coding: utf-8 -*-
from odoo import models, fields,api


class resCountryStateCity(models.Model):
    '''
    City management
    '''
    _name = 'res.country.state.city'
    _description = 'City management'

    name = fields.Char('City name')
    state_id = fields.Many2one('res.country.state', 'State/Province')
    country_id = fields.Many2one('res.country', 'Country',related='state_id.country_id')
    code = fields.Char('City code')
    geo_json = fields.Text('geo json')
    district_ids = fields.One2many('res.country.state.city.district','city_id',string='Districts/Counties')
