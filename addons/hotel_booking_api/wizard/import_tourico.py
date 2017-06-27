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

import suds.client
from suds.sax.element import Element
from suds.sax.attribute import Attribute

import os
import csv

class ImportTourico(models.TransientModel):
    _name = "import.tourico"
    _description = "Import Tourico Data"
    
    @api.multi
    def do_import_destn_only(self):
        res = [] 
        wsdl = "http://destservices.touricoholidays.com/DestinationsService.svc?wsdl"
        client = suds.client.Client(wsdl,headers={'Accept-Encoding': 'gzip'})
        service = client.service
         
        login_name, password ,dest_update_date,act_update_date = self.env['hotelapi.configuration'].get_turico_destinations_service()
        username  = Element('username').setText(login_name)
        password = Element('password').setText(password)
        culture = Element('culture').setText('en_US')
        version = Element('version').setText('7.123')
        AuthenticationHeader = Element('LoginHeader') 
        AuthenticationHeader.attributes.append(Attribute('xmlns', 'http://schemas.tourico.com/webservices/authentication'))
        AuthenticationHeader.children = [username, password, culture, version]
        client.set_options(soapheaders=[AuthenticationHeader])
        destination = client.factory.create('ns1:Destination')
        destination.StatusDate = dest_update_date
        destination.Continent = ''
         
        destinations = client.service.GetDestination(destination)
         
        for continent in destinations.Continent:
                for country in continent.Country:
                    for state in country.State:
                        for city in state.City:
                            res.append({
                                    'name' : city._name,
                                    'code' : city._destinationCode,
                                    'country' : country._name,
                                    'tourico_destinationId' : city._destinationId,
                                        })
        for destn in res:
            location_code = destn['code'].strip()
            location_name = destn['name'].strip()
            tourico_destinationId = destn['tourico_destinationId']
            location = self.env['hotel.location'].search([('tourico_destinationId', '=', tourico_destinationId)])
            location = location and location[0]
            if location:
                  location_country = location.country and location.country.id or \
                          location.tourico_country and location.tourico_country.id
            else:
                country_vals = {'name' : destn['country'].upper(), 
                                'code': '',
                                'isoCode': ''}
                country = self.env['location.country'].add_country(country_vals)
                location_country = country.id
                location = self.env['hotel.location'].search([('name', '=', location_name), ('country', '=', location_country)])
                location = location and location[0]
            vals = {
            'tourico_name' : location_name,
            'tourico_code' : location_code,
            'tourico_country' : location_country,
            'tourico_destinationId' : tourico_destinationId
               }    
            if location:
                #print "Updating Location>>",location_name
                location.write(vals)
            else:
                #print "Creating Location>>",location_name
                self.env['hotel.location'].create(vals)               
         
        return True
    
    @api.multi
    def do_import_destn_hotel_details(self):
        res = [] 
        wsdl = "http://destservices.touricoholidays.com/DestinationsService.svc?wsdl"
        client = suds.client.Client(wsdl,headers={'Accept-Encoding': 'gzip'})
        service = client.service
        
        hotel_wsdl = "http://demo-hotelws.touricoholidays.com/hotelflow.svc?wsdl"
        hotel_client = suds.client.Client(hotel_wsdl,headers={'Accept-Encoding': 'gzip'})
        hotel_service = hotel_client.service
        hlogin_name, hpassword = self.env['hotelapi.configuration'].get_turico_hotelflow()
        hLoginName  = Element('LoginName').setText(hlogin_name)
        hPassword = Element('Password').setText(hpassword)
        hCulture = Element('Culture').setText('en_US')
        hVersion = Element('Version').setText('7.123')
        hAuthenticationHeader = Element('AuthenticationHeader') 
        hAuthenticationHeader.attributes.append(Attribute('xmlns', 'http://schemas.tourico.com/webservices/authentication'))
        hAuthenticationHeader.children = [hLoginName, hPassword, hCulture, hVersion]
        hotel_client.set_options(soapheaders=[hAuthenticationHeader])
        
        ArrayHotel = hotel_client.factory.create('ns7:HotelIds')
        
        login_name, password ,dest_update_date,act_update_date = self.env['hotelapi.configuration'].get_turico_destinations_service()
        username  = Element('username').setText(login_name)
        password = Element('password').setText(password)
        culture = Element('culture').setText('en_US')
        version = Element('version').setText('7.123')
        AuthenticationHeader = Element('LoginHeader') 
        AuthenticationHeader.attributes.append(Attribute('xmlns', 'http://schemas.tourico.com/webservices/authentication'))
        AuthenticationHeader.children = [username, password, culture, version]
        client.set_options(soapheaders=[AuthenticationHeader])
        destination = client.factory.create('ns1:Destination')
        destination.StatusDate = dest_update_date
        destination.Continent = ''
        #destination.Country = ''
        #destination.State = ''
        #destination.City = ''
        import_error=''
        try:
            r = client.service.GetDestination(destination)
            
            for continent in r.Continent:
                for country in continent.Country:
                    for state in country.State:
                        for city in state.City:
                            #print continent._name, country._name, city._name
                            res.append({
                                    'name' : city._name,
                                    'code' : city._destinationCode,
                                    'country' : country._name,
                                    'tourico_destinationId' : city._destinationId,
                                        })
            for data in res:
                location_code = data['code'].strip()
                location_name = data['name'].strip()
                tourico_destinationId = data['tourico_destinationId']
                #location = self.env['hotel.location'].search(['|',('code', '=', location_code), ('tourico_code', '=', location_code)])
                location = self.env['hotel.location'].search([('tourico_destinationId', '=', tourico_destinationId)])
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
                    location = self.env['hotel.location'].search([('name', '=', location_name), ('country', '=', location_country)])
                    location = location and location[0]
                vals = {
                    'tourico_name' : location_name,
                    'tourico_code' : location_code,
                    'tourico_country' : location_country,
                    'tourico_destinationId' : tourico_destinationId
                       }    
                if location:
                    #print "Updating Location>>",location_name
                    location.write(vals)
                else:
                    #print "Creating Location>>",location_name
                    self.env['hotel.location'].create(vals)
            hotels = client.service.GetHotelsByDestination(destination)
            
            for cont in hotels.Continent:
                for country in cont.Country:
                    for state in country.State:
                        city_hotels=[]
                        for city in state.City:
                            for city_hotel in city.Hotels:
                                #print city_hotel[1][0], type( city_hotel[1][0])
                                city_hotel_data = city_hotel[1][0]
                                #print city_hotel_data._hotelName,"cccccc"
                                city_hotels.append({'hotelName':city_hotel_data._hotelName.encode('ascii', 'ignore'),
                                                    'hotelId':city_hotel_data._hotelId,
                                                     '_stars': city_hotel_data._stars,
                                                     '_destinationCode': city_hotel_data._destinationCode,
                                                     '_city':city_hotel_data._city,
                                                     '_countryCode':city_hotel_data._countryCode
                                                    })
                            #city_loc_hotels = []
                            if hasattr(city, 'CityLocation'):
                                for city_loc in city.CityLocation:
                                    for loc_hotel in city_loc.Hotels:
                                        loc_hotel_data = loc_hotel[1][0]
                                        #print loc_hotel_data._hotelName,"lllllllll"
                                        hotel_id = loc_hotel_data._hotelId
                                        city_hotels.append({'hotelName':loc_hotel_data._hotelName.encode('ascii', 'ignore'),
                                                        'hotelId':loc_hotel_data._hotelId,
                                                         '_stars': loc_hotel_data._stars,
                                                         '_destinationCode': loc_hotel_data._destinationCode,
                                                         '_city':loc_hotel_data._city,
                                                         '_countryCode':loc_hotel_data._countryCode
                                                        })
                        #all_hotels = list(set(city_hotels+city_loc_hotels))
                        #print city_hotels,len(city_hotels)
                        for chotel in city_hotels:
                            #print chotel['hotelId'],"cccccccccccccccc"
                            hotelId = hotel_client.factory.create('ns7:HotelID')
                            hotelId._id = chotel['hotelId']
                            ArrayHotel.HotelID =hotelId
                            hotel_detail = hotel_service.GetHotelDetailsV3(ArrayHotel)
                            #print hotel_detail.TWS_HotelDetailsV3.Hotel,"dddddddddddddddd",type(hotel_detail.TWS_HotelDetailsV3.Hotel.Descriptions)
                            
                            
                            hotel_data = self.env['hotel.data'].search([('turico_hotelId', '=', chotel['hotelId'])])
                            if hasattr(hotel_detail, 'TWS_HotelDetailsV3') and hasattr(hotel_detail.TWS_HotelDetailsV3, 'Hotel'):
                                #print hotel_detail.TWS_HotelDetailsV3.Hotel,"NNNNNNNNNNNNNN"
                                hotel_detail_data = hotel_detail.TWS_HotelDetailsV3.Hotel
                                #print hotel_detail_data.__dict__.keys(),"kkkkkkkkkkkkkkkk"
                                if hasattr(hotel_detail_data, 'Media') and hasattr(hotel_detail_data.Media, 'Images'):
                                    image_vals=[]
                                    #print hotel_detail_data.Media,"<<<<<<<<<<<<Media"
                                    for image in hotel_detail_data.Media.Images.Image:
                                        #print image,"IIIIIIIIIIIIIIIIIIIIIIIIIIII"
                                        image_vals.append({'name':hasattr(image, '_path') and image._path,
                                                           'type':hasattr(image, '_type') and image._type,})
                                    #print images,"IIIIIIIIIIIIIIIIIIIIII"
                                #dsfsdfg
                                vals = {'name': hotel_detail.TWS_HotelDetailsV3.Hotel._name.encode('ascii', 'ignore'),
                                        'checkin': hasattr(hotel_detail_data, '_checkInTime') and hotel_detail_data._checkInTime or '',
                                        'checkout': hasattr(hotel_detail_data, '_checkOutTime') and hotel_detail_data._checkOutTime or '',
                                        'tourico_destn_id': hasattr(hotel_detail.TWS_HotelDetailsV3.Hotel.Location,'_destinationId') and hotel_detail.TWS_HotelDetailsV3.Hotel.Location._destinationId or '',
                                        'country': hasattr(hotel_detail.TWS_HotelDetailsV3.Hotel.Location,'_country') and hotel_detail.TWS_HotelDetailsV3.Hotel.Location._country or '',
                                        'cityName': hasattr(hotel_detail.TWS_HotelDetailsV3.Hotel.Location,'_city') and hotel_detail.TWS_HotelDetailsV3.Hotel.Location._city or '',
                                        'latitude': hasattr(hotel_detail_data, '_latitude') and hotel_detail_data._latitude or '',
                                        'longitude': hasattr(hotel_detail_data, '_longitude') and hotel_detail_data._longitude or '',
                                        'addressLine1': hasattr(hotel_detail.TWS_HotelDetailsV3.Hotel.Location,'_address') and hotel_detail.TWS_HotelDetailsV3.Hotel.Location._address or '',
                                        'description': hasattr(hotel_detail.TWS_HotelDetailsV3.Hotel.Descriptions.LongDescription,'FreeTextLongDescription') and hotel_detail.TWS_HotelDetailsV3.Hotel.Descriptions.LongDescription.FreeTextLongDescription or '',
                                        'tourico_image_ids': map(lambda img: (0,0,img), image_vals)
                                                      }
                                if hotel_data:
                                    #print "Updating Hotel>>  ",hotel_detail.TWS_HotelDetailsV3.Hotel._name.encode('ascii', 'ignore'),'--',hasattr(hotel_detail.TWS_HotelDetailsV3.Hotel.Location,'_city') and hotel_detail.TWS_HotelDetailsV3.Hotel.Location._city
                                    hotel_data.tourico_image_ids.unlink()
                                    hotel_data.write(vals)
                                else:
                                    #print "Creating Hotel>>  ",hotel_detail.TWS_HotelDetailsV3.Hotel._name.encode('ascii', 'ignore'),'--',hasattr(hotel_detail.TWS_HotelDetailsV3.Hotel.Location,'_city') and hotel_detail.TWS_HotelDetailsV3.Hotel.Location._city
                                    vals.update({'turico_hotelId':hotel_detail.TWS_HotelDetailsV3.Hotel._hotelID})
                                    hotel_data.create(vals)
                    self.env.cr.commit()
                                        
            config = self.env['hotelapi.configuration'].search([('type', '=', 'turico-destinations-service')])
            config.dest_update_date = datetime.now()
        except suds.WebFault as detail:
            #print import_error,"---------------",detail
            import_error ="%s, %s" % (import_error, detail)
                
        return True
    
    
    
    @api.multi
    def do_import_hotels(self):
        return True
    
    @api.multi
    def do_import_act(self):
        res = [] 
        wsdl = "http://destservices.touricoholidays.com/DestinationsService.svc?wsdl"
        client = suds.client.Client(wsdl,headers={'Accept-Encoding': 'gzip'})
        service = client.service
        login_name, password ,dest_update_date,act_update_date = self.env['hotelapi.configuration'].get_turico_destinations_service()
        username  = Element('username').setText(login_name)
        password = Element('password').setText(password)
        culture = Element('culture').setText('en_US')
        version = Element('version').setText('7.123')
        AuthenticationHeader = Element('LoginHeader') 
        AuthenticationHeader.attributes.append(Attribute('xmlns', 'http://schemas.tourico.com/webservices/authentication'))
        AuthenticationHeader.children = [username, password, culture, version]
        client.set_options(soapheaders=[AuthenticationHeader])
        print client,"ccccccccccccccc"
        destination = client.factory.create('ns1:Destination')
        destination.StatusDate = act_update_date
        destination.Continent = ''
        #destination.Country = ''
        #destination.City = ''
        #r = client.service.GetDestination(destination)
        #print r
        activities = client.service.GetActivitiesByDestination(destination)
        #print activities,"AAAAAAAAAAAAAAAAAAA"
        activity_list=[]
        for cont in activities.Continent:
                for country in cont.Country:
                    for state in country.State:
                        for city in state.City:
                            for act in city.Activities:
                                activity=act[1]
                                #print act,"aAAAAAAAAAAAAAAAAA" 
                                activity_list.extend(activity)
        print len(activity_list),";lllllllllll"
        for activity in activity_list:
            act_data = self.env['activity.data'].search([('tourico_code', '=', activity._activityId)])
            vals = {'name': activity._activityName,
                    'destn_code': activity._destinationCode,
                    'tourico_destn_id': activity._destinationId,
                    'cityName': activity._city,
                    'country': activity._countryCode,
                    'stars': activity. _stars,
                    'address': activity._address,
                    }
            if act_data:
                act_data.write(vals)
            else:
                vals.update({'tourico_code': activity._activityId})
                act_data.create(vals)
        config = self.env['hotelapi.configuration'].search([('type', '=', 'turico-destinations-service')])
        config.act_update_date = datetime.now()
        
    @api.multi
    def do_import_olympus_hoteldata(self):
        import logging
        logging.basicConfig(level=logging.INFO)
        logging.getLogger('suds.client').setLevel(logging.DEBUG)
        res = [] 
        wsdl = "http://destservices.touricoholidays.com/DestinationsService.svc?wsdl"
        client = suds.client.Client(wsdl,headers={'Accept-Encoding': 'gzip'})
        service = client.service
        print client,"cccccccccccccc"
        #ladsjf
        config = self.env['hotelapi.configuration'].search([('type', '=', 'turico-destinations-service')])
        hotel_update_date = fields.Datetime.from_string(config.hotel_update_date).isoformat('T')
        login_name = config.username 
        password = config.password
        username  = Element('username').setText(login_name)
        password = Element('password').setText(password)
        culture = Element('culture').setText('en_US')
        version = Element('version').setText('7.123')
        AuthenticationHeader = Element('LoginHeader') 
        AuthenticationHeader.attributes.append(Attribute('xmlns', 'http://schemas.tourico.com/webservices/authentication'))
        AuthenticationHeader.children = [username, password, culture, version]
        client.set_options(soapheaders=[AuthenticationHeader])
        destination = client.factory.create('ns1:Destination')
        destination.StatusDate = hotel_update_date
        destination.Continent = '' 
        hotels = client.service.GetHotelsByDestination(destination) 
        config.hotel_update_date = datetime.now()
        hotel_list = [] 
        print "hhhhhhhhhhh",client.last_sent()
        #print "jjjjjjjjjjjjj",client.last_received()
        for cont in hotels.Continent:
            for country in cont.Country:
                for state in country.State:
                    city_hotels=[]
                    for city in state.City:
                        for city_hotel in city.Hotels:
                            city_hotel_data = city_hotel[1]
                            hotel_list.extend(city_hotel_data)
                        if hasattr(city, 'CityLocation'):
                            for city_loc in city.CityLocation:
                                for loc_hotel in city_loc.Hotels:
                                    loc_hotel_data = loc_hotel[1]
                                    hotel_list.extend(loc_hotel_data)
        
        all_hotels = list(set(hotel_list))
        print all_hotels,"*******************"
        for hotel in all_hotels:
            
            vals = {'name': hasattr(hotel,'_hotelName') and hotel._hotelName,#.encode('ascii', 'ignore'),
                    'country_code': hasattr(hotel,'_countryCode') and hotel._countryCode,#.encode('ascii', 'ignore'),
                    'cityName': hasattr(hotel,'_city') and hotel._city,#.encode('ascii', 'ignore'),
                    'addressLine1':hasattr(hotel,'_address') and hotel._address,#.encode('ascii', 'ignore'),
                    'latitude': hasattr(hotel,'_hotelLatitude') and hotel._hotelLatitude,#.encode('ascii', 'ignore'),
                    'longitude': hasattr(hotel,'_hotelLongitude') and hotel._hotelLongitude,#.encode('ascii', 'ignore'),
                    'zipcode': hasattr(hotel,'_zip') and hotel._zip#.encode('ascii', 'ignore')
                    } 
            hotel_data = self.env['hotel.data'].search([('turico_hotelId', '=', hotel._hotelId)])
            if hotel_data:
                hotel_data.write(vals)
                hotel_id = hotel_data.id
            else:
                vals.update({'turico_hotelId': hotel._hotelId,})
                hotel_id = hotel_data.create(vals)
#         path = os.path.dirname(os.path.abspath(__file__))
#         csv_path = "hotel_data.csv"
#         fullpath = os.path.join(path, csv_path)
#         with open(fullpath, "w") as csvfile:
#             fieldnames = ["Client ID", "Tourico Id",'Name','Country Code','State Code','City','Address','Phone','Fax','Latitude','Longitude','ZipCode',"Active / Inactive on the client's side"]
#             writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
# 
#             writer.writeheader()
#             hotel_data = self.env['hotel.data'].search([('turico_hotelId', '!=', False)])
#             for hotel in hotel_data:
#                 writer.writerow({'Client ID': unicode(hotel.id).encode("utf-8") or '', 
#                                  'Tourico Id':unicode(hotel.turico_hotelId).encode("utf-8") or '',
#                                  'Name':unicode(hotel.name).encode("utf-8") or '',
#                                  'Country Code': hotel.country_code and unicode(hotel.country_code).encode("utf-8") or '',
#                                  'City': hotel.cityName and unicode(hotel.cityName).encode("utf-8") or '',
#                                  'Address': hotel.addressLine1 and unicode(hotel.addressLine1).encode("utf-8") or '',
#                                  'Latitude': hotel.latitude and unicode(hotel.latitude).encode("utf-8") or '',
#                                  'Longitude': hotel.longitude and unicode(hotel.longitude).encode("utf-8") or '',
#                                  'ZipCode': hotel.zipcode and unicode(hotel.zipcode).encode("utf-8")
#                                   })

        dsfds
        return True
    
    @api.multi
    def generate_csv_hoteldata(self):
        
        path = os.path.dirname(os.path.abspath(__file__))
        csv_path = "hotel_data.csv"
        fullpath = os.path.join(path, csv_path)
        with open(fullpath, "w") as csvfile:
            fieldnames = ["Client ID", "Tourico Id",'Name','Country Code','State Code','City','Address','Phone','Fax','Latitude','Longitude','ZipCode',"Active / Inactive on the client's side"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            hotel_data = self.env['hotel.data'].search([('turico_hotelId', '!=', False)])
            for hotel in hotel_data:
                writer.writerow({'Client ID': unicode(hotel.id).encode("utf-8") or '', 
                                 'Tourico Id':unicode(hotel.turico_hotelId).encode("utf-8") or '',
                                 'Name':unicode(hotel.name).encode("utf-8") or '',
                                 'Country Code': hotel.country_code and unicode(hotel.country_code).encode("utf-8") or '',
                                 'City': hotel.cityName and unicode(hotel.cityName).encode("utf-8") or '',
                                 'Address': hotel.addressLine1 and unicode(hotel.addressLine1).encode("utf-8") or '',
                                 'Latitude': hotel.latitude and unicode(hotel.latitude).encode("utf-8") or '',
                                 'Longitude': hotel.longitude and unicode(hotel.longitude).encode("utf-8") or '',
                                 'ZipCode': hotel.zipcode and unicode(hotel.zipcode).encode("utf-8")
                                  })

        
        return True
    
    
    @api.multi
    def import_activitydetails(self):
        return True
    
    