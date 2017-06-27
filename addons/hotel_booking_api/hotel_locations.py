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
import time, hashlib
import requests
import json
import ast
import suds.client
from suds.sax.element import Element
from suds.sax.attribute import Attribute

class tourico_embarkationports(models.Model):
    _name = "tourico.embarkationports"
    rec_name = 'name'
    
    name = fields.Char(string='Name')
    port_Id = fields.Integer(string='Port ID')
    destination_id = fields.Many2one('cruisedestinations.tourico', string='Cruise Destination')
    
    @api.multi
    def get_embarkationports_tourico(self):
        wsdl = "http://demo-cruisews.touricoholidays.com/CruiseServiceFlow.svc?wsdl"
        client = suds.client.Client(wsdl,headers={'Accept-Encoding': 'gzip'})
        service = client.service
        login_name, password = self.env['hotelapi.configuration'].get_turico_reservations_service()
        LoginName  = Element('ns0:UserName').setText(login_name)
        Password = Element('ns0:Password').setText(password)
        Culture = Element('ns0:Culture').setText('en_US')
        Version = Element('ns0:Version').setText('7.123')
        AuthenticationHeader = Element('ns0:LoginHeader') 
        AuthenticationHeader.attributes.append(Attribute('xmlns', 'http://schemas.tourico.com/webservices/authentication'))
        AuthenticationHeader.children = [LoginName, Password, Culture, Version]
        client.set_options(soapheaders=[AuthenticationHeader])
        result = client.service.GetEmbarkationPortsByDestination()
        #print "result ==>> ", result
        for Destination in result.Destination:
            #print "Destination ==>> ", Destination._DestinationId
            destination = self.env['cruisedestinations.tourico'].search([('turico_Id', '=', Destination._DestinationId)])
            if destination:
                for Ports in Destination.Ports.Port:
                    vals = { 'name' : Ports._Name,
                             'port_Id' : Ports._Id,
                             'destination_id' : destination[0].id }
                    #print "vals ==>> ", vals
                    self.create(vals)
                

class tourico_cruiseline(models.Model):
    _name = "tourico.cruiseline"
    rec_name = 'name'

    name = fields.Char(string='Name')
    cruiseline_Id = fields.Integer(string='Cruise Line ID')
    shiplist_ids = fields.One2many('tourico.shiplist', 'cruiseline_id', string='Ship List')
    
    @api.multi
    def get_cruiseline_tourico(self):
        wsdl = "http://demo-cruisews.touricoholidays.com/CruiseServiceFlow.svc?wsdl"
        client = suds.client.Client(wsdl,headers={'Accept-Encoding': 'gzip'})
        service = client.service
        login_name, password = self.env['hotelapi.configuration'].get_turico_reservations_service()
        LoginName  = Element('ns0:UserName').setText(login_name)
        Password = Element('ns0:Password').setText(password)
        Culture = Element('ns0:Culture').setText('en_US')
        Version = Element('ns0:Version').setText('7.123')
        AuthenticationHeader = Element('ns0:LoginHeader') 
        AuthenticationHeader.attributes.append(Attribute('xmlns', 'http://schemas.tourico.com/webservices/authentication'))
        AuthenticationHeader.children = [LoginName, Password, Culture, Version]
        client.set_options(soapheaders=[AuthenticationHeader])
        result = client.service.GetCruiseLines()
        for CruiseLine in result.CruiseLine:
            shiplist = []
            for ShipList in CruiseLine.ShipList.Ship:
                ShipList_vals = {
                        'name' : ShipList._Name,
                        'ship_id' : int(ShipList._ID) }
                shiplist.append((0,0,ShipList_vals))
            vals = {
                    'name' : CruiseLine._CruiseLineName,
                    'cruiseline_Id' : CruiseLine._CruiseLineId,
                    'shiplist_ids' : shiplist }
            self.create(vals)
    
class tourico_shiplist(models.Model):
    _name = "tourico.shiplist"
    rec_name = 'name'

    name = fields.Char(string='Name')
    ship_id = fields.Integer(string='Ship ID')
    cruiseline_id = fields.Many2one('tourico.cruiseline', string='Cruise Line')


class cruisedestinations_tourico(models.Model):
    _name = "cruisedestinations.tourico"
    rec_name = 'name, country'

    parent_name = fields.Char(string='Name')
    parent_id = fields.Integer(string='Parent Id')
    turico_Id = fields.Integer(string='Turico Id')
    name = fields.Char(string='Name')
    image_ids = fields.Many2many('data.storage', string='Images')
    
    @api.multi
    def get_getcruisedestinations_tourico(self):
        wsdl = "http://demo-cruisews.touricoholidays.com/CruiseServiceFlow.svc?wsdl"
        client = suds.client.Client(wsdl,headers={'Accept-Encoding': 'gzip'})
        service = client.service
        login_name, password = self.env['hotelapi.configuration'].get_turico_reservations_service()
        LoginName  = Element('ns0:UserName').setText(login_name)
        Password = Element('ns0:Password').setText(password)
        Culture = Element('ns0:Culture').setText('en_US')
        Version = Element('ns0:Version').setText('7.123')
        AuthenticationHeader = Element('ns0:LoginHeader') 
        AuthenticationHeader.attributes.append(Attribute('xmlns', 'http://schemas.tourico.com/webservices/authentication'))
        AuthenticationHeader.children = [LoginName, Password, Culture, Version]
        client.set_options(soapheaders=[AuthenticationHeader])
        result = service.GetCruiseDestinations()
        #print "result ==>> ", result
        for cruisedestination in result.CruiseDestination:
            list_storage = []
            if cruisedestination.Images:
                for image in cruisedestination.Images.Image:
                    try:
                        storage = self.env['data.storage'].save_image(cruisedestination._Id, image._BigImg, type="cruisedestinations")
                        list_storage.append((4, storage.id))
                    except:
                        print "image._BigImg ===>> "
            vals = {
                    'parent_name' : cruisedestination._ParentName,
                    'parent_id' : cruisedestination._ParentId,
                    'turico_Id' : cruisedestination._Id,
                    'name' : cruisedestination._Name,
                    'image_ids' : list_storage }
            destination = self.search([('turico_Id', '=', cruisedestination._Id)])
            if destination:
                destination[0].write(vals)
            else:
                self.create(vals)
            


class hotel_location(models.Model):
    _name = "hotel.location"
    rec_name = 'name, country'
    
    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    isoCode = fields.Char(string='isoCode')
    country = fields.Many2one('location.country', string='Country')
    
    tourico_name = fields.Char(string='Tourico Name')
    tourico_code = fields.Char(string='Tourico Code')
    tourico_country = fields.Many2one('location.country', string='Tourico Country')
    tourico_destinationId = fields.Integer(string='Tourico DestinationId')
    
    @api.multi
    def get_location_tourico(self):
        res = self.env['hotelapi.configuration'].get_location_tourico()
        for data in res:
            location_code = data['code'].strip()
            location_name = data['name'].strip()
            tourico_destinationId = data['tourico_destinationId']
            location = self.search(['|',('code', '=', location_code), ('tourico_code', '=', location_code)])
            location = location and location[0]
            if location:
                location_country = location.country and location.country.id or \
                        location.tourico_country and location.tourico_country.id
            else:
                country_vals = {'name' : data['country'].upper(), 
                                'code': '',
                                'isoCode': ''}
                country = self.env['location.country'].add_country(country_vals)
                location_country = country.id
                location = self.search([('name', '=', location_name), ('country', '=', location_country)])
                location = location and location[0]
            vals = {
                'tourico_name' : location_name,
                'tourico_code' : location_code,
                'tourico_country' : location_country,
                'tourico_destinationId' : tourico_destinationId
                   }    
            if location:
                location.write(vals)
            else:
                self.create(vals)
        return res
    
    @api.multi
    def get_location(self):
        hotelapi = self.env['hotelapi.configuration'].search([('type', '=', 'hotelbeds-hotels')])
        if not hotelapi:
            return True
        hotelapi = hotelapi[0]
        result = hotelapi.get_country()
        for country in result['countries']:
          self.env['location.country'].add_country(country)
        result = hotelapi.get_location()
        for destinations in result:
            if destinations and destinations.get('name',False):
                #print destinations,"DDDDDDDDDDDDDDDDDDD"
                country = self.env['location.country'].search([('code', '=', destinations['countryCode'])])
                country = country and country[0]
                vals = {
                    'country' : country.id,
                    'code' : destinations['code'],    
                    'name' : destinations['name']['content'],
                    'isoCode' : destinations['isoCode'] }
                found = self.search([('code', '=', vals['code'])])
                if found:
                    found[0].write(vals)
                else:
                    print vals,"VVVVVVVVVVVVVVVVVVVV"
                    self.create(vals)
        return True
    
    @api.multi
    def get_hotels(self):
       hotelapi = self.env['hotelapi.configuration'].search([('type', '=', 'hotelbeds-hotels')])
       if not hotelapi:
            return True
       hotelapi = hotelapi[0]
       result = hotelapi.get_hotelbeds_hotels_data(self.code) 
       for res in result['hotels']:
           #print res,"RRRRRRRRRRRRR"
           hotelbed_hotel = self.env['hotel.data'].search([('hotelbeds_code','=',res['code'])])
           if  not hotelbed_hotel:
               img_vals = []
               for image in res.get('images',[]):
                   storage = self.env['data.storage'].save_image('hotelbeds', image['path'], "Hotel")
                   img_vals.append((4, storage.id))
               hotel_vals = {'hotelbeds_code': res['code'],
                           'name': res['name']['content'],
                           'destn_code': res['destinationCode'],
                           'images':img_vals,
                           
                                   }
               
               hotel = self.env['hotel.data'].create(hotel_vals)
               hotel.get_hotel_details()#Import each hotel data
               print "Creating New hotel>>>",hotel.name,hotel.id
           else:
              hotelbed_hotel.get_hotel_details()
              print "Updating Existing hotel>>>",hotelbed_hotel.name
               
       return True
        
    @api.multi
    def name_get(self):
        result = []
        for location in self:
            result.append((location.id, "%s, %s, %s" % (location.name, location.code, location.country.name)))
        return result
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = ['|', '|', ('name', operator, name), ('country.name', operator, name), ('code', operator, name)]
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()
        
        
        
class location_country(models.Model):     
    
    _name = "location.country"
    
    name = fields.Char(string='Name')
    code = fields.Char(string='Code')   
    isoCode = fields.Char(string='isoCode')   
    
    @api.multi
    def add_country(self, vals):
        if 'description' in vals:
            name = vals['description']['content'].strip()
        else:
             name = vals['name'].strip()
        country = self.search([('name', '=', name)])
        vals = {'name' : name, 
                'code': vals['code'].strip(),
                'isoCode': vals['isoCode'].strip()}
        if country:
            return country[0]
        else:
            country = self.create(vals)  
        return country    
    
   
    
