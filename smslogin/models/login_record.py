# -*- coding: utf-8 -*-
from odoo import fields, api, models
from odoo.exceptions import UserError, ValidationError
import time
class LoginRecord(models.Model):
    """
    Login record
    """
    _name = 'login.record'
    _description = "Login Record"
    # _rec_name = 'name'

 
    type = fields.Selection(
    [
        ('password', 'Password Login'),
        ('verifycode', 'Verification Code Login'),
    ], string="Login Method", required=True)
    login_ip = fields.Char('Login IP Address', required=True)
    login_time = fields.Char('Login Time', required=True)
    sid = fields.Char('SessionID', required=True)
    user_id = fields.Many2one('res.users', string='Account', required=True, ondelete='cascade' )

    
  


   
    
    
