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

from datetime import date

class PurchaseTests (TestCase):
    fixtures = ['base_data.xml']
    
    def setUp(self):
        self.admin_name = 'proveedorBase'
        self.admin_pass = '1234'
        
        self.customer_name = 'clienteBase'
        self.customer_pass = '1234'
        
        self.account_name = 'cuentaBase'
        self.account_pass = '1234'
        
        self.startdate = date.today()
        self.enddate = date(2005, 05, 01)
        self.futuredate = date(2900, 05, 01)

    def test_real_credit (self):
        p = Purchase.objects.get(pk=1)
        p.available = 10
        p.reserved = 6
        self.assertEqual (4, p.real_credit() )

    def test_real_credit_out_of_date (self):
        """
            Test out of date credit.
        """
        acc = Account.objects.get(name=self.account_name)        
        p = Purchase(account=acc, startDate=self.startdate, 
                     endDate=self.enddate, initial=1, reserved=1, 
                     available=1, price=1 )
        self.assertEqual (0, p.real_credit() )

    def test_real_credit_future (self):
        """
            Test credit not yet valid.
        """
        acc = Account.objects.get(name=self.account_name)
        p = Purchase(account=acc, startDate=self.futuredate, 
                     endDate=self.enddate, initial=1, reserved=1, 
                     available=1, price=1 )
        
        self.assertEqual (0, p.real_credit() )
