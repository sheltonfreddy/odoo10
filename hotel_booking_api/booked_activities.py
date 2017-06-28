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

from odoo.tools import float_is_zero, float_compare
from datetime import date,datetime

class booked_activities(models.Model):
    _name = "booked.activities"
    
    _order = 'booked_on desc'
    
    reservationId = fields.Char("ReservationId")
    tranNumber = fields.Char("TranNumber")
    currency = fields.Char("Currency")
    total = fields.Float("Total")
    
    name = fields.Char("Name")
    customer_id = fields.Many2one('res.partner', string='Customer')
    
    booking_date = fields.Date('Booking Date')
    booked_on = fields.Date("Booked On")
    cancellation_fee = fields.Float("Cancellation Fee")
    cancellation_fee_currency = fields.Char("Cancellation Fee Currency")
    passenger_ids = fields.One2many('act.passengers', 'act_id', string='Passengers')
    
    state = fields.Selection([
            ('draft', 'Draft'),
            ('Confirm', 'Confirm'),
            ('invoiced', 'Invoiced'),
            ('cancel', 'Cancelled')], 
        string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False)
    
    @api.multi
    def create_invoice(self):
        #return True
        company_id = self._context.get('company_id', self.env.user.company_id.id)
        domain = [
            ('type', '=', 'sale'),
            ('company_id', '=', company_id)]
        journal = self.env['account.journal'].search(domain, limit=1)
        vals = {}
        vals.update({
                'partner_id' : self.customer_id.id,
                'journal_id' : journal.id,
                'account_id': self.customer_id.property_account_receivable_id.id })
        account_revenue = self.env['account.account'].search([('user_type_id', '=', self.env.ref('account.data_account_type_revenue').id)], limit=1)
        inv_lines = []
        #for room in self.booked_rooms:
            #line_vals = product_id_change_vals['value'].copy()
        line_vals = ({
             'name' : self.name,
             'price_unit': self.total,
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
    
    @api.multi
    def action_cancel_booking(self):
        #print "self.booking_type ==>> ", self.booking_type
        #if self.booking_type == 'tourico_hotels':
        #for activit in self.booked_rooms:
        result = self.env['hotelapi.configuration'].tourico_GetCancellationFee(self.reservationId, datetime.now().strftime('%Y-%m-%d'))
        #print result,"rrrrrrrrrrrrr",self.id,self.reservationId
        CancellationFeeValue = result.CancellationFeeValue
        Currency = result.Currency
        vals = {
            'cancellation_fee' : CancellationFeeValue,
            'currency' : Currency,
            'booked_activity_id' : self.id }
        wiz_cancellation = self.env['cancellation.fee'].create(vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cancellation.fee',
            'res_id': wiz_cancellation.id,
            'view_mode': 'form',
            'target': 'new' }
        

class ActPassengers(models.Model):
    _name = "act.passengers"
    
    name = fields.Char("Name")
    type = fields.Char("Type")
    act_id = fields.Many2one('booked.activities','Activity')
    