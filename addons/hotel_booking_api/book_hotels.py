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
from datetime import datetime
import openerp
import suds.client
from suds.sax.element import Element
from suds.sax.attribute import Attribute

list_flexible_days = [(n, n) for n in range(1, 15)]
list_room = [(n, n) for n in range(1, 15)]
list_adults = [(n, n) for n in range(0, 8)]
list_child = [(n, n) for n in range(0, 8)]
list_room_selection = [(n, n) for n in range(1, 10)]

class book_hotels(models.Model):
    _name = "book.hotels"
    
    booking_type = fields.Selection([('hotels','Hotels'), ('activities','Activities')], 
                       string='Booking Type', required=True, default="hotels")
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    check_in = fields.Date(string='Check IN')
    check_out = fields.Date(string='Check OUT')
    date_flexible = fields.Boolean(string='Dates are flexible')
    flexible_days = fields.Selection(list_flexible_days, string='Flexible Days')
    rooms = fields.Selection(list_room, string='Rooms', default=1)
#     destination = fields.Char("Destination", default="MSY")
    destination_id = fields.Many2one('hotel.location', string='Destination', required=True)
    room_occupancy_ids = fields.One2many('room.occupancy', 'booking_id', string='Room Occupancy')
    hotel_searchresult_ids = fields.One2many('hotel.searchresult', 'booking_id', string='Hotels')
    
    @api.onchange('date_flexible', 'flexible_days')
    def onchange_date_flexible(self):
        res = {}
        if self.date_flexible:
            if not self.flexible_days:
                self.flexible_days = 1
        else:
            self.flexible_days = False
        return res
    
    @api.onchange('rooms')
    def onchange_quantity(self):
        res = {}
        if self.rooms == 0:
                self.rooms = 1
                warning = { 'title': _('Room'),
                           'message' : 'Room cannot be zero' }
                res.update({'warning': warning})
        if self.room_occupancy_ids:
            self.room_occupancy_ids = [(5)]
        self.room_occupancy_ids = [(0, 0, {'adults' : 2, 'child' : 0}) for a in range(0, self.rooms)]
        return res
    
    @api.one
    def search_hotel_details(self):
        if self.hotel_searchresult_ids:
            self.hotel_searchresult_ids = False
        if self.booking_type == "hotels":
            
            hotel_search_result =[]
            # commented for Tourico certification 4lines
            data = self.generate_data_for_hotelbeds()
            hotelapi = self.env['hotelapi.configuration'].search([('type', '=', 'hotelbeds-hotels')])
            result = hotelapi[0].get_availablity(data)
            hotel_search_result = self.create_search_result(result) or []
            
            # get hotels from turico
            #data = self.generate_data_for_turico()
            #if data:
             #   result = self.env['hotelapi.configuration'].get_hotels_tourico(data)
              #  hotel_search_result_turico = self.create_search_result_turico(result) or []
                #Combining search
               # hotel_search_result = hotel_search_result_turico#hotel_search_result + hotel_search_result_turico
            if hotel_search_result:
                self.hotel_searchresult_ids = hotel_search_result
        return True

#     @api.multi
#     def search_hotel_details_web(self, search_details):
#         occupancies = []

#         for room_detail in search_details['room_detail']:
#             paxes = [{'age':'30','type':'AD'} for i in range(int(room_detail['adult']))]
#             for child_age in room_detail.get('children_age',[]):
#                 paxes.append({'age':child_age,'type':'CH'})

#             data_occu ={
#                         'paxes':paxes,
#                         'children':room_detail['children'],
#                         'rooms':1,
#                         'adults':room_detail['adult'],
#                     }
#             occupancies.append(data_occu)
#         data ={
#             'occupancies':occupancies,
#             'destination':{'code':search_details['destination']},
#             'stay':{'checkIn': datetime.strptime(search_details['check_in'],"%d/%m/%Y").strftime("%Y-%m-%d"),
#                      'checkOut': datetime.strptime(search_details['check_out'],"%d/%m/%Y").strftime("%Y-%m-%d")   }

#             }



#         print data,'========================\n\n\n\n'
#         hotelapi = self.env['hotelapi.configuration'].search([('type', '=', 'hotelbeds-hotels')])
#         result = hotelapi[0].get_availablity([data])
        

#         hotel_data = self.create_search_result_web(result)
#         print "hotel_data -->> ", hotel_data
#         print hotel_data

#     @api.multi
#     def create_search_result_web(self, result):
#         if type(result) == list:
#             result = dict(result[0])
#         if 'hotels' not in result:
#              return False
#         list_hotels = result.get('hotels', {}).get('hotels')
#         if not list_hotels:
#             return False
#         hotel_search_result = []
#         count  = 0
#         for hotel in list_hotels:
#           count = count + 1
#           if count < 3:
#             occupancy = self.env['room.occupancy'].get_all_details(self.id)
            
            
#             image_url_list = self.env['hotel.data'].get_hotelbeds_images(str(hotel['code']))
#             data = {
#                 'name': hotel['name'] +  " // " + str(hotel['code']),
#                 'image_url_list' : image_url_list,
#                 'location' : "%s,  %s" % (hotel['zoneName'], hotel['destinationName']),
#                 'rate' : float(hotel['minRate']),
#                 'rooms' : occupancy['rooms'],
#                 'adults' : occupancy['adults'],
#                 'children' : occupancy['child'],
#                 'api_type' : 'HotelBeds'}
#             list_room_data = []
#             if hotel.get('rooms'):
#                 for rooms in hotel.get('rooms', []):
#                     for rate in rooms.get('rates', []):
#                         print "\n"
#                         print "rooms ===>> ", rooms['name'], rate['boardName']
#                         if rate.get('rateKey'):
#                             room_data = {
#                                   'name' : rooms['name'] + " - " + rate['boardName'],
#                                   'rateKey' : rate['rateKey'],
#                                   'rate' : rate['net'],
#                                   'adults' : int(rate['adults']),
#                                   'children' : int(rate['children']),
#                                   'default_date' : True}
#                             list_room_data.append(room_data)
#                         if rate.get('shiftRates'):
#                             for shiftRates in rate['shiftRates']:
#                                 if shiftRates.get('rateKey'):
#                                     shift_data = {
#                                           'name' : rooms['name'],
#                                           'rateKey' : shiftRates['rateKey'],
#                                           'rate' : shiftRates['net'],
#                                           'checkIn' : shiftRates['checkIn'],
#                                           'checkOut': shiftRates['checkOut'],
#                                           'adults' : int(rate['adults']),
#                                           'children' : int(rate['children']),
#                                           'default_date' : False}
#                                     list_room_data.append(shift_data)
#             data['room_rates_ids'] = list_room_data
#             hotel_search_result.append(data)
# #         if hotel_search_result:
# #             self.hotel_searchresult_ids = hotel_search_result
#         return hotel_search_result


    @api.multi
    def create_search_result_turico(self, result):
        if type(result) == list:
            result = dict(result[0])
        hotel_search_result = []
        for hotel_list in result.HotelList:
            for hotel in hotel_list[1]:
                #if hotel._name=='TESTING HOTEL - Demo':
                 #   print '\n'*30
                  #  print hotel
                   # print '\n'*30
                
                occupancy = self.env['room.occupancy'].get_all_details(self.id)
                img_url = hotel._thumb
                image = self.env['hotel.data'].get_image(img_url, turico_hotelId=hotel._hotelId, name=hotel._name)
                data = {
                    'name': hotel._name,
                    'location' : hotel.Location._address,
                    'rate' : hotel._minAverPublishPrice,
                    'rooms' : occupancy['rooms'],
                    'adults' : occupancy['adults'],
                    'children' : occupancy['child'],
                    'turico_hotelId' : hotel._hotelId,
                    'image' : image or False,
                    'api_type' : 'Turico',
                    'img_url' : img_url}
                list_room_data = []
                for roomtypes in hotel.RoomTypes:
                    #c=0
                    #if hotel._name=='TESTING HOTEL - Demo':
                     #   print roomtypes,"========================RRRRRRRRRRRR===================="
                    for roomtype in roomtypes[1]:
                        #if hotel._name=='TESTING HOTEL - Demo':
                         #   print roomtype.Occupancies.Occupancy
                        occupancies = roomtype.Occupancies[0][0]
                      #  if hotel._name=='TESTING HOTEL - Demo':
                       #     c+=1
                        #    print "-"*60,"<<",roomtype.Occupancies[0],">>"
                            #sadf
                         #   print occupancies
                          #  print "^"*60
                            
                            #sajdhf
                            
                        room_data = {
                                  'name' : roomtype._name+'Bed '+occupancies._bedding,
                                  'turico_roomId' : roomtype._roomId,
                                  'turico_hotelRoomTypeId' : roomtype._hotelRoomTypeId,
                                  'rateKey' : "",
                                  'rate' : occupancies._occupPrice,
                                  'base_rate' : occupancies._occupPrice,
                                  'checkIn' : self.check_in,
                                  'checkOut': self.check_out,
                                  'adults' :  occupancies._maxGuests,
                                  'children' : occupancies._maxChild,
                                  'currency' :hotel._currency,
                                  'default_date' : True}
                        room = self.env['room.rates'].create(room_data)
                        list_room_data.append((4, room.id))
                        SelctedSupplements = occupancies.SelctedSupplements
                        if SelctedSupplements:
#                             if hotel._name=='TESTING HOTEL - Demo':
#                                 print "<<SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS",hotel._name,roomtype._name
#                                 print SelctedSupplements
#                                 print 
#                                 print "SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS>>"
                            for supplements in SelctedSupplements:
                                #if hotel._name=='TESTING HOTEL - Demo':
                                    #print supplements,"11111111111111111111",type(supplements)
                                supplement = supplements[1]
                                for supp in supplement:
                                    age_lines=[]
                                    #if hotel._name=='TESTING HOTEL - Demo':
                                    #    print supp.__class__.__name__,"NNNNNNNNNNNNN"
                                    if supp.__class__.__name__=='PerRoomSupplement':
                                        supp_type = 'perroom'
                                    elif supp.__class__.__name__=='PerPersonSupplement':
                                        #if hotel._name=='TESTING HOTEL - Demo':
                                         #   print supp,"ssssssssssssss"
                                        supp_type = 'perperson'
                                        agegroup = supp.SuppAgeGroup.SupplementAge
                                        for age in agegroup:
                                           age_vals={'supp_from': age._suppFrom,
                                                     'supp_to': age._suppTo,
                                                     'supp_qty': age._suppQuantity
                                                  } 
                                           age_lines.append(age_vals)
                                        #sadfds
                                        #for 
#                                 if hotel._name=='TESTING HOTEL - Demo':
#                                     print supplement,"1111111111111111111111111",type(supplement),type(supplements),len(supplements)
#                                     print "<"*20
#                                     print supplements[1],"????????????????",supplements[1][0]
#                                     print ">"*20
                                #print supplement.PerRoomSupplement,"----------",supplement.PerPersonSupplement
                                #safsdaf
                                #if hotel._name=='TESTING HOTEL - Demo':
                                 #   print supplements,"sssssssssss000000000"
                                    #sadfsadf
                                    supplements_vals = {
                                            'supp_id' : supp._suppId,
                                            'is_mandatory' : supp._suppIsMandatory,
                                            'price' : supp._price,
                                            'supp_charge_type' : supp._suppChargeType,
                                            'supp_name' : supp._suppName,
                                            'supp_type' : supp._supptType,
                                            'type':supp_type,
                                            'rate_id' : room.id,
                                            'age_ids': [(0,0,ageval) for ageval in age_lines] }
                                    supplement_id = self.env['room.supplement'].create(supplements_vals)
                                    
                                    if supp._suppIsMandatory:
                                        room.write({'supplement_ids' : [(4,supplement_id.id)]})
                        BoardBases = occupancies.BoardBases
                        if BoardBases:
                            #if hotel._name=='TESTING HOTEL - Demo':
                             #   print BoardBases,"BBBBBBBBBBBBBBBBBBBB"
                            for bbases in BoardBases:
                                boardbase = bbases[1]
                                #if hotel._name=='TESTING HOTEL - Demo':
                                 #   print boardbase,"bbasesbbasesbbases"
                                for bbase in boardbase:
                                  #  if hotel._name=='TESTING HOTEL - Demo':
                                   #     print bbase,"*********************************"
                                    bbase_vals = {'name':bbase._bbName, 'price': bbase._bbPrice,'rate_id' : room.id,'bb_id': bbase._bbId}
                                    bbase_id = self.env['board.base'].create(bbase_vals)
                            
                #list_room_data = self.auto_select_rooms(list_room_data)       
                data['room_rates_ids'] = list_room_data
                hotel_search_result.append((0, 0, data))
                
#         if hotel_search_result:
#             self.hotel_searchresult_ids = hotel_search_result
        return hotel_search_result
    
    
    @api.one
    def generate_data_for_turico(self):
        data = {}
        if self.destination_id and self.destination_id.tourico_code \
                    and self.room_occupancy_ids:
            room_list = []
            for room in self.room_occupancy_ids:
                child_age = room.child_age
                if child_age:
                    #child_age = child_age.split(",")
                    child_age = [int(age) for age in child_age.split(",")]
                room_list.append({
                        'AdultNum' : room.adults and str(room.adults) or '0',
                        'ChildNum' : room.child and str(room.child) or '0',
                        'ChildAge' : child_age  })
            check_in = self.check_in
            check_out = self.check_out
            data = {
                    'Destination' : self.destination_id.tourico_code,
                    'RoomsInformation' : room_list,
                    'CheckIn' : check_in,
                    'CheckOut' : check_out,
                    }
        return data
    
    @api.multi
    def create_search_result(self, result):
        if type(result) == list:
            result = dict(result[0])
        if 'hotels' not in result:
             return False
        list_hotels = result.get('hotels', {}).get('hotels')
        if not list_hotels:
            return False
        hotel_search_result = []
        for hotel in list_hotels:
            occupancy = self.env['room.occupancy'].get_all_details(self.id)
            
            
            image = False#self.env['hotel.data'].get_image("", hotelbeds_code=str(hotel['code']), name=hotel['name'])
            #print image,"iiiiiiiii"
            #sssss
            data = {
                'name': hotel['name'] +  " // " + str(hotel['code']),
                'image' : image or False,
                'location' : "%s,  %s" % (hotel['zoneName'], hotel['destinationName']),
                'rate' : float(hotel['minRate']),
                'rooms' : occupancy['rooms'],
                'adults' : occupancy['adults'],
                'children' : occupancy['child'],
                'api_type' : 'HotelBeds'}
            list_room_data = []
            if hotel.get('rooms'):
                for rooms in hotel.get('rooms', []):
                    for rate in rooms.get('rates', []):
                        #print "\n"
                        #print "rooms ===>> ", rooms['name'], rate['boardName']
                        if rate.get('rateKey'):
                            room_data = {
                                  'name' : rooms['name'] + " - " + rate['boardName'],
                                  'rateKey' : rate['rateKey'],
                                  'rate' : rate['net'],
                                  'checkIn' : self.check_in,
                                  'checkOut': self.check_out,
                                  'adults' : int(rate['adults']),
                                  'children' : int(rate['children']),
                                  'default_date' : True}
                            list_room_data.append((0, 0, room_data))
                        if rate.get('shiftRates'):
                            for shiftRates in rate['shiftRates']:
                                if shiftRates.get('rateKey'):
                                    shift_data = {
                                          'name' : rooms['name'],
                                          'rateKey' : shiftRates['rateKey'],
                                          'rate' : shiftRates['net'],
                                          'checkIn' : shiftRates['checkIn'],
                                          'checkOut': shiftRates['checkOut'],
                                          'adults' : int(rate['adults']),
                                          'children' : int(rate['children']),
                                          'default_date' : False}
                                    list_room_data.append((0, 0, shift_data))
            list_room_data = self.auto_select_rooms(list_room_data)
            data['room_rates_ids'] = list_room_data
            hotel_search_result.append((0, 0, data))
#         if hotel_search_result:
#             self.hotel_searchresult_ids = hotel_search_result
        return hotel_search_result
    
    @api.multi
    def auto_select_rooms(self, list_room_data):
        booking_occupancy = self.env['room.occupancy'].get_grouped_occupancy(self.id)
        res = []
        for r, r, room_data in list_room_data:
            if room_data['default_date']:
                for booking in booking_occupancy:
                    if room_data['adults'] == booking['adults'] and \
                                            room_data['children'] == booking['children']:
                        room_data.update({'room_selection': booking['rooms']})
                        booking_occupancy.remove(booking)
             
            res.append((0, 0, room_data))
        return res
        
    @api.one
    def generate_data_for_hotelbeds(self):
        res = {}
        stay = {"checkIn": self.check_in,
                "checkOut": self.check_out}
        if self.flexible_days:
           stay['shiftDays'] = self.flexible_days
        res['stay'] = stay
        res["destination"] = {"code": self.destination_id.code}
        list_occupancies = []
        for occupancies in self.room_occupancy_ids:
            data = {"rooms": 1,
                  "adults": str(occupancies.adults),
                  "children": str(occupancies.child or 0)}
            paxes = [{"type": "AD", "age": "30"} for i in range(0, occupancies.adults)]
            
            if occupancies.child:
                if occupancies.child_age:
                   if "Example" in occupancies.child_age:
                       raise ValueError("Please enter childrens age in comma separated. Example: 5,2")
                   child_age = [int(age.strip()) for age in occupancies.child_age.split(",")]
                   if len(child_age) < occupancies.child:
                       raise ValueError("Please enter ages all of the children")
                   for age in child_age:
                       paxes = paxes + [{"type": "CH", "age": str(age)}]
            data['paxes'] = paxes
            list_occupancies.append(data)
        res['occupancies'] = list_occupancies
        return res
    
class room_occupancy(models.Model):
    _name = "room.occupancy"
    
    booking_id = fields.Many2one('book.hotels', string='Booking')
    adults = fields.Selection(list_adults, string='Adults')
    child = fields.Selection(list_child, string='Children')
    child_age = fields.Char("Children's Age")
    #occupancy_supplements = fields.one2Many('occupancy.supplement',"Supplement")
    
    @api.multi
    def name_get(self):
        result = []
        count = 0
        for occupancy in self:
            count = count + 1
            result.append((occupancy.id, "Room: %s, Adults : %s, Children : %s(%s)" % \
                           (count, occupancy.adults, occupancy.child or 0, occupancy.child_age or 0)))
        return result
    
    @api.multi
    def get_grouped_occupancy(self, booking_id=False):
        if not booking_id:
            booking_id = self.booking_id.id
        all_occupancy = self.search([('booking_id', '=', booking_id)])
        grouped_data = {}
        for occupancy in all_occupancy:
            key = (occupancy.adults, occupancy.child)
            if key in grouped_data:
                grouped_data[key] = grouped_data[key] + 1
            else:
                grouped_data[key] = 1
        res = []
        for key in grouped_data.keys():
            data = {
                    'rooms' : grouped_data[key],
                    'adults' : key[0],
                    'children' : key[1] }
            res.append(data)
        return res
    
    @api.multi
    def get_all_details(self, booking_id=False):
        if not booking_id:
            booking_id = self.booking_id.id
        rooms, adults, child  = 0, 0, 0
        all_occupancy = self.search([('booking_id', '=', booking_id)])
        rooms = len(all_occupancy)
        for occupancy in all_occupancy:
           if occupancy.adults:
                adults = adults + occupancy.adults
           if occupancy.child:
                child = child + occupancy.child
        return {"rooms" : rooms, 'adults' : adults, 'child' : child}               
    
class hotel_searchresult(models.Model):
    _name = "hotel.searchresult"
    
    @api.multi
    def book_room(self):
        if self.turico_hotelId:
            #print "TTTTTTTTTTTTTT"
            return self.book_room_turico()
        else:
            #print "HHHHHHHHHHHHHH"
            return self.book_room_hotelbeds()
        
    @api.one
    def generate_data_for_turico_prebooking(self):
        data = {}
        if self.booking_id.destination_id and self.booking_id.destination_id.tourico_code:
            room_list = []
            for room in self.room_rates_ids:
                for occup in room.occupancy_ids:
                     child_age = occup.child_age
                     if child_age:
                         child_age = [int(age) for age in child_age.split(",")]
                     room_list.append({
                             'AdultNum' : occup.adults or '0',
                             'ChildNum' : occup.child or '0',
                             'ChildAge' : child_age  })
                
                
            check_in = self.booking_id.check_in
            check_out = self.booking_id.check_out
            data = {
                    'Destination' : self.booking_id.destination_id.tourico_code,
                    'RoomsInformation' : room_list,
                    'CheckIn' : check_in,
                    'CheckOut' : check_out,
                    }
        return data
        
    @api.multi
    def turico_room_availability(self):    
        booking = self.booking_id
        data = self.generate_data_for_turico_prebooking()#self.booking_id.generate_data_for_turico()
        data = data[0]
        data['HotelId'] = self.turico_hotelId
        warning_msg = ""
        result = self.env['hotelapi.configuration'].tourico_CheckAvailabilityAndPrices(data)
        availablity_data = {}
        #print result,"R))))))))))))))))))))))))))))))))00000000000"
        for hotel_list in result.HotelList:
            for hotel in hotel_list[1]:
                occupancy = self.env['room.occupancy'].get_all_details(self.id)
                for roomtypes in hotel.RoomTypes:
                    for roomtype in roomtypes[1]:
                        availablity_data[str(roomtype._hotelRoomTypeId)] = roomtype._isAvailable
                        room_price = 0
                        for occup in roomtype.Occupancies:
                            #print "0"*30
                            #print occup[1]
                            #print "01"*30
                            for occ in occup[1]:
                                #print "!"*30
                                #print occ._bedding,">>",occ._occupPrice,roomtype._hotelRoomTypeId# = "2,1"
                                #print occ
                                #print "@"*30
                                room_price +=occ._occupPrice
        #print room_price,"PPPPPPPPPPPPPPP"
        #sadf
        
        #print "o"*100
        #print "self.turico_hotelId ==>> ", self.turico_hotelId
        #print "availablity_data    ==>> ", availablity_data
        for room in self.room_rates_ids:
            if room.occupancy_ids:
                if not availablity_data.get(room.turico_hotelRoomTypeId, False):
                    warning_msg = "%s, %s room is not available" % (warning_msg, room.name)
                    warning_msg = warning_msg.strip(",")
                    warning_msg = warning_msg.strip("")
        return warning_msg
        
                 
            
    @api.multi
    def book_room_turico(self):
        warning_msg = self.turico_room_availability()
        if warning_msg:
            raise osv.except_osv(_('Warning'), _(warning_msg))
            return False
        list_room_type_id = [rates.turico_hotelRoomTypeId for rates in self.room_rates_ids if rates.room_selection]
        #cancellationPolicies_txt = self.env['hotelapi.configuration'].turico_GetCancellationPolicies('964',
        #                                             '9814173','2017-06-07','2017-06-11')
        vals = {
            'hotel_searchresult_id' : self.id,
            'cancellation_policies' : "cancellationPolicies_txt",
            'rateComments' : "rateComments",
            'customer_id' : self.booking_id.customer_id.id,
            'customer_first_name' : self.booking_id.customer_id.name,
            'customer_last_name' : "",
            'customer_home_phone' : self.booking_id.customer_id.phone or "",
            'customer_mobile_phone' : self.booking_id.customer_id.mobile or ""}
        confirm_id = self.env['confirm.booking'].create(vals)
        #print "confirm_id ==>> ", confirm_id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'confirm.booking',
            'res_id': confirm_id.id,
            'view_mode': 'form',
            'target': 'new' }
    
    @api.multi
    def book_room_hotelbeds(self):
        hotelapi = self.env['hotelapi.configuration'].search([('type', '=', 'hotelbeds-hotels')])
        data = { "upselling": True }
        rooms = []
        for rates in self.room_rates_ids:
            if rates.room_selection:
                rooms.append({"rateKey": rates.rateKey})
        data['rooms'] = rooms
        result = {}
        try:
            result = hotelapi.hotelbeds_checkrates(data)
        except:
            raise osv.except_osv(_('Error'), _('Please try again'))
        print result,"RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR"
        if result.get('error', {}).get('message', False):
            raise osv.except_osv(_('Time OUT'), _('Please check hotels again'))
        cancellationPolicies_txt = ""
        rateComments = ""
        for rooms in result['hotel']['rooms']:
            for rate in rooms['rates']:
                rateComments = rate['rateComments']
                if rate.get('cancellationPolicies'):
                    cancellationPolicies = rate['cancellationPolicies'][0]
                    cancellationPolicies_txt = "Amount : %s, From: %s" % (cancellationPolicies['amount'],
                                                            cancellationPolicies['from'])
        vals = {
            'hotel_searchresult_id' : self.id,
            'cancellation_policies' : cancellationPolicies_txt,
            'rateComments' : rateComments,
            'customer_id' : self.booking_id.customer_id.id,
            'customer_first_name' : self.booking_id.customer_id.name,
            'customer_last_name' : "",
            }
        confirm_id = self.env['confirm.booking'].create(vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'confirm.booking',
            'res_id': confirm_id.id,
            'view_mode': 'form',
            'target': 'new' }
    
    @api.multi
    @api.depends('room_rates_ids.room_selection')
    def _compute_amount(self):
        #print "self =============>> ", self
        for search_result in self:
            for rates in search_result.room_rates_ids: 
                count = 0
                if rates.occupancy_ids:
                    for r in rates.occupancy_ids:
                        count = count + 1
                search_result.total_amount = count * rates.rate
        #self.total_amount = sum(rates.rate * len(rates.occupancy_ids) for rates in self.room_rates_ids if rates.occupancy_ids)
    
    _order = 'rate asc'
    
    booked = fields.Boolean('Booked')
    booking_id = fields.Many2one('book.hotels', string='Booking')
    name = fields.Char('Hotel Name')
    location = fields.Char('Location')
    rate = fields.Float('Rate')
    adults = fields.Integer('Adults')
    children = fields.Integer('Children')
    rooms = fields.Integer('Rooms')
    total_amount = fields.Float('Total Amount', readonly=True, compute='_compute_amount', track_visibility='always')
    room_rates_ids = fields.One2many('room.rates', 'searchresult_id', string='Rates')
    turico_hotelId = fields.Char('turico_hotelId')
    image = fields.Binary("Image")
    api_type = fields.Char('API Type')

class BoardBase(models.Model):
    _name = 'board.base'
    
    name = fields.Char(string='Name')
    price = fields.Float(string='Price')
    rate_id = fields.Many2one('room.rates', string='Rates')
    bb_id = fields.Char(string='BoardBase ID')
    
    @api.multi
    def name_get(self):
        result = []
        for bbase in self:
            result.append((bbase.id, "Name: %s, Price: %s" %(bbase.name, bbase.price)))
        return result

class room_supplement(models.Model):
    _name = "room.supplement"
    _rec_name = 'supp_name'
    
    supp_id = fields.Char(string='Supplement ID')
    is_mandatory = fields.Boolean(string='Is Mandatory')
    price = fields.Float(string='Price')
    supp_charge_type = fields.Char(string='Type')
    supp_name = fields.Char(string='Name')
    rate_id = fields.Many2one('room.rates', string='Rates')
    
    supp_type = fields.Char(string='Type')
    type = fields.Selection([('perroom','PerRoomSupplement'), ('perperson','PerPersonSupplement')], 
                       string='Supplement Type')
    age_ids = fields.One2many('supplement.agegroup','supplement_id','Supplement AgeGroup')
    
    @api.multi
    def name_get(self):
        result = []
        for supp in self:
            result.append((supp.id, "Name: %s, Price: %s, Mandatory: %s, Type: %s" % \
                           (supp.supp_name, supp.price, supp.is_mandatory, supp.supp_charge_type)))
        return result
    
class SupplementAgeGroup(models.Model):
    _name = "supplement.agegroup" 
    _rec_name =  'supp_from'
    
    supp_from = fields.Char(string='Supp From')
    supp_to = fields.Char(string='Supp To')
    supp_qty = fields.Char(string='Supp Qty') 
    supplement_id = fields.Many2one('room.supplement', 'Supplement') 
    
    
class room_rates(models.Model):
    _name = "room.rates"
    _order = 'checkIn asc,name asc,adults asc,children asc'
    
    searchresult_id = fields.Many2one('hotel.searchresult', string='Hotel Search Result')
    name = fields.Char('Room')
    rateKey = fields.Char('RateKey')
    checkIn = fields.Date('Check In')
    checkOut = fields.Date('Check Out')
    rate = fields.Float('Rate')
    
    base_rate = fields.Float('Base Rate')
    
    adults = fields.Integer('Max Adults')
    children = fields.Integer('Max Children')
    cancellation_policies = fields.Char('Cancellation Policies')
    room_selection = fields.Selection(list_room_selection, string='Select Room')
    default_date = fields.Boolean(string='Default Date')
    
    turico_roomId = fields.Char('Turico RoomId')
    turico_hotelRoomTypeId = fields.Char('Turico HotelRoomTypeId')
    currency = fields.Char('Currency')
    booking_id = fields.Many2one('book.hotels', string='Booking', related='searchresult_id.booking_id')
    occupancy_ids = fields.Many2many('room.occupancy', string='Select')
    supplement_ids = fields.Many2many('room.supplement', string='Supplements')
    boardbase_ids = fields.Many2many('board.base', string='Board Bases')
    
    @api.onchange('occupancy_ids', 'supplement_ids','boardbase_ids')
    def onchange_rates(self):
        rate = self.base_rate
        if self.supplement_ids:
            for supplement in self.supplement_ids:
                if supplement.supp_charge_type == 'Addition':
                    rate = supplement.price + rate
        if self.boardbase_ids:
            for bbase in self.boardbase_ids:
                rate+= bbase.price
        self.rate = rate
        
        
    
    
class confirm_booking(models.Model):
    _name = "confirm.booking"
    
    customer_id = fields.Many2one('res.partner', string='Customer')
    hotel_searchresult_id = fields.Many2one('hotel.searchresult', string='Room Rates')
    customer_first_name = fields.Char('First Name', required=True)
    customer_last_name = fields.Char('Surname', required=True)
    customer_home_phone = fields.Char('Home Phone')
    customer_mobile_phone = fields.Char('MobilePhone')
    cancellation_policies = fields.Char('Cancellation Policies')
    rateComments = fields.Text('rateComments')
    comments = fields.Char('Comments')
    
    @api.multi
    def confirm_booking(self):
        if self.hotel_searchresult_id.turico_hotelId:
            return self.confirm_booking_turico()
        else:
            return self.confirm_booking_hotelbeds()
        
        
    @api.multi
    def confirm_booking_turico(self):
        #print "0"*100
        data = {}
        #result = self.env['hotelapi.configuration'].tourico_BookHotel(data)
        
        wsdl = "http://demo-hotelws.touricoholidays.com/hotelflow.svc?wsdl"
        client = suds.client.Client(wsdl,headers={'Accept-Encoding': 'gzip'})
        service = client.service
        login_name, password = self.env['hotelapi.configuration'].get_turico_hotelflow()
        LoginName  = Element('LoginName').setText(login_name)
        Password = Element('Password').setText(password)
        Culture = Element('Culture').setText('en_US')
        Version = Element('Version').setText('7.123')
        AuthenticationHeader = Element('AuthenticationHeader') 
        AuthenticationHeader.attributes.append(Attribute('xmlns', 'http://schemas.tourico.com/webservices/authentication'))
        AuthenticationHeader.children = [LoginName, Password, Culture, Version]
        client.set_options(soapheaders=[AuthenticationHeader])
        #print client,"ccccccccccccccccccc"
        
        data['FirstName'] = self.customer_first_name
        data['LastName'] = self.customer_last_name
        data['HomePhone'] = self.customer_home_phone or ""
        data['MobilePhone'] = self.customer_mobile_phone or ""

        contact_passenger = client.factory.create('ns4:ContactPassenger')
        contact_passenger.FirstName = data['FirstName']
        contact_passenger.LastName = data['LastName']
        contact_passenger.MiddleName = ""
        contact_passenger.HomePhone = data['HomePhone']
        contact_passenger.MobilePhone = data['MobilePhone']
        
        hotel = self.hotel_searchresult_id
        booked_hotel = []
        booking_error = ""
        for room_rate in hotel.room_rates_ids:
            if room_rate.occupancy_ids:
                array_ofroomreserveinfo = client.factory.create('ns4:ArrayOfRoomReserveInfo')
                supplement_total = 0
                for occupancy in room_rate.occupancy_ids:
                    #print occupancy,"00000000000000000000000000000"
                    room_reserveinfo = client.factory.create('ns4:RoomReserveInfo')
                    room_reserveinfo.ContactPassenger = contact_passenger
                    room_reserveinfo.RoomId = room_rate.turico_roomId
                    room_reserveinfo.AdultNum = occupancy.adults or 0
                    room_reserveinfo.ChildNum = occupancy.child or 0
                    if occupancy.child_age:
                        ArrayOfChildAge = client.factory.create('ns4:ArrayOfChildAge')
                        for age in [int(age) for age in occupancy.child_age.split(',')]:
                            ChildAge = client.factory.create('ns4:ChildAge')
                            ChildAge._age = age
                            ArrayOfChildAge.ChildAge.append(ChildAge)
                        room_reserveinfo.ChildAges = ArrayOfChildAge
                        
                    ArrayOfSupplementInfo = client.factory.create('ns4:ArrayOfSupplementInfo')
                    
                    if room_rate.supplement_ids:
                        #print "RRRRRRRRRRRRRRRRRRRRRRRRR"
                        for supplement in room_rate.supplement_ids:
                            #print supplement.is_mandatory,supplement.supp_charge_type,"2222222222@@@@@@@"
                            if supplement.supp_charge_type=='Addition':
                                #if supplement.supp_type=='perroom':
                                 #   print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",supplement.price
                                    supplement_total+=supplement.price
                                #elif supplement.supp_type=='perperson':
                                 #   supplement_total+=supplement.
                            
                                
                                
                            SupplementInfo = client.factory.create('ns4:SupplementInfo')
                            
                            SupplementInfo._suppId = supplement.supp_id
                            SupplementInfo._supTotalPrice = supplement.price
                            SupplementInfo._suppType = supplement.supp_type
                            
                            ArrayOfSuppAges = client.factory.create('ns4:ArrayOfSuppAges')
                            if supplement.type=='perperson':
                                #print "xxxxxxxxxxx"
                                child=False
                                tot_num = 0
                                for age in supplement.age_ids:
                                    if int(age.supp_from)==1:
                                        child=True
                                        if int(age.supp_from)>50:
                                         
                                            child=False
                                    if child:
                                        tot_num = occupancy.adults
                                    else:
                                        tot_num = occupancy.adults+occupancy.child
                                    #print  tot_num,"tot_num" 
                                    SuppAge = client.factory.create('ns4:SuppAges')
                                    SuppAge._suppFrom=age.supp_from
                                    SuppAge._suppTo=age.supp_to
                                    SuppAge._suppQuantity=tot_num
                                
                                #print ArrayOfSuppAges
                                ArrayOfSuppAges.SuppAges.append(SuppAge)
                                #print SupplementInfo
                                SupplementInfo.SupAgeGroup=ArrayOfSuppAges
                            ArrayOfSupplementInfo.SupplementInfo.append(SupplementInfo)
                    ArrayOfBoardbase = client.factory.create('ns4:ArrayOfBoardbase')
                    if room_rate.boardbase_ids:
                        board_base_total = 0
                        #print ArrayOfBoardbase,"AAAAAAAAAAA"
                        for bbase in room_rate.boardbase_ids:
                            board_base_total += bbase.price
                            Boardbase = client.factory.create('ns4:Boardbase')
                            Boardbase._bbName = bbase.name
                            #Boardbase._bbPrice = bbase.price
                            Boardbase._bbPublishPrice = bbase.price
                            #print Boardbase
                            Boardbase._bbId = bbase.bb_id
                            Boardbase._bbPrice = bbase.price
                            ArrayOfBoardbase.Boardbase.append(Boardbase)
                    
                    room_reserveinfo.SelectedSupplements = ArrayOfSupplementInfo
                    #print ArrayOfBoardbase,"AAAAAAAAAA"
                    room_reserveinfo.SelectedBoardBase = ArrayOfBoardbase
                    array_ofroomreserveinfo.RoomReserveInfo.append(room_reserveinfo)
                #print array_ofroomreserveinfo
                #print  supplement_total,"SSSSSSSSSSSSTTTTTTTTTTTTTTT",room_rate.rate,len(room_rate.occupancy_ids)
                request = client.factory.create('ns4:BookV3Request')
                request.RoomsInfo = array_ofroomreserveinfo
                request.HotelId = hotel.turico_hotelId
                request.HotelRoomTypeId = room_rate.turico_hotelRoomTypeId
                request.CheckIn = hotel.booking_id.check_in
                request.CheckOut = hotel.booking_id.check_out
                request.AgentRefNumber = "odoo100"
                request.ContactInfo = "9814253665"
                request.RequestedPrice = room_rate.rate * len(room_rate.occupancy_ids)+supplement_total
                request.DeltaPrice = 0
                request.Currency = room_rate.currency
                request.IsOnlyAvailable = True
                request.ConfirmationEmail = "chandhuviswanath@zbeaztech.com"
                request.ConfirmationLogo = ""
                request.RecordLocatorId = 0
                request.PaymentType = 'Obligo'
                #print "<>"*50
                #print "request ==>> ", request
                try:
                    result = client.service.BookHotelV3(request)
                    #print client.last_sent()
                    #print "[["*50
                    #print client.last_received()
                    #print "]]"*50
                    booked_list = self.create_hotel_booking_turico(result)
                    booked_hotel = booked_hotel + booked_list 
                except suds.WebFault as detail:
                    #print "------------------>><<>>> ", client.last_sent()
                    booking_error = "%s, %s" % (booking_error, detail)
         
        if booking_error:
            booking_error = booking_error.strip(",")
            booking_error = booking_error.strip("")
            raise osv.except_osv(_('Booking Issues'), _(booking_error))           
        if booked_hotel:
            #booked_ids = [booked.id for booked in booked_hotel]
            return self.generate_redirect_view_return_turico(booked_hotel)
        return True
    
    def generate_redirect_view_return_turico(self, res_id):
        #mod_obj = self.pool.get('ir.model.data')
        mod_obj = self.env["ir.model.data"]
        #act_obj = self.pool.get('ir.actions.act_window')
        act_obj = self.env["ir.actions.act_window"]
        
        result = mod_obj.get_object_reference('hotel_booking_api', 'action_booked_hotels')
        id = result and result[1] or False
        
        result = act_obj.browse(id).read()[0]
        
        #print "LLLLLLLL ==>> ", result
        #result = act_obj.read(cr, uid, [id], context=context)[0]

        res = mod_obj.get_object_reference('hotel_booking_api', 'booked_hotels_view_form')
        result['views'] = [(res and res[1] or False, 'form')]
        result['res_id'] = res_id or False
        #registry = openerp.modules.registry.RegistryManager.new(cr.dbname, update_module=True)
        #menu_obj = registry['ir.ui.menu']
        menu_obj = self.env['ir.ui.menu']
        menu_ids = menu_obj.search([('name', '=', "Booked Hotels")])
        data = {'type': 'ir.actions.client',
           'tag': 'reload',
           'params': {'menu_id': menu_ids and menu_ids[0].id or False}}
        
        #print "data =====>>> ", data
        return data
    
    @api.multi
    def create_hotel_booking_turico(self, result):
       
       #print "\n\n\n"
       #print "c"*50
       
       #print result
       #print "c"*50
       ResGroup = result.ResGroup
       booked_list = []
       for reservations in ResGroup.Reservations:
           #print "========>> ", reservations[1]
           res = {}
           list_room_data = []
           
           for reservation in reservations[1]:
             HotelInfo = reservation.ProductInfo
             RoomExtraInfo = HotelInfo.RoomExtraInfo
             RoomInfo = RoomExtraInfo.RoomInfo
             SelectedSupplements = RoomExtraInfo.SelectedSupplements
             list_supp_data = []
             for supp in SelectedSupplements:
                 supplement = supp[1]
                 for supp_val in supplement:
                     supp_vals={'name':supp_val._suppName,
                                'price': supp_val._price
                                }
                     list_supp_data.append((0, 0, supp_vals))
             room_data = {
              'status' : reservation._status,
              'name' : HotelInfo._roomType,
              'rate': reservation._price,
              'reservationId' : reservation._reservationId,
              'tranNum' : reservation._tranNum,
              'adults': RoomInfo.AdultNum,
              'children': RoomInfo.ChildNum,
              'supplement_ids':list_supp_data
              }
             list_room_data.append((0, 0, room_data))
             if not res:
                 res = {'hotel' : HotelInfo._name,     
                          'check_in' : reservation._fromDate,
                          'check_out' : reservation._toDate,
                          'destinationName' : HotelInfo._address,
#                           'reservationId' : reservation._reservationId,
#                           'tranNum' : reservation._tranNum,
                          'name' : '/',
                          'currency' : ResGroup._currency,
                          'totalNet' : ResGroup._totalPrice,
                          'remark' : ResGroup._rgRemark,
                          'booked_user_id' : self.env.uid,
                          'state' : 'confirmed',
                          'customer_id' : self.customer_id.id,
                          'reference' : ResGroup._tranNum,
                          'pendingAmount' : 0,
                          'creationDate' : fields.Datetime.now(),
                          'remark' : ResGroup._rgRemark,
                          'booking_type' : 'tourico_hotels',
                          'booked_rooms' : [],
                          
                          'holder_name' : self.customer_first_name,
                          'holder_surname' : self.customer_last_name
                          }
           res['booked_rooms'] = list_room_data  
           booked = self.env['booked.hotels'].create(res)
           booked_list.append(booked.id)
       return booked_list
    
    
    
    @api.multi
    def confirm_booking_hotelbeds(self):
        data = {}
        rooms = []
        for rates in self.hotel_searchresult_id.room_rates_ids:
            if rates.room_selection:
                rooms.append({"rateKey": rates.rateKey})
        data['rooms'] = rooms
        data['holder'] = {
                "name": self.customer_first_name,
                "surname": self.customer_last_name }
        data.update({ "clientReference": "Apitude web ref",
          "remark": self.comments or "" })
        hotelapi = self.env['hotelapi.configuration'].search([('type', '=', 'hotelbeds-hotels')])
        result = hotelapi.confirm_booking(data)
        result = result or {}
        booking_status = False
        if result.get('booking', {}).get('status'):
            booking_status = result['booking']['status']
        #print "D>>>>>>>>>>",data
        #print "----------------"   
        #print "result      =============>> ", result
        booked = self.create_hotel_booking(result)
        #self.hotel_searchresult_id.booked = True
        return self.generate_redirect_view_return(booked.id)
    
    @api.multi   
    def generate_redirect_view_return(self, res_id):
#         mod_obj = self.pool.get('ir.model.data')
#         act_obj = self.pool.get('ir.actions.act_window')
#         
#         result = mod_obj.get_object_reference(cr, uid, 'hotel_booking_api', 'action_booked_hotels')
#         id = result and result[1] or False
#         result = act_obj.read(cr, uid, [id], context=context)[0]
# 
#         res = mod_obj.get_object_reference(cr, uid, 'hotel_booking_api', 'booked_hotels_view_form')
#         result['views'] = [(res and res[1] or False, 'form')]
#         result['res_id'] = res_id or False
#         registry = openerp.modules.registry.RegistryManager.new(cr.dbname, update_module=True)
#         menu_obj = registry['ir.ui.menu']
#         menu_ids = menu_obj.search(cr, uid, [('name', '=', "Booked Hotels")], context=context)
#         data = {'type': 'ir.actions.client',
#            'tag': 'reload',
#            'params': {'menu_id': menu_ids and menu_ids[0] or False}}
        
        menu_obj = self.env['ir.ui.menu']
        menu_ids = menu_obj.search([('name', '=', "Booked Hotels")])
        data = {'type': 'ir.actions.client',
           'tag': 'reload',
           'params': {'menu_id': menu_ids and menu_ids[0].id or False}}
        
        return data
        
    @api.multi
    def create_hotel_booking(self, result):
       result = result or {}
       if not result.get('booking'):
           return False
       booking = result['booking'] 
       res = {
              'name' : '/',
              'reference' : booking['reference'],
              'currency' : booking['currency'],
              'pendingAmount' : booking['pendingAmount'],
              'creationDate' : booking['creationDate'],
              'totalNet' : booking['totalNet'],
              'remark' : booking.get('remark', ""),
              'holder_name' : booking['holder']['name'],
              'holder_surname' : booking['holder']['surname'],
              'modification' : booking['modificationPolicies']['modification'],
              'cancellation' : booking['modificationPolicies']['cancellation'],
              'booked_user_id' : self.env.uid,
              'state' : 'confirmed',
              'customer_id' : self.customer_id.id }
       hotel = booking['hotel']
       res.update({
              'hotel' : hotel['name'],     
              'check_in' : hotel['checkIn'],
              'check_out' : hotel['checkOut'],
              'destinationName' : hotel['destinationName'],
              'latitude' : hotel['latitude'],
              'longitude' : hotel['longitude'],
              #'supplier_name' : hotel['supplier']['name'],
              #'supplier_vatNumber' : hotel['supplier']['vatNumber'] 
              })
       booked_rooms = []
       for rooms in hotel['rooms']:
           room_data = {
              'status' : rooms['status'],
              'name' : rooms['name'],
              'rate': rooms['rates'][0]['net']}
           booked_rooms.append([0, 0, room_data])
       if booked_rooms:
           res['booked_rooms'] = booked_rooms
       return self.env['booked.hotels'].create(res)
       
        
    
    
    
