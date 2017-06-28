# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _
import base64
import urllib2
from datetime import datetime

import time, hashlib
import requests
import json
import ast

import xml.etree.ElementTree as ET

class ActivityData(models.Model):
    _name = "activity.data"
    
    name = fields.Char("Activity Name")
    tourico_code = fields.Char("Tourico ID")
    destn_code = fields.Char('Destination Code')
    tourico_destn_id = fields.Char('Tourico Destination ID')
    cityName = fields.Char("City")
    country = fields.Char("Country")
    description = fields.Text("Description")
    stars = fields.Char("Stars")
    address = fields.Char("Address")
    phone = fields.Char("Phone")
    category = fields.Char("Category Name")
    
    
    @api.multi
    def get_act_details(self):
        #print "11111111111111"
        if self.tourico_code:
            act_data = self.env['hotelapi.configuration'].TouricoGetActivityDetails(self.tourico_code)
            self.write(act_data)
        return True
        