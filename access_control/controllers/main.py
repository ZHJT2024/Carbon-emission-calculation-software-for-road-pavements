# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class AccessControlApi(http.Controller):
    @http.route('/api/get_user_navigations', type='http', auth='user', methods=['GET'], csrf=False)
    def get_user_navigations(self, *args, **kwargs):
        try:
            user = request.env.user
            user_roles = user.security_role_ids
            data = {}
            for role in user_roles:
                data[role.id] = role.get_role_navigation_access_by_web()
            res = {
                "jsonrpc": 2.0,
                "id": None,
                "result": {
                    "code": 0,
                    "message": "ok",
                    "data": data
                }
            }
        except Exception as e:
            res = {
                "jsonrpc": 2.0,
                "id": None,
                "result": {
                    "code": 1,
                    "message": str(e),
                    "data": []
                }
            }
        return json.dumps(res)
    @http.route('/api/get_user_routes', type='http', auth='user', methods=['GET'], csrf=False)
    def get_user_routes(self, *args, **kwargs):
        user = request.env.user
        user_roles = user.security_role_ids
        data = {}
        for role in user_roles:
            data[role.id] = role.get_role_access_by_web()
        
        res = {
            "jsonrpc": 2.0,
            "id": None,
            "result": {
                "code": 0,
                "message": "ok",
                "data":data
            }
        }
        return json.dumps(res)

    @http.route('/api/routes', type='json',auth='user', methods=['POST'],csrf=False)
    def routes(self, *args, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            data = data.get('routes')
            request.env['access.route'].search([]).unlink()
            request.env['role.access.route'].search([]).unlink()

            def get_buttons(route):
                try:
                    if route.get('meta').get('buttons'):
                        return [(0,0,b) for b in route.get('meta').get('buttons')]
                except:
                    return []

            def depth_traversal(_route, route,ps):
                is_exist = ps.get('is_exist')
                exist_id = ps.get('exist_id')
                n = 1 if is_exist else 0
                if route.get('children'):
                    _route['children'] = []
                    for r in route.get('children'):
                        ps_r = {
                            'is_exist': False,
                            'exist_id': 0
                        }
                        _r = {
                            'path': r.get('path'),
                            'name': r.get('name'),
                            'buttons': get_buttons(r)
                        }
                        depth_traversal(_r, r,ps_r)
                        _route['children'].append((n, exist_id, _r))

            res = []
            for route in data:
                ps = {
                    'is_exist':False,
                    'exist_id':0
                }
                _route = {
                    'path': route.get('path'),
                    'name': route.get('name'),
                    'buttons':get_buttons(route)
                }
                depth_traversal(_route, route,ps)
                res.append(_route)

            for vals in res:
                request.env['access.route'].create(vals)

            res = {
                "code": 0,
                "message": 'ok',
                "data": [],
            }

        except Exception as e:
            res = {
                "code": 1,
                "message": str(e),
                "data": []
            }
        return res
