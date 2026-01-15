# -*- coding: utf-8 -*-
from odoo import fields, api, models

class RoleAccessRouteButton(models.Model):
    """
    Button permission
    """
    _name = 'role.access.route.button'
    _description = "Button Permission"

    domId = fields.Char('Button DOM ID',related='button_id.domId')
    name = fields.Char('Button Label',related='button_id.name')
    button_id = fields.Many2one('access.route.button', 'Button')
    state = fields.Selection([('active', 'active'),
                             ('disable', 'disable'),
                             ('invisible', 'invisible')], string='Button State',default='active')
    role_route_id = fields.Many2one('role.access.route', 'Route Permission',ondelete='cascade')















