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
from django.core import urlresolvers
from django.core.urlresolvers import reverse
from django.test.client import Client
from accounting import urls

class AcceptTests (TestCase):
    #fixtures = ['dump.json' ]
    parm = {}
    def setUp(self):
        self.parm['logPage'] = [0]
        self.parm['logCalendar'] = [20090102]
        self.parm['logPriority'] = [0]
        self.parm['logIndex'] = []	# Works
         
        self.base="/singularms/accounting/"

    def test_urls(self):    
        # This should fail if there are urls pointing to view's which aren't created yet.
        url = ''
        result = []
        
        username = 'GaloAdmin'
        password = '1234'
                
        response = self.client.post( reverse('root'), { 'username': username, 'password': password } )    # Works!
        for key in self.parm.keys():
            if len(self.parm[key]) == 0:
                url = reverse(key)
            elif len(self.parm[key])==1:
                url = reverse(key, args = self.parm[key] )
            result.append( self.client.post( url ) )
        for res in result:            
            if (res.status_code != 200):
                self.assertEqual(response.status_code,200)
            else:
                pass
        self.assertEqual(response.status_code,200)
