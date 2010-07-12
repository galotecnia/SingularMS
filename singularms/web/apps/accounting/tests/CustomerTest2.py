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
from django.contrib.auth.models import User
from accounting.models import Customer
from accounting.models import Purchase
from accounting.models import Account

class CustomerTests2 (TestCase):
    fixtures = ['base_data.xml']
    
    def setUp(self):
        self.admin_name = 'administrador'
        self.admin_pass = '1234'
        
        self.customer_name = 'customer1'
        self.customer_pass = '1234'
        
        self.account_name = 'cuentaBase'
        self.account_pass = '1234'
        
    def test_get_channel_from_customer(self):
        """
            Checks if a customer have a channel or not
        """
        customer = Customer.get_customer(self.customer_name, self.customer_pass)
        if customer is Customer.WRONG_USERNAME_OR_PASSWORD:
            self.fail('Couldnt get the customer')        
        self.assertEqual(False, Customer.can_send_to_channel(customer, channel='this_channel_doesnt_exists'))
