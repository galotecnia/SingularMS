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
from django.contrib.auth.models import User
from accounting.models import Customer
from accounting.models import Purchase
from accounting.models import Account, OutOfCredit

class CustomerTests (TestCase):
    #fixtures = [ 'customer_tests.json' ]
    fixtures = ['base_data.xml']
    #TODO: If we mix fixtures, seems to go bad. Googled for it, and seems a problem with Auth, 
    # maybe some changes in the models.    
    def setUp(self):
        self.admin_name = 'proveedorBase'
        self.admin_pass = '1234'
        
        self.customer_name = 'clienteBase'
        self.customer_pass = '1234'
        
        self.account_name = 'cuentaBase'
        self.account_pass = '1234'
    
    def test_check_customer_and_credit_wrong_username (self):
        ret = Customer.check_customer_and_credit ('pepito_malo', 'password', 'noAccount', 100)
        self.assertEqual (ret, Customer.WRONG_USERNAME_OR_PASSWORD)

    def test_check_customer_and_credit_wrong_password (self):
        ret = Customer.check_customer_and_credit ('customer1', 'no_password_de_customer1', 'noAccount', 100)
        self.assertEqual (ret, Customer.WRONG_USERNAME_OR_PASSWORD)

    def test_check_customer_and_credit_wrong_account (self):
        ret = Customer.check_customer_and_credit (self.customer_name, self.customer_pass, 'noAccount', 100)
        self.assertEqual (ret, Customer.WRONG_ACCOUNT)

    def test_check_customer_and_credit_insufficient_credit_no_purchase (self):
        #ret = Customer.check_customer_and_credit ('pepito', 'password', 'AccessNoPurchase', 2)
        try:
            ret = Customer.check_customer_and_credit (self.customer_name, self.customer_pass, self.account_name, 10000)
        except OutOfCredit:
            self.assertEqual
        else:
            self.fail('')        

    def test_check_customer_and_credit_insufficient_credit_purchas (self):
        #ret = Customer.check_customer_and_credit ('pepito', 'password', 'AccessWithPurchase', 10000)
        try:
            ret = Customer.check_customer_and_credit (self.customer_name, self.customer_pass, self.account_name, 10000)
        except OutOfCredit:
            self.assertEqual
        else:
        #self.assertEqual (ret, Purchase.INSUFFICIENT_CREDIT)
            self.fail('')

    def test_check_customer_and_credit_ok(self):
        account = Account.objects.get(name=self.account_name, customer__username=self.customer_name)
        ret = Customer.check_customer_and_credit (self.customer_name, self.customer_pass, self.account_name)
        self.assertEqual (ret, account)

    def test_get_customer_ok (self):
        """
            If you provide a correct username and password you'll get a Customer.
        """
        customer = Customer.get_customer (self.customer_name, self.customer_pass)
        self.assertEqual (customer, Customer.objects.get(username=self.customer_name) )

    def test_get_customer_invalid_user (self):
        """
            No valid username --> Customer.WRONG_USERNAME_OR_PASSWORD
        """
        customer = Customer.get_customer ('pepitoNoValid', 'password')
        self.assertEqual (customer, Customer.WRONG_USERNAME_OR_PASSWORD)

    def test_get_customer_invalid_password (self):
        """
            No valid password --> Customer.WRONG_USERNAME_OR_PASSWORD
        """
        customer = Customer.get_customer ('pepito', 'passwordNoValid')
        self.assertEqual (customer, Customer.WRONG_USERNAME_OR_PASSWORD)  	
