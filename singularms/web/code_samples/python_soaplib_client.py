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


#!/usr/bin/python

from soaplib.wsgi_soap import SimpleWSGISoapApp
from soaplib.service import soapmethod
from soaplib.serializers.primitive import String, Integer, Array
from soaplib.client import make_service_client
from soaplib.client import debug

USERNAME = 'username'
PASSWORD = 'password'
ACCOUNT = 'account'

class SingularService(SimpleWSGISoapApp):
    __tns__ = 'http://www.galotecnia.com/soap/'

    @soapmethod(String, Integer, _returns=Array(String))
    def say_hello(self, name, times):
        pass

    @soapmethod(String, String, String, String, String, _returns=Integer)
    def sendSMS(self, username, password, account, phoneNumber, text):
        pass

debug(True)

client = make_service_client('https://demo.galotecnia.com/singularms/ws/', SingularService())
greetings = client.say_hello("Test", 10)
for g in greetings:
    print g

#print client.sendSMS(USERNAME, PASSWORD, ACCOUNT, '34686202609', 'Desde ltsp')
