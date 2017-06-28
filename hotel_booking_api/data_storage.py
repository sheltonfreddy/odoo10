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

class data_storage(models.Model):
    _name = "data.storage"
    
    code = fields.Char('Code')
    type = fields.Char('Type')
    image = fields.Binary("Image")
    last_used = fields.Date(string='Last Used')
    url = fields.Char('url')
    
    @api.multi
    def get_image(self, code, url, type="Hotel"):
        data = self.search([('url', '=', url)])
        data = data and data[0] or False
        if data:
            data.last_used = datetime.now().strftime('%Y-%m-%d')
            return data.image
        vals = { 'image' : False,#base64.encodestring(urllib2.urlopen(url).read()),
                 'code' : code,
                 'type' : type,
                 'url' : url,
                 'last_used' : datetime.now().strftime('%Y-%m-%d') }
        
        return self.create(vals).image
    
    @api.multi
    def save_image(self, code, url, type="Hotel"):
        data = self.search([('url', '=', url)])
        data = data and data[0] or False
        if data:
            data.last_used = datetime.now().strftime('%Y-%m-%d')
            return data
        vals = { 'image' : False,#base64.encodestring(urllib2.urlopen(url).read()),
                 'code' : code,
                 'type' : type,
                 'url' : url,
                 'last_used' : datetime.now().strftime('%Y-%m-%d') }
        
        return self.create(vals)
        
        
    
    