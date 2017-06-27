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
from openerp.osv import osv

class cancellation_fee(osv.osv_memory):
    _name = "cancellation.fee"
    _description = "Cancellation Fee"
    
    cancellation_fee = fields.Float("Cancellation Fee", default=0.0)
    currency = fields.Char("Currency")
    reservationId = fields.Char('Reservation Id')
    booked_hotel_id = fields.Many2one('booked.hotels', string='Booked Hotel')
    booked_activity_id = fields.Many2one('booked.activities', string='Booked Activity')
    
    @api.multi
    def do_cancel(self):
        try:
            for room in self.booked_hotel_id.booked_rooms:
                result = self.env['hotelapi.configuration'].tourico_CancelReservation(room.reservationId)
                if result == True:
                     room.status = 'CANCELLED'
        except:
            pass
        self.booked_hotel_id.state = "cancel"
        self.booked_hotel_id.cancellation_fee = self.cancellation_fee
        self.booked_hotel_id.cancellation_fee_currency = self.currency
            
    @api.multi
    def do_cancel_activity(self):
        print "SSSSSSSSSSSS",self.booked_activity_id.reservationId
        result = self.env['hotelapi.configuration'].tourico_CancelReservation(self.booked_activity_id.reservationId)
        if result == True:
            self.booked_activity_id.state='cancel' 
            self.booked_activity_id.cancellation_fee = self.cancellation_fee
            self.booked_activity_id.cancellation_fee_currency = self.currency               
     


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
