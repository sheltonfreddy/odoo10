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
from datetime import date,datetime
import dateutil.parser as parser
from dateutil import relativedelta
import time

from odoo.tools import float_is_zero, float_compare

class booked_hotels(models.Model):
    _name = "booked.hotels"
    
    _order = 'name desc'
    
    @api.one
    @api.depends('booked_rooms.rate_curr_exc_markup', 'booked_rooms.rate_currency','agency_currency_id')
    def _compute_amount(self):
        self.amount_exc_markup = sum(room.rate_curr_exc_markup for room in self.booked_rooms)
        self.amount_total = sum(room.rate_currency for room in self.booked_rooms)
        #if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
         #   currency_id = self.currency_id.with_context(date=self.date_invoice)
          #  amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
           # amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        #sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        #self.amount_total_company_signed = amount_total_company_signed * sign
        #self.amount_total_signed = self.amount_total * sign
        #self.amount_untaxed_signed = amount_untaxed_signed * sign
    
    name = fields.Char("Name", default="/")
    booking_type = fields.Selection([('hotels','Hotels'),('tourico_hotels','Tourico Hotels')], 
                       string='Booking Type', required=True, default="hotels")
    hotel = fields.Char("Hotel Name")
    check_in = fields.Date(string='Check IN')
    check_out = fields.Date(string='Check OUT')
    destinationName = fields.Char("Destination Name")
    longitude = fields.Char("Longitude")
    latitude = fields.Char("Latitude")
    holder_name = fields.Char("Name")
    holder_surname = fields.Char("Surname")
    creationDate = fields.Date(string='Booking Date')
    totalNet = fields.Float("Net Amount")
    totalnet_currency = fields.Float("Net Amount")
    pendingAmount = fields.Float("Pending Amount")
    currency = fields.Char("API Currency")
    agency_currency_id = fields.Many2one('res.currency',"Agency Currency")
    reference = fields.Char("Reference")
    remark = fields.Char("Remark")
    modification = fields.Boolean("Modification")
    cancellation = fields.Boolean("Cancellation")
    booked_rooms = fields.One2many('room.booked', 'booked_hotel_id', string='Rooms Booked')
    booked_user_id = fields.Many2one('res.users', string='Booked User')
    customer_id = fields.Many2one('res.partner', string='Customer')
    supplier_name = fields.Char("Supplier")
    supplier_vatNumber = fields.Char("vatNumber")
    state = fields.Selection([
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('invoiced','Invoiced'),
            ('cancel', 'Cancelled')], 
        string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False)
    invoice_id = fields.Many2one('account.invoice', string='Invoice')
    reservationId = fields.Char('Reservation Id')
    tranNum = fields.Char('Tran Num')
    cancellationReference = fields.Char("Cancellation Reference")
    
    cancellation_fee = fields.Float("Cancellation Fee")
    cancellation_fee_currency = fields.Char("Cancellation Fee Currency")
    no_of_nights = fields.Integer("Number of Nights", compute = "calculate_no_of_nights")
    total_rate = fields.Float("Total Amount", compute = "calculate_total_amount")
    hotel_id = fields.Many2one('hotel.data', 'Hotel')
    agency_id = fields.Many2one('agency.data', 'Agency')
    agency_markup = fields.Char('Agency Markup Total')
    markup_percent = fields.Integer("Mark up Percent")
    amount_exc_markup = fields.Monetary(string='Amount without Markup',
        store=True, readonly=True, currency_field='agency_currency_id', compute='_compute_amount', track_visibility='always')
    amount_total = fields.Monetary(string='Total Amount',
        store=True, readonly=True, currency_field='agency_currency_id', compute='_compute_amount', track_visibility='always')
    
    def create(self, vals):
        if vals.get('name') == "/":
            #vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'booking.order') or '/'
            vals['name'] = self.env['ir.sequence'].sudo().next_by_code('booking.order') or 'New'
        res = super(booked_hotels, self).create(vals)
        booked = res
        if booked.state == "confirmed":
         #   print "xxxxxxxxxxxxxxx"
            booked.sudo().create_invoice()
        return res
    
    #def create_invoice(self):
     #   return res
    
    @api.multi
    def action_get_cancellation_policies(self):
        import suds.client
        from suds.sax.element import Element
        from suds.sax.attribute import Attribute
        wsdl = "http://demo-wsnew.touricoholidays.com/ReservationsService.asmx?wsdl"
        
        login_name, password = self.env['hotelapi.configuration'].get_turico_reservations_service()
        client = suds.client.Client(wsdl,headers={'Accept-Encoding': 'gzip'})
        service = client.service
        username  = Element('trav:username').setText(login_name)
        password = Element('trav:password').setText(password)
        culture = Element('trav:culture').setText('en_US')
        version = Element('trav:version').setText('8')
        AuthenticationHeader = Element('ns0:LoginHeader') 
        AuthenticationHeader.attributes.append(Attribute('xmlns:trav', 'http://tourico.com/travelservices/'))
        AuthenticationHeader.children = [username, password, culture, version]
        client.set_options(soapheaders=[AuthenticationHeader])
        for room in self.booked_rooms:
            #print "room.reservationId ======>> ", room.reservationId
            result = client.service.GetCancellationPolicies(room.reservationId)
            #print "+"*50
            #print result
            #print "*"*50
        
        
        
    
    @api.multi
    def action_cancel_booking(self):
        #print "self.booking_type ==>> ", self.booking_type
        if self.booking_type == 'tourico_hotels':
            CancellationFeeValue = 0
            Currency = ""
            for room in self.booked_rooms:
                result = self.env['hotelapi.configuration'].tourico_GetCancellationFee(room.reservationId, datetime.now().strftime('%Y-%m-%d'))
                CancellationFeeValue = CancellationFeeValue + result.CancellationFeeValue
                Currency = result.Currency
            vals = {
                'cancellation_fee' : CancellationFeeValue,
                'currency' : Currency,
                'booked_hotel_id' : self.id }
            wiz_cancellation = self.env['cancellation.fee'].create(vals)
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'cancellation.fee',
                'res_id': wiz_cancellation.id,
                'view_mode': 'form',
                'target': 'new' }
        hotelapi = self.env['hotelapi.configuration'].search([])
        result = hotelapi[0].cancel_booking(self.reference)
        self.cancellationReference = result['booking']['cancellationReference']
        status = result['booking']['status']
        if status == 'CANCELLED':
            self.state = "cancel"
            if self.booked_rooms:
                for room in self.booked_rooms:
                    room.status = 'CANCELLED'
    
    @api.multi
    def create_invoice(self):
        #return True
        company_id = self._context.get('company_id', self.env.user.company_id.id)
        domain = [
            ('type', '=', 'sale'),
            ('company_id', '=', company_id)]
        journal = self.env['account.journal'].search(domain, limit=1)
        vals = {}#self.env['account.invoice']._onchange_partner_id()#self.env['account.invoice']._onchange_partner_id('out_invoice', self.customer_id.id)['value']
        vals.update({
                'partner_id' : self.customer_id.id,
                'journal_id' : journal.id,
                'account_id': self.customer_id.property_account_receivable_id.id})
        #product = self.env['product.product'].search([('is_hotel_room', '=', True)])[0]
        #product_id_change_vals = self.env['account.invoice.line'].product_id_change(product.id, False, partner_id=self.customer_id.id)
        account_revenue = self.env['account.account'].search([('user_type_id', '=', self.env.ref('account.data_account_type_revenue').id)], limit=1)
        inv_lines = []
        for room in self.booked_rooms:
            #line_vals = product_id_change_vals['value'].copy()
            line_vals = {}
            line_vals.update({
                 'name' : self.hotel+'-'+room.name,
                 'price_unit': room.rate_curr_exc_markup,
                 'quantity' : 1 ,
                 'account_id' : account_revenue.id
                 })
            inv_lines.append((0, 0, line_vals))
        vals['invoice_line_ids'] = inv_lines
        invoice = self.env['account.invoice'].create(vals)
        self.invoice_id = invoice.id
        self.state = 'invoiced'
        invoice.action_invoice_open()
        if invoice.has_outstanding:
            if invoice.state == 'open':
                domain = [('account_id', '=', invoice.account_id.id), ('partner_id', '=', self.env['res.partner']._find_accounting_partner(self.customer_id).id), ('reconciled', '=', False), ('amount_residual', '!=', 0.0)]
            if invoice.type in ('out_invoice', 'in_refund'):
                domain.extend([('credit', '>', 0), ('debit', '=', 0)])
                #type_payment = _('Outstanding credits')
            lines = self.env['account.move.line'].search(domain)
            if len(lines) != 0:
                amount_to_show = 0
                for line in lines:
                    # get the outstanding residual value in invoice currency
                    if line.currency_id and line.currency_id == invoice.currency_id:
                        amount_to_show += abs(line.amount_residual_currency)
                    else:
                        amount_to_show += line.company_id.currency_id.with_context(date=line.date).compute(abs(line.amount_residual), invoice.currency_id)
                    if float_is_zero(amount_to_show, precision_rounding=invoice.currency_id.rounding):
                        continue
            if amount_to_show>=invoice.residual:
                for line in lines:
                    invoice.assign_outstanding_credit(line.id)
                    if invoice.residual==0:
                        break
                        
        menu_obj = self.env['ir.ui.menu']
        menu_ids = menu_obj.search([('name', '=', "Customer Invoices")])
        data = {'type': 'ir.actions.client',
           'tag': 'reload',
           'params': {'menu_id': menu_ids and menu_ids[0].id or False}}
        return data
    
    def action_view_invoice(self, cr, uid, ids, context=None):
        '''
        This function returns an action that display existing invoices of given sales order ids. It can either be a in a list or in a form view, if there is only one invoice to show.
        '''
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        result = mod_obj.get_object_reference(cr, uid, 'account', 'action_invoice_tree1')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        #compute the number of invoices to display
        inv_ids = []
        for booked in self.browse(cr, uid, ids, context=context):
            inv_ids += [booked.invoice_id.id]
        #choose the view_mode accordingly
        if len(inv_ids)>1:
            result['domain'] = "[('id','in',["+','.join(map(str, inv_ids))+"])]"
        else:
            res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = inv_ids and inv_ids[0] or False
        return result
    
    @api.multi
    def calculate_no_of_nights(self):
        check_in_date = datetime.strptime(str(self.check_in), '%Y-%m-%d')     # calculating age in months
        check_out_date = datetime.strptime(str(self.check_out), '%Y-%m-%d')
        r = relativedelta.relativedelta(check_out_date, check_in_date)
        self.no_of_nights = r.days
        
    @api.depends('booked_rooms.rate')
    def calculate_total_amount(self):
         """ Calculate the total amount """
         
         total_amount = 0.0
         #print "======================self==============",self
         for booking in self:
             
             for line in booking.booked_rooms:
                # print "==================line============",line
                 total_amount += line.rate
             booking.total_rate = total_amount
             #print booking.total_rate,"bbbbbbbbbbbbbbbbbbbbbbbb" 
#     @api.multi
#     def print_receipt(self):
#         '''This function prints the booking information'''
#         print "pppppppppppppppppppppppppppp"
#         active_ids=self._ids
#         context = dict(self._context or {}, active_ids)
#         self.write({'printed': True})
#         return self.env['report'].get_action(self._ids, 'hotel_booking_api.report_booking_info')

class room_booked(models.Model):
    _name = "room.booked"
    
    booked_hotel_id = fields.Many2one('booked.hotels', string='Hotel')
    name = fields.Char('Room')
    rate = fields.Float('Rate')
    rate_currency = fields.Float('Rate')
    rate_curr_exc_markup = fields.Float('Rate')
    adults = fields.Integer('Adults')
    children = fields.Integer('Children')
    status = fields.Char('Status')
    reservationId = fields.Char('Reservation Id')
    tranNum = fields.Char('tranNum')
    supplement_ids = fields.One2many('booked.supplement', 'room_id', 'Booked Supplements')
    pax = fields.Char('Paxes')
    boards = fields.Char('Boards')
    rate_comments = fields.Text('Rate Comments')

class BookedSupplement(models.Model):
    _name = "booked.supplement"
    
    name = fields.Char('Supplement Name')
    price = fields.Float('Price')
    room_id = fields.Many2one('room.booked','Room')
    
class BookingType(models.Model):  
    
    _name = "booking.type"
    
    @api.multi
    def _compute_booked_count(self):
        # TDE TODO count picking can be done using previous two
        if not self.user_has_groups('base.group_agency_admin'):
            agency_id =[self.env.user.agency_id.id]
        else:
            agency_id = []
            agencies = self.env['agency.data'].search([])
            for agency in agencies:
                agency_id.append(agency.id)
            
        domains = {
            'count_booked_invoiced_hotelbeds': [('state', '=', 'invoiced'),('booking_type','=','hotels'),('booked_user_id.agency_id','in',agency_id)],
            'count_booked_invoiced_tourico': [('state', '=', 'invoiced'),('booking_type','=','tourico_hotels'),('booked_user_id.agency_id','in',agency_id)],
            'count_booked_cancel': [('state', '=', 'cancel')],
            #'total_invoiced_hotelbeds': [('state', '=', 'invoiced')],
            #'count_picking_ready': [('state', 'in', ('assigned', 'partially_available'))],
            #'count_picking': [('state', 'in', ('assigned', 'waiting', 'confirmed', 'partially_available'))],
            #'count_picking_late': [('min_date', '<', time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), ('state', 'in', ('assigned', 'waiting', 'confirmed', 'partially_available'))],
            #'count_picking_backorders': [('backorder_id', '!=', False), ('state', 'in', ('confirmed', 'assigned', 'waiting', 'partially_available'))],
        }
        #print self,"ssssssssssssss"
        for field in domains:
            data = self.env['booked.hotels'].read_group(domains[field] +
                [('state', 'not in', ('done', 'cancelled'))],
                ['booking_type'], ['booking_type'])
            #print data,"ddddddddddddddddddd"
            count = dict(map(lambda x: (x['booking_type'] and x['booking_type'], x['booking_type_count']), data))
            #print count,"cccccccccccccccccc"
            for record in self:
                #print field
                record[field] = count.get(record.name, 0)
                 
        #for record in self:
         #   record.rate_picking_late = record.count_picking and record.count_picking_late * 100 / record.count_picking or 0
          #  record.rate_picking_backorders = record.count_picking and record.count_picking_backorders * 100 / record.count_picking or 0
    
#     @api.one
#     def _compute_inv_total(self):
#         if not self.user_has_groups('base.group_agency_admin'):
#             agency_id =[self.env.user.agency_id.id]
#         else:
#             agency_id = []
#             agencies = self.env['agency.data'].search([])
#             for agency in agencies:
#                 agency_id.append(agency.id)
#         domains = {
#             'invoice_total_hotelbeds': [('state', '=', 'invoiced'),('booking_type','=','hotels'),('booked_user_id.agency_id','in',agency_id)],
#             'invoice_total_tourico': [('state', '=', 'invoiced'),('booking_type','=','tourico_hotels'),('booked_user_id.agency_id','in',agency_id)],
#         }
#         for field in domains:
#             data =  self.env['booked.hotels'].search(domains[field])
#             data = self.env['booked.hotels'].read_group(domains[field] +
#                 [('state', '=', 'invoiced')],
#                 ['booking_type'], ['booking_type'])
#             #print data,"ddddddddddddddddddd"
#             count = dict(map(lambda x: (x['booking_type']), data))
#             #print count,"cccccccccccccccccc"
#             for record in self:
#                 #print field
#                 record[field] = count.get(record.name, 0)
    
    name = fields.Char('Booking Type')
    color = fields.Integer('Color')
    type = fields.Char('Dashboard Label')
    count_booked_invoiced_hotelbeds = fields.Integer(compute='_compute_booked_count')
    count_booked_invoiced_tourico = fields.Integer(compute='_compute_booked_count')
    count_booked_cancel = fields.Integer(compute='_compute_booked_count')
    #invoice_total = fields.Float(compute='_compute_inv_total')
    
    @api.multi
    def _get_action(self, action_xmlid):
        # TDE TODO check to have one view + custo in methods
        action = self.env.ref(action_xmlid).read()[0]
        if self:
            action['display_name'] = self.display_name
            action['domain'] = [('booking_type','=',self.name),('state','=','invoiced')]
        return action

    @api.multi
    def get_hotelbeds_bookings(self):
        return self._get_action('hotel_booking_api.booked_hotels_hotelbeds')
    
    @api.multi
    def _get_action_cancel(self, action_xmlid):
        # TDE TODO check to have one view + custo in methods
        action = self.env.ref(action_xmlid).read()[0]
        if self:
            action['display_name'] = self.display_name
            action['domain'] = [('booking_type','=',self.name),('state','=','cancel')]
        return action
    
    @api.multi
    def get_action_bookings_cancel(self):
        return self._get_action_cancel('hotel_booking_api.booked_hotels_hotelbeds')
    