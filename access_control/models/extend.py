# -*- coding: utf-8 -*-
from odoo import fields, api, models

class SecurityRoleExtend(models.Model):
    """
    Security role extension
    """
    _inherit = 'security.role'
    _description = "Security Role Extension"


    def get_role_navigation_access(self):
        if self:
            role = self
            role_dic = {
                'id': role.id,
                'name': role.name or '',
                'navigations': []
            }
            role_navigations = self.env['role.access.navigation'].search(
                [('role_id', '=', role.id), ('navigation_id.is_active', '=', True)])
            for role_navigation in role_navigations:
                navigation_dic = {
                    'id': role_navigation.id,
                    'display_name': role_navigation.display_name or '',
                    'name': role_navigation.name or '',
                    'path': role_navigation.path or '',
                }
                role_dic['navigations'].append(navigation_dic)
            return role_dic
        else:
            return {}

    def get_role_navigation_access_by_web(self):
        if self:
            role = self
            role_dic = {
                'id': role.id,
                'name': role.name or '',
                'navigations': []
            }
            role_navigations = self.env['role.access.navigation'].search(
                [('role_id', '=', role.id), ('navigation_id.is_active', '=', True)]).sorted(lambda x:x.navigation_id.sequence)
            for role_navigation in role_navigations:
                navigation_dic = {
                    'name': role_navigation.name or '',
                    'path': role_navigation.path or '',
                }
                if not role_navigation.available:
                    navigation_dic['disabled'] = True
                role_dic['navigations'].append(navigation_dic)
            return role_dic
        else:
            return {}


    def get_role_access(self):
        if self:
            role = self
            role_dic = {
                'id': role.id,
                'name': role.name or '',
                'routes': []
            }
            role_routes = self.env['role.access.route'].search([('role_id', '=', role.id),('route_id.is_active', '=', True)])
            for role_route in role_routes:
                route_dic = {
                    'id': role_route.id,
                    'display_name': role_route.display_name or '',
                    'name': role_route.name or '',
                    'path': role_route.path or '',
                    'buttons': []
                }
                buttons = self.env['role.access.route.button'].search([('role_route_id', '=', role_route.id)])
                route_buttons = self.env['access.route.button'].search([('route_id', '=', role_route.route_id.id),('is_active', '=', True)])
                for button in route_buttons:
                    selected = True if button.id in buttons.mapped('button_id').ids else False
                    button_dic = {
                        'id': button.id,
                        'domId': button.domId or '',
                        'name': button.name or '',
                        'selected': selected,
                        'state': buttons.filtered(
                            lambda x: x.button_id.id == button.id).state if selected else 'active',
                    }
                    route_dic['buttons'].append(button_dic)
                role_dic['routes'].append(route_dic)
            return role_dic
        else:return {}


    def get_role_access_by_web(self):
        if self:
            role = self
            role_dic = {
                'id': role.id,
                'name': role.name or '',
                'routes': []
            }
            role_routes = self.env['role.access.route'].search([('role_id', '=', role.id),('route_id.is_active', '=', True)])
            for role_route in role_routes:
                route_dic = {
                    'id': role_route.route_id.id,
                    'pid': role_route.route_id.pid.id if role_route.route_id.pid else None,
                    'name': role_route.route_id.name or '',
                    'path': role_route.route_id.path or '',
                    'buttons': []
                }
                buttons = self.env['role.access.route.button'].search([('role_route_id', '=', role_route.id)])
                route_buttons = self.env['access.route.button'].search([('route_id', '=', role_route.route_id.id),('is_active', '=', True)])
                for button in route_buttons:
                    button_dic = {
                        'domId': button.domId or '',
                        'name': button.name or '',
                        'state': buttons.filtered(lambda x: x.button_id.id == button.id).state,
                    }
                    route_dic['buttons'].append(button_dic)
                role_dic['routes'].append(route_dic)
            return role_dic
        else:return {}

    def configure_routing_permissions(self): 
        return {
            'type': 'ir.actions.client',
            'name': 'Configure Route Permissions',
            'tag': 'operate_access',
            'target': 'new',
            'context': {'active_role_id': self.id},
        }

    def configure_navigation_permissions(self): 
        return {
            'type': 'ir.actions.client',
            'name': 'Configure Navigation Permissions',
            'tag': 'operate_navigation_access',
            'target': 'new',
            'context': {'active_navigation_id': self.id},
        }















