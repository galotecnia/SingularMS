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
from webservice import SMSProcessor
from accounting.models import Customer
from accounting.models import Purchase


class WebServiceTests (TestCase):
    fixtures = ['customer_tests.json', ]

    username = 'pepito'
    password = 'password'
    wrong_username = 'noUser'
    wrong_password = 'bad_password'

    def setUp(self):
        pass

    def test_getAccounts_wrong_password (self):
        processor =  SMSProcessor ()
        retcode = processor.getAccounts (WebServiceTests.wrong_username, WebServiceTests.wrong_password)
        self.assertEqual (retcode, Customer.WRONG_USERNAME_OR_PASSWORD)

    def test_getAccounts_ok_with_accounts (self):
        processor =  SMSProcessor ()
        retcode = processor.getAccounts (WebServiceTests.username, WebServiceTests.password)
        self.assertEqual (len(retcode), 3)
        self.assertEqual (retcode[0], 'AccessNoPurchase')
        self.assertEqual (retcode[1], 'AccessWithPurchase')
        self.assertEqual (retcode[2], 'AccessServeralPurchases')

    def test_getAccounts_ok_without_accounts (self):
        processor =  SMSProcessor ()
        retcode = processor.getAccounts ('customer1', 'password')
        self.assertEqual (retcode, [])

    def test_getChannels_ok_without_channels (self):
        processor =  SMSProcessor ()
        retcode = processor.getChannels ('customer1', 'password')
        self.assertEqual (retcode, [])

    def test_getChannels_ok_with_channels (self):
        processor =  SMSProcessor ()
        retcode = processor.getChannels (WebServiceTests.username, WebServiceTests.password)
        self.assertEqual (retcode, [u'TestChannel'])

    def test_getCredit_wrong_password (self):
        processor =  SMSProcessor ()
        retcode = processor.getCredit (WebServiceTests.wrong_username, WebServiceTests.wrong_password, 'AccessNoPurchase')
        self.assertEqual (retcode, Customer.WRONG_USERNAME_OR_PASSWORD)

    def test_getCredit_no_credit(self):
        processor =  SMSProcessor ()
        retcode = processor.getCredit (WebServiceTests.username, WebServiceTests.password, 'AccessNoPurchase')
        self.assertEqual (retcode, 0)

    def test_getCredit_credit(self):
        processor =  SMSProcessor ()
        retcode = processor.getCredit (WebServiceTests.username, WebServiceTests.password, 'AccessServeralPurchases')
        self.assertEqual (retcode, 1907)

    def test_getStatus_wrong_password (self):
        processor =  SMSProcessor ()
        retcode = processor.getStatus (WebServiceTests.wrong_username, WebServiceTests.wrong_password, 'whatever')
        self.assertEqual (retcode, Customer.WRONG_USERNAME_OR_PASSWORD)

    def test_getStatus_wrong_id (self):
        processor =  SMSProcessor ()
        retcode = processor.getStatus (WebServiceTests.username, WebServiceTests.password, 'whatever')
        self.assertEqual (retcode[0], (True, 'badid'))

    def test_getStatus_wriht_id (self):
        processor =  SMSProcessor ()
        retcode = processor.getStatus (WebServiceTests.username, WebServiceTests.password, 'testMessage1')
        self.assertEqual (retcode[0], (False, u''))

    def test_getStatus_wriht_id_not_owner (self):
        processor =  SMSProcessor ()
        retcode = processor.getStatus ('customer1', 'password', 'testMessage1')
        self.assertEqual (retcode[0], (True, 'badid'))

    def test_sendSMS_wrong_password (self):
        processor =  SMSProcessor ()
        retcode = processor.sendSMS (WebServiceTests.wrong_username, WebServiceTests.wrong_password,
            'whatever', 'foo', 'bar', datetime.datetime.now())
        self.assertEqual (retcode, Customer.WRONG_USERNAME_OR_PASSWORD)

    def test_sendSMS_wrong_account (self):
        processor =  SMSProcessor ()
        retcode = processor.sendSMS (WebServiceTests.username, WebServiceTests.password,
            'wrongAccount', 'foo', 'bar', datetime.datetime.now())
        self.assertEqual (retcode, Customer.WRONG_ACCOUNT)

    def test_sendSMS_no_credit (self):
        processor =  SMSProcessor ()
        retcode = processor.sendSMS (WebServiceTests.username, WebServiceTests.password,
            'AccessNoPurchase', 'foo', 'bar', datetime.datetime.now())
        self.assertEqual (retcode, Purchase.INSUFFICIENT_CREDIT)

    def test_sendSMS (self):
        processor =  SMSProcessor ()
        retcode = processor.sendSMS (WebServiceTests.username, WebServiceTests.password,
            'AccessWithPurchase', 'foo', 'bar', datetime.datetime.now())
        self.assertEqual (retcode, 3)

