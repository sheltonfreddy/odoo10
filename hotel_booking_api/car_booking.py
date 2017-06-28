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
import base64
import urllib2
import ast

list_person_selection = [(n, n) for n in range(1, 10)]
pickup_dropoff_hour_selection = [(n, n) for n in range(0, 24)]
vehicle_type_selection = [(1, 'Car'), (2, 'Van'), (3, 'SUV'), (4,'Convert')]

class car_booking(models.Model):
    _name = "car.booking"
    
    destination_id = fields.Many2one('hotel.location', string='Destination', required=True)
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    
    pickup_date = fields.Date(string='PickUp Date')
    dropoff_date = fields.Date(string='DropOff Date')
    pickup_hour = fields.Selection(pickup_dropoff_hour_selection, string='PickUp Hour')
    dropoff_hour = fields.Selection(pickup_dropoff_hour_selection, string='DropOff Hour')
    vehicle_type = fields.Selection(vehicle_type_selection, string='Vehicle Type')
    
    car_company = fields.Integer("Car Company")
    
    total_pax = fields.Selection(list_person_selection, string='Passengers Number')
    car_searchresult_ids = fields.One2many('car.searchresult', 'car_booking_id', string='Cars')
    
    @api.multi
    def search_cars(self):
        print "====================================="
        import suds.client
        from suds.sax.element import Element
        from suds.sax.attribute import Attribute
        wsdl = "http://demo-carws.touricoholidays.com/CarWebService.svc?wsdl"
        client = suds.client.Client(wsdl,headers={'Accept-Encoding': 'gzip'})
        service = client.service
        login_name, password = self.env['hotelapi.configuration'].get_turico_car_web_service()
        LoginName  = Element('ns0:UserName').setText(login_name)
        Password = Element('ns0:Password').setText(password)
        Culture = Element('ns0:Culture').setText('en_US')
        Version = Element('ns0:Version').setText('7.123')
        AuthenticationHeader = Element('ns0:LoginHeader') 
        AuthenticationHeader.attributes.append(Attribute('xmlns:auth', 'http://schemas.tourico.com/webservices/authentication'))
        AuthenticationHeader.children = [LoginName, Password, Culture, Version]
        client.set_options(soapheaders=[AuthenticationHeader])
        
        print "o"*50
        print 'client ==>> ', client
        
        SearchCarsRequest = client.factory.create("ns4:SearchCarsRequest")
        #print "SearchCarsRequest ==>> ", SearchCarsRequest,self.pickup_date,self.dropoff_date

        SearchCarsRequest.Route.PickUp = self.destination_id.tourico_code #eg: MCO
        SearchCarsRequest.Route.DropOff = None
        SearchCarsRequest.PickUpDate = self.pickup_date
        SearchCarsRequest.DropOffDate = self.dropoff_date
        SearchCarsRequest.PickUpHour = self.pickup_hour
        SearchCarsRequest.DropOffHour = self.dropoff_hour
        SearchCarsRequest.VehicleType = self.vehicle_type 
        SearchCarsRequest.CarCompany = self.car_company
        SearchCarsRequest.TotalPax = self.total_pax
        SearchCarsRequest.DriverCountryCode = "US"
        SearchCarsRequest.DriverAge = 26

#         SearchCarsRequest.Route.PickUp = self.destination_id.tourico_code
#         SearchCarsRequest.Route.DropOff = None
#         SearchCarsRequest.PickUpDate = self.pickup_date
#         SearchCarsRequest.DropOffDate = self.dropoff_date
#         SearchCarsRequest.PickUpHour = self.pickup_hour
#         SearchCarsRequest.DropOffHour = self.dropoff_hour
#         SearchCarsRequest.VehicleType = 0
#         SearchCarsRequest.CarCompany = self.car_company
#         SearchCarsRequest.TotalPax = 0
#         SearchCarsRequest.DriverCountryCode = "US"
#         SearchCarsRequest.DriverAge = 26
        print SearchCarsRequest,"SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS"
        result = client.service.SearchCars(SearchCarsRequest)
        if result:
            car_search_result_turico = self.create_carsearch_result_turico(result) or []
        #print 'result ==>> ', result
        
    @api.multi
    def create_carsearch_result_turico(self, result):
        if type(result) == list:
            result = dict(result[0])
        #print "RRRRRRRRRRRRRR",result
        car_search_result = []
        print "*************",result.CarResults,type(result.CarResults)
        if self.car_searchresult_ids:
            self.car_searchresult_ids = False
        if result.CarResults:
            for car_res in result.CarResults.Car:
                
                print car_res._carName,"cccccccccccccc"
                img_url = car_res._carThumb
                #'rate' : hotel._minAverPublishPrice,
                car_data = {
                    'name': car_res._carName,
                    'api_type' : 'Tourico',
                    'min_price': car_res._minPrice,
                    'comp_name': car_res._carCompanyName,
                    'selected_pgm': car_res._productId
                        }
                car_search_result.append((0, 0, car_data))
        print car_search_result,"sdfsdfsf"
        self.car_searchresult_ids = car_search_result
        
class car_searchresult(models.Model):
    _name = "car.searchresult"
    
    name = fields.Char('Car Name')
    car_booking_id = fields.Many2one('car.booking', string='Car Booking')
    min_price = fields.Float('Min. Price')
    comp_name = fields.Char('Car Company Name')
    image = fields.Binary("Image")
    api_type = fields.Char('API Type')
    booked = fields.Boolean('Booked')
    selected_pgm = fields.Char('Selected Program')
    
    @api.multi
    def book_car(self):
        if self.api_type=='Tourico':
            return self.book_car_turico()
        
    @api.multi
    def book_car_turico(self):
        import logging
        logging.basicConfig(level=logging.INFO)
        logging.getLogger('suds.client').setLevel(logging.DEBUG)
        import suds.client
        from suds.sax.element import Element
        from suds.sax.attribute import Attribute
        wsdl = "http://demo-carws.touricoholidays.com/CarWebService.svc?wsdl"
        client = suds.client.Client(wsdl,headers={'Accept-Encoding': 'gzip'})
        service = client.service
        login_name, password = self.env['hotelapi.configuration'].get_turico_car_web_service()
        LoginName  = Element('LoginName').setText(login_name)
        Password = Element('Password').setText(password)
        Culture = Element('Culture').setText('en_US')
        Version = Element('Version').setText('8')
        AuthenticationHeader = Element('AuthenticationHeader') 
        AuthenticationHeader.attributes.append(Attribute('xmlns', 'http://schemas.tourico.com/webservices/authentication'))
        AuthenticationHeader.children = [LoginName, Password, Culture, Version]
        client.set_options(soapheaders=[AuthenticationHeader])
        
        BookCarRequest = client.factory.create("ns4:BookCarRequest")
        
        DriverInfo = client.factory.create('ns4:DriverInfo')
        BookCarRequest.recordLocatorId = 0
        BookCarRequest.SelectedProgram = self.selected_pgm
        DriverInfo._firstName= "Francis"
        DriverInfo._lastName = "Underwood"
        DriverInfo._age = '28'
        BookCarRequest.DriverInfo = DriverInfo
        BookCarRequest.PaymentType = 'Obligo'
        BookCarRequest.RequestedPrice = self.min_price
        BookCarRequest.DeltaPrice = self.min_price and self.min_price*1/100 or 0
        BookCarRequest.Currency = 'USD'
        print BookCarRequest,"BBBBBBBBB"
        client.service.BookCar(BookCarRequest)
        
