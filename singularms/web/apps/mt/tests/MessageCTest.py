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
from mt.models import Message
from mt.models import Account
from mt.models import Channel
from mt.models import ChannelMessage
from mt.models import Subscriber
import datetime
import simplejson
from django.core.urlresolvers import reverse

class MessageCTests ( TestCase):
    fixtures = ['base_data.xml', 'base_data.json', 'other_data.xml']

    def setUp(self):
        self.text = "Test sms"
        self.phoneNumber = "658106150"
        self.now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.OKaccount = Account.objects.get(name='cuentaBase', customer__username='clienteBase')
        self.username = 'clienteBase'

    def test_create_from_web_ok(self):
        username = self.username
        password = '1234'
        count = Message.objects.count()
        resp = self.client.post( reverse('root'), {'username':username,'password':password})
        self.failUnlessEqual( resp.status_code, 200 )						
        resp = self.client.post( reverse('sendToOne'), { 'mobile': self.phoneNumber, 'account' : 1, 'actiDate': self.now, 'typeMsg': 1, 'body': self.text }) 
        self.assertNotEqual( resp.status_code, 404 )
        if (count == Message.objects.count()):
            self.fail("Not insert object")
        else:
            self.assertEqual


    def test_create_msgchannel_ok(self):
        username = self.username
        password = "1234"
        resp = self.client.post( reverse('root'), {'username':username,'password':password})
        self.failUnlessEqual( resp.status_code, 200 )						
        id = Channel.create_one(text=self.text, account=self.OKaccount, activationDate=self.now,channel_name="canal1")
        if (id == Channel.CHANNEL_DOES_NOT_EXIST):
            self.fail("Dont send message to Channel")
        else:
            self.assertEqual

    def test_create_msgchannel_web_ok(self):
        username = self.username
        password = "1234"
        resp = self.client.post( reverse('root'), {'username':username,'password':password})
        self.failUnlessEqual( resp.status_code, 200 )						
        count = ChannelMessage.objects.count()
        resp = self.client.post( reverse('sendToChannels'),{'account':1, 'channel': [1], 'actiDate':self.now, 'typeMsg':1, 'body': self.text}) 
        self.assertNotEqual( resp.status_code, 404 )
        if (count == ChannelMessage.objects.count()):
            self.fail("Dont send message to Channel")
        else:
            self.assertEqual

    def test_use_easy_send_form(self):
        username = self.username
        password = '1234'
        resp = self.client.post( reverse('root'), {'username':username,'password':password})
        self.failUnlessEqual( resp.status_code, 200 )
        count = Message.objects.count()
        resp = self.client.post( reverse('easySend'), { 'mobile': self.phoneNumber, 'typeMsg': 1, 'body': self.text })
        self.assertNotEqual( resp.status_code, 404 )
        if (count == Message.objects.count()):
            self.fail("Not insert object")
        else:
            self.assertEqual

    def test_create_subscriber(self):
        username = self.username
        password = '1234'
        resp = self.client.post( reverse('root'), {'username':username,'password':password})
        self.failUnlessEqual( resp.status_code, 200 )
        resp = self.client.post(reverse('ajaxNewSubscriber'),{'mobile':'649868997','name':'nameTest','channels':[1]},**{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertNotEqual( resp.status_code, 404 )
        dats = simplejson.loads(resp.content)
        if dats['data'] == True:
            self.assertEqual
        else:
            self.fail('Not delete object')

    def test_delete_subscriber(self):
        username = self.username
        password = '1234'
        resp = self.client.post( reverse('root'), {'username':username,'password':password})
        self.failUnlessEqual( resp.status_code, 200 )
        sub = Subscriber(name='nameTest',mobile='649868997')
        sub.save()
        sub.channels=[1]
        sub.save()
        resp = self.client.get(reverse('ajaxDeleteSubscriber'),{'checked':[1]},**{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertNotEqual( resp.status_code, 404 )
        dats = simplejson.loads(resp.content)
        if dats['data'] == True:
            self.assertEqual
        else:
            self.fail('Not delete object')

    def test_create_channel_web(self):
        username = 'admin'
        password = '1234'
        resp = self.client.post( reverse('root'), {'username':username,'password':password})
        self.failUnlessEqual( resp.status_code, 200 )
        count = Channel.objects.count()
        resp = self.client.post( reverse('ajaxNewChannel'), { 'name': 'channelTest', 'description':'Channel Description', 'customer':[3]},**{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertNotEqual( resp.status_code, 404 )
        if (count == Channel.objects.count()):
            self.fail("Not insert object")
        else:
            self.assertEqual
