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
from accounting.models import Customer
from accounting.models import Purchase
from accounting.models import Account

class AccountTests (TestCase):
    #fixtures = ['customer_tests.json', ]
    fixtures = ['base_data.xml']
    
    def setUp(self):
        self.admin_name = 'proveedorBase'
        self.admin_pass = '1234'
        
        self.customer_name = 'clienteBase'
        self.customer_pass = '1234'
        
        self.account_name = 'cuentaBase'
        self.account_name2 = 'cuentaNoPurchase'
        self.account_name3 = 'cuentaVariosPurchase'
        
        self.purchase_id = 1        
        
    def test_get_credit_wo_purchase (self):
        """
            Get an account credit without purchases
        """
        account = Account.objects.get (name=self.account_name2, customer__username=self.customer_name)
        self.assertEqual (account.get_real_credit(), 0)

    def test_get_credit_one_purchase (self):
        """
            Get an account credit with one purchase
        """
        account = Account.objects.get (name=self.account_name, customer__username=self.customer_name)
        item = Purchase.objects.get(pk=self.purchase_id)
        credit = item.real_credit()
        
        self.assertEqual (account.get_real_credit(), credit)

    def test_get_credit_several_purchase (self):
        """
            Get an account credit with various purchases
        """
        account = Account.objects.get (name=self.account_name3, customer__username=self.customer_name)
        
        item1 = Purchase.objects.get(pk=2)
        item2 = Purchase.objects.get(pk=3)
        
        credit = item1.real_credit() + item2.real_credit()
        
        self.assertEqual (account.get_real_credit(), credit)
