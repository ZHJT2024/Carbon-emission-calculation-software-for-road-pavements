# -*- coding: utf-8 -*-
from odoo import fields, api, models
from odoo.exceptions import UserError, ValidationError
import time


class CalculationModel(models.Model):
    """
    Calculation model
    """
    _name = 'calculation.model'
    _description = "Calculation Model"
    # _rec_name = 'name'

  
    name = fields.Text(string="Name")
    params = fields.Text(string="Parameters")
    code = fields.Text(string="Code")


    def start_run(self, name, **params):
        m = self.search([('name','=',name)],limit=1)
        exec(m.code.replace(m.params,params.get(m.params)))
        

   
    
    
