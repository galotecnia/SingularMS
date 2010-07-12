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
from mocker import Mocker
from mocker import Mock
from mocker import expect
from mocker import ARGS
from mocker import ANY
from django.test import TestCase
from webservice import SMSProcessor
from singularmsd import AccountGroup
from singularmsd import MessageScheduler
from accounting.models import Customer
from accounting.models import Purchase
from accounting.models import Account
import threading


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


class AccountGroupTests (TestCase):
    fixtures = ['customer_tests.json', ]

    def setUp(self):
        self.mocker = Mocker()

    def tearDown(self):
        self.mocker.restore() 

    def test_process_from_queue_without_messages (self):
        account = Account.objects.get(name = 'AccessWithPurchase')
        ag = AccountGroup (account)
        retcode = ag.process_from_queue()
        self.assertEqual (retcode, False)

    def test_process_from_queue_with_messages (self):
        ev = threading.Event()
        mock_Event = self.mocker.replace(ev)

        mock_Event ()
        self.mocker.result (mock_Event)
        self.mocker.count (3)

        mock_Event.set()
        self.mocker.result (True)
        self.mocker.count (3)

        mock_Queue = self.mocker.replace('Queue')
        mock_Queue()
        self.mocker.result (True)
        self.mocker.count (3)

        self.mocker.replay ()

        ms = MessageScheduler ({})
        processor =  SMSProcessor ()
        for i in range (0, 10):
            processor.sendSMS (WebServiceTests.username, WebServiceTests.password,
                'AccessWithPurchase', 'foo', 'bar', datetime.datetime.now())
        account = Account.objects.get(name = 'AccessWithPurchase')
        ag = AccountGroup (account)
        ms.account_groups[account.id] = ag
        ms.enqueue_messages ()
        retcode = ag.process_from_queue()
        self.assertEqual (retcode, True)
        self.assertEqual (ag.work.qsize (),  10)

    def test_create_accountThreads (self):
        dummy_AccountThread = self.mocker.replace('singularmsd.AccountThread')

        dummy_AccountThread(ANY, ANY)
        self.mocker.result (dummy_AccountThread)
        self.mocker.count (4)

        dummy_AccountThread.num_threads
        self.mocker.result (4)
        self.mocker.count (4)

        dummy_AccountThread.start ()
        self.mocker.result (True)
        self.mocker.count (4)
        self.mocker.replay ()

        account = Account.objects.get(name = 'AccessWithPurchase')
        ag = AccountGroup (account)
        ag.create_accountThreads()
        self.assertEqual (len(ag.threads), 4)

class MessageSchedulerTests (TestCase):
    fixtures = ['customer_tests.json', ]

    def setUp(self):
        self.mocker = Mocker()

    def tearDown(self):
        self.mocker.restore() 

    def test_create_account_groups_without_accounts (self):
        dummy_Account = self.mocker.replace('accounting.models.Account')

        dummy_Account.objects.all ()
        self.mocker.result ([])
        self.mocker.count (2)

        self.mocker.replay ()

        ms = MessageScheduler ({})
        ms.create_account_groups()

    def test_create_account_groups_with_accounts (self):
        dummy_AccountGroup = self.mocker.replace('singularmsd.AccountGroup')

        dummy_AccountGroup(ANY)
        self.mocker.result (dummy_AccountGroup)
        self.mocker.count (3)

        dummy_AccountGroup.account.id
        self.mocker.result (1)
        self.mocker.count (3)

        dummy_AccountGroup.start ()
        self.mocker.result (True)
        self.mocker.count (3)
        self.mocker.replay ()

        ms = MessageScheduler ({})
        ms.create_account_groups()

    def test_enqueue_messages_without_messages (self):
        dummy_AccountGroup = self.mocker.replace('singularmsd.AccountGroup')

        dummy_AccountGroup(ANY)
        self.mocker.result (dummy_AccountGroup)
        self.mocker.count (3)

        dummy_AccountGroup.account.id
        self.mocker.result (1)
        self.mocker.count (3)

        dummy_AccountGroup.start ()
        self.mocker.result (True)
        self.mocker.count (3)

        self.mocker.replay ()

        ms = MessageScheduler ({})
        ms.create_account_groups()
        ms.enqueue_messages ()

    def test_enqueue_messages_with_messages_mocker (self):
        dummy_AccountGroup = self.mocker.replace('singularmsd.AccountGroup')

        dummy_AccountGroup.account.id
        self.mocker.result (1)
        self.mocker.count (6)

        dummy_AccountGroup(ANY)
        self.mocker.result (dummy_AccountGroup)
        self.mocker.count (6)

        dummy_AccountGroup.start ()
        self.mocker.result (True)
        self.mocker.count (6)

        dummy_AccountGroup.event.set ()
        self.mocker.result (True)
        self.mocker.count (20)

        self.mocker.replay ()

        ms = MessageScheduler ({})
        ms.create_account_groups()
        processor =  SMSProcessor ()
        for i in range (0, 10):
            processor.sendSMS (WebServiceTests.username, WebServiceTests.password,
                'AccessWithPurchase', 'foo', 'bar', datetime.datetime.now())
        for i in range (0, 10):
            processor.sendSMSToChannel (WebServiceTests.username, WebServiceTests.password,
                'AccessWithPurchase', 'TestChannel', 'bar', datetime.datetime.now())
        ms.enqueue_messages ()

