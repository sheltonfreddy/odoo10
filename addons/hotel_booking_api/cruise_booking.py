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
import openerp
import suds.client
from suds.sax.element import Element
from suds.sax.attribute import Attribute

list_cruise_length = [(n, n) for n in range(1, 1000)]

class cruise_booking(models.Model):
    _name = "cruise.booking"
    
    destination_id = fields.Many2one('cruisedestinations.tourico', string='Destination', required=True)
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    from_date = fields.Date(string='From')
    to_date = fields.Date(string='To')
    cruise_length = fields.Selection(list_cruise_length, string='Cruise Length')
    cruiseline_id = fields.Many2one('tourico.cruiseline', string='Cruise Line')
    
    ship_id = fields.Many2one('tourico.shiplist', string='Ship')
    port_id = fields.Many2one('tourico.embarkationports', string='Depart From')
    
    @api.multi
    def search_cruise(self):
        import logging
        logging.basicConfig(level=logging.INFO)
        logging.getLogger('suds.client').setLevel(logging.DEBUG)
        wsdl = "http://demo-cruisews.touricoholidays.com/CruiseServiceFlow.svc?wsdl"
        client = suds.client.Client(wsdl,headers={'Accept-Encoding': 'gzip'})
        service = client.service
        login_name, password = self.env['hotelapi.configuration'].get_turico_reservations_service()
        LoginName  = Element('ns0:UserName').setText(login_name)
        Password = Element('ns0:Password').setText(password)
        Culture = Element('ns0:Culture').setText('en_US')
        Version = Element('ns0:Version').setText('9')
        AuthenticationHeader = Element('ns0:LoginHeader') 
        AuthenticationHeader.attributes.append(Attribute('xmlns', 'http://schemas.tourico.com/webservices/authentication'))
        AuthenticationHeader.children = [LoginName, Password, Culture, Version]
        client.set_options(soapheaders=[AuthenticationHeader])
        
        print "client ========>> ", client,wsdl
        
        request = client.factory.create("ns2:SearchCruiseParams")
        #print "request =>> ", request
        
        request.CruiseLineID = self.cruiseline_id and self.cruiseline_id.cruiseline_Id or 0
        request.CruiseDestinationID = self.destination_id.turico_Id
        request.MarketCode = "US"
        request.Currency = "USD"
        request.DepartingFrom = self.from_date
        request.DepartingTo = self.to_date
        request.MinCruiseLength = 1
        request.MaxCruiseLength = 7#self.cruise_length
        request.PortID = 0#self.port_id and self.port_id.port_Id or 0
        request.ShipID = 0#self.ship_id and self.ship_id.cruiseline_id.id or 0
        #request.StateCode = 4
        request.IsSenior = False
        request.IsInterline = False
        request.IsMilitary = False
        request.IsPastPassenger = False
        print "1111111 request ==>> ", request
        response = client.service.Step_1_SearchCruises(request)
        print response,"<<==== response"
    
    
    