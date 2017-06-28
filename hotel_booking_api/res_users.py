# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class Users(models.Model):
    _inherit = 'res.users'
    
    travel_partner_id = fields.Many2one('res.partner','Travel Partner')
    agency_id = fields.Many2one('agency.data', 'Agency')