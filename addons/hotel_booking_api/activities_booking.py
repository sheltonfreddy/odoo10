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
import suds.client
from suds.sax.element import Element
from suds.sax.attribute import Attribute
import datetime

list_person_selection = [(n, n) for n in range(1, 10)]

class acivity_booking(models.Model):
    _name = "acivity.booking"
    
    destination_id = fields.Many2one('hotel.location', string='Destination', required=True)
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    from_date = fields.Date(string='From')
    to_date = fields.Date(string='To')
    activities_searchresult_ids = fields.One2many('activities.searchresult', 'booking_id', string='Activities')
    person_selection = fields.Selection(list_person_selection, string='Select Person')
    person_ages = fields.Char("Ages")
    
    @api.multi
    def search_acivity(self):
        try:
            ages = [int(age) for age in self.person_ages.split(",")]
            if len(ages) != self.person_selection:
                raise osv.except_osv(_('Error'), _('Please check person selection and ages'))
        except:
            raise osv.except_osv(_('Error'), _('Please check person selection and ages'))
        self.search_acivity_turico()
        #self.search_activity_hotelbeds()
        return True
    
    @api.multi
    def search_acivity_turico(self):
        result = self.get_acivity_turico()
        
        if not result and result.Categories:
            return False
        list_search_result = []
        for Categories in result.Categories:
            for Category in Categories[1]:
                for Activities in Category.Activities:
                    for Activity in Activities[1]:
                        #print Category._categoryName, " : ", Activity._name 
                        
                        #print "\n\n\n\n", Activity
                        #if Activity._activityId==1262659:
                         #   print "\n"*40
                          #  print Activity,type(Activity._activityId)
                           # print "\n"*40
                        search_data = {
                          'name' : Activity._name,# +' '+ str(Activity._activityId),
                          'code' : "",
                          #'rates_ids' : list_rates,
                          'amount' : 0,
                          'destination' : Activity.Location._address,
                          'currency' : Activity._currency,
                          'description' : Activity._description,
                          'type' : "turico",
                          
                          'turico_activityId' : Activity._activityId
                          
                          }
                        if Activity._thumbURL:
                            search_data['image'] = self.env['data.storage'].get_image("", Activity._thumbURL, 'activities')
                        
                        search = self.env['activities.searchresult'].create(search_data)
                        
                        list_search_result.append((4, search.id))
                        
                        for ActivityOptions in Activity.ActivityOptions:
                            for ActivityOption in ActivityOptions[1]:
                                #print "ActivityOption ===>> ", ActivityOption
                                
                                for Availabilities in ActivityOption.Availabilities:
                                    for Availability in Availabilities[1]:
                                        #print "Availability ===>> ", Availability
                                        val_avail = {
                                                    'booking_id' : self.id,
                                                    'searchresult_id' : search.id,
                                                    'to_Date' : Availability._toDate,
                                                    'child_Price' : Availability._childPrice,
                                                    'max_Children' : Availability._maxChildren,
                                                    'from_Date' : Availability._fromDate,
                                                    'adult_Price' : Availability._adultPrice,
                                                    'unit_price' : Availability._unitPrice,
                                                    'max_Adults' : Availability._maxAdults,
                                                    'type' : ActivityOption._type,
                                                    'name' : ActivityOption._name,
                                                    'optionId' : ActivityOption._optionId }
                                        self.env['activities.turico_availabilities'].create(val_avail)
                                        
                                        
                                
                        
                        
                    
            
            #print "*"*50
            #print "\n\n\n"
        
        
        if self.activities_searchresult_ids:
            self.activities_searchresult_ids = False
        self.activities_searchresult_ids = list_search_result    
        return True
        
        
    
    
    @api.multi
    def get_acivity_turico(self):
        import suds.client
        from suds.sax.element import Element
        from suds.sax.attribute import Attribute
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
        request = client.factory.create("ns1:SearchActivityByDestinationIdsRequest")
        ArrayOfInt = client.factory.create("ns1:ArrayOfInt")
        ArrayOfInt.int.append(self.destination_id.tourico_destinationId)
        request.destinationIds = ArrayOfInt
        request.fromDate = self.from_date
        request.toDate = self.to_date
        DestinationResultsFilters = client.factory.create("ns1:DestinationResultsFilters")
        MinAdultsFilter = client.factory.create("ns1:MinAdultsFilter")
        MinAdultsFilter.Value = 0
        MinChildrenFilter = client.factory.create("ns1:MinChildrenFilter")
        MinChildrenFilter.Value = 0
        MinUnitsFilter = client.factory.create("ns1:MinUnitsFilter")
        MinUnitsFilter.Value = 0
        DestinationResultsFilters.MinAdults = MinAdultsFilter
        DestinationResultsFilters.MinChildren = MinChildrenFilter
        DestinationResultsFilters.MinUnits = MinUnitsFilter
        request.filters = DestinationResultsFilters
        result = client.service.SearchActivityByDestinationIds(request)
        return result
        
    
    @api.multi
    def create_search_result(self, data):
        
        data = data or {}
        list_search_result = []
        for activities in data.get('activities', []):
            list_rates = []
            for modalities in activities.get('modalities', []):
                duration = modalities['duration']
                cancellationPolicies = modalities.get('cancellationPolicies', [{}])[0]
                cancellationPolicies_txt = ""
                for key in cancellationPolicies.keys():
                    cancellationPolicies_txt = "%s, %s: %s" % (cancellationPolicies_txt, 
                                                key, cancellationPolicies[key])
                cancellationPolicies_txt = cancellationPolicies_txt.strip(',').strip('')
                for amountsFrom in modalities.get('amountsFrom', []):
                    data_modalities = {
                            'type' :  amountsFrom['paxType'],
                            'ageFrom' :  amountsFrom['ageFrom'],
                            'amount' :  "%s  %s" % (amountsFrom['amount'], activities['currency']),
                            'ageTo' :  amountsFrom['ageTo'],
                            'duration' : "%s %s" % (duration['value'], duration['metric']),
                            'code' : modalities['code'],
                            'name' : modalities['name'],
                            'cancellationPolicies' : cancellationPolicies_txt,
                             }
                    list_rates.append((0, 0, data_modalities))
            country = activities.get("country", {})
            amountsFrom = activities.get("amountsFrom", [{}])[0]
            content = activities.get("content", {})
            search_data = {
              'name' : activities['name'],
              'code' : activities['code'],
              'rates_ids' : list_rates,
              'amount' : amountsFrom.get("amount"),
              'destination' : "%s, %s" % (country["destinations"][0]['name'], country["name"]),
              'currency' : activities['currency'],
              'description' : content['description']
              
              }
            url = self.get_image_url(content['media'])
            if url:
                search_data['image'] = self.env['data.storage'].get_image(activities['code'], url, 'activities')
            #print "----------------------------------"
            
            list_search_result.append((0, 0, search_data))
        if self.activities_searchresult_ids:
            self.activities_searchresult_ids = False
        self.activities_searchresult_ids = list_search_result
        return True
    
    
    def get_image_url(self, data):
        if not data:
            return False
        url = ""
        list_images = data.get("images")
        for images in list_images:
            urls = images['urls'][0]
            if urls["sizeType"] == "XLARGE":
                url = urls['resource']
                break
        return url
        
        
    
    
    
    @api.multi
    def generate_data_for_hotelbeds_activities(self):
        data = {
             "filters": [{"searchFilterItems": [{"type": "destination", "value": self.destination_id.code}]}],
             "from": self.from_date,
             "to": self.to_date,
             "language": "en",
             "order": "DEFAULT",
             #"pagination": { "itemsPerPage": 2, "page": 1}
                }
        return data
    
class activities_turico_availabilities(models.Model):
    _name = "activities.turico_availabilities"
    
    _rec_name = 'from_Date'
    
    booking_id = fields.Many2one('acivity.booking', string='Booking')
    searchresult_id = fields.Many2one('activities.searchresult', string='Search Result')
    to_Date = fields.Date('To Date')
    child_Price = fields.Float('Child Price')
    max_Children = fields.Integer('Max Children')
    from_Date = fields.Date('From Date')
    adult_Price = fields.Float('Adult Price')
    max_Adults = fields.Integer('Max Adults')
    type = fields.Char('Type')
    name = fields.Char('Name')
    optionId = fields.Integer('Option Id')
    unit_price = fields.Float('Unit Price')
    @api.multi
    def name_get(self):
        result = []
        for avail in self:
            if avail.name:
                result.append((avail.id, (avail.from_Date) + ' (' + avail.name + ')'))
            else:
                result.append((avail.id, avail.from_Date))
        return result
    
class activities_searchresult(models.Model):
    _name = "activities.searchresult"
    
    booking_id = fields.Many2one('acivity.booking', string='Booking')
    availabilities_id = fields.Many2one('activities.turico_availabilities', string='Availabile Dates')
    name = fields.Char('Name')
    code = fields.Char('Code')
    amount = fields.Float('From Amount')
    destination = fields.Char('Destination')
    currency = fields.Char('Currency')
    description = fields.Text(string = "Description")
    image_count = fields.Float("Image Count")
    image = fields.Binary("Image")
    type = fields.Char('Type', default="hotelbeds")
    turico_activityId = fields.Char('Turico ActivityId')
    
    
    child_Price = fields.Float('Child Price')
    adult_Price = fields.Float('Adult Price')
    unit_price = fields.Float('Unit Price')
    availabilities_type = fields.Char('Type')
    
    num_of_adults = fields.Selection(list_person_selection, string='Num Of Adults')
    num_of_children = fields.Selection(list_person_selection, string='Num Of Children')
    
    turico_detailed = fields.Boolean("Turico Detailed", default=False)
    ext_description = fields.Text(string = "Description")
    
    image_ids = fields.Many2many('data.storage', string='Images')
    
    @api.multi
    def turico_show_deatils(self):
        import suds.client
        from suds.sax.element import Element
        from suds.sax.attribute import Attribute
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
        
        #print "client ==>> ", client
        
        
        ArrayOfActivityId = client.factory.create('ns4:ArrayOfActivityId')
        #print "ArrayOfActivityId ==>> ", ArrayOfActivityId
        ActivityId = client.factory.create('ns1:ActivityId')
        #print "ActivityId ==>> ", ActivityId
        ActivityId._id = self.turico_activityId
        ArrayOfActivityId.ActivityId.append(ActivityId)
        
        result = client.service.GetActivityDetails(ArrayOfActivityId)
        #print 'Result ==>> ', result
        self.turico_detailed = True
        image_list = []
        for ActivitiesDetails in result.ActivitiesDetails.ActivityDetails:
            
            
            LongDescription = ActivitiesDetails.Description.LongDescription
            #ext_description = LongDescription.VoucherRemarks._desc
            ext_description = ""
            #print "\n\n\nLongDescription ==>> ", LongDescription
            
            
            for DescriptionFragment in LongDescription.Fragments.DescriptionFragment:
                
                ext_description = "%s%s"%(ext_description, DescriptionFragment._value)
                
            for Media in ActivitiesDetails.Media.Images.Image:
                #print "Media._path =======>> ", Media._path
                data_storage = self.env['data.storage'].save_image(self.code, Media._path, 'activities')
                image_list.append((4, data_storage.id))
            self.ext_description = ext_description
        self.image_ids = image_list
    
    @api.multi
    def PreBook_turico(self):
        import suds.client
        from suds.sax.element import Element
        from suds.sax.attribute import Attribute
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
        PreBookRequest = client.factory.create('ns1:PreBookRequest')
        ArrayOfPreBookOption = client.factory.create("ns1:ArrayOfPreBookOption")
        PreBookOption = client.factory.create("ns1:PreBookOption") 
        PreBookOption.ActivityId = self.turico_activityId
        PreBookOption.Date = self.availabilities_id.from_Date
        PreBookOption.OptionId = self.availabilities_id.optionId
        if self.availabilities_id.type=='PerUnit':
            PreBookOption.NumOfUnits = 1
            PreBookOption.NumOfAdults = 0
            PreBookOption.NumOfChildren = 0
        else:
            PreBookOption.NumOfUnits = 0
            PreBookOption.NumOfAdults = self.num_of_adults
            PreBookOption.NumOfChildren = self.num_of_children or 0
        ArrayOfPreBookOption.PreBookOption.append(PreBookOption)
        PreBookRequest.bookActivityOptions = ArrayOfPreBookOption
        
        #print PreBookRequest,"PPPPPPPPPPPPPPPPPPPPPPP"
        result = client.service.ActivityPreBook(PreBookRequest)
        return result
      
    
    
    @api.onchange('availabilities_id')
    def onchange_date_flexible(self):
        res = {}
        if self.availabilities_id:
            self.child_Price = self.availabilities_id.child_Price
            self.adult_Price = self.availabilities_id.adult_Price
            self.unit_price = self.availabilities_id.unit_price
            self.availabilities_type = self.availabilities_id.type
        else:
            self.child_Price = 0.0
            self.adult_Price = 0.0
            self.availabilities_type = ""
        return res
    
    @api.multi
    def show_rates(self):
        vals = {
              "code": self.code,
              "from": self.booking_id.from_date,
              "to": self.booking_id.to_date,
              "language": "en" } 
        ages = [{'age' : int(age)} for age in self.booking_id.person_ages.split(",")]
        vals['paxes'] = ages
        hotelapi = self.env['hotelapi.configuration'].search([('type', '=', 'hotelbeds-activity')])
        data = hotelapi.activity_detail_request(vals)
        activities_deatils = self.create_activities_deatils(data)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'activities.deatils',
            'res_id': activities_deatils.id,
            'view_mode': 'form',
            'target': 'new' }
     
    @api.multi    
    def create_activities_deatils(self, data):
        activity = data['activity']
        operationDays = activity['operationDays']
        operationDays_txt = ""
        for day in operationDays:
            operationDays_txt = "%s, %s" % (operationDays_txt, day['name'])
        operationDays_txt = operationDays_txt.strip("").strip(",")
        vals = {
            'code' : activity['code'],  
            'days' : operationDays_txt,
            'searchresult_id' : self.id }
        list_rates = []
        for modality in activity['modalities']:
            list_questions = []
            for questions in modality.get("questions", []):
                questions_data = { 'text' : questions['text'],
                        'code' : questions['code'],
                        'required' : questions['required']}
                list_questions.append((0, 0, questions_data))
            vals['questions_ids'] = list_questions
            for rates in modality['rates']:
                for rateDetails in rates['rateDetails']:
                    rateKey = rateDetails['rateKey']
                    paxAmounts_txt = ""
                    list_operationDates = []
                    for operationDates in rateDetails['operationDates']:
                        cancellationPolicies_txt = ""
                        for cancellationPolicies in operationDates['cancellationPolicies']:
                            cancellationPolicies_txt = "%s, Amount : %s From : %s" %(cancellationPolicies_txt,
                                    cancellationPolicies['amount'], cancellationPolicies['dateFrom'])
                        od_vals = {
                           'from_date' : operationDates['from'],
                           'to_date' : operationDates['to'],
                           'cancellationPolicies' :  cancellationPolicies_txt.strip(",").strip("")}
                        list_operationDates.append((0, 0, od_vals))
                    for paxAmounts in rateDetails['paxAmounts']:
                        paxAmounts_txt = "%s, %s(age %s to %s) : %s" % (paxAmounts_txt, 
                                paxAmounts['paxType'], paxAmounts['ageFrom'], paxAmounts['ageTo'], 
                                paxAmounts['amount'])
                    #for sessions in rateDetails.get('sessions', []):
                     #   print "\n\nssssssssss ====>> ", sessions
                    paxAmounts_txt = paxAmounts_txt.strip(",").strip("")
                    vals['total_amount'] = rateDetails['totalAmount']['amount']
                    vals['paxAmounts'] = paxAmounts_txt
                    vals['operationDates_ids'] = list_operationDates
                    vals['paxdata'] = str(rateDetails['paxAmounts'])
                    vals['rateKey'] = rateKey
        return self.env['activities.deatils'].create(vals)
    
    
    @api.multi
    def book_turico(self):
        result = self.PreBook_turico()
        option = result.ActivitiesSelectedOptions
        #print "TotalPrice ==>> ", option._totalPrice
        unit_amount = 0
        unit_numbers = 0
        adult_amount = 0
        adult_numbers = 0
        child_amount = 0
        child_numbers = 0
        
        questions_list = []
        cancellationPenalties_list = []
        for ActivitiesInfo in option.ActivitiesInfo:
            
            for ActivityInfo in ActivitiesInfo[1]:
                #print "ActivityInfo ==>> ", ActivityInfo
                
                PriceBreakdown = ActivityInfo.ActivityPricing.PriceBreakdown
                #print PriceBreakdown,"PriceBreakdown"
                unit_amount = 0
                unit_numbers = 0
                if hasattr(PriceBreakdown, 'Unit'):
                    unit_amount = PriceBreakdown.Unit._amount
                    unit_numbers = PriceBreakdown.Unit._numbers
                adult_amount = 0
                adult_numbers = 0
                if hasattr(PriceBreakdown, 'Adult'):
                    adult_amount = PriceBreakdown.Adult._amount
                    adult_numbers = PriceBreakdown.Adult._numbers
                child_amount = 0
                child_numbers = 0
                #print "+++++++++++++++++++++++++++++++++++++++++>>>>>>>>>>>>>>>>>>>>",PriceBreakdown
                if hasattr(PriceBreakdown, 'Child'):
                #if PriceBreakdown.get('Child'):
                    child_amount = PriceBreakdown.Child._amount
                    child_numbers = PriceBreakdown.Child._numbers
                #if hasattr(PriceBreakdown, 'Unit'):
                 #   PriceBreakdown.Unit._amount = 0
                  #  PriceBreakdown.Unit._numbers = 0
                
                CancellationPenalties = ActivityInfo.CancellationPolicy.CancellationPenalties
                for CancellationPenalty in CancellationPenalties.CancellationPenalty:
                    #print "CancellationPenalty ==>> ", CancellationPenalty
                    cancellationPenalties_vals = {
                        'offsetUnit' : CancellationPenalty.Deadline._offsetUnit,
                        'unitsFromCheckIn' : CancellationPenalty.Deadline._unitsFromCheckIn,
                        'basisType' : CancellationPenalty.Penalty._basisType, 
                        'value' : CancellationPenalty.Penalty._value }
                    cancellationPenalties_list.append((0, 0, cancellationPenalties_vals))
                
            
                ActivityAdditions = ActivityInfo.ActivityAdditions
                for TextAdditions in ActivityAdditions.TextAdditions:
                    for TextAddition in TextAdditions[1]:
                        qest_vals = {
                                'additionTypeID' : TextAddition._additionTypeID,
                                'text' : TextAddition._additionType,
                                'required' : True }
                        questions_list.append((0, 0, qest_vals))
        
#         for TextAddition in ActivityAdditions.TextAdditions:
#             print "TextAddition ==>> ", TextAddition
        
        vals = {
             'type' : 'turico',
             'total_amount' :  option._totalPrice,  
             'total_tax' : option._totalTax,
             'questions_ids' : questions_list,
             'currency' : option._currency,
             'total_amount_txt' : "%s %s" % (str(option._totalPrice), option._currency),
             'searchresult_id' : self.id,
             'unit_amount': unit_amount,
             'unit_numbers': unit_numbers,
             'adult_amount' : adult_amount,
             'adult_numbers' : adult_numbers,
             'child_amount' : child_amount,
             'child_numbers' : child_numbers,
             'turico_cancellation_ids' : cancellationPenalties_list
                }
        
        activities_deatils = self.env['activities.deatils'].create(vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'activities.deatils',
            'res_id': activities_deatils.id,
            'view_mode': 'form',
            'target': 'new' }
        
class turico_cancellationPenalty(models.Model):
    _name = "turico.cancellationpenalty"
    
    offsetUnit = fields.Char('Offset Unit')
    unitsFromCheckIn = fields.Integer('Units From CheckIn')
    basisType = fields.Char('Basis Type')
    value = fields.Float('Value')
    activities_id = fields.Many2one('activities.deatils', string='Activities')
    
class activities_deatils(models.Model):   
    _name = "activities.deatils"
    
    searchresult_id = fields.Many2one('activities.searchresult', string='Search Result')
    
    turico_cancellation_ids = fields.One2many('turico.cancellationpenalty', 
                                        'activities_id', string='Cancellation')
    
    days = fields.Char('Avaliable Days')
    code = fields.Char('Code')
    rateKey = fields.Char('rateKey')
    total_amount = fields.Float('Total Amount')
    total_tax = fields.Float('Total Tax')
    total_amount_txt = fields.Char('Total Amount')
    currency = fields.Char('Currency')
    
    paxAmounts = fields.Char('Amounts Details')
    paxdata = fields.Char('paxdata')
    operationDates_ids = fields.One2many('activities.operationdates', 'deatils_id', string='Rates')
    questions_ids = fields.One2many('activities.questions', 'deatils_id', string='Questions')
    type = fields.Char('Type', default="hotelbeds")
    
    unit_amount = fields.Float('Unit Price Breakdown Amount')
    unit_numbers = fields.Float('Unit Price Breakdown Numbers')
    
    adult_amount = fields.Float('Adult Price Breakdown Amount')
    adult_numbers = fields.Float('Adult Price Breakdown Numbers')
    
    child_amount = fields.Float('Child Price Breakdown Amount')
    child_numbers = fields.Float('Child Price Breakdown Numbers')
    
    @api.multi
    def confirm_booking(self):
        activities_paxes = []
        
        if self.type == "hotelbeds":
            paxAmounts = ast.literal_eval(self.paxdata)
            list_age = [int(age) for age in self.searchresult_id.booking_id.person_ages.split(",")]
            
            for age in list_age:
                type = ""
                for pa in paxAmounts:
                    if age <= pa['ageTo'] and age >= pa['ageFrom']:
                        type = pa['paxType']
                pax_vals = {
                      'type' : type,
                      'age' : age }
                activities_paxes.append((0, 0, pax_vals))
        elif self.type == "turico":
            num_of_adults = self.searchresult_id.num_of_adults
            num_of_children = self.searchresult_id.num_of_children
            #print num_of_adults,num_of_children,"nnnnnnnnnnnn"
            for count in range(0, num_of_adults - 1):
                pax_vals = {
                      'type' : "Adult",
                      'age' : 30 }
                activities_paxes.append((0, 0, pax_vals))
            for count in range(0, num_of_children):
                pax_vals = {
                      'type' : "Child",
                      'age' : 9 }
                activities_paxes.append((0, 0, pax_vals))
            
        #print activities_paxes,"ap????"
        
        customer = self.searchresult_id.booking_id.customer_id
        
        #print "customer       ====>> ", customer
        #print "searchresult_id ===>> ", self.searchresult_id
        vals = {
                'paxes_ids' : activities_paxes,
                'title' : customer.title.name,
                'name' : customer.name,
                'surname' : "",
                'address' : customer.street,
                'email' : customer.email,
                'zipCode' : customer.zip,
                'telephones' : customer.phone,
                'country_id' : False,
                'mailing' : True,
                'deatils_id' : self.id,
                'type' : self.type } 
        
        confirm_booking = self.env['activities.confirm_booking'].create(vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'activities.confirm_booking',
            'res_id': confirm_booking.id,
            'view_mode': 'form',
            'target': 'new' }
    
class activities_operationDates(models.Model):
    _name = "activities.operationdates"
    
    deatils_id = fields.Many2one('activities.deatils', string='Details')
    from_date = fields.Date("From")
    to_date = fields.Date("To")
    select_date = fields.Boolean("Select Date")
    cancellationPolicies = fields.Char("Cancellation Policies")
    
class activities_questions(models.Model):
    _name = "activities.questions"
    
    deatils_id = fields.Many2one('activities.deatils', string='Details')
    text = fields.Char("Question")
    code = fields.Char("Code")
    required = fields.Boolean("Required")
    answer = fields.Char("Answer")
    additionTypeID = fields.Integer("Addition TypeID")
    
    
class activities_confirm_booking(models.Model):
    _name = "activities.confirm_booking"
    
    deatils_id = fields.Many2one('activities.deatils', string='Details')
    name = fields.Char("Name")
    surname = fields.Char("Surname")
    title = fields.Char("Title")
    email = fields.Char("Email")
    address = fields.Char("Address")
    zipCode = fields.Char("ZipCode")
    mailing = fields.Boolean("Mailing")
    telephones = fields.Char("Telephone")
    mobilePhone = fields.Char("Mobile Phone")
    country_id = fields.Many2one('location.country', string='Country')
    paxes_ids = fields.One2many('activities.paxes', 'confrim_booking_id', string='Paxes')
    type = fields.Char('Type', default="hotelbeds")
    
    
    @api.multi
    def do_book_turico(self):
        searchresult = self.deatils_id.searchresult_id
        wsdl = "http://demo-activityws.touricoholidays.com/ActivityBookFlow.svc?wsdl"
        client = suds.client.Client(wsdl,headers={'Accept-Encoding': 'gzip'})
        login_name, password = self.env['hotelapi.configuration'].get_turico_activity_book_flow()
        LoginName  = Element('auth:LoginName').setText(login_name)
        Password = Element('auth:Password').setText(password)
        Culture = Element('auth:Culture').setText('en_US')
        Version = Element('auth:Version').setText('7.123')
        AuthenticationHeader = Element('auth:AuthenticationHeader') 
        AuthenticationHeader.attributes.append(Attribute('xmlns:auth', 'http://schemas.tourico.com/webservices/authentication'))
        AuthenticationHeader.children = [LoginName, Password, Culture, Version]
        client.set_options(soapheaders=[AuthenticationHeader])
        service = client.service
        
        BookRequest = client.factory.create("ns1:BookRequest")
        OrderInfo = client.factory.create("ns1:OrderInfo")
        OrderInfo._rgRefNum = 0
        OrderInfo._requestedPrice = self.deatils_id.total_amount
        OrderInfo._currency = self.deatils_id.currency
        OrderInfo._confirmationLogoUrl = "http://www.touricoholidays.com/logos/touricoholidays.jpg"
        OrderInfo._paymentType = "Obligo"
        OrderInfo._recordLocatorId = 0
        OrderInfo._confirmationEmail = "chandhuviswanath@zbeanztech.com"
        OrderInfo._agentRefNumber = "123NA"
        OrderInfo.DeltaPrice._basisType = "Percent"
        OrderInfo.DeltaPrice._value = 1
        
        BookRequest.orderInfo = OrderInfo
        
        ActivitiesSelectedOptions = client.factory.create("ns1:ActivitiesSelectedOptions")
        ArrayOfActivityInfo = client.factory.create("ns1:ArrayOfActivityInfo")
        ActivityInfo = client.factory.create("ns1:ActivityInfo")
        ActivityInfo._activityId = searchresult.turico_activityId
        ActivityInfo._date = searchresult.availabilities_id.from_Date
        ActivityInfo._optionId = searchresult.availabilities_id.optionId
        ActivityInfo.ActivityPricing.PriceBreakdown.Unit._numbers = int(self.deatils_id.unit_numbers)
        ActivityInfo.ActivityPricing.PriceBreakdown.Unit._amount = self.deatils_id.unit_amount
        ActivityInfo.ActivityPricing.PriceBreakdown.Adult._numbers = int(self.deatils_id.adult_numbers)
        ActivityInfo.ActivityPricing.PriceBreakdown.Adult._amount = self.deatils_id.adult_amount
        ActivityInfo.ActivityPricing.PriceBreakdown.Child._numbers = int(self.deatils_id.child_numbers)
        ActivityInfo.ActivityPricing.PriceBreakdown.Child._amount = self.deatils_id.child_amount
        ActivityInfo.ActivityPricing._price = self.deatils_id.total_amount
        ActivityInfo.ActivityPricing._currency = self.deatils_id.currency
        ActivityInfo.ActivityPricing._tax = self.deatils_id.total_tax

        ArrayOfPassengerInfo = client.factory.create("ns1:ArrayOfPassengerInfo")
        PassengerInfo = client.factory.create("ns1:PassengerInfo")
        PassengerInfo._mobilePhone = self.mobilePhone
        PassengerInfo._homePhone = self.telephones
        PassengerInfo._isMainContact = True
        PassengerInfo._seatNumber = ""
        PassengerInfo._lastName = "Pass"
        PassengerInfo._type = "Adult"
        PassengerInfo._seqNumber = 1
        PassengerInfo._middleName = self.surname
        PassengerInfo._firstName = self.name
        ArrayOfPassengerInfo.PassengerInfo.append(PassengerInfo)
        if self.paxes_ids:
            for paxes in self.paxes_ids:
                PassengerInfo = client.factory.create("ns1:PassengerInfo")
                PassengerInfo._mobilePhone = "111111"
                PassengerInfo._homePhone = "1111111"
                PassengerInfo._isMainContact = False
                PassengerInfo._seatNumber = ""
                PassengerInfo._lastName = "Pass"
                PassengerInfo._type = paxes.type
                PassengerInfo._seqNumber = 1
                PassengerInfo._middleName = paxes.surname
                PassengerInfo._firstName = paxes.name
                ArrayOfPassengerInfo.PassengerInfo.append(PassengerInfo)
        
        ActivityInfo.Passengers = ArrayOfPassengerInfo
        ArrayOfListAddition = client.factory.create("ns1:ArrayOfTextAddition")
        for questions in self.deatils_id.questions_ids:
            ListAddition = client.factory.create("ns1:TextAddition")
            ListAddition._additionTypeID = questions.additionTypeID
            ListAddition._additionType = questions.text
            ListAddition._value = questions.answer
            ArrayOfListAddition.TextAddition.append(ListAddition)
        
        ActivityInfo.ActivityAdditions.TextAdditions = ArrayOfListAddition
        ArrayOfCancellationPenalty = client.factory.create("ns1:ArrayOfCancellationPenalty")
        
        for cancellation in self.deatils_id.turico_cancellation_ids:
            CancellationPenalty = client.factory.create("ns1:CancellationPenalty")
            CancellationPenalty.Deadline._offsetUnit = cancellation.offsetUnit
            CancellationPenalty.Deadline._unitsFromCheckIn = cancellation.unitsFromCheckIn
            CancellationPenalty.Penalty._basisType = cancellation.basisType
            CancellationPenalty.Penalty._value = cancellation.value
            ArrayOfCancellationPenalty.CancellationPenalty.append(CancellationPenalty)
        
        ActivityInfo.CancellationPolicy.CancellationPenalties = ArrayOfCancellationPenalty
        ArrayOfActivityInfo.ActivityInfo.append(ActivityInfo)
        ActivitiesSelectedOptions.ActivitiesInfo = ArrayOfActivityInfo
        BookRequest.reservations = ActivitiesSelectedOptions
        booking_error = ""
        try:
            #print "\n\n\n"
            result = service.BookActivity(BookRequest)
            #print "result ====>>????????????????????? ", result
            return self.redirect_to_activity_booked_window(result)
        except suds.WebFault as detail:
            #print "------------------>><<>>> ", detail
            booking_error = "%s, %s" % (booking_error, detail)
        if booking_error:
            booking_error = booking_error.strip(",")
            booking_error = booking_error.strip("")
            raise osv.except_osv(_('Booking Issues'), _(booking_error))
        #pop
    
    @api.multi
    def redirect_to_activity_booked_window(self, result):
        ResGroup = result.ResGroup
        for reservations in ResGroup.Reservations:
           for reservation in reservations[1]:
                #print "rrrrr ======>>> ", reservation
                ActivityReservation = reservation
                
                deatils_id = self.deatils_id
                searchresult_id = deatils_id.searchresult_id
                booking_date = searchresult_id.availabilities_id.from_Date
                
                activity_data = {
                  'state' : ActivityReservation._status,
                  'name' : " ActivityReservation._roomTypeCategory",
                  'total': ActivityReservation._totalPrice,
                  'reservationId' : ActivityReservation._reservationId,
                  'tranNumber' : ActivityReservation._tranNumber,
                  'currency':  ActivityReservation._currency,
                  'booking_date' : booking_date,
                  'name' : searchresult_id.name,
                  'customer_id' : searchresult_id.booking_id.customer_id.id,
                  'booked_on' : datetime.datetime.now()
                  
                  }
                 
                booked = self.env['booked.activities'].create(activity_data)
                menu_obj = self.env['ir.ui.menu']
                menu_ids = menu_obj.search([('name', '=', "Booked Activities")])
                data = {'type': 'ir.actions.client',
                   'tag': 'reload',
                   'params': {'menu_id': menu_ids and menu_ids[0].id or False}}
                return data
        
        
    
    
    @api.multi
    def do_book(self):
        
        import logging
        logging.basicConfig(level=logging.INFO)
        logging.getLogger('suds.client').setLevel(logging.DEBUG)
        if self.type == "turico":
            return self.do_book_turico()
        activities_deatils = self.deatils_id
        from_date = ""
        to_date = ""
        for operationDates in activities_deatils.operationDates_ids:
            #print "operationDates.select_date ==>> ", operationDates.select_date
            if operationDates.select_date:
                from_date = operationDates.from_date
                to_date = operationDates.to_date
        paxes_list = []
        for paxes in self.paxes_ids:
            paxes_list.append({
              "age": paxes.age,
              "name": paxes.name,
              "surname": paxes.surname,
              "type": paxes.type })
        list_answers = []
        for questions in activities_deatils.questions_ids:
            answer_vals = {
                   'code' :  questions.code,
                    }
            list_answers.append({'question' : answer_vals, 'answer' : questions.answer})
        activities = {
            "preferedLanguage": "en",
            "serviceLanguage": "en",
            "rateKey": activities_deatils.rateKey,
            "from": from_date,
            "to": to_date,
            "paxes": paxes_list,
            'answers' : list_answers
          }
        holder = {
                "name": self.name or "xcvf",
                "surname": self.surname or "Test",
                #"title": self.title or "",
                #"email": self.email or "",
                #"address": self.address or "",
                #"zipCode": self.zipCode or "",
                #"mailing": self.mailing or "",
                #"country": self.country_id.code or "",
                #"telephones": self.telephones.split(",")
              }
        vals = {
                "language": "en",
                "holder": holder,
                "activities": [activities],
                 "clientReference": self.get_clientReference(),
                }
        hotelapi = self.env['hotelapi.configuration'].search([('type', '=', 'hotelbeds-activity')])
        data = hotelapi.hotelbeds_activity_confirm(vals)
        
        
        
    def get_clientReference(self, cr, uid, context=None):
        return self.pool.get('ir.sequence').get(cr, uid, 'activities.clientReference') or '/'
    
    
    
    
class activities_paxes(models.Model):
    _name = "activities.paxes"
    
    confrim_booking_id = fields.Many2one('activities.confirm_booking', string='Details')
    name = fields.Char("Name")
    surname = fields.Char("Surname")
    age = fields.Integer('Age')
    type = fields.Char("Type")
    

    
    
    