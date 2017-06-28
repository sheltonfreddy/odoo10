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

class hotelapi_configuration(models.Model):
    _name = "hotelapi.configuration"
    
    name = fields.Char(string='Name', required=True)
    url = fields.Char(string='URL')
    key = fields.Char(string='Api Key')
    secret = fields.Char(string='Shared Secret')
    
    username = fields.Char(string='User Name')
    password = fields.Char(string='Password')
    
    is_test = fields.Boolean(string='Is Test(Stage)')
    type = fields.Selection([('hotelbeds-hotels','Hotelbeds-Hotels'),
                             ('hotelbeds-activity','Hotelbeds-Activity'),
                             ('turico-reservations-service', 'Turico Reservations Service'),
                             
                             ('turico-destinations-service', 'Turico Destinations Service'),
                             
                             ('sabre','Sabre')], string='Type', required=True)
    update_date = fields.Datetime('Last Update Date')
    act_update_date = fields.Datetime('Activity Last Update Date')
    hotel_update_date = fields.Datetime('Hotel Last Update Date')
    
    @api.multi
    def get_turico_reservations_service(self):
        config = self.search([('type', '=', 'turico-reservations-service')])
        return config.username, config.password
    
    @api.multi
    def get_turico_hotelflow(self):
        config = self.search([('type', '=', 'turico-reservations-service')])
        return config.username, config.password
    
    @api.multi
    def get_turico_destinations_service(self):
        config = self.search([('type', '=', 'turico-destinations-service')])
        update_date = fields.Datetime.from_string(config.update_date).isoformat('T')
        act_update_date = fields.Datetime.from_string(config.act_update_date).isoformat('T')
        return config.username, config.password, update_date, act_update_date
    
    @api.multi
    def get_turico_car_web_service(self):
        config = self.search([('type', '=', 'turico-reservations-service')])
        return config.username, config.password
    
    @api.multi
    def get_turico_activity_book_flow(self):
        config = self.search([('type', '=', 'turico-reservations-service')])
        return config.username, config.password
    
    
    
    
    @api.multi
    def get_hotelbeds_hotel_content(self, hotelbeds_code):
        url = "https://api.test.hotelbeds.com/hotel-content-api/1.0/hotels/%s?language=ENG" % hotelbeds_code
        sharedSecret = self.secret
        apiKey = self.key
        sigStr = "%s%s%d" % (apiKey,sharedSecret,int(time.time()))
        signature = hashlib.sha256(sigStr).hexdigest()
        headers = {'content-type' : 'application/json',
                   "Api-Key": apiKey,
                   "Accept": "application/json",
                   "X-Signature" : signature }
        response = requests.get(url, headers=headers)
        
        return ast.literal_eval(response.text.replace('false', 'False').replace('true', 'True'))
    
    @api.multi
    def get_hotelbeds_hotels_data(self,loc_code):
        #loc_code = self.code
        #print loc_code,"sadfsdafgdsafdfa"
        url = "https://api.test.hotelbeds.com/hotel-content-api/1.0/hotels?fields=name%%2Crooms%%2Cimages%%2CdestinationCode&destinationCode=%s&language=ENG&from=1&to=1000" % loc_code
        #url = "https://api.test.hotelbeds.com/hotel-content-api/1.0/hotels/%s?language=ENG" % hotelbeds_code
        sharedSecret = self.secret
        apiKey = self.key
        sigStr = "%s%s%d" % (apiKey,sharedSecret,int(time.time()))
        signature = hashlib.sha256(sigStr).hexdigest()
        headers = {'content-type' : 'application/json',
                   "Api-Key": apiKey,
                   "Accept": "application/json",
                   "X-Signature" : signature }
        response = requests.get(url, headers=headers)
        #print  response.text,"TTTTTTTTTTTTTTTTTTTTT"
        return ast.literal_eval(response.text.replace('false', 'False').replace('true', 'True'))
    
    @api.multi
    def get_hotelbeds_hotels_details(self,hotel_code):
        #loc_code = self.code
        #print loc_code,"sadfsdafgdsafdfa"
        url = "https://api.test.hotelbeds.com/hotel-content-api/1.0/hotels/%s?language=ENG" % hotel_code
        #url = "https://api.test.hotelbeds.com/hotel-content-api/1.0/hotels/%s?language=ENG" % hotelbeds_code
        sharedSecret = self.secret
        apiKey = self.key
        sigStr = "%s%s%d" % (apiKey,sharedSecret,int(time.time()))
        signature = hashlib.sha256(sigStr).hexdigest()
        headers = {'content-type' : 'application/json',
                   "Api-Key": apiKey,
                   "Accept": "application/json",
                   "X-Signature" : signature }
        response = requests.get(url, headers=headers)
        #print  response.text,"TTTTTTTTTTTTTTTTTTTTT"
        return ast.literal_eval(response.text.replace('false', 'False').replace('true', 'True'))
    
    @api.multi
    def get_hotelbeds_hotel_all_facilities(self):
        url = "https://api.test.hotelbeds.com/hotel-content-api/1.0/types/facilities?fields=all&language=ENG&from=401&to=1000"
        sharedSecret = self.secret
        apiKey = self.key
        sigStr = "%s%s%d" % (apiKey,sharedSecret,int(time.time()))
        signature = hashlib.sha256(sigStr).hexdigest()
        headers = {'content-type' : 'application/json',
                   "Api-Key": apiKey,
                   "Accept": "application/json",
                   "X-Signature" : signature }
        response = requests.get(url, headers=headers)
        #print  response.text,"TTTTTTTTTTTTTTTTTTTTT"
        return ast.literal_eval(response.text.replace('false', 'False').replace('true', 'True'))
    
    
    @api.multi
    def activity_detail_request(self, data):
        
        url = "https://api.test.hotelbeds.com/activity-api/3.0/activities/details"
        url = "https://api.test.hotelbeds.com/activity-api/3.0/activities/details/full"
        
        sharedSecret = self.secret
        apiKey = self.key
        # Signature is generated by SHA256 (Api-Key + Shared Secret + Timestamp (in seconds))
        sigStr = "%s%s%d" % (apiKey,sharedSecret,int(time.time()))
        signature = hashlib.sha256(sigStr).hexdigest()
        headers = {'content-type' : 'application/json',
                   "Api-Key": apiKey,
                   "Accept": "application/json",
                   "X-Signature" : signature}
        response = requests.post(url, data=json.dumps(data), headers=headers)
        #print "activity_detail_request ======>> ", response
        return ast.literal_eval(response.text.replace('false', 'False').replace('true', 'True'))
    
    @api.one
    def hotelbeds_signature(self):
        # Shared secret
        sharedSecret = self.secret
        apiKey = self.key
        # Signature is generated by SHA256 (Api-Key + Shared Secret + Timestamp (in seconds))
        sigStr = "%s%s%d" % (apiKey,sharedSecret,int(time.time()))
        signature = hashlib.sha256(sigStr).hexdigest()
        return signature
    
    @api.multi
    def cancel_booking(self, booking_reference):
        url = "https://api.test.hotelbeds.com/hotel-api/1.0/bookings/%s?cancellationFlag=CANCELLATION" % booking_reference
        sharedSecret = self.secret
        apiKey = self.key
        # Signature is generated by SHA256 (Api-Key + Shared Secret + Timestamp (in seconds))
        sigStr = "%s%s%d" % (apiKey,sharedSecret,int(time.time()))
        signature = hashlib.sha256(sigStr).hexdigest()
        headers = {'content-type' : 'application/json',
                   "Api-Key": apiKey,
                   "Accept": "application/json",
                   "X-Signature" : signature}
        response = requests.delete(url, headers=headers)
        return ast.literal_eval(response.text.replace('false', 'False').replace('true', 'True'))
    
    @api.multi
    def get_country(self):
        url = "https://api.test.hotelbeds.com/hotel-content-api/1.0/locations/countries"
        url = "https://api.test.hotelbeds.com/hotel-content-api/1.0/locations/countries?fields=all&language=ENG&from=1&to=500&useSecondaryLanguage=false"
        sharedSecret = self.secret
        apiKey = self.key
        sigStr = "%s%s%d" % (apiKey,sharedSecret,int(time.time()))
        signature = hashlib.sha256(sigStr).hexdigest()
        headers = {'content-type' : 'application/json',
                   "Api-Key": apiKey,
                   "Accept": "application/json",
                   "X-Signature" : signature }
        data = {'fields' : 'all',
                'language' : 'ENG'}
        response = requests.get(url, data=json.dumps(data), headers=headers)
        return ast.literal_eval(response.text.replace('false', 'False'))
    
    @api.multi
    def get_location(self, from_count = 1, to_count = 1000):
        url = "https://api.test.hotelbeds.com/hotel-content-api/1.0/locations/destinations?fields=all&language=ENG&from=%s&to=%s&useSecondaryLanguage=false" % (from_count, to_count)
        sharedSecret = self.secret
        apiKey = self.key
        sigStr = "%s%s%d" % (apiKey,sharedSecret,int(time.time()))
        signature = hashlib.sha256(sigStr).hexdigest()
        headers = {'content-type' : 'application/json',
                   "Api-Key": apiKey,
                   "Accept": "application/json",
                   "X-Signature" : signature }
        response = requests.get(url, headers=headers)
        result = ast.literal_eval(response.text.replace('false', 'False'))
        total = result['total']
        destinations = result['destinations']
        if to_count < int(total):
            destinations = destinations + self.get_location(to_count + 1, to_count + 1000)
        return destinations
    
    @api.multi
    def TouricoGetActivityDetails(self, activity_id):
    
        wsdl = "http://demo-activityws.touricoholidays.com/ActivityBookFlow.svc?wsdl"
        client = suds.client.Client(wsdl,headers={'Accept-Encoding': 'gzip'})
        service = client.service
        login_name, password = self.env['hotelapi.configuration'].get_turico_activity_book_flow()
        LoginName  = Element('auth:LoginName').setText(login_name)
        Password = Element('auth:Password').setText(password)
        Culture = Element('auth:Culture').setText('en_US')
        Version = Element('auth:Version').setText('7.123')
        AuthenticationHeader = Element('auth:AuthenticationHeader') 
        AuthenticationHeader.attributes.append(Attribute('xmlns:auth', 'http://schemas.tourico.com/webservices/authentication'))
        AuthenticationHeader.children = [LoginName, Password, Culture, Version]
        client.set_options(soapheaders=[AuthenticationHeader])
        
        #print client,"ccccccccccccccc"
        ArrayOfActivityId = client.factory.create('ns4:ArrayOfActivityId')
        ActivityId = client.factory.create('ns1:ActivityId')
        ActivityId._id = activity_id
        ArrayOfActivityId.ActivityId.append(ActivityId)
        #print ">>>>>>>>>>>",ArrayOfActivityId
        result = client.service.GetActivityDetails(ArrayOfActivityId)
        #print result,"RRRRRRRRRRRRRRR"
        act_details= result.ActivitiesDetails.ActivityDetails and result.ActivitiesDetails.ActivityDetails[0]
        vals = {'phone': act_details._activityPhone,
                'category': act_details._categoryName,
                'description':act_details.Description.ShortDescription._desc
                }
        return vals
        
        
    @api.multi
    def turico_GetCancellationPolicies(self, turico_hotelId, list_room_type_id,checkin,checkout):
        #print 'Data ====>>> ', data
        #return True
        wsdl = "http://demo-wsnew.touricoholidays.com/ReservationsService.asmx?wsdl"
        client = suds.client.Client(wsdl,headers={'Accept-Encoding': 'gzip'})
        service = client.service
        login_name, password = self.get_turico_reservations_service()
        username  = Element('trav:username').setText(login_name)
        password = Element('trav:password').setText(password)
        culture = Element('trav:culture').setText('en_US')
        version = Element('trav:version').setText('8')
        AuthenticationHeader = Element('ns0:LoginHeader') 
        AuthenticationHeader.attributes.append(Attribute('xmlns:trav', 'http://tourico.com/travelservices/'))
        AuthenticationHeader.children = [username, password, culture, version]
        client.set_options(soapheaders=[AuthenticationHeader])
        #print client
        result = client.service.GetCancellationPolicies(0,turico_hotelId,list_room_type_id,'',checkin,checkout)
        #print result
        #sadfsdl
        request = client.factory.create('ns4:SearchHotelsByIdRequest')
        request.CheckIn = data['CheckIn']
        request.CheckOut = data['CheckOut']
        
        array_of_hotel_id_info = client.factory.create('ns4:ArrayOfHotelIdInfo')
        hotel_id_info = client.factory.create('ns4:HotelIdInfo')
        hotel_id_info._id = data['HotelId']
        array_of_hotel_id_info.HotelIdInfo.append(hotel_id_info)
        request.HotelIdsInfo = array_of_hotel_id_info
        
        
        array_of_room_info = client.factory.create('ns4:ArrayOfRoomInfo')
        
        for room_data in data['RoomsInformation']:
            room_info = client.factory.create('ns4:RoomInfo')
            room_info.AdultNum = room_data['AdultNum']
            room_info.ChildNum = room_data['ChildNum']
            array_of_room_info.RoomInfo.append(room_info)
        request.RoomsInformation = array_of_room_info
        
        
        request.AvailableOnly = 'true'
        request.MaxPrice = '0'
        request.StarLevel = '0'
        result = client.service.CheckAvailabilityAndPrices(request)
        return result
    
    @api.multi
    def tourico_CancelReservation(self, reservationId):
        wsdl = "http://demo-wsnew.touricoholidays.com/ReservationsService.asmx?wsdl"
        client = suds.client.Client(wsdl,headers={'Accept-Encoding': 'gzip'})
        service = client.service
        login_name, password = self.get_turico_reservations_service()
        username  = Element('trav:username').setText(login_name)
        password = Element('trav:password').setText(password)
        culture = Element('trav:culture').setText('en_US')
        version = Element('trav:version').setText('8')
        AuthenticationHeader = Element('ns0:LoginHeader') 
        AuthenticationHeader.attributes.append(Attribute('xmlns:trav', 'http://tourico.com/travelservices/'))
        AuthenticationHeader.children = [username, password, culture, version]
        client.set_options(soapheaders=[AuthenticationHeader])
        result = client.service.CancelReservation(reservationId)
        return result
    
    @api.multi
    def tourico_GetCancellationFee(self, reservationId, date):
        wsdl = "http://demo-wsnew.touricoholidays.com/ReservationsService.asmx?wsdl"
        client = suds.client.Client(wsdl,headers={'Accept-Encoding': 'gzip'})
        service = client.service
        login_name, password = self.get_turico_reservations_service()
        username  = Element('trav:username').setText(login_name)
        password = Element('trav:password').setText(password)
        culture = Element('trav:culture').setText('en_US')
        version = Element('trav:version').setText('8')
        AuthenticationHeader = Element('ns0:LoginHeader') 
        AuthenticationHeader.attributes.append(Attribute('xmlns:trav', 'http://tourico.com/travelservices/'))
        AuthenticationHeader.children = [username, password, culture, version]
        client.set_options(soapheaders=[AuthenticationHeader])
        result = client.service.GetCancellationFee(reservationId, date)
        return result
    
    
    
    
    @api.multi
    def tourico_CheckAvailabilityAndPrices(self, data):
        wsdl = "http://demo-hotelws.touricoholidays.com/hotelflow.svc?wsdl"
        client = suds.client.Client(wsdl,headers={'Accept-Encoding': 'gzip'})
        service = client.service
        # Setting authentication header
        login_name, password = self.env['hotelapi.configuration'].get_turico_hotelflow()
        LoginName  = Element('LoginName').setText(login_name)
        Password = Element('Password').setText(password)
        Culture = Element('Culture').setText('en_US')
        Version = Element('Version').setText('7.123')
        AuthenticationHeader = Element('AuthenticationHeader') 
        AuthenticationHeader.attributes.append(Attribute('xmlns', 'http://schemas.tourico.com/webservices/authentication'))
        AuthenticationHeader.children = [LoginName, Password, Culture, Version]
        client.set_options(soapheaders=[AuthenticationHeader])
        #Adding booking details
        request = client.factory.create('ns4:SearchHotelsByIdRequest')
        request.CheckIn = data['CheckIn']
        request.CheckOut = data['CheckOut']
        array_of_hotel_id_info = client.factory.create('ns4:ArrayOfHotelIdInfo')
        hotel_id_info = client.factory.create('ns4:HotelIdInfo')
        hotel_id_info._id = data['HotelId']
        array_of_hotel_id_info.HotelIdInfo.append(hotel_id_info)
        request.HotelIdsInfo = array_of_hotel_id_info
        #Adding Room Data
        array_of_room_info = client.factory.create('ns4:ArrayOfRoomInfo')
        for room_data in data['RoomsInformation']:
            room_info = client.factory.create('ns4:RoomInfo')
            room_info.AdultNum = room_data['AdultNum']
            room_info.ChildNum = room_data['ChildNum']
            ArrayOfChildAge = client.factory.create('ns4:ArrayOfChildAge')
            if room_data.get('ChildAge'):
                for age in room_data['ChildAge']:
                    ChildAge = client.factory.create('ns4:ChildAge')
                    ChildAge._age = age
                    ArrayOfChildAge.ChildAge.append(ChildAge)
            room_info.ChildAges = ArrayOfChildAge
            array_of_room_info.RoomInfo.append(room_info)
        request.RoomsInformation = array_of_room_info
        request.AvailableOnly = 'true'
        request.MaxPrice = '0'
        request.StarLevel = '0'
        result = client.service.CheckAvailabilityAndPrices(request)
        #print "++++++++++++++++++++++++++++++++++++++++++++++++++++++"
        #print client.last_sent()
        #print "======================================================"
        #print "\n \n \n"
        #print "*"*25
        #print "\n"
        #print client.last_received()
        #print "-"*25
        return result
    
    
    @api.multi
    def tourico_BookHotel(self, data):
        data = data[0]
        wsdl = "http://demo-hotelws.touricoholidays.com/hotelflow.svc?wsdl"
        client = suds.client.Client(wsdl,headers={'Accept-Encoding': 'gzip'})
        service = client.service
        
        # Setting authentication header
        login_name, password = self.env['hotelapi.configuration'].get_turico_hotelflow()
        LoginName  = Element('LoginName').setText(login_name)
        Password = Element('Password').setText(password)
        Culture = Element('Culture').setText('en_US')
        Version = Element('Version').setText('7.123')
        AuthenticationHeader = Element('AuthenticationHeader') 
        AuthenticationHeader.attributes.append(Attribute('xmlns', 'http://schemas.tourico.com/webservices/authentication'))
        AuthenticationHeader.children = [LoginName, Password, Culture, Version]
        client.set_options(soapheaders=[AuthenticationHeader])
        
        #Data
        ArrayOfRoomInfo = client.factory.create('ns4:ArrayOfRoomInfo')
        for room_info in data['RoomsInformation']:
            RoomInfo = client.factory.create('ns4:RoomInfo')
            RoomInfo.AdultNum = room_info['AdultNum']
            RoomInfo.ChildNum = room_info['ChildNum']
            ArrayOfRoomInfo.RoomInfo.append(RoomInfo)
            
        
        request = client.factory.create('ns4:SearchRequest')
        request.Destination = data['Destination']
        request.HotelCityName = ''
        request.HotelLocationName = ''
        request.HotelName = ''
        request.CheckIn = data['CheckIn']
        request.CheckOut = data['CheckOut']
        request.RoomsInformation = ArrayOfRoomInfo
        request.MaxPrice = 0
        request.StarLevel = 0
        request.AvailableOnly = 1
        request.PropertyType = 'NotSet'
        request.ExactDestination = True
        res = client.service.SearchHotels(request)
        
        #print "=================>> ", res
        
        return res
    
    
    @api.multi
    def get_hotels_tourico(self, data):
        data = data[0]
        wsdl = "http://demo-hotelws.touricoholidays.com/hotelflow.svc?wsdl"
        client = suds.client.Client(wsdl,headers={'Accept-Encoding': 'gzip'})
        service = client.service
        
        # Setting authentication header
        login_name, password = self.env['hotelapi.configuration'].get_turico_hotelflow()
        LoginName  = Element('LoginName').setText(login_name)
        Password = Element('Password').setText(password)
        Culture = Element('Culture').setText('en_US')
        Version = Element('Version').setText('7.123')
        AuthenticationHeader = Element('AuthenticationHeader') 
        AuthenticationHeader.attributes.append(Attribute('xmlns', 'http://schemas.tourico.com/webservices/authentication'))
        AuthenticationHeader.children = [LoginName, Password, Culture, Version]
        client.set_options(soapheaders=[AuthenticationHeader])
        
        #Data
        ArrayOfRoomInfo = client.factory.create('ns4:ArrayOfRoomInfo')
        for room_info in data['RoomsInformation']:
            RoomInfo = client.factory.create('ns4:RoomInfo')
            RoomInfo.AdultNum = room_info['AdultNum']
            RoomInfo.ChildNum = room_info['ChildNum']
            ArrayOfChildAge = client.factory.create('ns4:ArrayOfChildAge')
            if room_info.get('ChildAge'):
                for age in room_info['ChildAge']:
                    ChildAge = client.factory.create('ns4:ChildAge')
                    ChildAge._age = age
                    ArrayOfChildAge.ChildAge.append(ChildAge)
            RoomInfo.ChildAges = ArrayOfChildAge
            ArrayOfRoomInfo.RoomInfo.append(RoomInfo)
        request = client.factory.create('ns4:SearchRequest')
        request.Destination = data['Destination']
        request.HotelCityName = ''
        request.HotelLocationName = ''
        request.HotelName = ''
        request.CheckIn = data['CheckIn']
        request.CheckOut = data['CheckOut']
        request.RoomsInformation = ArrayOfRoomInfo
        request.MaxPrice = 0
        request.StarLevel = 0
        request.AvailableOnly = 1
        request.PropertyType = 'NotSet'
        request.ExactDestination = True
        print request,'>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<,,,'
        res = client.service.SearchHotels(request)
        return res
    
    
    
    @api.multi
    def get_location_tourico(self):
        res = [] 
        wsdl = "http://destservices.touricoholidays.com/DestinationsService.svc?wsdl"
        client = suds.client.Client(wsdl,headers={'Accept-Encoding': 'gzip'})
        service = client.service
        
        login_name, password = self.env['hotelapi.configuration'].get_turico_destinations_service()
        username  = Element('username').setText(login_name)
        password = Element('password').setText(password)
        culture = Element('culture').setText('en_US')
        version = Element('version').setText('7.123')
        AuthenticationHeader = Element('LoginHeader') 
        AuthenticationHeader.attributes.append(Attribute('xmlns', 'http://schemas.tourico.com/webservices/authentication'))
        AuthenticationHeader.children = [username, password, culture, version]
        client.set_options(soapheaders=[AuthenticationHeader])
        destination = client.factory.create('ns1:Destination')
        destination.StatusDate = "2008-12-17T00:00:00"
        destination.Continent = ''
        destination.Country = ''
        destination.City = ''
        r = client.service.GetDestination(destination)
        for continent in r.Continent:
            for country in continent.Country:
                for state in country.State:
                    for city in state.City:
                        #print continent._name, country._name, city._name, city._destinationCode
                        res.append({
                                'name' : city._name,
                                'code' : city._destinationCode,
                                'country' : country._name,
                                'tourico_destinationId' : city._destinationId,
                                    })
        return res
    
    @api.multi
    def hotelbeds_activity_confirm(self, data):
        url = "https://api.test.hotelbeds.com/activity-api/3.0/bookings"
        sharedSecret = self.secret
        apiKey = self.key
        # Signature is generated by SHA256 (Api-Key + Shared Secret + Timestamp (in seconds))
        sigStr = "%s%s%d" % (apiKey,sharedSecret,int(time.time()))
        signature = hashlib.sha256(sigStr).hexdigest()
        headers = {'content-type' : 'application/json',
                   "Api-Key": apiKey,
                   "Accept": "application/json",
                   "X-Signature" : signature}
        response = requests.put(url, data=json.dumps(data), headers=headers)
        #print "txt ======>> ",response.text
        #print "status_code ==>> ", response.status_code
        return ast.literal_eval(response.text.replace('false', 'False').replace('true', 'True'))
    
        
    
    @api.multi
    def hotelbeds_availablity(self, data, url):
        
        sharedSecret = self.secret
        apiKey = self.key
        # Signature is generated by SHA256 (Api-Key + Shared Secret + Timestamp (in seconds))
        sigStr = "%s%s%d" % (apiKey,sharedSecret,int(time.time()))
        signature = hashlib.sha256(sigStr).hexdigest()
        headers = {'content-type' : 'application/json',
                   "Api-Key": apiKey,
                   "Accept": "application/json",
                   "X-Signature" : signature}
        data = data[0]
        response = requests.post(url, data=json.dumps(data), headers=headers)
        #print response,"RRRRRRRRRRRRRR",response.text
        return ast.literal_eval(response.text.replace('false', 'False'))
    
    @api.multi
    def hotelbeds_checkrates(self, data):
        
        url = "http://testapi.hotelbeds.com/hotel-api/1.0/checkrates"
        sharedSecret = self.secret
        apiKey = self.key
        # Signature is generated by SHA256 (Api-Key + Shared Secret + Timestamp (in seconds))
        sigStr = "%s%s%d" % (apiKey,sharedSecret,int(time.time()))
        signature = hashlib.sha256(sigStr).hexdigest()
        headers = {'content-type' : 'application/json',
                   "Api-Key": apiKey,
                   "Accept": "application/json",
                   "X-Signature" : signature}
        response = requests.post(url, data=json.dumps(data), headers=headers)
        #print "hotelbeds_checkrates ======>> ", response
        return ast.literal_eval(response.text.replace('false', 'False'))
        
    @api.multi
    def get_availablity(self, data):
        res = {}
        if self.type in ['hotelbeds-hotels']:
            res = self.hotelbeds_availablity(data, "https://api.test.hotelbeds.com/hotel-api/1.0/hotels")
        if self.type in ['hotelbeds-activity']:
            res = self.hotelbeds_availablity(data, "https://api.test.hotelbeds.com/activity-api/3.0/activities")
        return res
        
    @api.multi
    def hotelbeds_confirm_booking(self, data):
        url = "https://api.test.hotelbeds.com/hotel-api/1.0/bookings"
        sharedSecret = self.secret
        apiKey = self.key
        # Signature is generated by SHA256 (Api-Key + Shared Secret + Timestamp (in seconds))
        sigStr = "%s%s%d" % (apiKey,sharedSecret,int(time.time()))
        signature = hashlib.sha256(sigStr).hexdigest()
        headers = {'content-type' : 'application/json',
                   "Api-Key": apiKey,
                   "Accept": "application/json",
                   "X-Signature" : signature}
        data = data
        response = requests.post(url, data=json.dumps(data), headers=headers)
        return ast.literal_eval(response.text.replace('false', 'False').replace('true', 'True'))        
        
    @api.multi
    def confirm_booking(self, data):
        if self.type in ['hotelbeds-hotels', 'hotelbeds-activity']:
            res = self.hotelbeds_confirm_booking(data)
            return res
    
    @api.one
    def test_get_hotel_details(self):
        res = self.get_availablity()
        return True
    
    
