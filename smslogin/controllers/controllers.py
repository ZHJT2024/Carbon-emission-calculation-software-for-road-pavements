# -*- coding: utf-8 -*-
from odoo.addons.base_rest.controllers import main
from odoo import http
from odoo.http import request, content_disposition
import requests
import os
import logging
import json
# import pdfkit
# from pydocx import PyDocX
_logger = logging.getLogger(__name__)


class ModelController(main.RestController):
    _root_path = '/api/sms/v2/'
    _collection_name = 'sms.services'
