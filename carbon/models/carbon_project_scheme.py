# -*- coding: utf-8 -*-
from odoo import fields, api, models
from odoo.exceptions import UserError, ValidationError
import os
import logging
_logger = logging.getLogger(__name__)

from ..tests.fun import (
    calc_LQ_A1,
    calc_LQ_A2,
    calc_LQ_A3,
    calc_LQ_B1,
    calc_LQ_B2,
    calc_JC_A1,
    calc_JC_A2,
    calc_JC_B2,
    calc_GNC_A1,
    calc_GNC_A2,
    calc_D1,
    calc_D2,
)
class CarbonProjectScheme(models.Model):
    """
    Project scheme
    """
    _name = 'carbon.project.scheme'
    _description = "Project Scheme"
    _rec_name = 'name'

  

    project_id = fields.Many2one('carbon.project',string='Project', ondelete='cascade')
    select = fields.Boolean(string='Selected')
    name = fields.Char(string='Scheme name')
    mode = fields.Selection(
            selection=[
                ('rough', 'Scheme Comparison'),
                ('fine', 'Carbon Accounting')
            ],
            default='rough', required=True)
    data = fields.Text(string='Submitted data')
    is_completed = fields.Boolean(string='Computation completed', compute='com_is_completed')
    res_all = fields.Char(string='Total GHG emissions', compute='com_res')
    res_area = fields.Char(string='Emission intensity per unit area', compute='com_res')
    res_year = fields.Char(string='Average annual emission intensity', compute='com_res')
    res_area_year = fields.Char(string='Average annual emission intensity per unit area', compute='com_res')
    result_ids = fields.One2many('carbon.project.result','scheme_id', 'Results')


    def del_report_images(self):

        def delete_files_in_folder(folder_path):
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

        path = os.path.dirname(os.path.abspath(__file__)).replace('models','static') + os.sep + 'src' + os.sep + 'images'
        _logger.info(path)

        delete_files_in_folder(path)

    def com_res(self):
        for record in self:
            record.res_all = sum([float(r.res_all) for r in record.result_ids])
            record.res_area = sum([float(r.res_area) for r in record.result_ids])
            record.res_year = sum([float(r.res_year) for r in record.result_ids])
            record.res_area_year = sum([float(r.res_area_year) for r in record.result_ids])


    def com_is_completed(self):
        for record in self:
            _stage_ids = record.project_id.stage_ids if record.mode == 'rough' else record.project_id.fine_stage_ids
            if sorted(_stage_ids.ids, key=lambda x:x) == sorted([r.stage_id.id for r in record.result_ids], key=lambda x:x):
                record.is_completed = True
            else:
                record.is_completed = False


    def calc_rough(self):
        import json
        import logging
        _logger = logging.getLogger(__name__)

        StructuralLayerComposition = self.env['structural.layer.composition'].sudo()
        MaterialLifeCycleInventory = self.env['material.life.cycle.inventory'].sudo()
        CarbonLifeCycleInventory = self.env['carbon.life.cycle.inventory'].sudo()
        CarbonStage = self.env['carbon.stage'].sudo()
        CarbonProjectResult = self.env['carbon.project.result'].sudo()


        data = json.loads(self.data)
        A_Year = float(data.get('A-Year'))
        A_Area = float(self.project_id.area)

        stage_names = self.project_id.stage_ids.mapped('name')

        stage_data = {}
        for s in self.project_id.stage_ids:
            stage_data[s.name] = []
        

        YCL_LIST = []
        YS_LIST = []
        SG_LIST = []



        A_ZHD_LIST = []

        LayerData = data.get('LayerData')
        wyData = data.get('wyData')
        F_RES_PERUNIT_YCL = 0 # Raw-material negative values
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
                        P_YSB = float(composition_value)
                    if composition_code == 'A-LQMH':
                        A_LQMH = float(composition_value)
                    if composition_code == 'A-LQHD':
                        A_LQHD = float(composition_value)
                        A_ZHD_LIST.append(A_LQHD)
                    if composition_code == 'P-KF':
                        P_KF = float(composition_value)

                    if composition_code == 'F-JHL':
                        F_JHL = float(MaterialLifeCycleInventory.browse(composition_value).carbon_factor)
                        JHL_HS = CarbonLifeCycleInventory.search([('material_id','=',composition_value)] ,limit=1)
                        if JHL_HS:
                            F_JHL_HS = float(JHL_HS.carbon_factor)
                    if composition_code == 'A-YJ-JHL':
                        A_YJ_JHL = float(composition_value)
                    if composition_code == 'F-KL':
                        KL = composition_value
                        _logger.info(KL)
                    if composition_code == 'T-HHL':
                        T_HHL = composition_value

                # Compute stage A.
                if 'Raw Materials and Mixtures (A)' in stage_names:
                    KL_LIST = []
                    YS_KL_LIST = []
                    for kl in KL:
                        F_KL = float(MaterialLifeCycleInventory.browse(kl.get('category')).carbon_factor)
                        P_KL = float(kl.get('quality_proportion'))
                        A_YJ_KL = float(kl.get('distance'))
                        KL_LIST.append(P_KL/100 * F_KL)
                        YS_KL_LIST.append((P_KL/100) * (0.1023 * A_YJ_KL + 0.3708))

                    
                    LQ_A1 = calc_LQ_A1(P_YSB, F_JHL, KL_LIST, A_LQMH, A_LQHD, A_Area)
                    LQ_A2 = calc_LQ_A2(P_YSB, YS_KL_LIST, A_YJ_JHL, A_LQMH, A_LQHD, A_Area)
                    LQ_A3 = calc_LQ_A3(A_LQMH, A_LQHD, A_Area)

                    _logger.info(f'LQ_A1:{LQ_A1}')
                    _logger.info(f'LQ_A2:{LQ_A2}')
                    _logger.info(f'LQ_A3:{LQ_A3}')

                    stage_data['Raw Materials and Mixtures (A)'].append({
                        'category': 'LQ_A1',
                        'res_all': LQ_A1,
                    })
                    stage_data['Raw Materials and Mixtures (A)'].append({
                        'category': 'LQ_A2',
                        'res_all': LQ_A2,
                    })
                    stage_data['Raw Materials and Mixtures (A)'].append({
                        'category': 'LQ_A3',
                        'res_all': LQ_A3,
                    })

                # Compute stage B (construction).
                if 'Construction (B)' in stage_names:
                    LQ_B1 = calc_LQ_B1(A_LQMH, A_LQHD, A_Area)
                    LQ_B2 = calc_LQ_B2(A_LQMH, A_LQHD, A_Area)

                    _logger.info(f'LQ_B1:{LQ_B1}')
                    _logger.info(f'LQ_B2:{LQ_B2}')
                    
                    stage_data['Construction (B)'].append({
                        'category': 'LQ_B1',
                        'res_all': LQ_B1,
                    })
                    stage_data['Construction (B)'].append({
                        'category': 'LQ_B2',
                        'res_all': LQ_B2,
                    })
            if layername == 'Base/Subbase':
                composition_value = l.get('composition_value')
                for c in composition_value:
                    composition_id = c.get('id')
                    composition_value = c.get('value')
                    # Lookup component code.
                    composition_code = StructuralLayerComposition.browse(composition_id).code
                    _logger.info('ZW',composition_value)
                    if composition_code == 'F-JC':
                        if composition_value:
                            F_JC = float(MaterialLifeCycleInventory.browse(composition_value[0].get('category')).carbon_factor)
                            F_JC_NAME = MaterialLifeCycleInventory.browse(composition_value[0].get('category')).name
                            JC_HS = CarbonLifeCycleInventory.search([('material_id','=',composition_value[0].get('category'))] ,limit=1)
                            if JC_HS:
                                F_JC_HS = float(JCC_HS.carbon_factor)
                                F_JC_NAME_HS = JC_HS.name
                            A_JC = float(composition_value[0].get('number'))
                            A_YJ_JC = float(composition_value[0].get('distance'))
                        else:
                            F_JC_NAME = ''
                            F_JC = A_JC = A_YJ_JC = 0
                    _logger.info('F_JC_NAME',F_JC_NAME)
                
                 # Compute stage A.
                if 'Raw Materials and Mixtures (A)' in stage_names:
                    JC_A1 = calc_JC_A1(F_JC, A_JC, A_Area)
                    JC_A2 = calc_JC_A2(A_YJ_JC, A_JC, A_Area)

                    _logger.info(f'JC_A1:{JC_A1}')
                    _logger.info(f'JC_A2:{JC_A2}')

                    stage_data['Raw Materials and Mixtures (A)'].append({
                        'category': 'JC_A1',
                        'res_all': JC_A1,
                    })
                    stage_data['Raw Materials and Mixtures (A)'].append({
                        'category': 'JC_A2',
                        'res_all': JC_A2,
                    })

                # Compute stage B (construction).
                if 'Construction (B)' in stage_names:
                    JC_B2 = calc_JC_B2(F_JC_NAME, A_JC, A_Area)

                    
                    _logger.info(f'JC_B2:{JC_B2}')
                    
                    stage_data['Construction (B)'].append({
                        'category': 'JC_B2',
                        'res_all': JC_B2,
                    })
            
          
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
                            GNC_HS = CarbonLifeCycleInventory.search([('material_id','=',composition_value[0].get('category'))] ,limit=1)
                            if GNC_HS:
                                F_GNC_HS = float(GNC_HS.carbon_factor)
                                F_GNC_NAME_HS = GNC_HS.name
                            F_GNC_NAME = MaterialLifeCycleInventory.browse(composition_value[0].get('category')).name
                            A_GNC = float(composition_value[0].get('number'))
                            A_YJ_GNC = float(composition_value[0].get('distance'))
                            Unit_GNC = composition_value[0].get('unit')
                        else:
                            F_GNC = A_GNC = A_YJ_GNC = 0


                  # Compute stage A.
                if 'Raw Materials and Mixtures (A)' in stage_names:
                    GNC_A1 = calc_GNC_A1(F_GNC, A_GNC, A_Area, Unit_GNC)
                    GNC_A2 = calc_GNC_A2(A_YJ_GNC, A_GNC, A_Area, Unit_GNC)
                 

                    _logger.info(f'GNC_A1:{GNC_A1}')
                    _logger.info(f'GNC_A2:{GNC_A2}')

                    stage_data['Raw Materials and Mixtures (A)'].append({
                        'category': 'GNC_A1',
                        'res_all': GNC_A1,
                    })
                    stage_data['Raw Materials and Mixtures (A)'].append({
                        'category': 'GNC_A2',
                        'res_all': GNC_A2,
                    })

                # Compute stage B (construction).
                if 'Construction (B)' in stage_names:
                    pass

              
            
        
        # Compute stage C (operation and maintenance).
        if 'Operation and Maintenance (C)' in stage_names:
            SUM_LIST = {}
            JTL_LIST = []
            for w in wyData:
                _logger.info(f'w:{w}')
                inv = MaterialLifeCycleInventory.browse(w.get('wystyleId'))
                F_WY = float(inv.carbon_factor)
                A_WY = float(w.get('num'))
                A_DXCD = float(w.get('dxcd'))
                A_LDCD = float(w.get('ldcd'))
                A_FBTS = float(w.get('fbts'))
                A_RJTL_XKC = float(w.get('rjtlxkc'))
                A_RJTL_HC = float(w.get('rjtlhc'))

                if f'{inv.name}&{inv.id}' not in SUM_LIST.keys():
                    SUM_LIST[f'{inv.name}&{inv.id}'] = [F_WY * A_WY * A_Area / 1000]
                else:
                    SUM_LIST[f'{inv.name}&{inv.id}'].append(F_WY * A_WY * A_Area / 1000)

                A_XZXS_JTL = 0
                if A_RJTL_XKC + A_RJTL_HC >= 72000:
                    A_XZXS_JTL = 1.2
                if 72000 > A_RJTL_XKC + A_RJTL_HC >= 50000:
                    A_XZXS_JTL = 1.1
                if 50000 > A_RJTL_XKC + A_RJTL_HC >= 40000:
                    A_XZXS_JTL = 1
                if 40000 > A_RJTL_XKC + A_RJTL_HC >= 25000:
                    A_XZXS_JTL = 0.8
                if 25000 > A_RJTL_XKC + A_RJTL_HC >= 10000:
                    A_XZXS_JTL = 0.6
                if 10000 > A_RJTL_XKC + A_RJTL_HC:
                    A_XZXS_JTL = 0.35

                A_XZXS_CDS = 0
                if 1 <= A_DXCD < 2:
                    A_XZXS_CDS = 1.4
                if 2 <= A_DXCD < 3:
                    A_XZXS_CDS = 1.1
                if 3 <= A_DXCD < 4:
                    A_XZXS_CDS = 1
                if 4 <= A_DXCD:
                    A_XZXS_CDS = 0.8
            
                JTL_LIST.append((0.0000199027 * A_RJTL_XKC + 0.0000312758 * A_RJTL_HC) * 2 * A_DXCD * A_LDCD * A_FBTS * A_XZXS_JTL * A_XZXS_CDS * A_WY)

            for k ,v in SUM_LIST.items():
                stage_data['Operation and Maintenance (C)'].append({
                    'category': k.split('&')[0],
                    'res_all': sum(v),
                })
            stage_data['Operation and Maintenance (C)'].append({
                'category': 'Traffic delay',
                'res_all': sum(JTL_LIST),
            })

          

        A_ZHD = sum(A_ZHD_LIST)
        if 'Demolition (D)' in stage_names:
            D1 = calc_D1(A_ZHD, A_Area)
            D2 = calc_D2(A_ZHD, A_Area)
            
            stage_data['Demolition (D)'].append({
                'category': 'D1',
                'res_all': D1,
            })

            stage_data['Demolition (D)'].append({
                'category': 'D2',
                'res_all': D2,
            })




        _logger.info(f'stage_data:{stage_data}')
        for k,v in stage_data.items():
            s_id = CarbonStage.search([('name','=',k)], limit=1).id
            _logger.info(s_id)
            _logger.info(v)

            result = CarbonProjectResult.search([('scheme_id','=',self.id),('stage_id','=',s_id)])
            if not result:
                result = CarbonProjectResult.create({
                    'scheme_id':self.id,
                    'stage_id':s_id,
                })
            
            


            sumv= sum([i.get('res_all') for i in v])
            
            result.res_all = sumv
            result.res_area = sumv * 1000 / A_Area
            result.res_year = sumv / A_Year
            result.res_area_year = (sumv * 1000)/(A_Year * A_Area)
            category_dic = {}
            if k == 'Raw Materials and Mixtures (A)':
                category_dic['A1'] = sum([i.get('res_all') for i in v if i.get('category').split('_')[1] == 'A1'])
                category_dic['A2'] = sum([i.get('res_all') for i in v if i.get('category').split('_')[1] == 'A2'])
                category_dic['A3'] = sum([i.get('res_all') for i in v if i.get('category').split('_')[1] == 'A3'])
            
            elif k == 'Construction (B)':
                category_dic['B1'] = sum([i.get('res_all') for i in v if i.get('category').split('_')[1] == 'B1'])
                category_dic['B2'] = sum([i.get('res_all') for i in v if i.get('category').split('_')[1] == 'B2'])


            else:
                for i in v:
                    if i.get('category') not in category_dic.keys():
                        category_dic[i.get('category')] = i.get('res_all')
                    else:
                        category_dic[i.get('category')] += i.get('res_all')
            
            category_result = [{
                'category': k,
                'res_all': '%.5f'% float(v),
            } for k,v in category_dic.items() if v != 0]
            
            result.category_result = json.dumps(category_result, ensure_ascii=False)
            

    def calc_fine(self, stage_id, scheme_id, scheme_data, project):
        import json
        CarbonStage = self.env['carbon.stage']
        CarbonProjectResult = self.env['carbon.project.result']
        result = CarbonProjectResult.search([('scheme_id','=',scheme_id),('stage_id','=',stage_id)])
        if not result:
            result = CarbonProjectResult.create({
                'scheme_id':scheme_id,
                'stage_id':stage_id,
            })

        stage = CarbonStage.browse(stage_id)


    
        sum_list = []
        category_list = {}
        for d in scheme_data.get(str(stage_id)):
            _logger.info(d)
            _logger.info(stage.code)
            factor_number = float(d.get('factor_number'))
            number = float(d.get('number'))
            category = d.get('category')
            s = factor_number*number

            link_id = d.get('link_id')
            if link_id:
                link_rec = self.env['carbon.link'].browse(int(link_id))
                if link_rec.exists() and link_rec.stage_id and link_rec.stage_id.code and link_rec.sequence:
                    derived_category = f"{link_rec.stage_id.code}{link_rec.sequence}"
                    if derived_category in {'A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'D1', 'D2'}:
                        category = derived_category

            if category == 'A2':
                distance = d.get('distance')
                if distance is not None:
                    s = factor_number * number * float(distance)

            if category == 'Demolition':
                category = 'D1'
            if category == 'Waste transport':
                category = 'D2'


            sum_list.append(s)

            
            if category not in category_list.keys():
                category_list[category] = [s]
            else:
                category_list[category].append(s)

            if stage.code == 'C':
                A_DXCD = float(d.get('dxcd'))
                A_LDCD = float(d.get('ldcd'))
                A_FBTS = float(d.get('fbts'))
                A_RJTL_XKC = float(d.get('rjtlxkc'))
                A_RJTL_HC = float(d.get('rjtlhc'))
                
                A_XZXS_JTL = 0
                if A_RJTL_XKC + A_RJTL_HC >= 72000:
                    A_XZXS_JTL = 1.2
                if 72000 > A_RJTL_XKC + A_RJTL_HC >= 50000:
                    A_XZXS_JTL = 1.1
                if 50000 > A_RJTL_XKC + A_RJTL_HC >= 40000:
                    A_XZXS_JTL = 1
                if 40000 > A_RJTL_XKC + A_RJTL_HC >= 25000:
                    A_XZXS_JTL = 0.8
                if 25000 > A_RJTL_XKC + A_RJTL_HC >= 10000:
                    A_XZXS_JTL = 0.6
                if 10000 > A_RJTL_XKC + A_RJTL_HC:
                    A_XZXS_JTL = 0.35

                A_XZXS_CDS = 0
                if 1 <= A_DXCD < 2:
                    A_XZXS_CDS = 1.4
                if 2 <= A_DXCD < 3:
                    A_XZXS_CDS = 1.1
                if 3 <= A_DXCD < 4:
                    A_XZXS_CDS = 1
                if 4 <= A_DXCD:
                    A_XZXS_CDS = 0.8
            
                jtyw = (0.0000199027 * A_RJTL_XKC + 0.0000312758 * A_RJTL_HC) * 2 * A_DXCD * A_LDCD * A_FBTS * A_XZXS_JTL * A_XZXS_CDS * 1000
                sum_list.append(jtyw)
                if 'Traffic delay' not in category_list.keys():
                    category_list['Traffic delay'] = [jtyw]
                else:
                    category_list['Traffic delay'].append(jtyw)
        
        
            

        
                
        A_Year = float(project.life)
        A_Area = float(project.area)


        
    
        res_all = sum(sum_list)/1000
        res_area = sum(sum_list)/A_Area
        res_year = sum(sum_list)/(A_Year * 1000)
        res_area_year = sum(sum_list)/(A_Year * A_Area)

        category_result = []
        for k,v in category_list.items():
            category_result.append({
                'category': k,
                'res_all': sum(v)/1000,
            })
        
        result.res_all = res_all
        result.res_area = res_area
        result.res_year = res_year
        result.res_area_year = res_area_year
        result.category_result = json.dumps(category_result, ensure_ascii=False)           


                









