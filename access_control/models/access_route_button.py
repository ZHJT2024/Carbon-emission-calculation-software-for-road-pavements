# -*- coding: utf-8 -*-
from odoo import fields, api, models

class AccessRouteButton(models.Model):
    """
    Button
    """
    _name = 'access.route.button'
    _description = "Button"

    domId = fields.Char('Button DOM ID')
    is_active = fields.Boolean('Active',default=True)
    name = fields.Char('Button Label')
    route_id = fields.Many2one('access.route', 'Parent Route',ondelete='cascade')















