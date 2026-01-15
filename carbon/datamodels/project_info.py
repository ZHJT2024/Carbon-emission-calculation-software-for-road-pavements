# from marshmallow import fields

from odoo.addons.datamodel.core import Datamodel
from odoo.addons.datamodel import fields


#===============================================================

class CarbonProjectUsersInfoParam(Datamodel):
    _name = "carbon.project.users.info.param"

    vals = fields.Dict(description='Field values')

class CarbonProjectUsersInfoResponse(Datamodel):
    _name = "carbon.project.users.info.response"

    code = fields.Integer(required=True)
    message = fields.String(required=True, allow_none=False)
    data = fields.NestedModel('carbon.project.users.info.data', many=False)


class CarbonProjectUsersInfoData(Datamodel):
    _name = "carbon.project.users.info.data"

    success = fields.Boolean(required=True, description='Whether the request succeeded')
    message = fields.String()
    data = fields.NestedModel('carbon.project.users.info.data.data', many=False)

class CarbonProjectUsersInfoDataData(Datamodel):
    _name = "carbon.project.users.info.data.data"

    id = fields.Integer(required=True, description='User ID')
    is_master = fields.Boolean(required=True, description='Whether this is the primary account')
    name = fields.String(required=True, description='Username')
    phone = fields.String(required=True, description='Phone number')
    email = fields.String(required=True, description='Email address')

#===============================================================

class CarbonProjectUsersRolesResponse(Datamodel):
    _name = "carbon.project.users.roles.response"

    code = fields.Integer(required=True)
    message = fields.String(required=True, allow_none=False)
    data = fields.NestedModel('carbon.project.users.roles.data', many=True)


class CarbonProjectUsersRolesData(Datamodel):
    _name = "carbon.project.users.roles.data"

    role_id = fields.Integer(required=True, description='Role ID')
    role_name = fields.String(required=True, description='Role name')


#===============================================================

class CarbonProjectUsersProjectsParam(Datamodel):
    _name = "carbon.project.users.projects.param"

    keyword = fields.String(description='Search keyword')
    vals = fields.Dict(description='Parameters')
    curPage = fields.Integer(description='Current page')
    pageSize = fields.Integer(description='Page size')


class CarbonProjectUsersProjectsResponse(Datamodel):
    _name = "carbon.project.users.projects.response"

    code = fields.Integer(required=True)
    message = fields.String(required=True, allow_none=False)
    data = fields.NestedModel('carbon.project.users.projects.data', many=False)


class CarbonProjectUsersProjectsData(Datamodel):
    _name = "carbon.project.users.projects.data"

    success = fields.Boolean(required=True, description='Whether the request succeeded')
    curPage = fields.Integer(description='Current page')
    pageSize = fields.Integer(description='Page size')
    total = fields.Integer(description='Total count')
    data = fields.NestedModel('carbon.project.users.projects.data.data', many=True)

class CarbonProjectUsersProjectsDataData(Datamodel):
    _name = "carbon.project.users.projects.data.data"

    sequence = fields.Integer(required=True, description='Sequence number')
    id = fields.Integer(required=True, description='Project ID')
    city_id = fields.List(fields.Integer, required=True, description='City ID')
    checked_stages = fields.List(fields.String, required=True, description='List of stage names')
    fine_checked_stages = fields.List(fields.String, required=True, description='List of stage names')
    name = fields.String(required=True, description='Project name')
    location = fields.String(description='Project location', required=True)
    is_completed = fields.Boolean(description='Whether computation is completed', required=True)
    calc_stage = fields.String(description='Computation stage')
    mode = fields.String(description='Computation mode', required=True)
    life = fields.String(required=True, description='Service life (years)')
    area = fields.String(required=True, description='Pavement area')
    type = fields.String(required=True, description='Pavement type')
    has_fine_scheme = fields.Boolean(description='Whether an accounting scheme has been created')
    has_rough_scheme = fields.Boolean(description='Whether a preliminary scheme has been created')
    fine_report_id = fields.String(description='Accounting report ID')
    can_fine_report = fields.Boolean(description='View accounting report')
    can_compare_report = fields.Boolean(description='View comparison report')
    schemes = fields.NestedModel('carbon.project.users.projects.schemes.data', many=True)

class CarbonProjectUsersProjectsSchemesData(Datamodel):
    _name = "carbon.project.users.projects.schemes.data"

    sequence = fields.String(required=True, description='Sequence number')
    id = fields.Integer(required=True, description='Scheme ID')
    name = fields.String(required=True, description='Scheme name')
    res_all = fields.String(required=True, description='Total carbon emissions')
    res_area = fields.String(required=True, description='Carbon intensity per unit area')
    res_year = fields.String(required=True, description='Average annual carbon intensity')
    res_area_year = fields.String(required=True, description='Average annual carbon intensity per unit area')
    select = fields.Boolean(required=True, description='Selected')
    is_completed = fields.Boolean(required=True, description='Computation completed')

#===============================================================

class CarbonProjectUsersProjectsIdResultParam(Datamodel):
    _name = "carbon.project.users.projects.id.result.param"

    stage_id = fields.Integer(description='Stage ID')
    scheme_id = fields.Integer(description='Scheme ID')


class CarbonProjectUsersProjectsIdResultResponse(Datamodel):
    _name = "carbon.project.users.projects.id.result.response"

    code = fields.Integer(required=True)
    message = fields.String(required=True, allow_none=False)
    data = fields.NestedModel('carbon.project.users.projects.id.result.data', many=False)


class CarbonProjectUsersProjectsIdResultData(Datamodel):
    _name = "carbon.project.users.projects.id.result.data"

    success = fields.Boolean(required=True, description='Whether the request succeeded')
    project_info = fields.NestedModel('carbon.project.users.projects.id.result.project.info.data', many=False)
    res_all = fields.NestedModel('carbon.project.users.projects.id.result.data.data', many=False)
    res_area = fields.NestedModel('carbon.project.users.projects.id.result.data.data', many=False)
    res_year = fields.NestedModel('carbon.project.users.projects.id.result.data.data', many=False)
    res_area_year = fields.NestedModel('carbon.project.users.projects.id.result.data.data', many=False)
    stage_result = fields.Dict()
    stage_category = fields.Dict()
    

class CarbonProjectUsersProjectsIdResultProjectInfoData(Datamodel):
    _name = "carbon.project.users.projects.id.result.project.info.data"

    name = fields.String(string='Project name', required=True)
    location = fields.String(string='Project location', required=True)
    life = fields.String(string='Service life (years)', required=True)
    area = fields.String(string='Pavement area', required=True)
    mode = fields.String(string='Mode', required=True)
    scheme_mode = fields.String(string='Mode', required=True)

class CarbonProjectUsersProjectsIdResultDataData(Datamodel):
    _name = "carbon.project.users.projects.id.result.data.data"

    label = fields.String()
    unit = fields.String()
    value = fields.String(string='Total')
    z_value = fields.String()
    f_value = fields.String()
    bh_value = fields.String(string='Mixing')
    tp_value = fields.String(string='Paving')
    ny_value = fields.String(string='Compaction')
    stage_result = fields.NestedModel('carbon.project.users.projects.id.result.data.data.data', many=True)

class CarbonProjectUsersProjectsIdResultDataDataData(Datamodel):
    _name = "carbon.project.users.projects.id.result.data.data.data"

    stage_id = fields.Integer(description='Stage ID')
    stage_name = fields.String(description='Stage name')
    label = fields.String()
    unit = fields.String()
    value = fields.String()
    z_value = fields.String()
    f_value = fields.String()


#===============================================================

class CarbonProjectUsersProjectsIdResponse(Datamodel):
    _name = "carbon.project.users.projects.id.response"

    code = fields.Integer(required=True)
    message = fields.String(required=True, allow_none=False)
    data = fields.NestedModel('carbon.project.users.projects.id.data', many=False)

class CarbonProjectUsersProjectsIdData(Datamodel):
    _name = "carbon.project.users.projects.id.data"

    inventory_id = fields.Integer(required=True, description='Inventory ID')
    schemes = fields.List(fields.Dict, required=True, description='Schemes')
    stages = fields.List(fields.Dict, required=True, description='Stages')
    fine_stages = fields.List(fields.Dict, required=True, description='Stages')
    data = fields.Dict(required=True, allow_none=True, description='Submitted data')
    project_info = fields.Dict(required=True, allow_none=True, description='Project information')
    inventory_data = fields.Dict(required=True, allow_none=True, description='Inventory data')


#===============================================================
class CarbonProjectUsersInventoriesParam(Datamodel):
    _name = "carbon.project.users.inventories.param"

    del_all = fields.Boolean(description='Delete all')
    is_active = fields.Boolean(description='Active')
    inventory_id = fields.Integer(description='Inventory ID')
    inventory_name = fields.String(description='Inventory name')
    remark = fields.String(description='Remarks')
    keyword = fields.String(description='Search keyword')
    curPage = fields.Integer(description='Current page')
    pageSize = fields.Integer(description='Page size')

class CarbonProjectUsersInventoriesResponse(Datamodel):
    _name = "carbon.project.users.inventories.response"

    code = fields.Integer(required=True)
    message = fields.String(required=True, allow_none=False)
    data = fields.NestedModel('carbon.project.users.inventories.data', many=False)

class CarbonProjectUsersInventoriesData(Datamodel):
    _name = "carbon.project.users.inventories.data"

    success = fields.Boolean(required=True, description='Whether the request succeeded')
    message = fields.String()
    curPage = fields.Integer(description='Current page')
    pageSize = fields.Integer(description='Page size')
    total = fields.Integer(description='Total count')
    data = fields.NestedModel('carbon.project.users.inventories.data.data', many=True)

class CarbonProjectUsersInventoriesDataData(Datamodel):
    _name = "carbon.project.users.inventories.data.data"

    sequence = fields.Integer(required=True, description='Sequence number')
    is_active = fields.Boolean(required=True, description='Active')
    inventory_id = fields.Integer(required=True, description='Inventory ID')
    inventory_name = fields.String(required=True, description='Inventory name')
    remark = fields.String(required=True, description='Remarks')

#===============================================================
class CarbonProjectUsersProjectsIdSchemesParam(Datamodel):
    _name = "carbon.project.users.projects.id.schemes.param"

    id = fields.Integer(description='ID')
    select = fields.Boolean(description='Select')


class CarbonProjectUsersProjectsIdSchemesResponse(Datamodel):
    _name = "carbon.project.users.projects.id.schemes.response"

    code = fields.Integer(required=True)
    message = fields.String(required=True, allow_none=False)
    data = fields.NestedModel('carbon.project.users.projects.id.schemes.data', many=False)

class CarbonProjectUsersProjectsIdSchemesData(Datamodel):
    _name = "carbon.project.users.projects.id.schemes.data"

    success = fields.Boolean(required=True, description='Whether the request succeeded')

#===============================================================
class CarbonProjectUsersInventoriesDetailsParam(Datamodel):
    _name = "carbon.project.users.inventories.details.param"

    parent_id = fields.Integer(description='Parent inventory ID')
    stage_id = fields.Integer(description='Stage ID')
    del_all = fields.Boolean(description='Delete all')
    vals = fields.Dict(description='Field values')

class CarbonProjectUsersInventoriesDetailsResponse(Datamodel):
    _name = "carbon.project.users.inventories.details.response"

    code = fields.Integer(required=True)
    message = fields.String(required=True, allow_none=False)
    data = fields.NestedModel('carbon.project.users.inventories.details.data', many=False)

class CarbonProjectUsersInventoriesDetailsData(Datamodel):
    _name = "carbon.project.users.inventories.details.data"

    success = fields.Boolean(required=True, description='Whether the request succeeded')
    data = fields.NestedModel('carbon.project.users.inventories.details.data.data', many=False)

class CarbonProjectUsersInventoriesDetailsDataData(Datamodel):
    _name = "carbon.project.users.inventories.details.data.data"

    inventory_id = fields.Integer(required=True, description='Inventory ID')
    inventory_name = fields.String(required=True, description='Inventory name')
    details = fields.List(fields.Dict, required=True, description='Inventory details')


#===============================================================
class CarbonProjectUnitsParam(Datamodel):
    _name = "carbon.project.units.param"

    type = fields.String(description='Unit category')
    inv_id = fields.Integer(description='Inventory ID')

class CarbonProjectUnitsResponse(Datamodel):
    _name = "carbon.project.units.response"

    code = fields.Integer(required=True)
    message = fields.String(required=True, allow_none=False)
    data = fields.NestedModel('carbon.project.units.response.data', many=True)

class CarbonProjectUnitsResponseData(Datamodel):
    _name = "carbon.project.units.response.data"

    name = fields.String(required=True, description='Category name')
    id = fields.Integer(required=True, description='Category ID')
    units = fields.NestedModel('carbon.project.units.response.data.data', many=True)

class CarbonProjectUnitsResponseDataData(Datamodel):
    _name = "carbon.project.units.response.data.data"

    id = fields.Integer(required=True, description='Unit ID')
    name = fields.String(required=True, description='Unit name')

#===============================================================

class CarbonProjectStagesResponse(Datamodel):
    _name = "carbon.project.stages.response"

    code = fields.Integer(required=True)
    message = fields.String(required=True, allow_none=False)
    data = fields.NestedModel('carbon.project.stages.response.data', many=True)

class CarbonProjectStagesResponseData(Datamodel):
    _name = "carbon.project.stages.response.data"

    id = fields.Integer(required=True, description='Stage ID')
    name = fields.String(required=True, description='Stage name')
    code = fields.String(required=True, description='Stage code')

#===============================================================   
class CarbonProjectStagesIdLinksResponse(Datamodel):
    _name = "carbon.project.stages.id.links.response"

    code = fields.Integer(required=True)
    message = fields.String(required=True, allow_none=False)
    data = fields.NestedModel('carbon.project.stages.id.links.response.data', many=True)

class CarbonProjectStagesResponseData(Datamodel):
    _name = "carbon.project.stages.id.links.response.data"

    id = fields.Integer(required=True, description='Stage ID')
    name = fields.String(required=True, description='Stage name')
    code = fields.String(required=True, description='Stage code')
    units = fields.List(fields.Dict)
    
#===============================================================

class CarbonProjectStagesIdInventoriesResponse(Datamodel):
    _name = "carbon.project.stages.id.inventories.response"

    code = fields.Integer(required=True)
    message = fields.String(required=True, allow_none=False)
    data = fields.NestedModel('carbon.project.stages.id.inventories.response.data', many=True)

class CarbonProjectStagesIdInventoriesResponseData(Datamodel):
    _name = "carbon.project.stages.id.inventories.response.data"

    id = fields.Integer(required=True, description='Inventory ID')
    name = fields.String(required=True, description='Inventory name')
    unit = fields.String(required=True, description='Unit')
    carbon_factor = fields.String(required=True, description='Emission factor')
    carbon_unit = fields.String(required=True, description='Emission factor unit')


#===============================================================

class CarbonProjectWycolumnsResponse(Datamodel):
    _name = "carbon.project.wycolumns.response"

    code = fields.Integer(required=True)
    message = fields.String(required=True, allow_none=False)
    data = fields.NestedModel('carbon.project.wycolumns.response.data', many=False)

class CarbonProjectWycolumnsResponseData(Datamodel):
    _name = "carbon.project.wycolumns.response.data"

    wycolumns = fields.List(fields.Dict)

    
#===============================================================

class CarbonProjectCitysResponse(Datamodel):
    _name = "carbon.project.citys.response"

    code = fields.Integer(required=True)
    message = fields.String(required=True, allow_none=False)
    data = fields.NestedModel('carbon.project.citys.response.data', many=True)

class CarbonProjectCitysResponseData(Datamodel):
    _name = "carbon.project.citys.response.data"

    value = fields.Integer(required=True, description='State/Province ID')
    label = fields.String(required=True, description='State/Province name')
    children = fields.NestedModel('carbon.project.citys.response.data.data', many=True)

class CarbonProjectCitysResponseDataData(Datamodel):
    _name = "carbon.project.citys.response.data.data"

    value = fields.Integer(required=True, description='City ID')
    label = fields.String(required=True, description='City name')

#===============================================================

class CarbonProjectCompositionsResponse(Datamodel):
    _name = "carbon.project.compositions.response"

    code = fields.Integer(required=True)
    message = fields.String(required=True, allow_none=False)
    data = fields.NestedModel('carbon.project.compositions.response.data', many=True)

class CarbonProjectCompositionsResponseData(Datamodel):
    _name = "carbon.project.compositions.response.data"

    id = fields.Integer(required=True, description='Structural layer component ID')
    name = fields.String(required=True, description='Structural layer component name')

#===============================================================

class CarbonProjectLayersResponse(Datamodel):
    _name = "carbon.project.layers.response"

    code = fields.Integer(required=True)
    message = fields.String(required=True, allow_none=False)
    data = fields.NestedModel('carbon.project.layers.response.data', many=True)

class CarbonProjectLayersResponseData(Datamodel):
    _name = "carbon.project.layers.response.data"

    id = fields.Integer(required=True, description='Structural layer ID')
    name = fields.String(required=True, description='Structural layer name')

#===============================================================

class CarbonProjectLayersIdCompositionsParam(Datamodel):
    _name = "carbon.project.layers.id.compositions.param"

    inventory_id = fields.Integer(required=True, description='Inventory ID')

class CarbonProjectLayersIdCompositionsResponse(Datamodel):
    _name = "carbon.project.layers.id.compositions.response"

    code = fields.Integer(required=True)
    message = fields.String(required=True, allow_none=False)
    data = fields.NestedModel('carbon.project.layers.id.compositions.response.data', many=True)

class CarbonProjectLayersIdCompositionsResponseData(Datamodel):
    _name = "carbon.project.layers.id.compositions.response.data"

    id = fields.Integer(required=True, description='Structural layer component ID')
    max_length = fields.Integer(description='Maximum number of selections')
    name = fields.String(required=True, description='Structural layer component name')
    type = fields.String(required=True, description='Type')
    unit = fields.String(description='Unit')
    columns = fields.List(fields.Dict, description='Column configuration for multi-select table')
    options = fields.List(fields.Dict, description='Options configuration for single-select')

#===============================================================
class CarbonProjectGeojsonParam(Datamodel):
    _name = "carbon.project.geojson.param"

    type = fields.String(required=True, description='Type')
    adcode = fields.String(required=True, description='adcode')

class CarbonProjectGeojsonResponse(Datamodel):
    _name = "carbon.project.geojson.response"

    code = fields.Integer(required=True)
    message = fields.String(required=True, allow_none=False)
    data = fields.NestedModel('carbon.project.geojson.response.data', many=False)

class CarbonProjectGeojsonResponseData(Datamodel):
    _name = "carbon.project.geojson.response.data"

    geojson = fields.String(required=True, description='geojson')

#===============================================================
class CarbonProjectUsersChildsParam(Datamodel):
    _name = "carbon.project.users.childs.param"

    vals = fields.Dict(description='Field values')


class CarbonProjectUsersChildsResponse(Datamodel):
    _name = "carbon.project.users.childs.response"

    code = fields.Integer(required=True)
    message = fields.String(required=True, allow_none=False)
    data = fields.NestedModel('carbon.project.users.childs.response.data', many=False)

class CarbonProjectUsersChildsResponseData(Datamodel):
    _name = "carbon.project.users.childs.response.data"

    success = fields.Boolean(required=True, description='Whether the request succeeded')
    result = fields.String(description='Result')
    has_database_manager = fields.Boolean(description='Whether a database administrator is assigned')
    database_manager = fields.String(description='Database administrator username')
    is_master = fields.Boolean(description='Whether this is the primary account')
    master_name = fields.String(description='Primary account name')
    database_manager_id = fields.Integer(description='Database administrator ID')
    org_data = fields.Dict(description='Organization chart data')
    data = fields.NestedModel('carbon.project.users.childs.response.data.data', many=True)

class CarbonProjectUsersChildsResponseDataData(Datamodel):
    _name = "carbon.project.users.childs.response.data.data"

    id = fields.Integer(required=True, description='Sub-account ID')
    name = fields.String(required=True, description='Sub-account name')
    password = fields.String(description='Sub-account password')
    roles = fields.NestedModel('carbon.project.users.childs.response.data.data.data', many=True)

class CarbonProjectUsersChildsResponseDataDataData(Datamodel):
    _name = "carbon.project.users.childs.response.data.data.data"

    id = fields.Integer(required=True, description='Role ID')
    name = fields.String(required=True, description='Role name')


#===============================================================
class CarbonProjectUsersProjectsRankingParam(Datamodel):
    _name = "carbon.project.users.projects.ranking.param"

    type = fields.String(required=True, description='Type')
    user_id = fields.Integer(description='User ID')

class CarbonProjectUsersProjectsRankingResponse(Datamodel):
    _name = "carbon.project.users.projects.ranking.response"

    code = fields.Integer(required=True)
    message = fields.String(required=True, allow_none=False)
    data = fields.NestedModel('carbon.project.users.projects.ranking.response.data', many=False)

class CarbonProjectUsersProjectsRankingResponseData(Datamodel):
    _name = "carbon.project.users.projects.ranking.response.data"

    x_data = fields.List(fields.String, required=True, description='X-axis data')
    y_data = fields.List(fields.String, required=True, description='Y-axis data')

#===============================================================
class CarbonProjectUsersProjectsOverviewParam(Datamodel):
    _name = "carbon.project.users.projects.overview.param"

    user_id = fields.Integer(description='User ID')

class CarbonProjectUsersProjectsOverviewResponse(Datamodel):
    _name = "carbon.project.users.projects.overview.response"

    code = fields.Integer(required=True)
    message = fields.String(required=True, allow_none=False)
    data = fields.NestedModel('carbon.project.users.projects.overview.response.data', many=False)

class CarbonProjectUsersProjectsOverviewResponseData(Datamodel):
    _name = "carbon.project.users.projects.overview.response.data"

    total = fields.Integer(required=True, description='Total number of projects')
    completed_number = fields.Integer(required=True, description='Number of completed projects')
    city_projects = fields.NestedModel('carbon.project.users.projects.overview.response.data.city', many=True , description='Cities')
    completed_projects = fields.NestedModel('carbon.project.users.projects.overview.response.data.completed', many=True , description='List of completed projects')

class CarbonProjectUsersProjectsOverviewResponseDataCity(Datamodel):
    _name = "carbon.project.users.projects.overview.response.data.city"

    id = fields.Integer(required=True, description='City ID')
    name = fields.String(required=True, description='City name')
    adcode = fields.String(required=True, description='adcode')
    geojson = fields.String(required=True, description='geojson')
    projects = fields.NestedModel('carbon.project.users.projects.overview.response.data.completed', many=True , description='Project list')

class CarbonProjectUsersProjectsOverviewResponseDataCompleted(Datamodel):
    _name = "carbon.project.users.projects.overview.response.data.completed"

    id = fields.Integer(required=True, description='Project ID')
    active_scheme_id = fields.Integer(description='Scheme ID')
    name = fields.String(required=True, description='Project name')
    username = fields.String(required=True, description='Account')
    location = fields.String(required=True, description='Project location')
    life = fields.String(required=True, description='Service life (years)')
    area = fields.String(required=True, description='Pavement area')
    geojson = fields.String(required=True, description='geojson')
    show_detail_btn = fields.Boolean(required=True, description='Whether to show the row detail button')

#===============================================================
class CarbonProjectVerifycodeParam(Datamodel):
    _name = "carbon.project.verifycode.param"

    vals = fields.Dict(description='Field values')

class CarbonProjectVerifycodeResponse(Datamodel):
    _name = "carbon.project.verifycode.response"

    code = fields.Integer(required=True)
    message = fields.String(required=True, allow_none=False)
    data = fields.NestedModel('carbon.project.verifycode.data', many=False)

class CarbonProjectVerifycodeData(Datamodel):
    _name = "carbon.project.verifycode.data"

    success = fields.Boolean(required=True, description='Whether the request succeeded')
