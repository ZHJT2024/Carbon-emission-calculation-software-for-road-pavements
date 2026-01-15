# -*- coding: utf-8 -*-
from odoo import fields, api, models


class RoleAccessRoute(models.Model):
    """
    Route permission
    """
    _name = 'role.access.route'
    _description = "Route Permission"

    name = fields.Char('Name', related='route_id.name')
    path = fields.Char('Path', related='route_id.path')
    route_id = fields.Many2one('access.route', 'Route')
    role_id = fields.Many2one('security.role', 'Role')
    buttons = fields.One2many('role.access.route.button', 'role_route_id', 'Buttons')


    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, '%s (%s)' % (record.name, record.path)))
        return res

    @api.model
    def get_roles_access(self,active_role_id):
        if active_role_id:
            roles = self.env['security.role'].search([('id','=',active_role_id)])
        else:
            roles = self.env['security.role'].search([])
        return [role.get_role_access() for role in roles]

    @api.model
    def set_button_access(self,arg):
        button_id = int(arg.get('button_id'))
        route_id = int(arg.get('route_id'))
        state = arg.get('state')
        role_route = self.env['role.access.route'].browse(route_id)
        if button_id in role_route.buttons.mapped('button_id').ids:
            role_route.buttons.filtered(lambda x:x.button_id.id == button_id).unlink()
            return False
        else:
            role_route.buttons = [(0,0,{
                'button_id':button_id,
                'state':state,
            })]
            return True

    @api.model
    def set_button_access_state(self,arg):
        button_id = int(arg.get('button_id'))
        route_id = int(arg.get('route_id'))
        state = arg.get('state')
        role_route = self.env['role.access.route'].browse(route_id)
        if button_id in role_route.buttons.mapped('button_id').ids:
            role_route.buttons.filtered(lambda x:x.button_id.id == button_id).update({
                'state':state,
            })
            return False
        return 'success'

    @api.model
    def get_selected_route(self,arg):
        role_id = int(arg.get('role_id'))
        routes = self.env['access.route'].search([('is_active','=',True)]) - self.env['role.access.route'].search([('role_id', '=', role_id)]).mapped('route_id')
        return [{
            'id':route.id,
            'display_name':route.display_name or '',
        } for route in routes]

    @api.model
    def add_route_to_role(self,arg):
        route_ids = list(map(lambda x:int(x),arg.get('route_ids')))
        role_id = int(arg.get('role_id'))
        role_routes = self.env['role.access.route'].search([('role_id','=',role_id)])
        for r_id in route_ids:
            if r_id not in role_routes.mapped('route_id').ids:
                role_route = self.env['role.access.route'].create({
                    'role_id':role_id,
                    'route_id':r_id,
                })
                buttons = self.env['access.route.button'].search([('route_id', '=', r_id)])
                role_route.buttons = [(0,0,{
                                            'button_id':b.id,
                                            'state':'active',
                                        }) for b in buttons]

    @api.model
    def delete_route_from_role(self, arg):
        route_id = int(arg.get('route_id'))
        self.env['role.access.route'].browse(route_id).unlink()

