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
from mt.models import Body
from mt.models import Message
from mt.models import SMSQueue
from accounting.models import Account
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group
import datetime

class MessageTests (TestCase):
    #fixtures = ['customer_tests.json', ]
    fixtures = ['base_data.xml', 'base_data.json']

    def setUp(self):
        self.text = "Test sms"
        self.phoneNumber = "666554433"
        self.now = datetime.datetime.now ()
        #self.OKaccount = Account.objects.get(name='AccessWithPurchase', customer__username='pepito')
        self.OKaccount = Account.objects.get(name='cuentaBase', customer__username='clienteBase')

    def test_create_one_ok (self):
        Message.create_one (self.text, self.phoneNumber, self.now, self.OKaccount)
        self.assertEqual (3, Message.objects.all().count())

    def test_put_in_the_queue (self):
        self.assertEqual(0, SMSQueue.objects.all().count())
        id = Message.create_one (self.text, self.phoneNumber, self.now, self.OKaccount)
        m = Message.objects.get (id = id)
        m.put_in_the_queue ()
        self.assertEqual (1, SMSQueue.objects.all().count())
