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
from openerp.addons.hotel_booking_api.sabre_api import Sabre


class import_locations(osv.osv_memory):
    _name = "import.locations"
    _description = "Import Locations"
    
    @api.multi
    def do_import(self):
        self.env["hotel.location"].get_location()
        
    @api.multi
    def do_import_hotels(self):
        #self.pool.get("hotels.hotel").get_hotels(cr, uid, [], context=context)
        print 'h'*100
        self.env["hotel.data"].get_all_hotels()
        
    @api.multi
    def do_import_all_hotel_facilities(self):
        self.env["all.hotel.facilities"].get_all_hotel_facilities()
        
    @api.multi
    def do_import_loc_hotel_data(self):
        hotelbeds_locations = self.env["hotel.location"].search([('code','!=',False)])
        for location in hotelbeds_locations:
            print "Importing Hotel Data from >>>",location.name
            location.get_hotels()
        return True
       
    @api.multi
    def do_import_sabre_hotels(self):
        client_id = 'V1:f7yoc2jnolmpynz9:DEVCENTER:EXT'
        client_secret = 'r4wlH3TN'
        sabre = Sabre(client_id, client_secret)
        print "*"*100
        print sabre.api_list()
        print "-"*100
        country_list = sabre.api.v1.lists.supported.countries(pointofsalecountry='US')
        print country_list,"1111111111"
        #return True
        #airlines = sabre.api.v1.lists.utilities.airlines()
        #print airlines,"aaaaaaaaaaaaaaaaaa"
#         cities = sabre.api.v1.lists.supported.cities(country='US')
#         for city in cities['Cities']:
#             airportcity = self.pool.get('airport.cities').search(cr, uid, [('name','=',city['name'])])
#             if not airportcity:
#                 vals = {'name': city['name'], 
#                         'sabre_code': city['code'], 
#                         'country_code': city['countryCode'],
#                         'country_name': city['countryName'],
#                         'region_name': city['regionName']
#                         }
#                 self.pool.get('airport.cities').create(cr, uid, vals)
#         return True
#         #city_pairs = sabre.api.v1.lists.supported.shop.flights.origins.destinations()
        #print city_pairs,"ccccccccccccccccccc"
        #top_destns = sabre.api.v1.lists.top.destinations()
        #airports = sabre.api.v1.lists.supported.cities.airports()
        #cars = sabre.api.v2.shop.cars()
        #print top_destns,">>>>>>>>>>>aAAAAAAAAAA"
        #sdf
        #print city_pairs,"cccccccc"
#         for pcity in city_pairs['OriginDestinationLocations']:
#  #           print city,"xxxxxxxxx"
#             vals = {
#                     'name': pcity['OriginDestinationLocations'],
#                     'origin': pcity['OriginLocation']['AirportCode'],
#                     'origin_airport': pcity['OriginLocation']['AirportName'],
#                     'origin_city': pcity['OriginLocation']['CityName'],
#                     'origin_country': pcity['OriginLocation']['CountryName'],
#                     'origin_countrycode': pcity['OriginLocation']['CountryCode'],
#                     'origin_region': pcity['OriginLocation']['RegionName'],
#                     'destination': pcity['DestinationLocation']['AirportCode'],
#                     'destination_airport': pcity['DestinationLocation']['AirportName'],
#                     'destination_city': pcity['DestinationLocation']['CityName'],
#                     'destination_country': pcity['DestinationLocation']['CountryName'],
#                     'destination_countrycode': pcity['DestinationLocation']['CountryCode'],
#                     'destination_region': pcity['DestinationLocation']['RegionName'],
#                     }
#             a = self.pool.get('airline.origin.destination').create(cr, uid, vals)
#             #print "xxxxxxxxxxxxxx",a
            #sd
#         fares = sabre.api.v1.historical.flights.fares(
#                     origin='LAX', destination='JFK', 
#                     earliestdeparturedate='2017-01-30', 
#                     latestdeparturedate='2017-01-30', 
#                     lengthofstay=1,
#                     )
#         print fares
        #pos = sabre.api.v1.lists.supported.pointofsalecountries()
        #print pos,"pppppppppppp"
        #print cities,"AAAAAAAAAAAAAAAAAA"
        data = { "OTA_AirLowFareSearchRQ": {
        
                                    "Target": "Production",
        
                                        "POS": {
        
                    "Source": [{
        
                        "PseudoCityCode":"F9CE",
        
                        "RequestorID": {
        
                            "Type": "1",
        
                          "ID": "1",
        
                            "CompanyName": {
        
                                
        
                          }
        
                     }
        
                 }]
        
                },
        
                "OriginDestinationInformation": [{
        
                  "RPH": "1",
        
                   "DepartureDateTime": "2017-04-07T11:00:00",
        
                   "OriginLocation": {
        
                     "LocationCode": "DFW"
        
                 },
        
                    "DestinationLocation": {
        
                        "LocationCode": "CDG"
        
                 },
        
                    "TPA_Extensions": {
        
                     "SegmentType": {
        
                            "Code": "O"
        
                       }
        
                 }
        
             },
        
                {
        
                 "RPH": "2",
        
                   "DepartureDateTime": "2017-04-08T11:00:00",
        
                   "OriginLocation": {
        
                     "LocationCode": "CDG"
        
                 },
        
                    "DestinationLocation": {
        
                        "LocationCode": "DFW"
        
                 },
        
                    "TPA_Extensions": {
        
                     "SegmentType": {
        
                            "Code": "O"
        
                       }
        
                 }
        
             }],
        
               "TravelPreferences": {
        
                  "ValidInterlineTicket": True,
        
                   "CabinPref": [{
        
                     "Cabin": "Y",
        
                     "PreferLevel": "Preferred"
        
                    }],
        
                   "TPA_Extensions": {
        
                     "TripType": {
        
                           "Value": "Return"
        
                     },
        
                        "LongConnectTime": {
        
                            "Min": 780,
        
                         "Max": 1200,
        
                            "Enable": True
        
                      },
        
                        "ExcludeCallDirectCarriers": {
        
                          "Enabled": True
        
                     }
        
                 }
        
             },
        
                "TravelerInfoSummary": {
        
                    "SeatsRequested": [1],
        
                  "AirTravelerAvail": [{
        
                      "PassengerTypeQuantity": [{
        
                         "Code": "ADT",
        
                            "Quantity": 1
        
                       }]
        
                    }]
        
                },
        
                "TPA_Extensions": {
        
                 "IntelliSellTransaction": {
        
                     "RequestType": {
        
                            "Name": "50ITINS"
        
                     }
        
                 }
        
             }
        
         }
        
        }
        search = sabre.api.v3.shop.flights(mode='live',limit=2,data=data,json=True)
#                     origin='LAX', 
#                     destination='DFW',
#                     departuredate='2017-04-07',limit=50)
        print "="*30
        print search
        print "="*30
        print search.keys()
        #print search['OTA_AirLowFareSearchRS']['PricedItineraries']
        
        sadf
        search = sabre.api.v3.shop.flights(enabletagging=True,
                    limit=10,
                    #view='BFM_ITIN_BASE_TAX_TOTAL_PRICE',
                    origin='DFW', 
                    destination='CDG',
                    departuredate='2017-04-07')#(origin='AUH', destination='DXB', departuredate='2017-01-20')
        #print search,"SSSSSSSSSSSSSSS"
        #adv_search = sabre.api.v1.shop.calendar.flights()
        #lpc = sabre.api.v1.shop.flights.fares(origin='ATL', destination='LAS', lengthofstay='3')
        #print lpc,"PPPPPPPPPPPPPPPPP"
        
        
        for line in airlines['AirlineInfo']:
            airline = self.pool.get('air.lines').search(cr, uid, [('name','=',line['AirlineName'])])
            if not airline:
                vals = {'name': line['AirlineName'], 'sabre_code': line['AirlineCode'], 'business_name': line['AlternativeBusinessName']}
                self.pool.get('air.lines').create(cr, uid, vals)
        for city in cities['Cities']:
            airportcity = self.pool.get('airport.cities').search(cr, uid, [('name','=',city['name'])])
            if not airportcity:
                vals = {'name': city['name'], 
                        'sabre_code': city['code'], 
                        'country_code': city['countryCode'],
                        'country_name': city['countryName'],
                        'region_name': city['regionName']
                        }
                self.pool.get('airport.cities').create(cr, uid, vals)
        #print country_list,"ssssssssssssssssssssssssscccccccccccc",type(country_list)
        #print country_list['DestinationCountries']
        #for country in country_list['DestinationCountries']:
         #   print country['CountryCode'],"cccccccc"
          #  self.pool.get("hotel.data").
            
#         fares = sabre.api.v1.historical.flights.fares(
#                     origin='LAX', 
#                     destination='JFK', 
#                     earliestdeparturedate='2017-03-30', 
#                     latestdeparturedate='2017-03-30', 
#                     lengthofstay=1,
#                     )
#         print fares,"fffffffffffffffffff"
        return True
        #wsdl = "http://demo-hotelws.touricoholidays.com/hotelflow.svc?wsdl"
        #client = suds.client.Client(wsdl)
        #service = client.service
        
    @api.multi   
    def import_giata(self):
        #self.pool.get("hotel.data").import_giata(cr, uid, [], context=context)
        self.env["hotel.data"].import_giata()
        
    #to be combine with do_import
    @api.multi
    def do_import_tourico(self):
        
        self.env["hotel.location"].get_location_tourico()
        #self.pool.get("hotel.location").
        
        self.env["cruisedestinations.tourico"].get_getcruisedestinations_tourico()
        #self.pool.get("").
        
        self.env["tourico.cruiseline"].get_cruiseline_tourico()
        #self.pool.get("").
        
        self.env["tourico.embarkationports"].get_embarkationports_tourico()
        #self.pool.get("").
     


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
