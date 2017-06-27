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
import json
from openerp import models, fields, api, _
from openerp.addons.hotel_booking_api.sabre_api import Sabre
from datetime import datetime

list_adults = [(n, n) for n in range(1, 7)]
list_child = [(n, n) for n in range(0, 7)]
list_infant = [(n, n) for n in range(0, 2)]

class FlightSearch(models.Model):
    _name = "flight.search"
    
    origin_id = fields.Many2one('airport.cities', string='From', required=True)
    destination_id = fields.Many2one('airport.cities', string='To', required=True)
    depart_date = fields.Date(string='Departure Date', required=True)
    return_date = fields.Date(string='Return Date', required=True)
    adult = fields.Selection(list_adults, string='Adult')
    child = fields.Selection(list_child, string='Children')
    infant = fields.Selection(list_infant, string='Infant')
    itinerary_ids = fields.One2many('air.itinerary', 'flightsearch_id', 'AirItinerary')
    
    @api.multi
    def search_flights(self):
        if self.itinerary_ids:
            self.itinerary_ids = False
        client_id = 'V1:f7yoc2jnolmpynz9:DEVCENTER:EXT'
        client_secret = 'r4wlH3TN'
        
        origin = self.origin_id.sabre_code
        destn = self.destination_id.sabre_code
        depart_date = fields.Datetime.from_string(self.depart_date).isoformat('T')
        return_date = fields.Datetime.from_string(self.return_date).isoformat('T')
        data = {"OTA_AirLowFareSearchRQ": {
                    "Target": "Production",
                    "POS": {
                      "Source": [
                        {
                          "PseudoCityCode": "F9CE",
                          "RequestorID": {
                            "Type": "1",
                            "ID": "1",
                            "CompanyName": {
                              
                            }
                          }
                        }
                      ]
                    },
                    "OriginDestinationInformation": [
                      {
                        "RPH": "1",
                        "DepartureDateTime": depart_date,
                        "OriginLocation": {
                          "LocationCode": origin
                        },
                        "DestinationLocation": {
                          "LocationCode": destn
                        },
                        "TPA_Extensions": {
                          "SegmentType": {
                            "Code": "O"
                          }
                        }
                      },
                      {
                        "RPH": "2",
                        "DepartureDateTime": return_date,
                        "OriginLocation": {
                          "LocationCode": destn
                        },
                        "DestinationLocation": {
                          "LocationCode": origin
                        },
                        "TPA_Extensions": {
                          "SegmentType": {
                            "Code": "O"
                          }
                        }
                      }
                    ],
                    "TravelPreferences": {
                      "ValidInterlineTicket": True,
                      "CabinPref": [
                        {
                          "Cabin": "Y",
                          "PreferLevel": "Preferred"
                        }
                      ],
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
                      "SeatsRequested": [
                        1
                      ],
                      "AirTravelerAvail": [
                        {
                          "PassengerTypeQuantity": [
                            {
                              "Code": "ADT",
                              "Quantity": 1
                            }
                          ]
                        }
                      ]
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
        sabre = Sabre(client_id, client_secret)
        search = sabre.api.v3.shop.flights(mode='live',limit=1,data=data,json=True)
        print "="*30
        print type(search)
        print "="*30
        result=[]
        itineraries = search['OTA_AirLowFareSearchRS'] and search['OTA_AirLowFareSearchRS']['PricedItineraries'] and search['OTA_AirLowFareSearchRS']['PricedItineraries']['PricedItinerary']
        for itin in itineraries:
            print "???",itin
            print "111111111111111111111"
            print itin['AirItinerary']
            print "11111111111111111111"
            print "********************"
            print "22222222222222222222"
            print itin['SequenceNumber']
            print "22222222222222222222"
            print "********************"
            print "33333333333333333333"
            print itin['AirItineraryPricingInfo']
            print "33333333333333333333"
            data = {'total_fare': itin['AirItineraryPricingInfo'][0]['ItinTotalFare']['TotalFare']['Amount'],
                    'from_flight': itin['AirItinerary']['OriginDestinationOptions']['OriginDestinationOption'][0]['FlightSegment'][0]['FlightNumber'],
                    'to_flight': itin['AirItinerary']['OriginDestinationOptions']['OriginDestinationOption'][1]['FlightSegment'][0]['FlightNumber'],
                    'to_airline': itin['AirItinerary']['OriginDestinationOptions']['OriginDestinationOption'][0]['FlightSegment'][0]['MarketingAirline']['Code'],
                    'return_airline': itin['AirItinerary']['OriginDestinationOptions']['OriginDestinationOption'][1]['FlightSegment'][0]['MarketingAirline']['Code'],
                    'departure_date': datetime.strptime(itin['AirItinerary']['OriginDestinationOptions']['OriginDestinationOption'][0]['FlightSegment'][0]['DepartureDateTime'], '%Y-%m-%dT%H:%M:%S').strftime("%Y-%m-%d %H:%M:%S"),
                    'arrival_date': datetime.strptime(itin['AirItinerary']['OriginDestinationOptions']['OriginDestinationOption'][1]['FlightSegment'][0]['ArrivalDateTime'], '%Y-%m-%dT%H:%M:%S').strftime("%Y-%m-%d %H:%M:%S"),
                    }
            #asddsa
            
            result.append((0, 0, data))
        self.itinerary_ids = result
        return True
        

class AirItinerary(models.Model):
    _name = "air.itinerary"
    
    name = fields.Char(string='Flight')
    flightsearch_id = fields.Many2one('flight.search', 'Flight Search')
    total_fare = fields.Float('Total Fare')
    from_flight = fields.Char(string='Flight No')
    to_flight = fields.Char(string='Return Flight No')    
    #from_airport = fields.Char(string='Flight')
    departure_date = fields.Datetime(string='Departure')
    arrival_date = fields.Datetime(string='Arrival')
    departure_airport = fields.Char(string='Departure Airport')
    arrival_airport = fields.Char(string='Arrival Airport')
    to_airline = fields.Char(string='Airlines')
    return_airline = fields.Char(string='Return Airlines')
    
class AirLines(models.Model):
    _name = "air.lines"
    
    name = fields.Char(string='Name', required=True)
    sabre_code = fields.Char(string='AirlineCode')
    business_name = fields.Char(string='AlternativeBusinessName')
    
class AirportCities(models.Model):
    _name = "airport.cities"
    
    name = fields.Char(string='Name', required=True)
    sabre_code = fields.Char(string='Code')
    country_code = fields.Char(string='CountryCode')
    country_name = fields.Char(string='CountryName')
    region_name = fields.Char(string='RegionName')
    
class AirlineOriginDestination(models.Model):
    _name = 'airline.origin.destination'
    
    name = fields.Char(string='Route', required=True)
    origin = fields.Char(string='Origin', required=True)
    origin_airport = fields.Char(string='Origin Airport Name')
    origin_city = fields.Char(string='Origin CityName')
    origin_country = fields.Char(string='Origin CountryName')
    origin_countrycode = fields.Char(string='Origin CountryCode')
    origin_region = fields.Char(string='Origin RegionName')
    destination = fields.Char(string='Destination', required=True)
    destination_airport = fields.Char(string='Destination Airport Name')
    destination_city = fields.Char(string='Destination CityName')
    destination_country = fields.Char(string='Destination CountryName')
    destination_countrycode = fields.Char(string='Destination CountryCode')
    destination_region = fields.Char(string='Destination RegionName')
    