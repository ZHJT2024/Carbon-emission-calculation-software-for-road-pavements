# -*- coding: utf-8 -*-
from odoo import fields, api, models


class RoleAccessNavigation(models.Model):
    """
    Navigation permission
    """
    _name = 'role.access.navigation'
    _description = "Navigation Permission"

    name = fields.Char('Name', related='navigation_id.name')
    path = fields.Char('Path', related='navigation_id.path')
    navigation_id = fields.Many2one('access.navigation', 'Navigation Item')
    role_id = fields.Many2one('security.role', 'Role')
    available = fields.Boolean('Enabled',default=True)



    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, '%s (%s)' % (record.name, record.path)))
        return res

    @api.model
    def get_roles_navigation_access(self,active_navigation_id):
        if active_navigation_id:
            roles = self.env['security.role'].search([('id','=',active_navigation_id)])
        else:
            roles = self.env['security.role'].search([])
        return [role.get_role_navigation_access() for role in roles]


    @api.model
    def get_selected_navigation(self,arg):
        role_id = int(arg.get('role_id'))
        navigations = self.env['access.navigation'].search([('is_active','=',True)]) - self.env['role.access.navigation'].search([('role_id', '=', role_id)]).mapped('navigation_id')
        return [{
            'id':navigation.id,
            'display_name':navigation.display_name or '',
        } for navigation in navigations]

    @api.model
    def add_navigation_to_role(self,arg):
        navigation_ids = list(map(lambda x:int(x),arg.get('navigation_ids')))
        role_id = int(arg.get('role_id'))
        role_navigations = self.env['role.access.navigation'].search([('role_id','=',role_id)])
        for r_id in navigation_ids:
            if r_id not in role_navigations.mapped('navigation_id').ids:
                role_navigation = self.env['role.access.navigation'].create({
                    'role_id':role_id,
                    'navigation_id':r_id,
                })


    @api.model
    def delete_navigation_from_role(self, arg):
        navigation_id = int(arg.get('navigation_id'))
        self.env['role.access.navigation'].browse(navigation_id).unlink()

