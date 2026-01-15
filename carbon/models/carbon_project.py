# -*- coding: utf-8 -*-
from odoo import fields, api, models
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class CarbonProject(models.Model):
    """
    Project
    """
    _name = 'carbon.project'
    _description = "Project"
    _rec_name = 'name'

  

    name = fields.Char(string='Project name', required=True)
    city_id = fields.Many2one('res.country.state.city', string='Project location')
    life = fields.Char(string='Service life (years)', required=True)
    area = fields.Char(string='Pavement area', required=True)
    type = fields.Char(string='Pavement type', required=True)
    mode = fields.Selection(
            selection=[
                ('rough', 'Screening-level'),
                ('fine', 'Detailed')
            ],
            default='rough', required=True)
    stage_ids = fields.Many2many('carbon.stage', 'carbon_project_stage', 'project_id', 'stage_id', string="Stages", copy=False)
    fine_stage_ids = fields.Many2many('carbon.stage', 'carbon_project_stage_fine', 'project_id', 'stage_id', string="Assessment stages", copy=False)
    inventory_id = fields.Many2one('life.cycle.inventory', 'Inventory', required=True, ondelete='restrict' )
    user_id = fields.Many2one('res.users', string='Owner', required=True, ondelete='cascade' )
    data = fields.Text(string='Input data')
    is_completed = fields.Boolean(string='Computation completed', compute='com_is_completed')
    calc_stage = fields.Char(string='Computation stage', compute='com_calc_stage')
    res_all = fields.Char(string='Total carbon emissions')
    res_area = fields.Char(string='Carbon emission intensity per unit area')
    res_year = fields.Char(string='Average annual carbon emission intensity')
    res_area_year = fields.Char(string='Average annual carbon emission intensity per unit area')
    result_ids = fields.One2many('carbon.project.result','project_id', 'Results')
    scheme_ids = fields.One2many('carbon.project.scheme','project_id', 'Project schemes')
    active_scheme_id = fields.Integer(compute='com_active_scheme_id')

    def com_active_scheme_id(self):
        for record in self:
            fine_sc = record.scheme_ids.filtered(lambda x:x.mode == 'fine')
            rough_sc = record.scheme_ids.filtered(lambda x:x.mode == 'rough' and x.select)
            if len(fine_sc) and fine_sc.is_completed:
                record.active_scheme_id = fine_sc.id
            elif len(rough_sc) and rough_sc.is_completed:
                record.active_scheme_id = rough_sc.id
            else:
                record.active_scheme_id = 0

    def com_calc_stage(self):
        for record in self:
            if record.mode == 'fine':
                record.calc_stage = '0-1'
            else:
                record.calc_stage = '1-0'
                if len(record.scheme_ids.filtered(lambda x:x.mode == 'fine')):
                    record.calc_stage = '1-1'

    def com_res(self):
        for record in self:
            if record.active_scheme_id:
                scheme = self.env['carbon.project.scheme'].browse(record.active_scheme_id)
                record.res_all = scheme.res_all
                record.res_area = scheme.res_area
                record.res_year = scheme.res_year
                record.res_area_year = scheme.res_area_year
            else:
                record.res_all = 0
                record.res_area = 0
                record.res_year = 0
                record.res_area_year = 0

    @api.depends('scheme_ids')
    def com_is_completed(self):
        for record in self:
            fine_sc = record.scheme_ids.filtered(lambda x:x.mode == 'fine')
            rough_sc = record.scheme_ids.filtered(lambda x:x.mode == 'rough' and x.select)
            if len(fine_sc) and fine_sc.is_completed:
                record.is_completed = True
            elif len(rough_sc) and rough_sc.is_completed:
                record.is_completed = True
            else:
                record.is_completed = False


    def calc_rough(self):
        import json
        import logging
        _logger = logging.getLogger(__name__)

        StructuralLayerComposition = self.env['structural.layer.composition'].sudo()
        MaterialLifeCycleInventory = self.env['material.life.cycle.inventory'].sudo()
        CarbonStage = self.env['carbon.stage'].sudo()
        CarbonProjectResult = self.env['carbon.project.result'].sudo()


        data = json.loads(self.data)
        A_YJ = float(data.get('A-YJ'))

        A_Year = float(self.life)
        A_Area = float(self.area)

        stage_names = self.stage_ids.mapped('name')
        stage_raw_materials = 'Raw materials'
        stage_transport = 'Transport'
        stage_construction = 'Construction'
        stage_demolition = 'Demolition'

        stage_data = {}
        for s in self.stage_ids:
            stage_data[s.name] = []
        

        YCL_LIST = []
        YS_LIST = []
        SG_LIST = []



        A_ZHD_LIST = []

        LayerData = data.get('LayerData')
        for l in LayerData:
            layerid = l.get('layer').split('&')[0]
            layername = l.get('layer').split('&')[1]
            if layername == 'Asphalt concrete surface layer':
                composition_value = l.get('composition_value')
                for c in composition_value:
                    composition_id = c.get('id')
                    composition_value = c.get('value')
                    # Lookup component code.
                    composition_code = StructuralLayerComposition.browse(composition_id).code
                    _logger.info(composition_code)
                    if composition_code == 'P-YSB':
                        P_YSB = float(composition_value)/100
                    if composition_code == 'A-LQMH':
                        A_LQMH = float(composition_value)
                    if composition_code == 'A-LQHD':
                        A_LQHD = float(composition_value)
                        A_ZHD_LIST.append(A_LQHD)
                    if composition_code == 'P-KF':
                        P_KF = float(composition_value)/100

                    if composition_code == 'F-JHL':
                        F_JHL = float(MaterialLifeCycleInventory.browse(composition_value).carbon_factor)
                    if composition_code == 'F-KL':
                        KL = composition_value
                        _logger.info(KL)
                    if composition_code == 'T-HHL':
                        T_HHL = composition_value


                # Raw materials
                if stage_raw_materials in stage_names:
                    s1 = P_YSB/(1+P_YSB) * A_LQHD/100 * A_LQMH * F_JHL / 1000

                    s2 = 1/(1+P_YSB) * A_LQHD/100 * A_LQMH/ 1000

                    KL_LIST = []
                    for kl in KL:
                        F_KL = float(MaterialLifeCycleInventory.browse(kl.get('category')).carbon_factor)
                        P_KL = float(kl.get('quality_proportion'))
                        KL_LIST.append(P_KL/100 * F_KL)

                    s3 = (1 - P_KF) * sum(KL_LIST) + 7.355 * P_KF

                    RES_PERUNIT_YCL_AC = s1 + s2 * s3

                    _logger.info(f'Asphalt concrete surface layer - raw materials: {RES_PERUNIT_YCL_AC}')
                    stage_data[stage_raw_materials].append(RES_PERUNIT_YCL_AC)
                    YCL_LIST.append(RES_PERUNIT_YCL_AC)


                # Transport
                if stage_transport in stage_names:
                    if T_HHL in ['AC','SMA'] or 'EA' in T_HHL:
                        RES_PERUNIT_YS_AC = 214.83 * (6.91 + ( A_YJ - 1 ) * 0.29) * A_LQHD/100000
                    else: #GA
                        RES_PERUNIT_YS_AC = 9 * A_LQHD * A_LQMH / 10000000 * A_YJ

                    _logger.info(f'Asphalt concrete surface layer - transport: {RES_PERUNIT_YS_AC}')
                    stage_data[stage_transport].append(RES_PERUNIT_YS_AC)
                    YS_LIST.append(RES_PERUNIT_YS_AC)


                # Construction
                if stage_construction in stage_names:
                    if T_HHL in ['AC','SMA']:
                        RES_PERUNIT_SG_AC = 0.7216618 * A_LQHD
                    elif 'EA' in T_HHL: 
                        RES_PERUNIT_SG_AC = 0.7482419 * A_LQHD
                    else: #GA
                        RES_PERUNIT_SG_AC = 0.76445 * A_LQHD

                    _logger.info(f'Asphalt concrete surface layer - construction: {RES_PERUNIT_SG_AC}')
                    stage_data[stage_construction].append(RES_PERUNIT_SG_AC)
                    SG_LIST.append(RES_PERUNIT_SG_AC)

            
            if layername == 'Cement concrete surface layer':
                composition_value = l.get('composition_value')
                for c in composition_value:
                    composition_id = c.get('id')
                    composition_value = c.get('value')
                    # Lookup component code.
                    composition_code = StructuralLayerComposition.browse(composition_id).code
                    _logger.info(composition_code)
                    if composition_code == 'F-KL':
                        KL = composition_value
                        _logger.info(KL)
                    if composition_code == 'F-SN':
                        F_SN = float(MaterialLifeCycleInventory.browse(composition_value).carbon_factor)
                    if composition_code == 'P-SN':
                        P_SN = float(composition_value)/100
                    if composition_code == 'A-SNHM':
                        A_SNHM = float(composition_value)
                    if composition_code == 'A-SNHD':
                        A_SNHD = float(composition_value)
                        A_ZHD_LIST.append(A_SNHD)
                # Raw materials
                if stage_raw_materials in stage_names:
                    KL_LIST = []
                    for kl in KL:
                        F_KL = float(MaterialLifeCycleInventory.browse(kl.get('category')).carbon_factor)
                        P_KL = float(kl.get('quality_proportion'))
                        KL_LIST.append(P_KL/100 * F_KL)

                    s1 = P_SN * F_SN + (1 - P_SN) * sum(KL_LIST)

                    RES_PERUNIT_YCL_CC = A_SNHD/100 * A_SNHM * s1 / 1000
                    _logger.info(f'Cement concrete surface layer - raw materials: {RES_PERUNIT_YCL_CC}')
                    stage_data[stage_raw_materials].append(RES_PERUNIT_YCL_CC)
                    YCL_LIST.append(RES_PERUNIT_YCL_CC)

                # Transport
                if stage_transport in stage_names:
                    RES_PERUNIT_YS_CC = 194.93 * (5.41 + (A_YJ - 1) * 0.34) * A_SNHD / 100000
                    _logger.info(f'Cement concrete surface layer - transport: {RES_PERUNIT_YS_CC}')
                    stage_data[stage_transport].append(RES_PERUNIT_YS_CC)
                    YS_LIST.append(RES_PERUNIT_YS_CC)

                # Construction
                if stage_construction in stage_names:
                    RES_PERUNIT_SG_CC = 0.8710122 if A_SNHD <= 20 else (871.01195 + (A_SNHD - 20) * 16.84802)/1000
                    _logger.info(f'Cement concrete surface layer - construction: {RES_PERUNIT_SG_CC}')
                    stage_data[stage_construction].append(RES_PERUNIT_SG_CC)
                    SG_LIST.append(RES_PERUNIT_SG_CC)

            if layername == 'Functional layer':
                composition_value = l.get('composition_value')
                for c in composition_value:
                    composition_id = c.get('id')
                    composition_value = c.get('value')
                    # Lookup component code.
                    composition_code = StructuralLayerComposition.browse(composition_id).code
                    _logger.info(composition_code)
                    if composition_code == 'F-GNC':
                        _logger.info(MaterialLifeCycleInventory.browse(composition_value))
                        if composition_value:
                            F_GNC = float(MaterialLifeCycleInventory.browse(composition_value[0].get('category')).carbon_factor)
                    # if composition_code == 'A-GNC':
                            A_GNC = float(composition_value[0].get('number'))
                            Unit_GNC = composition_value[0].get('unit')
                        else:
                            F_GNC = A_GNC = 0

                # Raw materials
                if stage_raw_materials in stage_names:
                    # RES_PERUNIT_YCL_FL = F_GNC * A_GNC / 100
                    RES_PERUNIT_YCL_FL = F_GNC * A_GNC
                    if Unit_GNC == 'cm':
                        RES_PERUNIT_YCL_FL = F_GNC * A_GNC / 100
                    _logger.info(f'Functional layer - raw materials: {RES_PERUNIT_YCL_FL}')
                    stage_data[stage_raw_materials].append(RES_PERUNIT_YCL_FL)
                    YCL_LIST.append(RES_PERUNIT_YCL_FL)

                # Transport and construction are not calculated for the functional layer.

            if layername == 'Base/Subbase layer':
                composition_value = l.get('composition_value')
                for c in composition_value:
                    composition_id = c.get('id')
                    composition_value = c.get('value')
                    # Lookup component code.
                    composition_code = StructuralLayerComposition.browse(composition_id).code
                    _logger.info(composition_code)
                    if composition_code == 'F-JC':
                        if composition_value:
                            F_JC = float(MaterialLifeCycleInventory.browse(composition_value[0].get('category')).carbon_factor)
                            F_JC_NAME = MaterialLifeCycleInventory.browse(composition_value[0].get('category')).name
                            A_JC = float(composition_value[0].get('number'))
                        else:
                            F_JC_NAME = ''
                            F_JC = A_JC = 0

                # Raw materials
                if stage_raw_materials in stage_names:
                    RES_PERUNIT_YCL_BL = F_JC * A_JC / 100
                    _logger.info(f'Base/Subbase layer - raw materials: {RES_PERUNIT_YCL_BL}')
                    stage_data[stage_raw_materials].append(RES_PERUNIT_YCL_BL)
                    YCL_LIST.append(RES_PERUNIT_YCL_BL)

                # Transport
                if stage_transport in stage_names:
                    RES_PERUNIT_YS_BL = 214.83 * (4.54 + (A_YJ - 1) * 0.23) * A_JC / 100000
                    _logger.info(f'Base/Subbase layer - transport: {RES_PERUNIT_YS_BL}')
                    stage_data[stage_transport].append(RES_PERUNIT_YS_BL)
                    YS_LIST.append(RES_PERUNIT_YS_BL)

                # Construction
                if stage_construction in stage_names:
                    if F_JC_NAME == 'Cement-stabilized soil':
                        RES_PERUNIT_SG_BL = 0.3097497 if A_JC <= 20 else (309.7479 + (A_JC - 20) * 16.31901) / 1000
                    if F_JC_NAME == 'Lime-stabilized soil':
                        RES_PERUNIT_SG_BL = 0.2897850 if A_JC <= 20 else (289.7850 + (A_JC - 20) * 12.67516) / 1000
                    if F_JC_NAME == 'Lime-fly ash gravel':
                        RES_PERUNIT_SG_BL = 0.2930728 if A_JC <= 20 else (293.0728 + (A_JC - 20) * 16.31901) / 1000
                    _logger.info(f'Base/Subbase layer - construction: {RES_PERUNIT_SG_BL}')
                    stage_data[stage_construction].append(RES_PERUNIT_SG_BL)
                    SG_LIST.append(RES_PERUNIT_SG_BL)


        A_ZHD = sum(A_ZHD_LIST)
        # Demolition
        if stage_demolition in stage_names:
            RES_PERUNIT_CC = 0.38398 if A_ZHD <= 5 else (383.98 + (A_ZHD - 5) * 77.98) / 1000
            _logger.info(f'Demolition: {RES_PERUNIT_CC}')
            stage_data[stage_demolition].append(RES_PERUNIT_CC)



        _logger.info(f'Raw materials total: {sum(YCL_LIST)}')
        _logger.info(f'Transport total: {sum(YS_LIST)}')
        _logger.info(f'Construction total: {sum(SG_LIST)}')

        _logger.info(stage_data)
        for k,v in stage_data.items():
            s_id = CarbonStage.search([('name','=',k)], limit=1).id
            _logger.info(s_id)
            _logger.info(v)

            result = CarbonProjectResult.search([('project_id','=',self.id),('stage_id','=',s_id)])
            if not result:
                result = CarbonProjectResult.create({
                    'project_id':self.id,
                    'stage_id':s_id,
                })
            result.res_all = sum(v) * A_Area / 1000
            result.res_area = sum(v)
            result.res_year = sum(v) * A_Area / (A_Year * 1000)
            result.res_area_year = sum(v)/A_Year
                


                









