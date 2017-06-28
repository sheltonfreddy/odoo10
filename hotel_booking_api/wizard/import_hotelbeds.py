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

from openerp.osv import osv
from openerp import models, fields, api, _
from openerp.tools.translate import _
from datetime import datetime


class ImportHotelBeds(models.TransientModel):
    _name = "import.hotelbeds"
    _description = "Import HotelBeds Data"
    
    @api.multi
    def do_update_hotelbeds_hoteldata(self):
        hotels = self.env['hotel.data'].search([('hotelbeds_code', '!=', False)])
        for hotel in hotels:
            hotel.get_hotel_details()
        return True