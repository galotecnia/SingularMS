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
from mo.views import processIncomingMsgs as pim
from django.http import HttpRequest, HttpResponse
from mo.models import Command, ReplyCommand
from mo.models import ADMIN, REPLY, EXTERNAL
from mt.models import Body
from accounting.models import Account
from mo.connectors import * 

class ProcessIncomingMsgTests (TestCase):
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

        acc = Account.objects.get(name = self.account_name)
       
        cmd = Command(pattern = 'CANDELARIA AVISO', type = REPLY, active = True,
                      account = acc, priority = 0)
        cmd.save()
        body = Body(plainTxt = 'DUMMY ENCODE')
        body.save()
        rep = ReplyCommand(command = cmd, answer = body)
        rep.save()

    # TEST ACEPTACION
    def test_pim_dummy_connector (self):
        "Test if an incoming msg process was sucesfull for dummy connector"
        req = HttpRequest()
        req.GET['message'] = 'CANDELARIA AVISO'
        res = pim(req, 'Dummy')
        self.assertEqual (str(res.content), 'DUMMY ENCODE')

    # TEST ACEPTACION
    def test_pim_wpr_connector_ok (self):
        "Test if an incoming msg process was sucessfull for wpr connector"
        req = HttpRequest()
        req.GET = {'movil':'699998877', 'texto':'CANDELARIA AVISO', 'alias':'CANDELARIA', \
                   'msg':'AVISO', 'ticket':'1', 'numcorto':'4404', 'mcc':'', 'mnc':'', }
        res = pim(req, 'WPR')
        self.assertEqual (str(res.content), 'TYPE=SMS&TEXT=DUMMY ENCODE')

    def test_pim_wrong_connector (self):
        "Test if a wrong connector is get it"
        req = HttpRequest()
        res = pim(req, 'Crazy')
        self.assertEqual (res, None)

            


