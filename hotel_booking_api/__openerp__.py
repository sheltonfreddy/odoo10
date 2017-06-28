# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 ZestyBeanz Technologies Pvt Ltd(<http://www.zbeanztech.com>)
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

{
    'name': 'Hotel Booking API',
    'version': '1.16',
    'author': 'Zesty Beanz Technology (P) Ltd.',
    'website': 'www.zbeanztech.com',
#    'depends': ['account', 'web_tree_image'],
    'depends': ['account'],
    'demo': [],
    'description': """
Hotel Booking API Integration
    """,
    'data': [
            'security/hotel_booking_security.xml',
            'security/ir.model.access.csv',
            'data/hotel_data.xml',
            'report_booking_info.xml',
            'report_act_booking.xml',
            'booking_report.xml',
            'menu_view.xml',
            'api_configuration_view.xml',
            'booked_hotels_view.xml',
            'hotel_locations_view.xml',
            'book_hotels_view.xml',
            'booking_sequence.xml',
            'booked_activities_view.xml',
            'activities_booking_view.xml',
              
            'car_booking_view.xml',
            'cruise_booking_view.xml',
              
            'hotels_data_view.xml',
            'activity_data_view.xml',
              
            'wizard/import_locations_view.xml',
            'wizard/import_tourico_view.xml',
            'wizard/cancellation_fee_view.xml',
            'sabre_data_view.xml',
            'res_users.xml',
            'agency_data_view.xml',
            #'hotel_dashboard_view.xml'
            ],
    'test': [],
    'installable': True,
    'auto_install': False,
    'images': [],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
