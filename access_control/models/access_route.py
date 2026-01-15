# -*- coding: utf-8 -*-
from odoo import fields, api, models

class AccessRoute(models.Model):
    """
    Route
    """
    _name = 'access.route'
    _description = "Route"

    name = fields.Char('Name')
    pid = fields.Many2one('access.route','Parent')
    children = fields.One2many('access.route','pid','Children')
    is_active = fields.Boolean('Active',default=True)
    path = fields.Char('Path')
    buttons = fields.One2many('access.route.button','route_id','Buttons')


    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, '%s (%s)' % (record.name, record.path)))
        return res















