# -*- coding: utf-8 -*-
from odoo import fields, api, models
from odoo.exceptions import UserError, ValidationError


class ResUsers(models.Model):
    _inherit = 'res.users'

    parent_id = fields.Many2one('res.users', 'Primary account')
    child_ids = fields.One2many('res.users','parent_id', 'Sub-accounts')


    def bind_user_default_data(self):
        user_id = self.id
        user_name = self.name
        import os
        path = os.path.dirname(os.path.abspath(__file__)).replace('models', 'data')
        import xlrd
        bok = xlrd.open_workbook(path + '/default_inventory_data.xlsx')
        sheets = bok.sheets()

        LifeCycleInventory = self.env['life.cycle.inventory'].sudo()
        MaterialLifeCycleInventory = self.env['material.life.cycle.inventory'].sudo()

        inventory_id = LifeCycleInventory.create({
            'user_id': user_id,
            'name': f'{user_name}-Life Cycle Inventory (Default)',
            'remark': 'System default configuration',
            'is_active': True,
        }).id
        for i,sheet in enumerate(sheets):
            if i == 0:
                for j in range(0,sheet.nrows):
                    if j>0:
                        row = sheet.row_values(j)
                        stage_id = int(row[1])
                        link_id = int(row[3])
                        type_id = int(row[5])
                        composition_id = int(row[7]) if row[7] else False
                        name = row[8]
                        carbon_factor = row[9]
                        unit_id = row[11]
                        MaterialLifeCycleInventory.create({
                            'inventory_id': inventory_id,
                            'stage_id': stage_id,
                            'link_id': link_id,
                            'type_id': type_id,
                            'composition_id': composition_id,
                            'name': name,
                            'carbon_factor': carbon_factor,
                            'unit_id': unit_id,
                        })
