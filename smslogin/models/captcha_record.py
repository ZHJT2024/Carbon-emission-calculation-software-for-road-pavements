# -*- coding: utf-8 -*-
from odoo import fields, api, models
from odoo.exceptions import UserError, ValidationError
import time
class CaptchaRecord(models.Model):
    """
    CAPTCHA record
    """
    _name = 'captcha.record'
    _description = "CAPTCHA Record"
    # _rec_name = 'name'

 
    captcha = fields.Char(string="CAPTCHA Token", required=True)
    token = fields.Char(string="token", required=True)
    ip = fields.Char(string="IP Address")
    generation_time = fields.Char(string="Generated Timestamp", required=True)
    is_expired = fields.Boolean(string="Is Expired", compute='com_is_expired')
    is_used = fields.Boolean(string="Is Used")

    
    def com_is_expired(self):
        for record in self:
            current_time = time.time()
            elapsed_time = current_time - float(record.generation_time)
            if elapsed_time > 60 * 5:
                record.is_expired = True
            else:
                record.is_expired = False


   
    
    
