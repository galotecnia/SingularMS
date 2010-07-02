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
from mt.models import Body
from mt.models import Message
from accounting.models import Account, Provider
from django.contrib import admin
from django.test.client import Client
import datetime

class AdminTests (TestCase):
    fixtures = ['base_data.xml', ]
    
    def setUp(self):
        self.username = 'GaloAdmin'
        self.password = '1234'

    def test_admin (self):
        ''' Admin interface testing ... '''
        username = self.username
        password = self.password
        urls = []

        admin.autodiscover()
        for model, model_admin in admin.site._registry.items():
            app_label = model._meta.app_label
            if app_label in ('mt', 'mo', 'manager', 'accounting'):
                model_url = '/%(urlBase)sadmin/%(app)s/%(model)s/' % \
                            {'urlBase': settings.URL_BASE, 
                             'app': app_label, 
                             'model': model.__name__.lower()
                            }
                urls.append (model_url)
                for obj in model.objects.all()[:10]:
                    urls.append ('%(modelUrl)s%(modelId)s/' % \
                            {'modelUrl': model_url, 
                             'modelId': obj.id
                            })        
        c = Client()
        if not c.login(username=username, password=password):
            self.fail ("Don't login")
        else:
            for url in urls:                
                response = c.get(url)
                self.assertEqual (response.status_code, 200,
                                    'url="%(url)s", response=%(code)d' % \
                                    {'url':url, 
                                     'code': response.status_code
                                    })
