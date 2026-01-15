from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component
from odoo.http import request
from odoo import http
import json
import time
import requests
import string
import datetime
import random
import uuid
import hashlib
import os
import hmac
import logging
import base64
import xml.etree.ElementTree as ET
_logger = logging.getLogger(__name__)
import xml.etree.ElementTree as ET


def xml_to_dict(xml_string):
    """
    Convert an XML string to a Python dictionary.

    Args:
        xml_string (str): The XML string to be converted.

    Returns:
        dict: The converted dictionary.
    """

    def _element_to_dict(element):
        """
        Recursively convert an XML element to a dictionary.
        """
        # If the element has no children, return its text content directly.
        if not list(element):
            return element.text

        # Handle elements with children.
        result = {}
        for child in element:
            # If a tag already exists in the result, convert to a list.
            if child.tag in result:
                if isinstance(result[child.tag], list):
                    result[child.tag].append(_element_to_dict(child))
                else:
                    result[child.tag] = [result[child.tag], _element_to_dict(child)]
            else:
                result[child.tag] = _element_to_dict(child)

        # Add attributes (if any).
        if element.attrib:
            if not result:  # Attributes only.
                result = element.attrib
            else:  # Both children and attributes.
                result['@attributes'] = element.attrib

        return result

    try:
        # Parse the XML string.
        root = ET.fromstring(xml_string)
        return {root.tag: _element_to_dict(root)}
    except ET.ParseError as e:
        raise ValueError(f"Invalid XML format: {e}")



def get_one_page_data(page, page_size , data):
    """

    :param self: 
    :param page_size: Page size
    :param page: Page number
    :return: Data for the given page
    """
    totalPages = int(len(data) / page_size) if len(data) % page_size == 0 else int(len(data) / page_size) + 1
    if page == totalPages:
        res = data[(page - 1) * page_size:]
    else:
        res = data[(page - 1) * page_size:page * page_size]
    return res,totalPages


def res_success(parent, data):
    """
    REST API success response.
    """
    res = parent(partial=True, data=data)
    res.code = 0
    res.message = 'success'
    return res


class CarbonProjectServices(Component):
    _inherit = 'base.rest.service'
    _name = 'sms'
    _usage = 'sms'
    _collection = 'sms.services'
    _description = ""


    @restapi.method(
    [
        (['/sendsms'], 'POST')
    ],
    input_param=restapi.Datamodel("sendsms.param"),
    output_param=restapi.Datamodel("sendsms.response"),auth='public')
    def sendsms(self, param):
        """
        Send a verification code.
        """
        VerifyCode = self.env['verify.code'].sudo()

        phone = param.phone
        captcha_param = param.captchaVerifyParam
        ACCESS_KEY_ID = self.env["ir.config_parameter"].sudo().get_param("ACCESS_KEY_ID")
        ACCESS_KEY_SECRET = self.env["ir.config_parameter"].sudo().get_param("ACCESS_KEY_SECRET")
        sms_config = self.env["ir.config_parameter"].sudo().get_param("sms.config")


        params = {
        "Action": "VerifyIntelligentCaptcha",
        "Version": "2023-03-05", # API version; CAPTCHA 2.0 uses 2023-03-05
        "AccessKeyId": ACCESS_KEY_ID,
        "SignatureMethod": "HMAC-SHA1",
        "SignatureVersion": "1.0",
        "SignatureNonce": str(uuid.uuid4()), # Unique nonce
        "Timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "CaptchaVerifyParam": captcha_param, # Verification parameter from the client
        "SceneId": "1hfw1r2d"
        }
        sorted_items = sorted(params.items(), key=lambda x: x[0])
        query_string = "&".join(f"{k}={requests.utils.quote(str(v), safe='')}" for
        k, v in sorted_items)
        # Build the string to sign.
        string_to_sign = "GET&%2F&" + requests.utils.quote(query_string, safe='')
        # Compute the HMAC-SHA1 signature.
        key = (ACCESS_KEY_SECRET + "&").encode('utf-8')
        signature = base64.b64encode(hmac.new(key, string_to_sign.encode('utf-8'),
        hashlib.sha1).digest()).decode()
        params["Signature"] = signature
        # try:
        api_url = "https://captcha.cn-shanghai.aliyuncs.com/"
        response = requests.get(api_url, params=params)

        xml_data = response.content.decode()
        result = xml_to_dict(xml_data)
        if result.get('VerifyIntelligentCaptchaResponse').get('Result').get('VerifyResult') == 'true':
            # Verification passed.
            code = ''.join(random.choices('0123456789', k=6))
            sms_config = sms_config.replace('%',code).replace('$',phone)
            sms_config = json.loads(sms_config)
            active_platform = sms_config.get('active_platform')
            platform = sms_config.get(active_platform)
            url = platform.get('url')
            params = platform.get('params')
            resp = requests.post(url, data=params)

            VerifyCode.create({
                'phone': phone,
                'code': code,
                'token': str(int(time.time())) + ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16)),
                'generation_time':str(int(time.time())),
                'is_used':False,
            })

            res = {
                'success': True,
                'message': 'Verification code sent.'
            }
        else:
            res = {
                'success': True,
                'message': 'Security verification failed.'
            }

        Parent = self.env.datamodels["sendsms.response"]
        return res_success(Parent, res)


    @restapi.method(
    [
        (['/register'], 'POST')
    ],
    input_param=restapi.Datamodel("register.param"),
    output_param=restapi.Datamodel("register.response"),auth='public')
    def register(self, param):
        """
        Register.
        """
        VerifyCode = self.env['verify.code'].sudo()
        ResUsers = self.env['res.users'].sudo()
        IrModelData = self.env['ir.model.data'].sudo()

        username = param.username
        phone = param.phone
        password = param.password
        verifycode = param.verifycode

        # Verify the verification code.
        check_res = VerifyCode.check_verify_code(verifycode, phone)
        if check_res == 'ok':
            user = ResUsers.search(['|',('phone','=',phone),('name','=',username)])
            if user:
                res = {
                    'result': 'User already registered.'
                }
            else:
                user = ResUsers.create({
                    'name':username,
                    'login':username,
                    'phone':phone,
                    'password_text':password,
                })
                user.write({
                    'password': password,
                    'security_role_ids': [IrModelData.xmlid_to_res_id('carbon.role_manager'), IrModelData.xmlid_to_res_id('carbon.role_project_manager'), IrModelData.xmlid_to_res_id('carbon.role_database_manager')]
                })
                user.bind_user_default_data()
                res = {
                    'result': 'Registration successful.'
                }
        else:
            res = {
                'result': check_res
            }

        Parent = self.env.datamodels["register.response"]
        return res_success(Parent, res)
    
    @restapi.method(
    [
        (['/prelogin'], 'POST')
    ],
    input_param=restapi.Datamodel("prelogin.param"),
    output_param=restapi.Datamodel("prelogin.response"),auth='public')
    def prelogin(self, param):
        """
        Pre-login (check whether the phone number is registered).
        """
        ResUsers = self.env['res.users'].sudo()

        phone = param.phone

        user = ResUsers.search([('phone','=',phone)])
        if user:
            res = {
                'success': True
            }
        else:
            res = {
                'success': False,
                'message': 'Phone number is not registered. Please register first.'
            }
        Parent = self.env.datamodels["prelogin.response"]
        return res_success(Parent, res)

    @restapi.method(
    [
        (['/login'], 'POST')
    ],
    input_param=restapi.Datamodel("login.param"),
    output_param=restapi.Datamodel("login.response"),auth='public')
    def login(self, param):
        """
        Login (password login or SMS verification-code login).
        """
        ResUsers = self.env['res.users'].sudo()
        VerifyCode = self.env['verify.code'].sudo()
        LoginRecord = self.env['login.record'].sudo()

        passwordType = param.passwordType
        nameOrPhone = param.nameOrPhone
        phone = param.phone
        verifycode = param.verifycode

        def tologin(user, password, is_password):
            request.session.authenticate(request.db, user.login, password)
            request.httprequest.session.rotate = False
            this_sid = request.httprequest.session.sid

            # Get the client IP address.
            ip_address = request.httprequest.environ.get('REMOTE_ADDR')
            
            # Or get the real IP behind a proxy (if X-Forwarded-For is present).
            if 'HTTP_X_FORWARDED_FOR' in request.httprequest.environ:
                ip_address = request.httprequest.environ['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()

            LoginRecord.create({
                'user_id': user.id,
                'sid': this_sid,
                'login_ip': ip_address,
                'type': 'password' if is_password else 'verifycode',
                'login_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })

            # Determine the maximum number of concurrent sessions.
            max_session = self.env["ir.config_parameter"].sudo().get_param("max.session")
            if max_session:
                max_session = int(max_session)
            else:
                max_session = 1
            # Get user sessions.
            records = LoginRecord.search([('user_id','=',user.id)])
            session_list = []
            for r in records:
                _logger.info(r.login_time)
                if r.sid and r.sid != this_sid:
                    session_list.append(r.sid)
            session_list = list(set(session_list))
            _logger.info(session_list)

            # Keep active (non-expired) sessions by checking whether they exist in the session directory,
            # e.g. werkzeug_a341f6c9273894327d0dbb0c588ef6e957f580bb.sess
            # Get session_store.
            active_session_list = []
            session_store = http.root.session_store
            _logger.info('self.session_store')
            _logger.info(session_store.path)
            for fname in os.listdir(session_store.path):
                path = os.path.join(session_store.path, fname)
                _logger.info(path)
                sid = path.split('werkzeug_')[1].split('.')[0]
                if sid in session_list:
                    active_session_list.append(sid)
            _logger.info(active_session_list)

        

            # Number of sessions to delete.
            del_len = len(active_session_list)  + 1 -  max_session
            for i in range(0,del_len):
                sid = active_session_list.pop()
                path = f'{session_store.path}/werkzeug_{sid}.sess'
                os.unlink(path)

            return this_sid

        if passwordType:
            user = ResUsers.search(['|',('name','=',nameOrPhone),('phone','=',nameOrPhone)],limit=1)
            password = param.password
            if user:
                try:
                    sid = tologin(user,password,passwordType)
                    res = {
                        'success': True,
                        'session': sid
                    }
                except:
                    res = {
                        'success': False,
                        'message': 'Incorrect password.'
                    }
            else:
                res = {
                    'success': False,
                    'message': 'User not registered.'
                }
        else:
            user = ResUsers.search([('phone','=',phone)],limit=1)
            password = user.password_text
            if user:
                # Verify the verification code.
                check_res = VerifyCode.check_verify_code(verifycode, phone)
                if check_res == 'ok':
                    try:
                        sid = tologin(user,password,passwordType)
                        res = {
                            'success': True,
                            'session': sid
                        }
                    except:
                        res = {
                            'success': False,
                            'message': 'An error occurred.'
                        }
                else:
                    res = {
                        'success': False,
                        'message': check_res
                    }
            else:
                res = {
                    'success': False,
                    'message': 'Phone number is not registered.'
                }

        Parent = self.env.datamodels["login.response"]
        return res_success(Parent, res)

    @restapi.method(
    [
        (['/password'], 'POST')
    ],
    input_param=restapi.Datamodel("password.param"),
    output_param=restapi.Datamodel("password.response"),auth='user')
    def password(self, param):
        """
        Change password.
        """
        user = request.env.user
        old_password = param.old_password
        new_password = param.new_password

        try:
            user.change_password(old_password, new_password)
            user.password_text = new_password
            res = {
                'result': 'Password changed successfully.'
            }
        except:
            res = {
                'result': 'Incorrect current password.'
            }
            
        Parent = self.env.datamodels["password.response"]
        return res_success(Parent, res)

   
