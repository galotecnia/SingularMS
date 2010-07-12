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
from django.http import HttpRequest, HttpResponse
from mo.connectors import * 

class ConnectorsTests (TestCase):

    def test_wpr_connector_decode_ok (self):
        req = HttpRequest()
        req.GET = {'movil':'699998877', 'texto':'CANDELARIA AVISO', 'alias':'CANDELARIA', \
                   'msg':'AVISO', 'ticket':'1', 'numcorto':'4404', 'mcc':'', 'mnc':'', }
        con = WPRConnector()
        dec = con.decode(req)
        [mob, text] = dec
        self.assertEqual (text, 'CANDELARIA AVISO')
        self.assertEqual (mob, '699998877')

    def test_wpr_connector_decode_request_error (self):
        req = HttpRequest()
        req.GET = {'movil':'699998877', 'texto':'CANDELARIA AVISO', 'alias':'CANDELARIA', \
                   'msg':'AVISO', 'ticket':'1', 'numcorto':'4404', 'mcc':'', }
        con = WPRConnector()
        dec = con.decode(req)
        self.assertEqual (dec, None)

    def test_wpr_connector_decode_attribute_error (self):
        req = 'Un churro como un demonio'
        con = WPRConnector()
        dec = con.decode(req)
        self.assertEqual (dec, None)

    def test_wpr_connector_encode_msg (self):
        answer = 'THIS IS ESPARTA'
        con = WPRConnector()
        enc = con.encode(None,answer)
        res = HttpResponse('TYPE=SMS&TEXT=THIS IS ESPARTA', mimetype='text/plain')
        self.assertEqual (enc.content, res.content)

    def test_wpr_connector_encode_ok (self):
        con = WPRConnector()
        enc = con.encode(None)
        res = HttpResponse('TYPE=SMS&TEXT=OK', mimetype='text/plain')
        self.assertEqual (enc.content, res.content)

