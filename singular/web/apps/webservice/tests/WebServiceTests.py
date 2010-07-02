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

import datetime
from django.test import TestCase
from webservice.views import SingularService
from accounting.models import Customer
from accounting.models import Purchase, OutOfCredit
from mt.models import Channel


class WebServiceTests (TestCase):    
    fixtures = ['base_data.xml', 'base_data.json', 'other_data.xml']
    #fixtures = ['base_data.xml', 'other_data.xml']

    username = 'pepito'
    password = 'password'
    password2 = '1234'
    wrong_username = 'noUser'
    wrong_password = 'bad_password'

    def setUp(self):
        pass

    def test_getAccounts_wrong_password (self):
        processor =  SingularService ()
        retcode = processor.getAccounts (WebServiceTests.wrong_username, WebServiceTests.wrong_password)
        self.assertEqual (retcode, Customer.WRONG_USERNAME_OR_PASSWORD)

    def test_getAccounts_ok_with_accounts (self):
        processor =  SingularService ()
        retcode = processor.getAccounts (WebServiceTests.username, WebServiceTests.password)
        self.assertEqual (len(retcode), 3)
        self.assertEqual (retcode[0], 'AccessNoPurchase')
        self.assertEqual (retcode[1], 'AccessWithPurchase')
        self.assertEqual (retcode[2], 'AccessSeveralPurchases')

    def test_getAccounts_ok_without_accounts (self):
        processor =  SingularService ()
        retcode = processor.getAccounts ('customer1', WebServiceTests.password2)
        self.assertEqual (retcode, [])

    def test_getChannels_ok_without_channels (self):
        processor =  SingularService ()
        retcode = processor.getChannels ('customer1', WebServiceTests.password2)
        self.assertEqual (retcode, [])

    def test_getChannels_ok_with_channels (self): 
        processor =  SingularService ()
        retcode = processor.getChannels ('clienteBase', WebServiceTests.password2)
        self.assertEqual (retcode, [u'canal1'])

    def test_getCredit_wrong_password (self):
        processor =  SingularService ()
        retcode = processor.getCredit (WebServiceTests.wrong_username, WebServiceTests.wrong_password, 'AccessNoPurchase')
        self.assertEqual (retcode, Customer.WRONG_USERNAME_OR_PASSWORD)

    def test_getCredit_no_credit(self):
        processor =  SingularService ()
        try:
            retcode = processor.getCredit (WebServiceTests.username, WebServiceTests.password, 'AccessNoPurchase')
        except OutOfCredit:
            self.assertTrue
        else:
            self.fail('')
        #self.assertEqual (retcode, 0)

    def test_getCredit_credit(self):
        processor =  SingularService ()
        retcode = processor.getCredit (WebServiceTests.username, WebServiceTests.password, 'AccessSeveralPurchases')
        # TODO: Don't hardcode this:
        self.assertEqual (retcode, 28)

    def test_getStatus_wrong_password (self):
        processor =  SingularService ()
        retcode = processor.getStatus (WebServiceTests.wrong_username, WebServiceTests.wrong_password, 'whatever')
        self.assertEqual (retcode, Customer.WRONG_USERNAME_OR_PASSWORD)

    def test_getStatus_wrong_id (self):
        processor =  SingularService ()
        retcode = processor.getStatus (WebServiceTests.username, WebServiceTests.password, 'whatever')
        self.assertEqual (retcode[0], (True, 'badid'))

    def test_getStatus_with_id (self):
        processor =  SingularService ()
        retcode = processor.getStatus (WebServiceTests.username, WebServiceTests.password, 'testMessage1')
        self.assertEqual (retcode[0], (False, u''))

    def test_getStatus_with_id_not_owner (self):
        processor =  SingularService ()
        retcode = processor.getStatus ('customer1', WebServiceTests.password2, 'testMessage1')
        self.assertEqual (retcode[0], (True, 'badid'))

    def test_sendSMS_wrong_password (self):
        processor =  SingularService ()
        retcode = processor.sendSMS (WebServiceTests.wrong_username, WebServiceTests.wrong_password,
            'whatever', 'foo', 'bar', datetime.datetime.now())
        self.assertEqual (retcode, Customer.WRONG_USERNAME_OR_PASSWORD)

    def test_sendSMS_wrong_account (self):
        processor =  SingularService ()
        retcode = processor.sendSMS (WebServiceTests.username, WebServiceTests.password,
            'wrongAccount', 'foo', 'bar', datetime.datetime.now())
        self.assertEqual (retcode, Customer.WRONG_ACCOUNT)

    def test_sendSMS_no_credit (self):
        processor =  SingularService ()
        try:
            retcode = processor.sendSMS (WebServiceTests.username, WebServiceTests.password,
            'AccessNoPurchase', 'foo', 'bar', datetime.datetime.now())
        except OutOfCredit:
            self.assertTrue
        else:
            self.fail('')
        #self.assertEqual (retcode, Purchase.INSUFFICIENT_CREDIT)

    def test_sendSMS (self):
        processor =  SingularService ()
        retcode = processor.sendSMS (WebServiceTests.username, WebServiceTests.password,
            'AccessWithPurchase', 'foo', 'bar', datetime.datetime.now())
        self.assertEqual (retcode, 3)

