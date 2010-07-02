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
import Queue
import threading



class AccountGroupTests (TestCase):
    fixtures = ['customer_tests.json', ]

    username = 'pepito'
    password = 'password'
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
        self.mocker.count (0, 10)

        mock_Event.set()
        self.mocker.result (True)
        self.mocker.count (0, 10)

        mock_Queue = self.mocker.replace('Queue')
        mock_Queue()
        self.mocker.result (True)
        self.mocker.count (0, 3)

        self.mocker.replay ()

        ms = MessageScheduler ({})
        processor =  SMSProcessor ()
        for i in range (0, 10):
            processor.sendSMS (AccountGroupTests.username, AccountGroupTests.password,
                'AccessWithPurchase', 'foo', 'bar', datetime.datetime.now())
        account = Account.objects.get(name = 'AccessWithPurchase')
        ag = AccountGroup (account)
        ms.account_groups[account.id] = ag
        ms.enqueue_messages ()
        retcode = ag.process_from_queue()
        self.assertEqual (retcode, True)
        self.assertEqual (ag.work.qsize (),  10)
        self.fail ("Este test no funciona, hay que rehacerlo")
        self.mocker.verify()

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
        self.mocker.verify()
