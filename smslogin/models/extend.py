# -*- coding: utf-8 -*-
from odoo import fields, api, models
from odoo.exceptions import UserError, ValidationError


class ResUsers(models.Model):
    _inherit = 'res.users'

    password_text = fields.Char('Password', help='Plaintext password, for record-keeping only.')


    def bind_user_default_data(self):
        return super(ResUsers, self).bind_user_default_data()

