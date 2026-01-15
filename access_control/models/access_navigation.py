# -*- coding: utf-8 -*-
from odoo import fields, api, models
from odoo.exceptions import ValidationError

class AccessNavigation(models.Model):
    """
    Navigation item
    """
    _name = 'access.navigation'
    _description = "Navigation Item"

    name = fields.Char('Name',required=True)
    path = fields.Char('Path',related='route_id.path')
    route_id = fields.Many2one('access.route', 'Route',required=True)
    is_active = fields.Boolean('Active',default=True)
    sequence = fields.Integer('Sequence')


    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, '%s (%s)' % (record.name, record.path)))
        return res
    
    @api.onchange('sequence')
    def sequence_check(self):
        for record in self:
            if record.sequence:
                res_sequence = self.env['access.navigation'].sudo().search([('sequence', '=', record.sequence)])
                if len(res_sequence) >= 1:
                    raise ValidationError('This sequence already exists. Please choose another value.')















