from odoo.addons.datamodel.core import Datamodel
from odoo.addons.datamodel import fields

class SendsmsParam(Datamodel):
    _name = "sendsms.param"

    phone = fields.String()
    captchaVerifyParam = fields.String()

class SendsmsResponse(Datamodel):
    _name = "sendsms.response"

    code = fields.Integer(required=True)
    message = fields.String(required=True, allow_none=False)
    data = fields.NestedModel('sendsms.data', many=False)

class SendsmsData(Datamodel):
    _name = "sendsms.data"

    success = fields.Boolean(required=True, description='Whether the request succeeded')
    message = fields.String()


#####################################################################

class RegisterParam(Datamodel):
    _name = "register.param"

    username = fields.String(required=True, description='Username')
    phone = fields.String(required=True, description='Phone number')
    verifycode = fields.String(required=True, description='Verification code')
    password = fields.String(required=True, description='Password')

class RegisterResponse(Datamodel):
    _name = "register.response"

    code = fields.Integer(required=True)
    message = fields.String(required=True, allow_none=False)
    data = fields.NestedModel('register.data', many=False)


class RegisterData(Datamodel):
    _name = "register.data"

    result = fields.String(required=True, description='Result')
#####################################################################

class PreloginParam(Datamodel):
    _name = "prelogin.param"

    phone = fields.String(required=True, description='Phone number')

class PreloginResponse(Datamodel):
    _name = "prelogin.response"

    code = fields.Integer(required=True)
    message = fields.String(required=True, allow_none=False)
    data = fields.NestedModel('prelogin.data', many=False)


class PreloginData(Datamodel):
    _name = "prelogin.data"

    success = fields.Boolean(required=True, description='Whether the request succeeded')
    message = fields.String()
#####################################################################

class LoginParam(Datamodel):
    _name = "login.param"

    passwordType = fields.Boolean()
    nameOrPhone = fields.String()
    phone = fields.String()
    verifycode = fields.String()
    password = fields.String()

class LoginResponse(Datamodel):
    _name = "login.response"

    code = fields.Integer(required=True)
    message = fields.String(required=True, allow_none=False)
    data = fields.NestedModel('login.data', many=False)


class LoginData(Datamodel):
    _name = "login.data"

    success = fields.Boolean(required=True, description='Whether the request succeeded')
    message = fields.String()
    session = fields.String()


#===============================================================
class PasswordParam(Datamodel):
    _name = "password.param"

    old_password = fields.String(required=True, description='Current password')
    new_password = fields.String(required=True, description='New password')

class PasswordResponse(Datamodel):
    _name = "password.response"

    code = fields.Integer(required=True)
    message = fields.String(required=True, allow_none=False)
    data = fields.NestedModel('password.data', many=False)


class PasswordData(Datamodel):
    _name = "password.data"

    result = fields.String(required=True, description='Result')
