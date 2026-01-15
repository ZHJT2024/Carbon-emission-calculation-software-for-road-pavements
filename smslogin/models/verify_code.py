# -*- coding: utf-8 -*-
from odoo import fields, api, models
from odoo.exceptions import UserError, ValidationError
import time
class VerificationCode(models.Model):
    """
    Verification code
    """
    _name = 'verify.code'
    _description = "Verification Code"
    # _rec_name = 'name'

 
    phone = fields.Char(string="Phone Number", required=True)
    code = fields.Char(string="Verification Code", required=True)
    token = fields.Char(string="token", required=True)
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

    def check_verify_code(self, verifycode, phone):
        # Verify the verification code.
        verifycode_record = self.search([('code', '=', verifycode),('phone', '=', phone)],limit=1)
        if verifycode_record:
            if not verifycode_record.is_used and not verifycode_record.is_expired:
                # Verification succeeded.
                verifycode_record.is_used = True
                return 'ok'
            else:
                return 'The verification code has expired or has already been used.'
        else:
            return 'Invalid verification code.'



   
    
    
