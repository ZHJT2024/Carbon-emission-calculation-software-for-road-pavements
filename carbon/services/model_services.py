from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component
from odoo.http import request
from odoo import http
import datetime
import time
import calendar
import logging
import os
import json
_logger = logging.getLogger(__name__)

def get_one_page_data(page, page_size , data):
    """

    :param self: 
    :param page_size: Page size
    :param page: Page number
    :return: Data for the given page
    """
    totalPages = int(len(data) / page_size) if len(data) % page_size == 0 else int(len(data) / page_size) + 1
    if page == totalPages:
        res = data[(page - 1) * page_size:]
    else:
        res = data[(page - 1) * page_size:page * page_size]
    return res,totalPages


def res_success(parent, data):
    """
    REST API success response.
    """
    res = parent(partial=True, data=data)
    res.code = 0
    res.message = 'success'
    return res


class CarbonProjectServices(Component):
    _inherit = 'base.rest.service'
    _name = 'carbon.project'
    _usage = 'carbon_project'
    _collection = 'carbon.project.services'
    _description = ""

    @restapi.method(
    [
        (['/users/info'], 'GET'),
        (['/users/info'], 'PUT')
    ],
    input_param=restapi.Datamodel("carbon.project.users.info.param"),
    output_param=restapi.Datamodel("carbon.project.users.info.response"),auth='user')
    def users_info(self, param):
        """
        Get the current user's profile (GET).
        Update the current user's profile (PUT).
        """
        user = request.env.user
        method = request.httprequest.method
        ResUsers = self.env['res.users'].sudo()
            
        if method == 'GET':

            res = {
                'success': True,
                'data': {
                    'id': user.id,
                    'is_master': False if user.parent_id else True,
                    'name': user.name,
                    'phone': user.phone or '',
                    'email': user.email or '',
                }
            }

        if method == 'PUT':
            vals = param.vals
            _logger.info(vals)
            other_user = ResUsers.search([('phone','=',vals.get('phone')),('name','!=',vals.get('name'))])
            if other_user:
                res = {
                    'success': False,
                    'message': 'This phone number is already associated with another user.'
                }
            else:
                user.name = vals.get('name')
                user.phone = vals.get('phone')
                user.email = vals.get('email')
                res = {
                    'success': True,
                    'message': 'Updated successfully.'
                }

        Parent = self.env.datamodels["carbon.project.users.info.response"]

        return res_success(Parent, res)
    
    @restapi.method(
    [
        (['/users/roles'], 'GET')
    ],
    output_param=restapi.Datamodel("carbon.project.users.roles.response"),auth='user')
    def users_roles(self):
        """
        Get all roles of the current user.
        """
        user = request.env.user

        res = [{
            'role_id': role.id,
            'role_name': role.name,
        } for role in user.security_role_ids]
        Parent = self.env.datamodels["carbon.project.users.roles.response"]

        return res_success(Parent, res)

    @restapi.method(
    [
        (['/roles'], 'GET')
    ],
    output_param=restapi.Datamodel("carbon.project.users.roles.response"),auth='public')
    def roles(self):
        """
        Get the list of available roles.
        """
        Parent = self.env.datamodels["carbon.project.users.roles.response"]

        return res_success(Parent, res)

    @restapi.method(
    [
        (['/users/projects'], 'GET'),
        (['/users/projects'], 'POST'),
        (['/users/projects'], 'PUT'),
        (['/users/projects'], 'DELETE')
    ],
    input_param=restapi.Datamodel("carbon.project.users.projects.param"),
    output_param=restapi.Datamodel("carbon.project.users.projects.response"),auth='user')
    def users_projects(self, param):
        """
        Get projects for the current user (GET).
        Create a project for the current user (POST).
        Update a project for the current user (PUT).
        Delete a project for the current user (DELETE).
        """
        user = request.env.user
        method = request.httprequest.method
        
        CarbonStage = self.env['carbon.stage'].sudo()

        if method == 'GET':

            user_ids = [user.id]
            user_ids.extend(user.child_ids.ids)
            keyword = param.keyword
            curPage = param.curPage or 0
            pageSize = param.pageSize or 0
            totalPages = 0
            if keyword:
                projects = self.env['carbon.project'].search([('user_id','in',user_ids),('name','ilike',keyword)])
            else:
                projects = self.env['carbon.project'].search([('user_id','in',user_ids)])
            res_projects = projects
            if curPage and pageSize:
                res_projects, totalPages = get_one_page_data(curPage, pageSize, projects)
            res = {
                'success': True,
                'curPage': curPage,
                'pageSize': pageSize,
                'total': len(projects),
                'data':[{
                    'sequence': (curPage-1)*pageSize + idx + 1,
                    'id': project.id,
                    'name': project.name,
                    'location': project.city_id.name,
                    'city_id': [project.city_id.state_id.id, project.city_id.id],
                    'checked_stages': [s.name for s in project.stage_ids],
                    'fine_checked_stages': [s.name for s in project.fine_stage_ids],
                    'is_completed': project.is_completed,
                    'calc_stage': project.calc_stage,
                    'mode': project.mode,
                    'life': project.life,
                    'area': project.area,
                    'type': project.type,
                    'has_rough_scheme': len(project.scheme_ids.filtered(lambda x:x.mode == 'rough'))>0,
                    'has_fine_scheme': len(project.scheme_ids.filtered(lambda x:x.mode == 'fine')),
                    'fine_report_id': str(project.scheme_ids.filtered(lambda x:x.mode == 'fine').id) if project.scheme_ids.filtered(lambda x:x.mode == 'fine').id else '0',
                    'can_fine_report': project.scheme_ids.filtered(lambda x:x.mode == 'fine').is_completed,
                    'can_compare_report': len(project.scheme_ids.filtered(lambda x:x.mode == 'rough')) > 1 and all([sc.is_completed for sc in project.scheme_ids.filtered(lambda x:x.mode == 'rough')]) ,
                    'schemes': [{
                        'sequence': f'{idx+1}-{idx2+1}',
                        'id': sc.id,
                        'name': sc.name,
                        'is_completed': sc.is_completed,
                        'res_all': '%.5f'% float(sc.res_all),
                        'res_area': '%.5f'% float(sc.res_area),
                        'res_year': '%.5f'% float(sc.res_year),
                        'res_area_year': '%.5f'% float(sc.res_area_year),
                        'select': sc.select,
                    } for idx2, sc in enumerate(project.scheme_ids.filtered(lambda x:x.mode == 'rough'))]
                } for idx, project in enumerate(res_projects)]
            }
        if method == 'POST':
            vals = param.vals
            stages = vals.pop('stages')
            stage_ids = [CarbonStage.search([('name', '=', i)],limit=1).id for i in stages]
            vals['stage_ids'] = [(6, 0, stage_ids)]
            vals['fine_stage_ids'] = [(6, 0, stage_ids)]
            vals['user_id'] = user.id
            _logger.info(vals)
            try:
                project = self.env['carbon.project'].create(vals)
                res = {
                    'success': True,
                    'data': [{
                        'sequence': 1,
                        'id': project.id,
                        'name': project.name,
                        'location': project.city_id.name,
                        'city_id': [project.city_id.state_id.id, project.city_id.id],
                        'checked_stages': [s.name for s in project.stage_ids],
                        'fine_checked_stages': [s.name for s in project.fine_stage_ids],
                        'is_completed': project.is_completed,
                        'mode': project.mode,
                        'life': project.life,
                        'area': project.area,
                        'type': project.type
                    }]
                }
            except:
                res = {
                    'success': False
                }

        if method == 'PUT':
            # try:
                vals = param.vals
                project = self.env['carbon.project'].search([('id','=',vals.get('id'))])
                _logger.info(vals)
              
                if 'change' in vals.keys():
                    change = vals.pop('change')
                    if 'fine_stages' in vals.keys():
                        fine_stages = vals.pop('fine_stages')
                        if change.get('isfineCheckedStages'):
                            stage_ids = [CarbonStage.search([('name', '=', i)],limit=1).id for i in fine_stages]
                            _logger.info(stage_ids)
                            if stage_ids:
                                vals['fine_stage_ids'] = [(6, 0, stage_ids)]
                            _logger.info(vals)
                            # Delete accounting results.
                            project.scheme_ids.filtered(lambda x:x.mode == 'fine').mapped('result_ids').unlink()
                    if 'rough_stages' in vals.keys():
                        rough_stages = vals.pop('rough_stages')
                        if change.get('ischeckedStages'):
                            stage_ids = [CarbonStage.search([('name', '=', i)],limit=1).id for i in rough_stages]
                            _logger.info(stage_ids)
                            if stage_ids:
                                vals['stage_ids'] = [(6, 0, stage_ids)]
                            _logger.info(vals)
                            # Delete estimation results.
                            project.scheme_ids.filtered(lambda x:x.mode == 'rough').mapped('result_ids').unlink()
                    if change.get('isChangeLife'):
                        # Delete accounting results.
                        project.scheme_ids.filtered(lambda x:x.mode == 'fine').mapped('result_ids').unlink()
                    if change.get('isChangeArea'):
                        # Delete accounting results and estimation results.
                        project.scheme_ids.mapped('result_ids').unlink()

               
                if 'schemeData' in vals.keys():
                    schemeData = vals.pop('schemeData')
                    _logger.info(schemeData)
                    if schemeData:
                        _logger.info('wwwwwwwww')
                        sc_id = schemeData.get('id')
                        if sc_id:
                            sc = self.env['carbon.project.scheme'].search([('id','=',sc_id)])
                            sc.data = json.dumps(schemeData.get('data'), ensure_ascii=False)
                            sc.name = schemeData.get('name')
                            sc.mode = schemeData.get('mode')
                        else:
                            sc = self.env['carbon.project.scheme'].create({
                                'project_id': project.id,
                                'data': json.dumps(schemeData.get('data'), ensure_ascii=False),
                                'name': schemeData.get('name'),
                                'mode': schemeData.get('mode')
                            })
                
                if 'fineSchemeData' in vals.keys():
                    fineSchemeData = vals.pop('fineSchemeData')
                    if fineSchemeData:
                        sc = self.env['carbon.project.scheme'].search([('project_id','=',project.id),('mode','=','fine')],limit=1)
                        if sc:
                            sc.data = fineSchemeData
                        else:
                            sc = self.env['carbon.project.scheme'].create({
                                'project_id': project.id,
                                'data': fineSchemeData,
                                'mode': 'fine'
                            })

                project.write(vals)
                res = {
                    'success': True,
                    'data': [{
                        'sequence': 1,
                        'id': project.id,
                        'name': project.name,
                        'location': project.city_id.name,
                        'city_id': [project.city_id.state_id.id, project.city_id.id],
                        'checked_stages': [s.name for s in project.stage_ids],
                        'fine_checked_stages': [s.name for s in project.fine_stage_ids],
                        'is_completed': project.is_completed,
                        'mode': project.mode,
                        'life': project.life,
                        'area': project.area,
                        'type': project.type
                    }]
                }
            # except:
            #     res = {
            #         'success': False
            #     }

        if method == 'DELETE':
            try:
                vals = param.vals
                project = self.env['carbon.project'].search([('id','=',vals.get('id'))])
                project.unlink()
                res = {
                    'success': True
                }
            except:
                res = {
                    'success': False
                }


        Parent = self.env.datamodels["carbon.project.users.projects.response"]

        return res_success(Parent, res)

    @restapi.method(
    [
        (['/users/projects/<int:project_id>/schemes'], 'PUT'),
        (['/users/projects/<int:project_id>/schemes'], 'DELETE')
    ],
    input_param=restapi.Datamodel("carbon.project.users.projects.id.schemes.param"),
    output_param=restapi.Datamodel("carbon.project.users.projects.id.schemes.response"),auth='user')
    def users_projects_id_schemes(self, project_id, param):
        """
        Update a project scheme for the current user (PUT).
        Delete a project scheme for the current user (DELETE).
        """
        _logger.info(param)
        method = request.httprequest.method

        CarbonProject = self.env['carbon.project']
        CarbonProjectScheme = self.env['carbon.project.scheme']
        project = CarbonProject.browse(project_id)
        if method == 'PUT':
            scheme = CarbonProjectScheme.browse(param.id)
            schemes = project.scheme_ids.filtered(lambda x:x.mode == 'rough')
            if param.select:
                scheme.select = True
                (schemes - scheme).select = False
            res = {
                'success': True
            }
        if method == 'DELETE':
            scheme = CarbonProjectScheme.browse(param.id)
            scheme.unlink()
            res = {
                'success': True
            }

        Parent = self.env.datamodels["carbon.project.users.projects.id.schemes.response"]
        return res_success(Parent, res)

    
    @restapi.method(
    [
        (['/users/projects/<int:id>/result'], 'GET'),
        (['/users/projects/<int:id>/result'], 'POST')
    ],
    input_param=restapi.Datamodel("carbon.project.users.projects.id.result.param"),
    output_param=restapi.Datamodel("carbon.project.users.projects.id.result.response"),auth='user')
    def users_projects_id_result(self, id, param):
        """
        Get project computation results for the current user (GET).
        Run project computation for the current user (POST).
        """
        user = request.env.user
        method = request.httprequest.method

        

        CarbonStage = self.env['carbon.stage']
        CarbonProject = self.env['carbon.project']
        CarbonProjectScheme = self.env['carbon.project.scheme']
        CarbonProjectResult = self.env['carbon.project.result']

        def deal_float(res):
            if 0< abs(float(res)) <= 0.00001:
                return '0'
            if 0.00001< abs(float(res)) <= 999:
                return '%.5f'% float(res)
            if 999< abs(float(res)) <= 9999:
                return '%.4f'% float(res)
            if 9999< abs(float(res)) <= 99999:
                return '%.2f'% float(res)
            return '%.0f'% float(res)

        if method == 'GET':
            scheme = CarbonProjectScheme.browse(id)
            project = scheme.project_id
            scheme_result_ids = scheme.result_ids.sorted(lambda x:x.stage_id.sequence)

            stage_result = {}
            stage_category = {}
            for r in scheme_result_ids:
                stage_category[r.stage_id.name] = json.loads(r.category_result) if r.category_result else []
                stage_result[r.stage_id.id] = {
                    'res_all': {
                        'label': 'GHG emissions',
                        'unit': 'tCO2e',
                        'value': deal_float(r.res_all),
                    },
                    'res_area': {
                        'label': 'Emission intensity per unit area',
                        'unit': 'kgCO2e/m^2',
                        'value': deal_float(r.res_area),
                    },
                    'res_year': {
                        'label': 'Average annual emission intensity',
                        'unit': 'tCO2e/a',
                        'value': deal_float(r.res_year),
                    },
                    'res_area_year': {
                        'label': 'Average annual emission intensity per unit area',
                        'unit': 'kgCO2e/(a*m^2)',
                        'value': deal_float(r.res_area_year),
                    }
                }

            res = {
                'success': True,
                'project_info': {
                    'name': project.name,
                    'life': project.life if scheme.mode == 'fine' else json.loads(scheme.data).get('A-Year'),
                    'location': project.city_id.name,
                    'area': project.area,
                    'mode': project.mode,
                    'scheme_mode': scheme.mode,
                },
                'res_all': {
                    'value': deal_float(scheme.res_all),
                    'label': 'GHG emissions',
                    'unit': 'tCO2e',
                    'stage_result': [{
                        'stage_id': r.stage_id.id,
                        'stage_name': r.stage_id.name,
                        'label': r.stage_id.name,
                        'unit': 'tCO2e',
                        'value': deal_float(r.res_all),
                    } for r in scheme_result_ids],
                },
                'res_area': {
                    'value':  deal_float(scheme.res_area),
                    'label': 'Emission intensity per unit area',
                    'unit': 'kgCO2e/m^2',
                    'stage_result': [{
                        'stage_id': r.stage_id.id,
                        'stage_name': r.stage_id.name,
                        'label': r.stage_id.name,
                        'unit': 'kgCO2e/m^2',
                        'value': deal_float(r.res_area),
                    } for r in scheme_result_ids],
                },
                'res_year': {
                    'value': deal_float(scheme.res_year),
                    'label': 'Average annual emission intensity',
                    'unit': 'tCO2e/a',
                    'stage_result': [{
                        'stage_id': r.stage_id.id,
                        'stage_name': r.stage_id.name,
                        'label': r.stage_id.name,
                        'unit': 'tCO2e/a',
                        'value': deal_float(r.res_year),
                    } for r in scheme_result_ids],
                },
                'res_area_year': {
                    'value': deal_float(scheme.res_area_year),
                    'label': 'Average annual emission intensity per unit area',
                    'unit': 'kgCO2e/(a*m^2)',
                    'stage_result': [{
                        'stage_id': r.stage_id.id,
                        'stage_name': r.stage_id.name,
                        'label': r.stage_id.name,
                        'unit': 'kgCO2e/(a*m^2)',
                        'value': deal_float(r.res_area_year),
                    } for r in scheme_result_ids],
                },
                'stage_result':stage_result,
                'stage_category':stage_category
            }
        if method == 'POST':
            project = CarbonProject.browse(id)
            mode = project.mode
            scheme_id = param.scheme_id
            _logger.info(scheme_id)
            scheme = CarbonProjectScheme.browse(scheme_id)
            if scheme.mode == 'fine':
                if scheme.data:
                    data = json.loads(scheme.data)
                    stage_id = param.stage_id
                    if stage_id: # Compute a single stage.
                        CarbonProjectScheme.calc_fine(stage_id, scheme_id, data, project)
                    else:
                        # Compute all stages.
                        for stage_id in project.fine_stage_ids.ids:
                            CarbonProjectScheme.calc_fine(stage_id, scheme_id, data, project)
                  

            if scheme.mode == 'rough':
                scheme.calc_rough()

            res = {
                        'success': True
                    }


        Parent = self.env.datamodels["carbon.project.users.projects.id.result.response"]

        return res_success(Parent, res)


    @restapi.method(
    [
        (['/users/projects/<int:id>'], 'GET')
    ],
    output_param=restapi.Datamodel("carbon.project.users.projects.id.response"),auth='user')
    def users_projects_id(self, id):
        """
        Get project details.
        """
        project = self.env['carbon.project'].search([('id','=',id)])
        res = {
            'project_info':{
                'id': project.id,
                'name': project.name,
                'life': project.life or '',
                'city_id': [project.city_id.state_id.id, project.city_id.id],
                'has_rough_scheme': len(project.scheme_ids.filtered(lambda x:x.mode == 'rough'))>0,
                'location': project.city_id.name,
                'area': project.area
            },
            'inventory_id':project.inventory_id.id,
            'inventory_data':{
                'name': project.inventory_id.name or '',
                'A': [{
                    'id': link.id,
                    'name': link.name,
                    'types': [{
                        'id': ty.id,
                        'name': ty.name,
                        'inventories': [{
                        'id': inv.id,
                        'name': inv.name,
                        'type_id': inv.type_id.id,
                        'link_id': inv.link_id.id,
                        'unit':inv.unit_id.name.split('/')[1],
                        'carbon_factor': inv.carbon_factor,
                        'carbon_unit': inv.unit_id.name,
                    } for inv in self.env['material.life.cycle.inventory'].search([('type_id','=',ty.id),('inventory_id.is_active','=',True),('inventory_id.user_id.id','=',self.env.user.id)])],
                    } for ty in self.env['life.cycle.inventory.type'].search([('link_id','=',link.id)])],
                    'inventories': [{
                        'id': inv.id,
                        'name': inv.name,
                        'type_id': inv.type_id.id,
                        'link_id': inv.link_id.id,
                        'unit':inv.unit_id.name.split('/')[1],
                        'carbon_factor': inv.carbon_factor,
                        'carbon_unit': inv.unit_id.name,
                    } for inv in self.env['material.life.cycle.inventory'].search([('link_id','=',link.id),('inventory_id.is_active','=',True),('inventory_id.user_id.id','=',self.env.user.id)])]
                } for link in self.env['carbon.link'].search([('stage_id.code','=','A')])],
                'B': [{
                    'id': link.id,
                    'name': link.name,
                    'types': [{
                        'id': ty.id,
                        'name': ty.name,
                        'inventories': [{
                        'id': inv.id,
                        'name': inv.name,
                        'type_id': inv.type_id.id,
                        'link_id': inv.link_id.id,
                        'unit':inv.unit_id.name.split('/')[1],
                        'carbon_factor': inv.carbon_factor,
                        'carbon_unit': inv.unit_id.name,
                    } for inv in self.env['material.life.cycle.inventory'].search([('type_id','=',ty.id),('inventory_id.is_active','=',True),('inventory_id.user_id.id','=',self.env.user.id)])],
                    } for ty in self.env['life.cycle.inventory.type'].search([('link_id','=',link.id)])],
                    'inventories': [{
                        'id': inv.id,
                        'name': inv.name,
                        'type_id': inv.type_id.id,
                        'link_id': inv.link_id.id,
                        'unit':inv.unit_id.name.split('/')[1],
                        'carbon_factor': inv.carbon_factor,
                        'carbon_unit': inv.unit_id.name,
                    } for inv in self.env['material.life.cycle.inventory'].search([('link_id','=',link.id),('inventory_id.is_active','=',True),('inventory_id.user_id.id','=',self.env.user.id)])]
                } for link in self.env['carbon.link'].search([('stage_id.code','=','B')])],
                'C': [{
                    'id': link.id,
                    'name': link.name,
                    'types': [{
                        'id': ty.id,
                        'name': ty.name,
                        'inventories': [{
                        'id': inv.id,
                        'name': inv.name,
                        'type_id': inv.type_id.id,
                        'link_id': inv.link_id.id,
                        'unit':inv.unit_id.name.split('/')[1],
                        'carbon_factor': inv.carbon_factor,
                        'carbon_unit': inv.unit_id.name,
                    } for inv in self.env['material.life.cycle.inventory'].search([('type_id','=',ty.id),('inventory_id.is_active','=',True),('inventory_id.user_id.id','=',self.env.user.id)])],
                    } for ty in self.env['life.cycle.inventory.type'].search([('link_id','=',link.id)])],
                    'inventories': [{
                        'id': inv.id,
                        'name': inv.name,
                        'type_id': inv.type_id.id,
                        'link_id': inv.link_id.id,
                        'unit':inv.unit_id.name.split('/')[1],
                        'carbon_factor': inv.carbon_factor,
                        'carbon_unit': inv.unit_id.name,
                    } for inv in self.env['material.life.cycle.inventory'].search([('link_id','=',link.id),('inventory_id.is_active','=',True),('inventory_id.user_id.id','=',self.env.user.id)])]
                } for link in self.env['carbon.link'].search([('stage_id.code','=','C')])],
                'D': [{
                    'id': link.id,
                    'name': link.name,
                    'types': [{
                        'id': ty.id,
                        'name': ty.name,
                        'inventories': [{
                        'id': inv.id,
                        'name': inv.name,
                        'type_id': inv.type_id.id,
                        'link_id': inv.link_id.id,
                        'unit':inv.unit_id.name.split('/')[1],
                        'carbon_factor': inv.carbon_factor,
                        'carbon_unit': inv.unit_id.name,
                    } for inv in self.env['material.life.cycle.inventory'].search([('type_id','=',ty.id),('inventory_id.is_active','=',True),('inventory_id.user_id.id','=',self.env.user.id)])],
                    } for ty in self.env['life.cycle.inventory.type'].search([('link_id','=',link.id)])],
                    'inventories': [{
                        'id': inv.id,
                        'name': inv.name,
                        'type_id': inv.type_id.id,
                        'link_id': inv.link_id.id,
                        'unit':inv.unit_id.name.split('/')[1],
                        'carbon_factor': inv.carbon_factor,
                        'carbon_unit': inv.unit_id.name,
                    } for inv in self.env['material.life.cycle.inventory'].search([('link_id','=',link.id),('inventory_id.is_active','=',True),('inventory_id.user_id.id','=',self.env.user.id)])]
                } for link in self.env['carbon.link'].search([('stage_id.code','=','D')])],
            },
            'data':json.loads(project.data) if project.data else None,
            'schemes':[{
                'id': sc.id,
                'name': sc.name,
                'mode': sc.mode,
                'data': json.loads(sc.data) if sc.data else None,
            } for sc in project.scheme_ids],
            'stages':[{
                'id': s.id,
                'name': s.name,
                'code': s.code,
            } for s in sorted(project.stage_ids, key=lambda x:x.sequence)],
            'fine_stages':[{
                'id': s.id,
                'name': s.name,
                'code': s.code,
            } for s in sorted(project.fine_stage_ids, key=lambda x:x.sequence)]
        }

        Parent = self.env.datamodels["carbon.project.users.projects.id.response"]

        return res_success(Parent, res)


    @restapi.method(
    [
        (['/users/inventories'], 'GET'),
        (['/users/inventories'], 'POST'),
        (['/users/inventories'], 'PUT'),
        (['/users/inventories'], 'DELETE')
    ],
    input_param=restapi.Datamodel("carbon.project.users.inventories.param"),
    output_param=restapi.Datamodel("carbon.project.users.inventories.response"),auth='user')
    def users_inventories(self, param):
        """
        Get all inventories for the current user (GET).
        Create an inventory for the current user (POST).
        Update an inventory for the current user (PUT).
        Delete an inventory for the current user (DELETE).
        """
        user = request.env.user
        method = request.httprequest.method

        if method == 'GET':
            keyword = param.keyword
            curPage = param.curPage or 0
            pageSize = param.pageSize or 0
            totalPages = 0
            if keyword:
                inventories = self.env['life.cycle.inventory'].search([('user_id','=',user.parent_id.id or user.id),('name','ilike',keyword)])
            else:
                inventories = self.env['life.cycle.inventory'].search([('user_id','=',user.parent_id.id or user.id)])
            res_inventories = inventories
            if curPage and pageSize:
                res_inventories, totalPages = get_one_page_data(curPage, pageSize, inventories)
            res = {
                'success': True,
                'curPage': curPage,
                'pageSize': pageSize,
                'total': len(inventories),
                'data':[{
                    'sequence': idx + 1,
                    'inventory_id': inventory.id,
                    'inventory_name': inventory.name,
                    'remark': inventory.remark or '',
                    'is_active': inventory.is_active,
                } for idx, inventory in enumerate(res_inventories)]
            }

        if method == 'POST':
            inventory_name = param.inventory_name
            remark = param.remark

            try:
                inventory_objs = self.env['life.cycle.inventory'].search([('user_id', '=', user.parent_id.id or user.id),('name','=',inventory_name)])
                if len(inventory_objs):
                    res = {
                        'success': False,
                        'message': 'This inventory name already exists. Please choose another name.'
                    }
                else:
                    inventory = self.env['life.cycle.inventory'].create({
                        'user_id': user.parent_id.id or user.id,
                        'name': inventory_name,
                        'remark': remark
                    })
                    res = {
                        'success': True
                    }
            except:
                res = {
                    'success': False
                }
        if method == 'PUT':
            inventory_id = param.inventory_id
            inventory_name = param.inventory_name
            remark = param.remark
            is_active = param.is_active
            _logger.info(remark)

            try:
                inventory_objs = self.env['life.cycle.inventory'].search([('user_id', '=', user.parent_id.id or user.id),('name','=',inventory_name)])
                if len(inventory_objs):
                    res = {
                        'success': False,
                        'message': 'This inventory name already exists. Please choose another name.'
                    }
                else:
                    inventory = self.env['life.cycle.inventory'].search([('id','=',inventory_id)])
                    if inventory_name:
                        inventory.name = inventory_name
                    if remark:
                        inventory.remark = remark
                    if is_active:
                        inventory.is_active = True
                        inventories = self.env['life.cycle.inventory'].search([('user_id','=',user.parent_id.id or user.id)])
                    
                        (inventories - inventory).is_active = False
                    res = {
                        'success': True
                    }
            except:
                res = {
                    'success': False
                }
        if method == 'DELETE':
            del_all = param.del_all
            inventory_id = param.inventory_id

            try:
                if del_all:
                    inventory = self.env['life.cycle.inventory'].search([('user_id','=',user.parent_id.id or user.id)])
                else:
                    inventory = self.env['life.cycle.inventory'].search([('id','=',inventory_id)])
                inventory.unlink()
                res = {
                    'success': True
                }
            except:
                res = {
                    'success': False
                }


        Parent = self.env.datamodels["carbon.project.users.inventories.response"]

        return res_success(Parent, res)



    @restapi.method(
    [
        (['/users/inventories/details'], 'GET'),
        (['/users/inventories/details'], 'POST'),
        (['/users/inventories/details'], 'PUT'),
        (['/users/inventories/details'], 'DELETE')
    ],
    input_param=restapi.Datamodel("carbon.project.users.inventories.details.param"),
    output_param=restapi.Datamodel("carbon.project.users.inventories.details.response"),auth='user')
    def users_inventories_details(self, param):
        """
        Get inventory details for the current user (GET).
        Create an inventory detail record for the current user (POST).
        Update an inventory detail record for the current user (PUT).
        Delete inventory detail records for the current user (DELETE).
        """
        method = request.httprequest.method
        user = request.env.user

        parent_id = param.parent_id
        vals = param.vals
        stage_id = param.stage_id
        
        model = 'material.life.cycle.inventory'
        if method == 'GET':
            stage = self.env['carbon.stage'].browse(stage_id)
            inventory = self.env['life.cycle.inventory'].search([('user_id','=',user.parent_id.id or user.id),('id','=',parent_id)])
           
            inventories = self.env[model].search([('inventory_id','=',parent_id), ('stage_id','=',stage_id)])
            details = []
            for idx, i in enumerate(inventories):
                _d = {
                        'sequence': idx + 1,
                        'id': i.id,
                        'name': i.name,
                        'category': i.type_id.name,
                        'category_id': i.type_id.id,
                        'carbon_factor': i.carbon_factor,
                        'carbon_unit': i.unit_id.name,
                        'unit_id': i.unit_id.id,
                        'link': i.link_id.name,
                        'link_id': i.link_id.id,
                }
                if stage.code == 'A':
                    _d['composition_id'] = i.composition_id.id or ''
                details.append(_d)
            res = {
                'success': True,
                'data':{
                    'inventory_id': inventory.id,
                    'inventory_name': inventory.name,
                    'details': details
                }
            }
        if method == 'POST':
            try:
                vals['inventory_id'] = parent_id
                inventory = self.env[model].create(vals)
                res = {
                    'success': True
                }
            except:
                res = {
                    'success': False
                }
        
        if method == 'PUT':
            try:
                inventory = self.env[model].search([('id','=',vals.get('id'))])
                
                inventory.write(vals)
                res = {
                    'success': True
                }
            except:
                res = {
                    'success': False
                }

        if method == 'DELETE':
            del_all = param.del_all
            try:
                if del_all:
                    inventory = self.env[model].search([('inventory_id','=',parent_id)])
                else:
                    inventory = self.env[model].search([('id','in',vals.get('ids'))])
                inventory.unlink()
                res = {
                    'success': True
                }
            except:
                res = {
                    'success': False
                }


        Parent = self.env.datamodels["carbon.project.users.inventories.details.response"]

        return res_success(Parent, res)




    @restapi.method(
    [
        (['/units'], 'GET')
    ],
    input_param=restapi.Datamodel("carbon.project.units.param"),
    output_param=restapi.Datamodel("carbon.project.units.response"),auth='public')
    def units(self, param):
        """
        Get units.
        """
        type = param.type
        inv_id = param.inv_id

        LifeCycleInventoryType = self.env['life.cycle.inventory.type'].sudo()

        types = LifeCycleInventoryType.search([('category','=',type)])
        res = [{
            'name':ty.name,
            'id':ty.id,
            'units': [{
                'id':unit.id,
                'name':unit.name,
            } for unit in ty.unit_ids]
        } for ty in types]
            
        Parent = self.env.datamodels["carbon.project.units.response"]
        return res_success(Parent, res)


    @restapi.method(
    [
        (['/stages'], 'GET')
    ],
    output_param=restapi.Datamodel("carbon.project.stages.response"),auth='public')
    def stages(self):
        """
        Get stages.
        """

        CarbonStage = self.env['carbon.stage'].sudo()

        stages = CarbonStage.search([], order="sequence")
        res = [{
            'id':stage.id,
            'name':stage.name,
            'code':stage.code,
        } for stage in stages]
            
        Parent = self.env.datamodels["carbon.project.stages.response"]
        return res_success(Parent, res)
    
    @restapi.method(
    [
        (['/stages/<int:id>/links'], 'GET')
    ],
    output_param=restapi.Datamodel("carbon.project.stages.id.links.response"),auth='public')
    def stages_id_links(self, id):
        """
        Get process steps.
        """

        CarbonLink = self.env['carbon.link'].sudo()
        LifeCycleInventoryType = self.env['life.cycle.inventory.type'].sudo()

        links = CarbonLink.search([('stage_id','=',id)], order="sequence")
 
        res = [{
            'id':l.id,
            'name':l.name,
            'code':l.code or '',
            'units':[{
            'name':ty.name,
            'id':ty.id,
            'units': [{
                'id':unit.id,
                'name':unit.name,
            } for unit in ty.unit_ids]
        } for ty in LifeCycleInventoryType.search([('link_id','=',l.id)])],
        } for l in links]
            
        Parent = self.env.datamodels["carbon.project.stages.id.links.response"]
        return res_success(Parent, res)


    @restapi.method(
    [
        (['/stages/<int:id>/inventories'], 'GET')
    ],
    output_param=restapi.Datamodel("carbon.project.stages.id.inventories.response"),auth='user')
    def stages_id_inventories(self, id):
        """
        Get the selectable inventories for a stage.
        """
        user = request.env.user

        CarbonStage = self.env['carbon.stage'].sudo()
        LifeCycleInventory = self.env['life.cycle.inventory'].sudo()
        MaterialLifeCycleInventory = self.env['material.life.cycle.inventory'].sudo()
        MechanicalLifeCycleInventory = self.env['mechanical.life.cycle.inventory'].sudo()
        MaintenanceLifeCycleInventory = self.env['maintenance.life.cycle.inventory'].sudo()

        stage = CarbonStage.browse(id)

        active_inventory = LifeCycleInventory.search([('user_id','=',user.parent_id.id or user.id),('is_active','=',True)],limit=1)
        domain = [('inventory_id','=',active_inventory.id)]
        if stage.name == 'Raw Materials':
            inventories = MaterialLifeCycleInventory.search(domain)
        elif stage.name == 'Maintenance':
            inventories = MaintenanceLifeCycleInventory.search(domain)
        else:
            inventories = MechanicalLifeCycleInventory.search(domain)
        res = [{
            'id':i.id,
            'name':i.name + i.remark if stage.name == 'Maintenance' else i.name,
            'carbon_factor':i.carbon_factor,
            'carbon_unit':i.unit_id.name,
            'unit':i.unit_id.name.split('/')[1],
        } for i in inventories]
            
        Parent = self.env.datamodels["carbon.project.stages.id.inventories.response"]
        return res_success(Parent, res)


    @restapi.method(
    [
        (['/wycolumns'], 'GET')
    ],
    output_param=restapi.Datamodel("carbon.project.wycolumns.response"),auth='user')
    def wycolumns(self):
        """
        Get dynamic column configuration for maintenance.
        """
        MaterialLifeCycleInventory = self.env['material.life.cycle.inventory'].sudo()
        invs = MaterialLifeCycleInventory.search([('stage_id.code','=','C'),('inventory_id.is_active','=',True),('inventory_id.user_id.id','=',self.env.user.id)])
        _logger.info(len(invs))
        _logger.info(invs)
        res = {
            'wycolumns': [{
                'name':'wystyleId',
                'label':'Maintenance method',
                'type':'select',
                'options':[{
                    'value': i.id,
                    'label': i.name,
                } for i in invs],
                'disabled': False,
                'width': '150',
            },{
                'name': 'num',
                'label': 'Number of occurrences',
                'type': 'input',
                'disabled': False,
                'width': '120',
            },{
                'name': 'dxcd',
                'label': 'Number of one-way lanes',
                'type': 'input',
                'disabled': False,
                'width': '120',
            },{
                'name': 'ldcd',
                'label': 'Maintenance section length (m)',
                'type': 'input',
                'disabled': False,
                'width': '120',
            },{
                'name': 'fbts',
                'label': 'Closure days',
                'type': 'input',
                'disabled': False,
                'width': '120',
            },{
                'name': 'rjtlxkc',
                'label': 'Daily passenger-car traffic (vehicles)',
                'type': 'input',
                'disabled': False,
                'width': '120',
            },{
                'name': 'rjtlhc',
                'label': 'Daily truck traffic (vehicles)',
                'type': 'input',
                'disabled': False,
                'width': '120',
            }]
        }
            
        Parent = self.env.datamodels["carbon.project.wycolumns.response"]
        return res_success(Parent, res)
    
    @restapi.method(
    [
        (['/citys'], 'GET')
    ],
    output_param=restapi.Datamodel("carbon.project.citys.response"),auth='public')
    def citys(self):
        """
        Get cities.
        """

        ResCountryState = self.env['res.country.state'].sudo()
        ResCountryStateCity = self.env['res.country.state.city'].sudo()

        states = ResCountryState.search([('country_id.code', '=', 'CN')])
        citys = ResCountryStateCity.search([])
        res = [{
            'value':s.id,
            'label':s.name,
            'children': [{
                'value':c.id,
                'label':c.name,
            } for c in s.city_ids],
        } for s in states]
            
        Parent = self.env.datamodels["carbon.project.citys.response"]
        return res_success(Parent, res)

    @restapi.method(
    [
        (['/compositions'], 'GET')
    ],
    output_param=restapi.Datamodel("carbon.project.compositions.response"),auth='public')
    def compositions(self):
        """
        Get all structural layer components.
        """

        StructuralLayerComposition = self.env['structural.layer.composition'].sudo()

        compositions = StructuralLayerComposition.search([])
        res = [{
            'id':c.id,
            'name':f"{c.name}({', '.join(c.layer_ids.mapped('name'))})",
        } for c in compositions]
            
        Parent = self.env.datamodels["carbon.project.compositions.response"]
        return res_success(Parent, res)

    @restapi.method(
    [
        (['/layers'], 'GET')
    ],
    output_param=restapi.Datamodel("carbon.project.layers.response"),auth='public')
    def layers(self):
        """
        Get structural layers.
        """

        StructuralLayer = self.env['structural.layer'].sudo()

        layers = StructuralLayer.search([('is_active','=',True)])
        res = [{
            'id':layer.id,
            'name':layer.name,
        } for layer in layers]
            
        Parent = self.env.datamodels["carbon.project.layers.response"]
        return res_success(Parent, res)
    
    
    @restapi.method(
    [
        (['/layers/<int:id>/compositions'], 'GET')
    ],
    input_param=restapi.Datamodel("carbon.project.layers.id.compositions.param"),
    output_param=restapi.Datamodel("carbon.project.layers.id.compositions.response"),auth='public')
    def layers_id_compositions(self, id, param):
        """
        Get the component configuration of a structural layer.
        """
        inventory_id = param.inventory_id

        StructuralLayerComposition = self.env['structural.layer.composition'].sudo()
        MaterialLifeCycleInventory = self.env['material.life.cycle.inventory'].sudo()

        compositions = StructuralLayerComposition.search([('layer_ids', 'in', id)])
        res = []
        for composition in compositions:
            _d = {
                'id':composition.id,
                'name':composition.name,
                'type':composition.type,
                'unit':composition.unit or '',
            }
            if composition.type == 'checkbox':
                _d['max_length'] = composition.max_length
                if composition.columns:
                    columns = json.loads(composition.columns)
                    for col in columns:
                        if col.get('type') == 'select':
                            if col.get('name') == 'category':
                                inventories = MaterialLifeCycleInventory.search([('inventory_id','=', inventory_id), ('composition_id','=', composition.id)])
                                col['options'] = [{
                                    'value': i.id,
                                    'label': i.name,
                                } for i in inventories]
                        if col.get('type') == 'input':
                            if 'value_k_name' in col.keys() and 'value_v_list' in col.keys() and 'value_kv_dic' in col.keys():
                                v = {}
                                inventories = MaterialLifeCycleInventory.search([('inventory_id','=', inventory_id), ('composition_id','=', composition.id)])
                                for idx,i in enumerate(inventories):
                                    v[i.id] = {
                                        'kgCO₂e/L': 'L/m²',
                                        'kgCO₂e/m³': 'cm'
                                    }[i.unit_id.name] # Use dynamic mapping.
                                col['value_kv_dic'] = {
                                    'k_name':col['value_k_name'],
                                    'v_name':col['name'],
                                    'kv_dic':v
                                }
                    _d['columns'] = columns
                else:
                    _d['columns'] = []
            if composition.type == 'radio':
                inventories = MaterialLifeCycleInventory.search([('inventory_id','=', inventory_id), ('composition_id','=', composition.id)])
                _d['options'] = [{
                    'value': i.id,
                    'label': i.name,
                } for i in inventories]
                if composition.name == 'Mixture Type':
                    _d['options'] = [{
                        'value': 'AC',
                        'label': 'AC',
                    },{
                        'value': 'SMA',
                        'label': 'SMA',
                    },{
                        'value': 'EA-30',
                        'label': 'EA-30',
                    },{
                        'value': 'EA-40',
                        'label': 'EA-40',
                    },{
                        'value': 'GA',
                        'label': 'GA',
                    }]
                if composition.name == 'Binder Haul Distance':
                    _d['options'] = [{
                        'value': '30',
                        'label': '30km',
                    },{
                        'value': '50',
                        'label': '50km',
                    },{
                        'value': '100',
                        'label': '100km',
                    },{
                        'value': '150',
                        'label': '150km',
                    },{
                        'value': '200',
                        'label': '200km',
                    },{
                        'value': '250',
                        'label': '250km',
                    },{
                        'value': '300',
                        'label': '300km',
                    }]
            res.append(_d)

            
        Parent = self.env.datamodels["carbon.project.layers.id.compositions.response"]
        return res_success(Parent, res)


    @restapi.method(
    [
        (['/geojson'], 'GET')
    ],
    input_param=restapi.Datamodel("carbon.project.geojson.param"),
    output_param=restapi.Datamodel("carbon.project.geojson.response"),auth='public')
    def geojson(self, param):
        """
        Get GeoJSON.
        """
        type = param.type
        adcode = param.adcode
        if type == 'country':
            country = self.env['res.country'].sudo().search([('code','=','CN')],limit=1)
            res = {
                'geojson': country.geo_json
            }
        else:
            country = self.env['res.country.state'].sudo().search([('code','=',adcode)],limit=1)
            res = {
                'geojson': country.geo_json
            }
        Parent = self.env.datamodels["carbon.project.geojson.response"]
        return res_success(Parent, res)

    @restapi.method(
    [
        (['/users/childs'], 'GET'),
        (['/users/childs'], 'POST'),
        (['/users/childs'], 'PUT'),
        (['/users/childs'], 'DELETE')
    ],
    input_param=restapi.Datamodel("carbon.project.users.childs.param"),
    output_param=restapi.Datamodel("carbon.project.users.childs.response"),auth='user')
    def users_childs(self, param):
        """
        Get sub-accounts (GET).
        Create a sub-account (POST).
        Update a sub-account (PUT).
        Delete sub-accounts (DELETE).
        """
        method = request.httprequest.method
        user = request.env.user

        if method == 'GET':
            children = []
            idx = 2
            database_manager_id = 0
            database_manager = user.name
            has_database_manager = False
            for child in user.child_ids:
                role_names = child.security_role_ids.mapped('name')
                if 'Database Administrators' in role_names:
                    database_manager_id = child.id
                    database_manager = child.name
                    has_database_manager = True
                if 'Project Execution Staff' in role_names:
                    children.append({
                            'label': f'Project Execution Staff {idx}',
                            'name': child.name
                    })
                    idx += 1
            children.insert(0, {
                    'label': 'Database Administrators',
                    'name': database_manager
            })
            children.insert(1, {
                    'label': 'Project Execution Staff 1',
                    'name': user.name
            })
            org_data = {
                'label': 'Administrators',
                'children': children
            }

            is_master = False if user.parent_id else True
            master_name = user.name if is_master else user.parent_id.name

            child_users = user.child_ids if is_master else user

            res = {
                'success': True,
                'database_manager_id': database_manager_id,
                'database_manager': database_manager,
                'has_database_manager': has_database_manager,
                'org_data': org_data,
                'is_master': is_master,
                'master_name': master_name,
                'data': [{
                    'id':child.id,
                    'name':child.name,
                    'password':child.password_text or '',
                    'roles': [{
                        'id': r.id,
                        'name': r.name,
                    } for r in child.security_role_ids]
                } for child in child_users]
            }
        if method == 'POST':
            vals = param.vals
            
            username = vals.get('username')
            password = vals.get('password')
            roleList = vals.get('roleList')

            

            ResUsers = self.env['res.users'].sudo()
            IrModelData = self.env['ir.model.data'].sudo()

            new_user = ResUsers.search([('name','=',username)])
            if new_user:
                res = {
                    'success': False,
                    'result': 'Username already exists.'
                }
            else:
                new_user = ResUsers.create({
                    'name':username,
                    'login':username,
                    'password_text':password,
                    'parent_id':user.id,
                })
                security_role_ids = []
                if 'Project Execution Staff' in roleList:
                    security_role_ids.append(IrModelData.xmlid_to_res_id('carbon.role_project_manager'))
                if 'Database Administrators' in roleList:
                    security_role_ids.append(IrModelData.xmlid_to_res_id('carbon.role_database_manager'))
                new_user.write({
                    'password': password,
                    'security_role_ids': security_role_ids
                })
                res = {
                    'success': True,
                    'result': 'Created successfully.'
                }
        if method == 'PUT':
            try:
                ResUsers = self.env['res.users'].sudo()
                IrModelData = self.env['ir.model.data'].sudo()

                vals = param.vals
                
                id = vals.get('id')
                username = vals.get('username')
                password = vals.get('password')
                roleList = vals.get('roleList')

                security_role_ids = []
                if 'Project Execution Staff' in roleList:
                    security_role_ids.append(IrModelData.xmlid_to_res_id('carbon.role_project_manager'))
                if 'Database Administrators' in roleList:
                    security_role_ids.append(IrModelData.xmlid_to_res_id('carbon.role_database_manager'))

                ResUsers.browse(id).write({
                    'name':username,
                    'login':username,
                    'parent_id':user.id,
                    'password':password,
                    'password_text':password,
                    'security_role_ids':security_role_ids,
                })
                res = {
                        'success': True,
                        'result': 'Updated successfully.'
                }
            except:
                res = {
                        'success': False,
                        'result': 'Username already exists.'
                }

        if method == 'DELETE':
            try:
                vals = param.vals
                ids = vals.get('ids')
                ResUsers = self.env['res.users'].sudo()
                ResUsers.browse(ids).unlink()
                res = {
                    'success': True
                }
            except:
                res = {
                    'success': False
                }

        Parent = self.env.datamodels["carbon.project.users.childs.response"]
        return res_success(Parent, res)

    @restapi.method(
    [
        (['/users/projects/ranking'], 'GET')
    ],
    input_param=restapi.Datamodel("carbon.project.users.projects.ranking.param"),
    output_param=restapi.Datamodel("carbon.project.users.projects.ranking.response"),auth='user')
    def users_projects_ranking(self, param):
        """
        Get the carbon-emissions ranking.
        """
        user = request.env.user
        type = param.type
        user_id = param.user_id

        if user_id:
            user = self.env['res.users'].sudo().browse(user_id)


        user_ids = [user.id]
        user_ids.extend(user.child_ids.ids)
        projects = self.env['carbon.project'].search([('user_id','in',user_ids)]).filtered(lambda x: x.is_completed)
        projects.com_res()
        projects = sorted(projects, key=lambda x:float(x[type]), reverse=True)

        if len(projects) >= 5:
            projects = projects[0:5]

        res = {
            'x_data': [p.name for p in projects],
            'y_data': ['%.2f' % float(p[type]) for p in projects],
        }

        Parent = self.env.datamodels["carbon.project.users.projects.ranking.response"]
        return res_success(Parent, res)

    @restapi.method(
    [
        (['/users/projects/overview'], 'GET')
    ],
    input_param=restapi.Datamodel("carbon.project.users.projects.overview.param"),
    output_param=restapi.Datamodel("carbon.project.users.projects.overview.response"),auth='user')
    def users_projects_overview(self, param):
        """
        Get a project overview.
        """
        user = request.env.user

        user_id = param.user_id

        if user_id:
            user = self.env['res.users'].sudo().browse(user_id)


        user_ids = [user.id]
        user_ids.extend(user.child_ids.ids)

        projects = self.env['carbon.project'].search([('user_id','in',user_ids)])
        completed_projects = projects.filtered(lambda x:x.is_completed)

        res = {
            'total': len(projects),
            'completed_number': len(completed_projects),
            'city_projects': [{
                'id':c.id,
                'name':c.name,
                'adcode':c.code,
                'geojson':c.geo_json,
                'projects':[{
                    'id':p.id,
                    'name':p.name,
                    'username':p.user_id.name,
                    'location':p.city_id.name,
                    'life':p.life,
                    'area':p.area,
                    'geojson':p.city_id.geo_json,
                    'active_scheme_id':p.active_scheme_id,
                    'show_detail_btn':False
                } for p in projects.filtered(lambda x:x.city_id.id == c.id)],
            } for c in projects.mapped('city_id')],
            'completed_projects': [{
                'id':p.id,
                'name':p.name,
                'username':p.user_id.name,
                'location':p.city_id.name,
                'life':p.life,
                'area':p.area,
                'geojson':p.city_id.geo_json,
                'active_scheme_id':p.active_scheme_id,
                'show_detail_btn':False
            } for p in completed_projects],
        }

        Parent = self.env.datamodels["carbon.project.users.projects.overview.response"]
        return res_success(Parent, res)
    

    @restapi.method(
    [
        (['/verifycode'], 'POST')
    ],
    input_param=restapi.Datamodel("carbon.project.verifycode.param"),
    output_param=restapi.Datamodel("carbon.project.verifycode.response"),auth='public')
    def verifycode(self, param):
        """
        Verification code endpoint.
        """
        
            
        Parent = self.env.datamodels["carbon.project.verifycode.response"]
        return res_success(Parent, res)
