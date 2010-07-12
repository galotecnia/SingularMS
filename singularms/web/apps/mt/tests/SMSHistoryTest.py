# -*- coding: utf-8 -*-

#######################################################################
#  SingularMS version 1.0                                             #
#######################################################################
#  This file is a part of SingularMS.                                 #
#                                                                     #
#  SingularMs is free software; you can copy, modify, and distribute  #
#  it under the terms of the GNU Affero General Public License        #
#  Version 1.0, 21 May 2007.                                          #
#                                                                     #
#  SingularMS is distributed in the hope that it will be useful, but  #
#  WITHOUT ANY WARRANTY; without even the implied warranty of         #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.               #
#  See the GNU Affero General Public License for more details.        #
#                                                                     #
#  You should have received a copy of the GNU Affero General Public   #
#  License with this program; if not, contact Galotecnia              #
#  at contacto[AT]galotecnia[DOT]org. If you have questions about the #
#  GNU Affero General Public License see "Frequently Asked Questions" #
#  at http://www.gnu.org/licenses/gpl-faq.html                        #
#######################################################################

from django.test import TestCase
from django.conf import settings
from mt.models import  SMSHistory
from accounting.models import Customer

class SMSHistoryTests (TestCase):
    #fixtures = ['customer_tests.json', ]
    fixtures = ['base_data.xml', 'base_data.json']

    def test_check_id_invalid_id (self):
        """
            If the Id is invalid
        """
        customer = Customer.get_customer ('pepito', 'password')
        (status, status_msg) = SMSHistory.check_id (customer, '{--Invalid_ID--}')[0]
        self.assertEqual ((status, status_msg), (True, 'badid'))

    def test_check_id_not_owner (self):
        """
            If the Id is valid but pepito is not the owner of the message.
        """
        #customer = Customer.objects.get (user__username='customer1')
        customer = Customer.objects.get(username='customer1')
        (status, status_msg) = SMSHistory.check_id (customer, 'testMessage1')[0]
        self.assertEqual ((status, status_msg), (True, 'badid'))

    def test_check_id_not_error (self):
        """
            If the Id is valid, pepito is the owner of the message and there isn't an error
        """
        customer = Customer.get_customer ('pepito', 'password')
        (status, status_msg) = SMSHistory.check_id (customer, 'testMessage1')[0]
        self.assertEqual ((status, status_msg), (False, ''))

    def test_check_id_error (self):
        """
            If the Id is valid and pepito is the owner of the message and there is an error.
        """
        customer = Customer.get_customer ('pepito', 'password')
        (status, status_msg) = SMSHistory.check_id (customer, 'testMessage2')[0]
        self.assertEqual ((status, status_msg), (True, 'A critical error'))

