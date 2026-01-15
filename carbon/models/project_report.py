# -*- coding: utf-8 -*-
from odoo import fields, api, models
from odoo.exceptions import UserError, ValidationError
import logging
import os
import time
import uuid
import json
import matplotlib
import matplotlib.pyplot as plt
from odoo.http import request
import requests
from datetime import datetime,timedelta




import numpy as np
_logger = logging.getLogger(__name__)

def create_pie(x,labels,explode,title,save_path_image):
    # No negative values: generate a pie chart.
    path = os.path.dirname(os.path.abspath(__file__)).replace('models','static')
    font_props = matplotlib.font_manager.FontProperties(fname=path + '/fonts/simhei.ttf')

    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    _, l_text, autotexts = ax.pie(x = x, labels=labels, shadow=0,autopct='%.2f%%', explode=explode)

    # Set pie chart label color to white.
    for autotext in autotexts:
        autotext.set_color('white')
    for t in l_text: 
        t.set_fontproperties(font_props)
    ax.set_title(title, loc="center", fontsize=16, fontproperties=font_props)
    plt.savefig(path + save_path_image)


def create_two_pie(z_x,f_x,labels,explode,title,save_path_image):
    # Negative values exist: generate an outer ring (positive) and an inner ring (negative).
    path = os.path.dirname(os.path.abspath(__file__)).replace('models','static')
    font_props = matplotlib.font_manager.FontProperties(fname=path + '/fonts/simhei.ttf')

    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    size = 0.3
    vals = np.array([[60., 32.], [37., 40.], [29., 10.]])
    cmap = plt.get_cmap("tab20c")
    outer_colors = cmap(np.arange(5)*4)
    inner_colors = cmap([1, 2, 5, 6, 9, 10])

    _logger.info('vals.sum(axis=1)')
    _logger.info(vals.sum(axis=1))
    _logger.info(vals.flatten())
    _, l_text, autotexts = ax.pie(z_x, radius=1,labels=labels,pctdistance=0.85, colors=outer_colors,autopct='%.2f%%', wedgeprops=dict(width=size, edgecolor='w'))
    for autotext in autotexts:
        autotext.set_color('white')
    for t in l_text: 
        t.set_fontproperties(font_props)
    ax.set_title(title, loc="center", fontsize=16, fontproperties=font_props)
    _, l_text, autotexts = ax.pie([10], radius=0.5,labels=np.array(['Carbon sink']),pctdistance=0.7, colors=['red'],autopct='-%.2f%%', wedgeprops=dict(width=size, edgecolor='w'))
    for t in l_text: 
        t.set_fontproperties(font_props)
    for autotext in autotexts:
        autotext.set_color('white')
    plt.savefig(path + save_path_image)

def create_bar(x,y,title,save_path_image):
    path = os.path.dirname(os.path.abspath(__file__)).replace('models','static')
    font_props = matplotlib.font_manager.FontProperties(fname=path + '/fonts/simhei.ttf')

    fig, ax = plt.subplots(1, 1, figsize=(8, 8))

    ax.set_title(title, loc="center", fontsize=16, fontproperties=font_props)
    ax.bar(x, y, color='#547ccb')
    for label in ax.get_xticklabels():
        label.set_fontproperties(font_props)
    plt.savefig(path + save_path_image)


class ProjectReportRough(models.AbstractModel):
    _name = 'report.carbon.project_report_rough'

    @api.model
    def _get_report_values(self, docids, data=None):
        path = os.path.dirname(os.path.abspath(__file__)).replace('models','static')
        timestamp = time.time()

        base_url = self.env["ir.config_parameter"].sudo().get_param("server.base.url")
        CarbonProjectScheme = self.env['carbon.project.scheme'].sudo()
        docs = CarbonProjectScheme.browse(docids)
        scheme = docs[0]
        project = docs[0].project_id
        A_Area = float(project.area)
        

        data = json.loads(scheme.data)
        def get_constructs(data):
            constructs = []

            
            LayerData = data.get('LayerData')
            _logger.info(LayerData)
            for l in LayerData:
                composition_value = l.get('composition_value')
                layer_name = l.get('layer').split('&')[1]
                k = layer_name
                v = []
                for c in composition_value:
                    _id = c.get('id')
                    value = c.get('value')
                    composition = self.env['structural.layer.composition'].sudo().browse(_id)
                
                    if composition.type == 'fill':
                        unit = composition.unit
                        v.append(f'{composition.name}({value}{unit})')
                    if composition.type == 'radio':
                        display_value = value
                        try:
                            inventory = self.env['material.life.cycle.inventory'].sudo().browse(int(value))
                            if inventory.exists():
                                display_value = inventory.name
                        except Exception:
                            pass
                        v.append(f'{composition.name}({display_value})')

                    if composition.type == 'checkbox':
                        if value and isinstance(value, list) and any(isinstance(i, dict) and 'quality_proportion' in i for i in value):
                            parts = []
                            for i in value:
                                category = i.get('category')
                                quality_proportion = i.get('quality_proportion')
                                n = self.env['material.life.cycle.inventory'].browse(category).name
                                parts.append(f'{n} {quality_proportion}%')
                            v.append(f"Aggregate({', '.join(parts)})")
                        elif len(value):
                            category = value[0].get('category')
                            number = value[0].get('number')
                            unit = value[0].get('unit')
                            n = self.env['material.life.cycle.inventory'].browse(category).name
                            v.append(f'{n}({number}{unit})')
                 
                constructs.append(f"{k}:  {', '.join(v)}")
            _logger.info(constructs)
            return constructs


        scheme_data = {
            'name': scheme.name or '',
            'life': data.get('A-Year'),
            'res_all': '%.5f'% float(scheme.res_all),
            'constructs': get_constructs(data),
            # 'constructs': [],
        }

        A_Year = float(scheme_data.get('life'))

        
        images = []
        _logger.info('xxxxxxxxxxxxxxxxxxxxx')
        _logger.info([float(r.res_all) * 10000 for r in scheme.result_ids])
        has_f = False  # Whether negative values exist.
        if has_f:
            save_path_image = '/src/images/' + f'rough_two_pie_scheme_{scheme.id}_{timestamp}.png'
            create_two_pie(np.array([float(r.res_all) * 10000 for r in scheme.result_ids if float(r.res_all)>0]),np.array([]),np.array([r.stage_id.name for r in scheme.result_ids if float(r.res_all)>0]),[0 for r in scheme.result_ids if float(r.res_all)>0],'Figure 1. Share of carbon emissions by unit process', save_path_image)
            images.append(f'{base_url}/carbon/static{save_path_image}')
        else:
            result_ids = scheme.result_ids.filtered(lambda x: float(x.res_all) >= 0)
            save_path_image = '/src/images/' + f'rough_pie_scheme_{scheme.id}_{timestamp}.png'
            create_pie(np.array([float(r.res_all) * 10000 for r in result_ids]),np.array([r.stage_id.name for r in result_ids]),[0 for r in result_ids],'Figure 1. Share of carbon emissions by unit process', save_path_image)
            images.append(f'{base_url}/carbon/static{save_path_image}')

        save_path_image = '/src/images/' + f'rough_bar_year_scheme_{scheme.id}_{timestamp}.png'
        create_bar(np.array([r.stage_id.name for r in scheme.result_ids]), np.array([float(r.res_year) for r in scheme.result_ids]), 'Figure 2. Average annual carbon emission intensity', save_path_image)
        images.append(f'{base_url}/carbon/static{save_path_image}')

        save_path_image = '/src/images/' + f'rough_bar_area_scheme_{scheme.id}_{timestamp}.png'
        create_bar(np.array([r.stage_id.name for r in scheme.result_ids]), np.array([float(r.res_area) for r in scheme.result_ids]), 'Figure 3. Carbon emission intensity per unit area', save_path_image)
        images.append(f'{base_url}/carbon/static{save_path_image}')
        
        save_path_image = '/src/images/' + f'rough_bar_area_year_scheme_{scheme.id}_{timestamp}.png'
        create_bar(np.array([r.stage_id.name for r in scheme.result_ids]), np.array([float(r.res_area_year) for r in scheme.result_ids]), 'Figure 4. Average annual carbon emission intensity per unit area', save_path_image)
        images.append(f'{base_url}/carbon/static{save_path_image}')

        _logger.info(images)
        result_data = []
        category_name_dic = {
            'A1':'Raw material production (A1)',
            'A2':'Raw material transport (A2)',
            'A3':'Mixture mixing (A3)',
            'B1':'Construction transport (B1)',
            'B2':'Paving (B2)',
            'B3':'Compaction (B3)',
            'Other':'Other',
            'Milling and overlay':'Milling and overlay',
            'Micro-surfacing':'Micro-surfacing',
            'D1':'Pavement demolition (D1)',
            'D2':'Reclaimed material transport (D2)',
        }
        for r in scheme.result_ids:
            category_data = []
            for i in json.loads(r.category_result):
                res_all = float(i.get('res_all'))
                res_area = float(i.get('res_all')) * 1000 / A_Area
                res_year = float(i.get('res_all')) / A_Year
                res_area_year = float(i.get('res_all')) * 1000 / (A_Area * A_Year)
                category_data.append({
                    'category': category_name_dic.get(i.get('category')),
                    'res_all': '%.5f'% float(res_all),
                    'res_area': '%.5f'% float(res_area),
                    'res_year': '%.5f'% float(res_year),
                    'res_area_year': '%.5f'% float(res_area_year),
                })
            result_data.append({
                'name':r.stage_id.name,
                'res_all':'%.5f'% float(r.res_all),
                'res_area':'%.5f'% float(r.res_area),
                'res_year':'%.5f'% float(r.res_year),
                'res_area_year':'%.5f'% float(r.res_area_year),
                'category_data': category_data,
            })
        host = request.httprequest.host
        return {
            'doc_ids': docids,
            'doc_model': 'carbon.project',
            'docs': docs,
            'project': project,
            'current_time': (datetime.now()+timedelta(hours=8)).strftime('%Y-%m-%d'),
            'scheme_data': scheme_data,
            'life': json.loads(scheme.data).get('A-Year'),
            'result_data': result_data,
            'images': images,
        }

class ProjectReportRoughCompare(models.AbstractModel):
    _name = 'report.carbon.project_report_rough_compare'

    @api.model
    def _get_report_values(self, docids, data=None):
        path = os.path.dirname(os.path.abspath(__file__)).replace('models','static')
        timestamp = time.time()

        base_url = self.env["ir.config_parameter"].sudo().get_param("server.base.url")
        CarbonProjectScheme = self.env['carbon.project.scheme'].sudo()
        docs = CarbonProjectScheme.browse(docids)
        scheme = docs[0]
        project = docs[0].project_id
        A_Area = float(project.area)
        schemes_data = []

        def get_constructs(data):
            constructs = []

            
            LayerData = data.get('LayerData')
            for l in LayerData:
                composition_value = l.get('composition_value')
                layer_name = l.get('layer').split('&')[1]
                k = layer_name
                v = []
                for c in composition_value:
                    _id = c.get('id')
                    value = c.get('value')
                    composition = self.env['structural.layer.composition'].sudo().browse(_id)
                    if composition.type == 'fill':
                        unit = composition.unit
                        v.append(f'{composition.name}({value}{unit})')
                    if composition.type == 'radio':
                        display_value = value
                        try:
                            inventory = self.env['material.life.cycle.inventory'].sudo().browse(int(value))
                            if inventory.exists():
                                display_value = inventory.name
                        except Exception:
                            pass
                        v.append(f'{composition.name}({display_value})')

                    if composition.type == 'checkbox':
                        if value and isinstance(value, list) and any(isinstance(i, dict) and 'quality_proportion' in i for i in value):
                            parts = []
                            for i in value:
                                category = i.get('category')
                                quality_proportion = i.get('quality_proportion')
                                n = self.env['material.life.cycle.inventory'].browse(category).name
                                parts.append(f'{n} {quality_proportion}%')
                            v.append(f"Aggregate({', '.join(parts)})")
                        elif len(value):
                            category = value[0].get('category')
                            number = value[0].get('number')
                            unit = value[0].get('unit')
                            n = self.env['material.life.cycle.inventory'].browse(category).name
                            v.append(f'{n}({number}{unit})')
                
                constructs.append(f"{k}:  {', '.join(v)}")
            _logger.info(constructs)
            return constructs


        table_idx = 2
        category_name_dic = {
            'A1':'Raw material production (A1)',
            'A2':'Raw material transport (A2)',
            'A3':'Mixture mixing (A3)',
            'B1':'Construction transport (B1)',
            'B2':'Paving (B2)',
            'B3':'Compaction (B3)',
            'Other':'Other',
            'Milling and overlay':'Milling and overlay',
            'Micro-surfacing':'Micro-surfacing',
            'D1':'Pavement demolition (D1)',
            'D2':'Reclaimed material transport (D2)',
        }
        for sc in docs:
            A_Year = float(json.loads(sc.data).get('A-Year'))
            result_data = []
            for r in sc.result_ids:
                category_data = []
                for i in json.loads(r.category_result):
                    res_all = float(i.get('res_all'))
                    res_area = float(i.get('res_all')) * 1000 / A_Area
                    res_year = float(i.get('res_all')) / A_Year
                    res_area_year = float(i.get('res_all')) * 1000 / (A_Area * A_Year)
                    category_data.append({
                        'category': category_name_dic.get(i.get('category')),
                        'res_all': '%.5f'% float(res_all),
                        'res_area': '%.5f'% float(res_area),
                        'res_year': '%.5f'% float(res_year),
                        'res_area_year': '%.5f'% float(res_area_year),
                    })
                result_data.append({
                    'name':r.stage_id.name,
                    'table_idx':table_idx,
                    'res_all':'%.5f'% float(r.res_all),
                    'res_area':'%.5f'% float(r.res_area),
                    'res_year':'%.5f'% float(r.res_year),
                    'res_area_year':'%.5f'% float(r.res_area_year),
                    'category_data':category_data,
                })
                table_idx += 1
            schemes_data.append({
                'name': sc.name,
                'life': json.loads(sc.data).get('A-Year'),
                'constructs': get_constructs(json.loads(sc.data)),
                'result_data': result_data,
            })

        images = [] 
        for idx, scheme in enumerate(docs):
            _logger.info(scheme.name)
            has_f = False  # Whether negative values exist.
            if has_f:
                save_path_image = '/src/images/' + f'rough_two_pie_scheme_{scheme.id}_{timestamp}.png'
                create_two_pie(np.array([float(r.res_all) * 10000 for r in scheme.result_ids if float(r.res_all)>0]),np.array([]),np.array([r.stage_id.name for r in scheme.result_ids if float(r.res_all)>0]),[0 for r in scheme.result_ids if float(r.res_all)>0],f'Figure {idx+1}. Share of carbon emissions by unit process (Scheme {idx+1})', save_path_image)
                images.append(f'{base_url}/carbon/static{save_path_image}')
            else:
                result_ids = scheme.result_ids.filtered(lambda x: float(x.res_all) >= 0)
                save_path_image = '/src/images/' + f'rough_pie_scheme_{scheme.id}_{timestamp}.png'
                create_pie(np.array([float(r.res_all) * 10000 for r in result_ids]),np.array([r.stage_id.name for r in result_ids]),[0 for r in result_ids],f'Figure {idx+1}. Share of carbon emissions by unit process (Scheme {idx+1})', save_path_image)
                images.append(f'{base_url}/carbon/static{save_path_image}')


        save_path_image = '/src/images/' + f'rough_compare_bar_all_scheme_{scheme.id}_{timestamp}.png'
        create_bar(np.array([sc.name for sc in docs]), np.array([float(sc.res_all) for sc in docs]), f'Figure {len(docs)+1}. Total carbon emissions', save_path_image)
        images.append(f'{base_url}/carbon/static{save_path_image}')

        save_path_image = '/src/images/' + f'rough_compare_bar_year_scheme_{scheme.id}_{timestamp}.png'
        create_bar(np.array([sc.name for sc in docs]), np.array([float(sc.res_year) for sc in docs]), f'Figure {len(docs)+2}. Average annual carbon emission intensity', save_path_image)
        images.append(f'{base_url}/carbon/static{save_path_image}')

        save_path_image = '/src/images/' + f'rough_compare_bar_area_scheme_{scheme.id}_{timestamp}.png'
        create_bar(np.array([sc.name for sc in docs]), np.array([float(sc.res_area) for sc in docs]), f'Figure {len(docs)+3}. Carbon emission intensity per unit area', save_path_image)
        images.append(f'{base_url}/carbon/static{save_path_image}')

        save_path_image = '/src/images/' + f'rough_compare_bar_area_year_scheme_{scheme.id}_{timestamp}.png'
        create_bar(np.array([sc.name for sc in docs]), np.array([float(sc.res_area_year) for sc in docs]), f'Figure {len(docs)+4}. Average annual carbon emission intensity per unit area', save_path_image)
        images.append(f'{base_url}/carbon/static{save_path_image}')


        _logger.info(images)
        
        result_data = [{
            'name':r.stage_id.name,
            'res_all':'%.5f'% float(r.res_all),
            'res_area':'%.5f'% float(r.res_area),
            'res_year':'%.5f'% float(r.res_year),
            'res_area_year':'%.5f'% float(r.res_area_year),
        } for r in scheme.result_ids]
        host = request.httprequest.host
        return {
            'doc_ids': docids,
            'doc_model': 'carbon.project',
            'docs': docs,
            'schemes_data': schemes_data,
            'project': project,
            'current_time': (datetime.now()+timedelta(hours=8)).strftime('%Y-%m-%d'),
            'life': json.loads(scheme.data).get('A-Year'),
            'result_data': result_data,
            'images': images,
        }



class ProjectReportFine(models.AbstractModel):
    _name = 'report.carbon.project_report_fine'

    @api.model
    def _get_report_values(self, docids, data=None):
        path = os.path.dirname(os.path.abspath(__file__)).replace('models','static')
        timestamp = time.time()

        base_url = self.env["ir.config_parameter"].sudo().get_param("server.base.url")
        CarbonProjectScheme = self.env['carbon.project.scheme'].sudo()
        docs = CarbonProjectScheme.browse(docids)
        scheme = docs[0]
        project = docs[0].project_id
        A_Area = float(project.area)
        A_Year = float(project.life)

        images = []

        has_f = False  # Whether negative values exist.
        result_ids = sorted(scheme.result_ids, key=lambda k: k.stage_id.sequence)
        save_path_image = '/src/images/' + f'rough_pie_scheme_{scheme.id}_{timestamp}.png'
        create_pie(np.array([float(r.res_all) * 10000 for r in result_ids]),np.array([r.stage_id.name for r in result_ids]),[0 for r in result_ids],'Figure 1. Share of carbon emissions by unit process', save_path_image)
        images.append(f'{base_url}/carbon/static{save_path_image}')


        save_path_image = '/src/images/' + f'fine_bar_year_scheme_{scheme.id}_{timestamp}.png'
        create_bar(np.array([r.stage_id.name for r in result_ids]), np.array([float(r.res_year) for r in result_ids]), 'Figure 2. Average annual carbon emission intensity', save_path_image)
        images.append(f'{base_url}/carbon/static{save_path_image}')

        save_path_image = '/src/images/' + f'fine_bar_area_scheme_{scheme.id}_{timestamp}.png'
        create_bar(np.array([r.stage_id.name for r in result_ids]), np.array([float(r.res_area) for r in result_ids]), 'Figure 3. Carbon emission intensity per unit area', save_path_image)
        images.append(f'{base_url}/carbon/static{save_path_image}')
        
        save_path_image = '/src/images/' + f'fine_bar_area_year_scheme_{scheme.id}_{timestamp}.png'
        create_bar(np.array([r.stage_id.name for r in result_ids]), np.array([float(r.res_area_year) for r in result_ids]), 'Figure 4. Average annual carbon emission intensity per unit area', save_path_image)
        images.append(f'{base_url}/carbon/static{save_path_image}')

        _logger.info(images)

        detail = json.loads(scheme.data)
        _logger.info(detail)

        result_data = []
        for r in result_ids:
            category_data = []
            for i in json.loads(r.category_result):
                res_all = i.get('res_all')
                res_area = i.get('res_all') * 1000 / A_Area
                res_year = i.get('res_all') / A_Year
                res_area_year = i.get('res_all') * 1000 / (A_Area * A_Year)
                category_data.append({
                    'category': i.get('category'),
                    'res_all': '%.5f'% float(res_all),
                    'res_area': '%.5f'% float(res_area),
                    'res_year': '%.5f'% float(res_year),
                    'res_area_year': '%.5f'% float(res_area_year),
                })
            result_data.append({
                'name':r.stage_id.name,
                'res_all':'%.5f'% float(r.res_all),
                'res_area':'%.5f'% float(r.res_area),
                'res_year':'%.5f'% float(r.res_year),
                'res_area_year':'%.5f'% float(r.res_area_year),
                'detail_data':detail.get(str(r.stage_id.id)),
                'category_data':category_data
            })

        

        _logger.info(result_data)

        host = request.httprequest.host
        return {
            'doc_ids': docids,
            'doc_model': 'carbon.project',
            'docs': docs,
            'project': project,
            'current_time': (datetime.now()+timedelta(hours=8)).strftime('%Y-%m-%d'),
            'result_data': result_data,
            'images': images,
        }

   
    
class ProjectReportFineCompare(models.AbstractModel):
    _name = 'report.carbon.project_report_fine_compare'

    @api.model
    def _get_report_values(self, docids, data=None):
        path = os.path.dirname(os.path.abspath(__file__)).replace('models','static')
        timestamp = time.time()

        base_url = self.env["ir.config_parameter"].sudo().get_param("server.base.url")
        CarbonProjectScheme = self.env['carbon.project.scheme'].sudo()
        docs = CarbonProjectScheme.browse(docids)
        scheme = docs[0]
        rough_scheme = docs[1]
        project = docs[0].project_id
        A_Area = float(project.area)
        A_Year = float(project.life)

        images = []

        has_f = False  # Whether negative values exist.
 
        result_ids = sorted(scheme.result_ids, key=lambda k: k.stage_id.sequence)
        save_path_image = '/src/images/' + f'rough_pie_scheme_{scheme.id}_{timestamp}.png'
        create_pie(np.array([float(r.res_all) * 10000 for r in result_ids]),np.array([r.stage_id.name for r in result_ids]),[0 for r in result_ids],'Figure 1. Share of carbon emissions by unit process', save_path_image)
        images.append(f'{base_url}/carbon/static{save_path_image}')


        save_path_image = '/src/images/' + f'fine_bar_year_scheme_{scheme.id}_{timestamp}.png'
        create_bar(np.array([r.stage_id.name for r in result_ids]), np.array([float(r.res_year) for r in result_ids]), 'Figure 2. Average annual carbon emission intensity', save_path_image)
        images.append(f'{base_url}/carbon/static{save_path_image}')

        save_path_image = '/src/images/' + f'fine_bar_area_scheme_{scheme.id}_{timestamp}.png'
        create_bar(np.array([r.stage_id.name for r in result_ids]), np.array([float(r.res_area) for r in result_ids]), 'Figure 3. Carbon emission intensity per unit area', save_path_image)
        images.append(f'{base_url}/carbon/static{save_path_image}')
        
        save_path_image = '/src/images/' + f'fine_bar_area_year_scheme_{scheme.id}_{timestamp}.png'
        create_bar(np.array([r.stage_id.name for r in result_ids]), np.array([float(r.res_area_year) for r in result_ids]), 'Figure 4. Average annual carbon emission intensity per unit area', save_path_image)
        images.append(f'{base_url}/carbon/static{save_path_image}')

        _logger.info(images)

        detail = json.loads(scheme.data)
        _logger.info(detail)

        result_data = []
        for r in result_ids:
            category_data = []
            for i in json.loads(r.category_result):
                res_all = i.get('res_all')
                res_area = i.get('res_all') * 1000 / A_Area
                res_year = i.get('res_all') / A_Year
                res_area_year = i.get('res_all') * 1000 / (A_Area * A_Year)
                category_data.append({
                    'category': i.get('category'),
                    'res_all': '%.5f'% float(res_all),
                    'res_area': '%.5f'% float(res_area),
                    'res_year': '%.5f'% float(res_year),
                    'res_area_year': '%.5f'% float(res_area_year),
                })
            result_data.append({
                'name':r.stage_id.name,
                'res_all':'%.5f'% float(r.res_all),
                'res_area':'%.5f'% float(r.res_area),
                'res_year':'%.5f'% float(r.res_year),
                'res_area_year':'%.5f'% float(r.res_area_year),
                'detail_data':detail.get(str(r.stage_id.id)),
                'category_data':category_data
            })

        
        _logger.info(result_data)

        

        compare_data = []

        for _type in ['res_all','res_area','res_year','res_area_year']:
            _t_dic = {
                'res_all': 'Total carbon emissions',
                'res_area': 'Carbon emission intensity per unit area',
                'res_year': 'Average annual carbon emission intensity',
                'res_area_year': 'Average annual carbon emission intensity per unit area',
            }
            c_data = {
                'type': _t_dic[_type],
                'data': [],
            }
            for stage in project.fine_stage_ids:
                scheme_result = scheme.result_ids.filtered(lambda x:x.stage_id.id == stage.id)
                fine_value = '%.2f' % float(scheme_result[_type])

                rough_scheme_result = rough_scheme.result_ids.filtered(lambda x:x.stage_id.id == stage.id)
                _logger.info(rough_scheme_result)
                value = '%.2f' % float(rough_scheme_result[_type])
                _logger.info(value)
                if float(value) > 0:
                    compare_rate = '+' +  '%.2f'% float((float(fine_value) - float(value)) / float(value) * 100) if float(fine_value) > float(value) else '%.2f'% float((float(fine_value) - float(value)) / float(value) * 100)
                else:
                    compare_rate = '/'
                    
                c_data['data'].append({
                    'stage_name': stage.name,
                    'value': value,
                    'fine_value': fine_value,
                    'compare_rate': compare_rate,
                })
            compare_data.append(c_data)

        _logger.info(compare_data)

        

        host = request.httprequest.host
        return {
            'doc_ids': docids,
            'doc_model': 'carbon.project',
            'docs': docs,
            'project': project,
            'current_time': (datetime.now()+timedelta(hours=8)).strftime('%Y-%m-%d'),
            'result_data': result_data,
            'compare_data': compare_data,
            'images': images,
        }
