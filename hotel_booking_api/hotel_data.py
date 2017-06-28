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

class hotel_data(models.Model):
    _name = "hotel.data"
    
    name = fields.Char("Hotel Name")
    # IDs and codes of hotels from api
    turico_hotelId = fields.Char("Turico HotelId")
    hotelbeds_code = fields.Char("HotelBeds Code")
    giataId = fields.Char("GiataId")
    
    destn_code = fields.Char('Destination Code')
    destn_name = fields.Char('Destination Name')
    tourico_destn_id = fields.Char('Tourico Destination ID')
    
    chainId = fields.Char("chainId")
    chainName = fields.Char("chainName")
    
    
    # Attached images of hotel
    images = fields.Many2many('data.storage', string='Images')
    
    img_url = fields.Char("Img Url")
    image = fields.Binary("Image")
    last_used = fields.Date(string='Last Used')
    
    propertycodes_ids = fields.One2many('hotel.propertycodes', 'hotel_id', string='Property Codes')
    facility_ids = fields.One2many('hotel.facilities', 'hotel_id', string='Hotel Facilities')
    room_ids = fields.One2many('hotel.rooms', 'hotel_id', string='Hotel Rooms')
    tourico_image_ids = fields.One2many('tourico.images','hotel_id',string='Tourico Images')
    
    #General Information
    addressLine1 = fields.Char("Address Line1")
    addressLine2 = fields.Char("Address Line2")
    addressLine3 = fields.Char("Address Line3")
    addressLine4 = fields.Char("Address Line4")
    street = fields.Char("Street")
    cityName = fields.Char("City")
    country = fields.Char("Country")
    country_code = fields.Char("Country Code")
    zipcode = fields.Char("Zipcode")
    phone = fields.Char("Phone")
    fax = fields.Char("Fax")
    email = fields.Char("Email")
    url = fields.Char("URL")
    
    latitude = fields.Char("Latitude")
    longitude = fields.Char("Longitude")
    description = fields.Text("Description")
    
    checkin = fields.Char("Checkin Time")
    checkout = fields.Char("Checkout Time")
    
    @api.multi
    def get_hotel_details(self):
        hotelapi = self.env['hotelapi.configuration'].search([('type', '=', 'hotelbeds-hotels')])
        if not hotelapi:
            return True
        hotelapi = hotelapi[0]
        if self.hotelbeds_code:
            result = hotelapi.get_hotelbeds_hotels_details(self.hotelbeds_code)
            #print result.keys(),"!!!!!!!!!!!!!!!!!!!!!!!!!"
#         print "================Audit Data==================="
#         print result['auditData']
#         print "*********************************************"
            #print "<<==============Hotel Data=================>>"
            #print result['hotel']['facilities']
            #print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
            #print result['hotel'].keys(),"@@@@@@@@@@@@@@"
            hotel = result['hotel']
            print hotel,"hhhhhhhhhhhhhhhhhhhh",hotel.keys()
            print hotel['categoryGroup']
            self.phone = hotel.get('phones',False) and hotel['phones'] and hotel['phones'][0] and hotel['phones'][0]['phoneNumber']
            self.cityName = hotel.get('city',False) and hotel['city'] and hotel['city']['content']
            self.addressLine1 = hotel.get('address',False) and hotel['address'] and hotel['address']['content']
            self.url = hotel.get('web',False) and hotel['web']
            self.email = hotel.get('email',False) and hotel['email']
            self.zipcode = hotel.get('postalCode',False) and hotel['postalCode'] 
            self.name = hotel.get('name',False) and hotel['name']['content']
            self.destn_code = hotel.get('destination',False) and hotel['destination']['code']
            self.destn_name = hotel.get('destination',False) and hotel['destination']['name'] and hotel['destination']['name']['content']
            #for hotel in result['hotel']:
            if hotel.get('facilities',{}):
                self.facility_ids.unlink()
                for facility in hotel['facilities']:
                    vals = {'name' : facility['description']['content'],
                        'paid' : facility.get('indFee',False),
                        'code' : facility['facilityCode'],
                        'currency' : facility.get('currency',''),
                        'hotel_id': self.id
                        }
                    self.env['hotel.facilities'].create(vals)
            if hotel.get('description',{}):
                self.description = hotel['description']['content']
            if hotel.get('rooms',{}):
                self.room_ids.unlink()
                for room in hotel.get('rooms',{}):
                    room_vals = {'name' : room['description'],
                        'code' : room['roomCode'],
                        'hotel_id': self.id
                        }
                    room_id = self.env['hotel.rooms'].create(room_vals)
                    #print room,"rrrrrrrrrrrrrrr",room.keys()
                    if room.get('roomFacilities',[]):
                        for roomfacility in room.get('roomFacilities',[]):
                            facility_vals = {'name': roomfacility['description']['content'],
                                             'code': roomfacility['facilityCode'],
                                             'paid': roomfacility.get('indFee',False),
                                             'currency': roomfacility.get('currency',''),
                                             #'amount': roomfacility.get('currency',''),
                                             }
                            room_facility = self.env['room.facilities'].create(facility_vals)
                            room_id.write({'facility_ids' : [(4,room_facility.id)]})
            if hotel.get('images',[]):
                self.images.unlink()
                #print hotel.get('images',[]),")))))))))))))))))))))))))))))"
                image_data = hotel.get('images',[])
                image_url_list = []
                for image in image_data:
                    url = "http://photos.hotelbeds.com/giata/" + image['path']
                    image_url_list.append(url)
                img_vals = []
                #image_ret = False
                #try:
                for url in image_url_list:
                    storage = self.env['data.storage'].save_image("hotelbeds", url, "Hotel")
                    img_vals.append((4, storage.id))
                #imgvals = {
                 #       'hotelbeds_code' : self.hotelbeds_code,
                  #      'last_used' : datetime.now().strftime('%Y-%m-%d'),
                   #     'images' : img_vals,
                    #    'name' : self.name,
                        #'hotel_id': self.id
                     #   }
                self.images = img_vals
                    
        return True
    
    @api.multi
    def get_all_hotels(self):
        
        locations =  self.env['hotel.location'].search([('tourico_code', '!=', 'False')])
        total = len(locations)
        count = 0
        for location in locations:
            #print total, ' :: ', count, ' : ', location.tourico_name
            count = count + 1
            data = [{'RoomsInformation': [{'AdultNum': '2', 'ChildNum': '0', 'ChildAge': False}], 
                     'Destination': location.tourico_code, 
                     'CheckOut': '2017-04-2', 
                     'CheckIn': '2017-04-1'}]
            result = self.env['hotelapi.configuration'].get_hotels_tourico(data)
            
            
            if result:
                htotal = len(result.HotelList)
                hcount = 0
                for hotel_list in result.HotelList:
                    
                    hcount = hcount + 1
                    
                    for hotel in hotel_list[1]:
                        img_url = hotel._thumb
                        #print htotal, " : ", hcount, " url: -> ", img_url
                        image = self.env['hotel.data'].get_image(img_url, turico_hotelId=hotel._hotelId, name=hotel._name)
    
    
    
    @api.multi
    def get_image(self, url, turico_hotelId = False, hotelbeds_code=False, name=""):
        data = False
        type="general"
        if turico_hotelId:
            data = self.search([('turico_hotelId', '=', turico_hotelId)])
            type = "turico"
        if hotelbeds_code:
            data = self.search([('hotelbeds_code', '=', hotelbeds_code)])
            type = "hotelbeds"
        data = data and data[0] or False
        if not data or not data.images:
            if url:
                try:
                    storage = self.env['data.storage'].save_image(type, url, "Hotel")
                    vals = {
                        'turico_hotelId' : turico_hotelId,
                        'last_used' : datetime.now().strftime('%Y-%m-%d'),
                        'images' : [(4, storage.id)],
                        'name' : name
                        }
                    self.create(vals)
                    return storage.image
                except:
                    return False
            
            if hotelbeds_code:
                image_url_list = self.get_hotelbeds_images(hotelbeds_code)
                img_vals = []
                image_ret = False
                try:
                    for url in image_url_list:
                        storage = self.env['data.storage'].save_image(type, url, "Hotel")
                        img_vals.append((4, storage.id))
                        if not image_ret:
                            image_ret = storage.image
                        break
                            
                except:
                    pass
                vals = {
                        'hotelbeds_code' : hotelbeds_code,
                        'last_used' : datetime.now().strftime('%Y-%m-%d'),
                        'images' : img_vals,
                        'name' : name
                        }
                self.create(vals)
                return image_ret
                
            
            return False
        if data:
            data.last_used = datetime.now().strftime('%Y-%m-%d')
            return data.images[0].image
        return False
    
    @api.multi
    def get_hotelbeds_images(self, hotelbeds_code):
        image_url_list = []
        hotelapi = self.env['hotelapi.configuration'].search([('type', '=', 'hotelbeds-hotels')])
        result = hotelapi[0].get_hotelbeds_hotel_content(hotelbeds_code)
        for image in result['hotel'].get('images', []):
            url = "http://photos.hotelbeds.com/giata/" + image['path']
            image_url_list.append(url)
        return image_url_list
    
    @api.multi
    def get_hotelbeds_facilities(self, hotelbeds_code):
        hotelapi = self.env['hotelapi.configuration'].search([('type', '=', 'hotelbeds-hotels')])
        result = hotelapi[0].get_hotelbeds_hotel_content(hotelbeds_code)
        return result['hotel'].get('facilities', [])
    
    
    @api.multi
    def import_giata(self):
        url = "http://multicodes.giatamedia.com/webservice/rest/1.0/properties/EG"
        req = urllib2.Request(url)
        base64string = base64.encodestring('%s:%s' % ('se|spire.bh', 'oFVm4bRQ')).replace('\n', '')
        req.add_header("Authorization", "Basic %s" % base64string)   
        d =  urllib2.urlopen(req)
        data = d.read()
        tree = ET.ElementTree(ET.fromstring(data))
        root = tree.getroot()
        
        count = 1
        for root_child in root:
            #print root_child.attrib['giataId']
            
            link = root_child.attrib['{http://www.w3.org/1999/xlink}href']
            req = urllib2.Request(link)
            base64string = base64.encodestring('%s:%s' % ('se|spire.bh', 'oFVm4bRQ')).replace('\n', '')
            req.add_header("Authorization", "Basic %s" % base64string)   
            d =  urllib2.urlopen(req)
            data = d.read()
            hotel_tree = ET.ElementTree(ET.fromstring(data))
            hotel_root = hotel_tree.getroot()
            for child in hotel_root:
                #print "\n\n"
                #print root_child.attrib['giataId'], child.find('name').text, " :: ",child.find('country').text, " :: ", child.find('city').text
                
                #Getting PRoperty Codes
                propertyCodes =[]
                if child.find('propertyCodes'):
                    for provider in child.find('propertyCodes'):
                        #print "\n\n"
                        #print "====>>> ", provider.attrib
                        for code in provider.findall('code'):
                            field_map = {
                                'Hotel Code' : 'hotel_code',
                                'Country Code' : 'country_code',
                                'City Code' : 'city_code' }
                            pcode_vals = {'providerCode' : provider.attrib['providerCode'],
                                          'providerType' : provider.attrib['providerType']}
                            for value in code.findall('value'):
                                #print ":: ->", value.text, value.attrib
                                if value.attrib:
                                    attrib_name = value.attrib['name']
                                    pcode_vals[field_map.get(attrib_name, attrib_name)] = value.text
                                else:
                                    pcode_vals['value'] = value.text
                            #print "pcode_vals ===>> ", pcode_vals
                            propertyCodes.append((0, 0, pcode_vals))    
                
                hotel_val = {
                    'name' : child.find('name').text,
                    'giataId' : root_child.attrib['giataId'],
                    'propertycodes_ids' : propertyCodes
                    }
                
                #Getting Addresses
                if child.find('addresses'):
                    for addresses in child.find('addresses', []):
                        for addressLine in addresses.findall('addressLine', []):
                            #print "addressLine -->> ", addressLine.attrib, " :: ", addressLine.text
                            hotel_val['addressLine' + addressLine.attrib.get('addressLineNumber', '1')] = addressLine.text
                        for street in addresses.findall('street', []):
                            hotel_val['street'] = street.text
                        for cityName in addresses.findall('cityName', []):
                            hotel_val['cityName'] = cityName.text
                        for country in addresses.findall('country', []):
                            hotel_val['country'] = country.text
                        
                #Getting Phone Numbers
                if child.find('phones'):
                    for phones in child.find('phones', []):
                        if phones.attrib.get('tech') == "voice":
                            hotel_val['phone'] = phones.text
                        if phones.attrib.get('tech') == "fax":
                            hotel_val['fax'] = phones.text
                        
                
                #Getting Email
                if child.find('emails'):
                    for email in child.find('emails', []):
                        hotel_val['email'] = email.text
                
                #Getting URL
                if child.find('urls'):
                    for url in child.find('urls', []):
                        hotel_val['url'] = url.text
                    
                #Getting Email
                if child.find('geoCodes'):
                    for geoCodes in child.find('geoCodes', []):
                        #print "=ddddd>> ", geoCodes.getchildren()
                        
                        for latitude in geoCodes.findall('latitude', []):
                            hotel_val['latitude'] = latitude.text
                        for longitude in geoCodes.findall('longitude', []):
                            hotel_val['longitude'] = longitude.text
                        
                #Getting Chain Details
                if child.find('chains'):
                    for chain in child.find('chains', []):
                        hotel_val['chainId'] = chain.attrib.get('chainId', '')
                        hotel_val['chainName'] = chain.attrib.get('chainName', '')
                    
                    
                #print "hotel_val ==>> ", hotel_val            
                
                hotel = self.search([('giataId', '=', root_child.attrib['giataId'])])
                if hotel:
                    hotel[0].write(hotel_val)
                else:
                    self.create(hotel_val)
                
            #print "\n\n\n\n"
            #print "count ===>>> ", count
            count = count + 1
        
        
class hotel_propertycodes(models.Model):
    _name = "hotel.propertycodes"
    
    providerCode = fields.Char("Provider Code") 
    providerType = fields.Char("Provider Type")  
    value = fields.Char("Value")  
    
    country_code = fields.Char("Country Code")
    city_code = fields.Char("City Code")
    hotel_code = fields.Char("Hotel Code")   
    
    hotel_id = fields.Many2one('hotel.data', string='Hotel')
    
class HotelFacilities(models.Model):
    _name = "hotel.facilities"
    
    name = fields.Char("Facility Name")
    code = fields.Char("Facility Code")
    paid = fields.Boolean("Paid Facility")
    amount = fields.Float("Facility Amount")  
    currency = fields.Char("Currency")  
    hotel_id = fields.Many2one('hotel.data', string='Hotel')
    
class HotelRooms(models.Model):
    _name = "hotel.rooms"
    
    name = fields.Char("Room Name")
    code = fields.Char("Room Code")
    description = fields.Char("Room Description")
    hotel_id = fields.Many2one('hotel.data', string='Hotel')
    #facility_ids = fields.One2many('room.facilities', 'room_id', string='Room Facilities')
    facility_ids = fields.Many2many('room.facilities', string='Room Facilities')
    
class RoomFacilities(models.Model):
    _name = "room.facilities"
    
    name = fields.Char("Facility Name")
    code = fields.Char("Facility Code")
    paid = fields.Boolean("Paid Facility")
    amount = fields.Float("Facility Amount")  
    currency = fields.Char("Currency")  
    room_id = fields.Many2one('hotel.rooms', string='Room')
    
class TouricoImages(models.Model):
    _name = "tourico.images"
    
    name = fields.Char("Path")
    type = fields.Char("Type")
    hotel_id = fields.Many2one('hotel.data', string='Hotel')
    
class AllHotelFacilities(models.Model):
    _name = "all.hotel.facilities"
    
    name = fields.Char("Facility Name")
    code = fields.Char("Facility Code")
    groupcode = fields.Char("Facility GroupCode")
    typologycode = fields.Char("Facility TypologyCode")
    
    @api.multi
    def get_all_hotel_facilities(self):
        hotelapi = self.env['hotelapi.configuration'].search([('type', '=', 'hotelbeds-hotels')])
        result = hotelapi[0].get_hotelbeds_hotel_all_facilities()
        #print  result.get('facilities', []),"XXXXXXXXXXXXXXX"
        for facility in result.get('facilities', []):
            if 'description' in facility:
                #print facility,"fffffffffffffff"
                vals={'name': facility['description']['content'],
                      'code': facility['code'],
                      'groupcode': facility['facilityGroupCode'],
                      'typologycode': facility['facilityTypologyCode'],
                      }
                self.create(vals)
    
    
    
    
    
    
    
        
        
    
    
    