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
from accounting.models import Account


class MessageSchedulerTests (TestCase):
    fixtures = ['customer_tests.json', ]

    username = 'pepito'
    password = 'password'

    def setUp(self):
        self.mocker = Mocker()

    def tearDown(self):
        self.mocker.restore() 

    def test_create_account_groups_without_accounts (self):
        dummy_Account = self.mocker.replace('accounting.models.Account')

        dummy_Account.objects.all ()
        self.mocker.result ([])
        self.mocker.count (1)

        self.mocker.replay ()

        ms = MessageScheduler ({})
        ms.create_account_groups()
        self.mocker.verify()

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
        self.mocker.verify()

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
        self.mocker.verify()

    def test_enqueue_messages_with_messages_mocker (self):
        dummy_AccountGroup = self.mocker.replace('singularmsd.AccountGroup')

        dummy_AccountGroup.account.id
        self.mocker.result (1)
        self.mocker.count (1, None)

        dummy_AccountGroup(ANY)
        self.mocker.result (dummy_AccountGroup)
        self.mocker.count (1, None)

        dummy_AccountGroup.start ()
        self.mocker.result (True)
        self.mocker.count (1, None)

        dummy_AccountGroup.event.set ()
        self.mocker.result (True)
        self.mocker.count (1, None)

        self.mocker.replay ()

        ms = MessageScheduler ({})
        ms.create_account_groups()
        processor =  SMSProcessor ()
        for i in range (0, 10):
            processor.sendSMS (MessageSchedulerTests.username, MessageSchedulerTests.password,
                'AccessWithPurchase', 'foo', 'bar', datetime.datetime.now())
        for i in range (0, 10):
            processor.sendSMSToChannel (MessageSchedulerTests.username, MessageSchedulerTests.password,
                'AccessWithPurchase', 'TestChannel', 'bar', datetime.datetime.now())
        ms.enqueue_messages ()
        self.mocker.verify()

