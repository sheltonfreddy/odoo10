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
import time
from openerp import models, fields, api, tools, _
from odoo.exceptions import UserError, ValidationError


class AgencyData(models.Model):
    _name = "agency.data"
    
    #def _compute_logo_web(self):
    #    for agency in self:
    #        agency.logo_report = tools.image_resize_image(agency.agency_logo, (180, None))
    
    name = fields.Char("Agency Name", required=True)
    login_ids = fields.One2many('agency.login','agency_id','Agency Logins')
    travel_partner_id = fields.Many2one('res.partner','Travel Partner', required=True)
    user_limit = fields.Integer('User Limit')
    credit_limit = fields.Float('Credit Limit', groups='base.group_erp_manager')
    agency_logo = fields.Binary('Agency Logo')
    #logo_report = fields.Binary(compute='_compute_logo_web', store=True)
    agency_commission_tourico = fields.Float('Tourico Agency Commission')
    commission_tourico_type = fields.Selection([('amount','Amount'),('percent','Percentage')],string='Commission Type', default='amount')
    agency_currency_id = fields.Many2one('res.currency', 'Agency Currency', required=True)
    currency_rate = fields.Float(related='agency_currency_id.rate', string='Currency Rate')
    
class AgencyLogin(models.Model):
    _name = "agency.login" 
    
    name = fields.Char("Username", required=True)
    password =  fields.Char("Password", required=True)
    manager_login = fields.Boolean('Manager Login?')
    agency_id = fields.Many2one('agency.data','Agency')
    
    @api.model
    def create(self, vals):
        login_user= super(AgencyLogin, self).create(vals)
        group_user = self.env.ref('base.group_user')
        booking_user = self.env.ref('base.group_can_book_hotel')
        booking_manager = self.env.ref('base.group_hotel_booking_manager')
        users = [group_user.id,booking_user.id]
        if login_user.manager_login:
            users.append(booking_manager.id)
        if login_user and login_user.name and login_user.password:
            login_ids = self.search([('agency_id','=',login_user.agency_id.id)])
            user_limit = login_user.agency_id.user_limit
            if len(login_ids)>user_limit:
                raise UserError(_('User Limit Exceeded.'))
            user_vals = {'name': login_user.name,
                         'login': login_user.name,
                         'password': login_user.password,
                         'agency_id': login_user.agency_id.id,
                         'travel_partner_id': login_user.agency_id.travel_partner_id.id,
                         'groups_id': [(6, 0, users)],
                        }
            self.env['res.users'].create(user_vals)
        return login_user

# class ResPartner(models.Model):
#     _inherit = "res.partner"
#     
#     def _compute_logo_web(self):
#         for partner in self:
#             agency = self.env['agency.data'].search([('travel_partner_id','=',partner.id)])
#             print agency,"aaaaaaaaaaaaaaaaaaaa"
#             partner.report_logo = tools.image_resize_image(agency.agency_logo, (180, None))
#     
#     report_logo = fields.Binary(compute='_compute_logo_web', store=True)

class AgencyHelpdesk(models.Model):
    _name = "agency.helpdesk"
    
    name = fields.Char('Subject', required=True, readonly=True, states={'draft': [('readonly', False)]})
    ticket_no = fields.Char('Ticket No:')
    agency_id = fields.Many2one('agency.data', 'Agency', default=lambda self: self.env.user.agency_id, readonly=True)
    category_id = fields.Many2one('helpdesk.category', 'Category')
    date = fields.Date('Date')
    description = fields.Text('Description', readonly=True, states={'draft': [('readonly', False)]})
    user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.user,readonly=True)
    state = fields.Selection([('draft', 'New'), ('confirm', 'On Process'),('done','Closed'),('cancel','Cancelled')], string='Status', default='draft')
    comments = fields.Text('Comments',readonly=True, states={'confirm': [('readonly', False)]})
    @api.multi
    def do_submit(self):
        self.state='confirm'
        self.ticket_no = self.env['ir.sequence'].next_by_code('agency.helpdesk')
        self.date = time.strftime('%Y-%m-%d')
        return True
    
    @api.multi
    def do_cancel(self):
        self.state='cancel'
        return True
    
    @api.multi
    def do_close(self):
        self.state='done'
        return True
    
class HelpdeskCategory(models.Model):
    _name = "helpdesk.category"
    
    name = fields.Char('Category Name', required=True)
    
class EducationSubmission(models.Model):
    _name = "education.submission"
    
    name = fields.Char('Name', required=True)
    phone = fields.Char('Phone No:')
    cpr_no = fields.Char('CPR')
    dob = fields.Date('Date of Birth')
    qualifcn = fields.Char('Qualification')
    experience = fields.Char('Experience')
    country = fields.Char('Country')
    course_details = fields.Text('Course Details')
    agency_id = fields.Many2one('agency.data', 'Agency', default=lambda self: self.env.user.agency_id, readonly=True)
    user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.user,readonly=True)
    state = fields.Selection([('draft', 'New'), ('confirm', 'On Process'),('done','Closed'),('cancel','Cancelled')], string='Status', default='draft')
    date = fields.Date('Date')
    
    @api.multi
    def do_submit(self):
        self.state='confirm'
        self.date = time.strftime('%Y-%m-%d')
        return True
    
    @api.multi
    def do_cancel(self):
        self.state='cancel'
        return True
    
    @api.multi
    def do_close(self):
        self.state='done'
        return True
    
class MedicalSubmission(models.Model):
    _name = "medical.submission"
    
    name = fields.Char('Name', required=True)
    phone = fields.Char('Phone No:')
    cpr_no = fields.Char('CPR')
    dob = fields.Date('Date of Birth')
    country = fields.Char('Country')
    medical_details = fields.Text('Medical Details')
    agency_id = fields.Many2one('agency.data', 'Agency', default=lambda self: self.env.user.agency_id, readonly=True)
    user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.user,readonly=True)
    state = fields.Selection([('draft', 'New'), ('confirm', 'On Process'),('done','Closed'),('cancel','Cancelled')], string='Status', default='draft')
    date = fields.Date('Date')
    
    @api.multi
    def do_submit(self):
        self.state='confirm'
        self.date = time.strftime('%Y-%m-%d')
        return True
    
    @api.multi
    def do_cancel(self):
        self.state='cancel'
        return True
    
    @api.multi
    def do_close(self):
        self.state='done'
        return True
    
    
          