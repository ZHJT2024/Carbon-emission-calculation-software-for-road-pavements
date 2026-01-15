# -*- coding: utf-8 -*-
from odoo import models, fields,api
import logging
import requests
_logger = logging.getLogger(__name__)


class resCountryStateCityDistrict(models.Model):
    '''
    District/county management
    '''
    _name = 'res.country.state.city.district'
    _description = 'District/County management'

    name = fields.Char('District/County name')
    city_id = fields.Many2one('res.country.state.city', 'City')

    state_id = fields.Many2one('res.country.state', 'State/Province',related='city_id.state_id')
    country_id = fields.Many2one('res.country', 'Country',related='state_id.country_id')
    code = fields.Char('Code')
    geo_json = fields.Text('geo json')


    @api.model
    def district_import(self,args):
        state_id = None
        city_id = None
        country_id = self.env['res.country'].search([('code','=','CN')],limit=1).id
        data = args.get('file_data').rstrip('\r\n').split('\r\n')
        for lis in data[1:]:
            row_list = lis.split(',')
            code,name = (row_list[i] for i in range(0,2))
            url = f'https://geo.datav.aliyun.com/areas_v2/bound/{code}.json'
            geo_json = requests.get(url).text
           
            code_end_2 = code[4:6]
            code_end_4 = code[2:6]
            if code_end_4 == '0000':
                state_id = self.env['res.country.state'].create({
                    'name':name,
                    'code':code,
                    'geo_json':geo_json,
                    'country_id':country_id,
                }).id
            elif code_end_2 == '00':
                city_id = self.env['res.country.state.city'].create({
                    'name':name,
                    'code':code,
                    'geo_json':geo_json,
                    'state_id':state_id,
                }).id
            else:
                self.env['res.country.state.city.district'].create({
                    'name':name,
                    'code':code,
                    'geo_json':geo_json,
                    'city_id':city_id,
                })
        return 'Import successful.'
        

            
            




