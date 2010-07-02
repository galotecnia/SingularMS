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
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest
from django.template import RequestContext
from django.test.client import Client
from django.core.urlresolvers import reverse

from accounting.views import showItem, ITEM_URL_DICT
from accounting.urls import *
from accounting.models import Provider, Customer, checkAdmin, \
    checkChannelAdmin, checkCustomer, Account, Access, Purchase, \
    Capabilities

from manager.views import getProfile
import datetime
from smlog.models import Log

# URl list
URLS = ['account', 'access', 'purchase', 'customer', 'provider', 'basecommand']
# Constants block:
FORM_USERNAME = 'testguy'
FORM_PASSWORD = '1234'
FORM_PROVIDER = 2
FORM_NAME = 'object'

URLS_ALL_USERS_START_INDEX = 3

class rolTests(TestCase):    
    fixtures = ['base_data.xml', ]
    
    def setUp(self):
        self.admin_name = 'proveedorBase'
        self.admin_pass = '1234'
        self.itemName = 'testItem'
        
        self.username = 'testguy'
        self.username2 = 'testguyedited'
        self.password = '1234'
        self.last_login = '2009-03-23 17:58:47'
        self.date_joined = '2009-03-23 17:58:47'
        self.startdate = '2009-03-23'
        self.enddate = '2109-03-23'
        
        self.accountName = 'cuentaBase'
        self.account = Account.objects.get(name='cuentaBase')        
        self.customer = Customer.objects.get(username='clienteBase')
        self.accessName = 'accesoBase'
        self.accessName2 = 'accesoBaseneo'
        self.access = Access.objects.get(name=self.accessName)
        self.accessBackend = self.access.backend
        self.provider = Provider.objects.get(username='proveedorBase')
        self.Capabilities = Capabilities.objects.get(typeSMS='sms')
        
        body = Body(plainTxt='testing')
        body.save()
        self.body = body
                
        self.decorators = [checkAdmin, checkChannelAdmin]
        
        self.FORM_DATA_LIST = {
            #Account
            URLS[0]: {'customer': self.customer.pk, 'name': self.itemName, 'access': self.access.pk,                      
                      'args2': 'none', 'num_threads': 1 },
            #Access
            URLS[1]: {'provider': self.provider.pk, 'name': self.itemName, 'description': 'none', 
                      'backend': self.accessBackend, 'args1': 'none', 'capabilities':1},
            #Purchase
            URLS[2]: {'account': self.account.pk, 'startDate': self.startdate, 'endDate': self.enddate,
                      'initial': 30},
            #Customer:
            URLS[3]: {'username': FORM_USERNAME, 'password': FORM_PASSWORD, 'password2': FORM_PASSWORD, 'providers': FORM_PROVIDER, 
                      'params': {'username': FORM_USERNAME} },
            #Provider:
            URLS[4]: {'username': FORM_USERNAME, 'password': FORM_PASSWORD, 'password2': FORM_PASSWORD, 
                                      'params': {'username': FORM_USERNAME} },
            #basecommand
            URLS[5]: {'pattern': 'just_testing', 'type': 1, 'account': self.account.pk, 'priority': 1, 'defaultAnswer': body.pk, 
                      'activationDate': '2009-06-26 14:40:15', 'params': {'pattern': 'just_testing', 'type': 1} }
            }
        
        self.MODIFY_FORM_DATA_LIST = {
            #Account
            URLS[0]: {'customer': self.customer.pk, 'name': self.itemName, 'access': self.access.pk, 
                      'args2': 'neo', 'num_threads': 2 },
            #Access
            URLS[1]: {'provider': self.provider.pk, 'name': self.accessName2, 'description': 'nueva descripcion', 
                      'backend': self.accessBackend, 'args1': 'neo', 'capabilities':1},
            #Purchase
            URLS[2]: {'account': self.account.pk, 'startDate': self.enddate, 'endDate': self.startdate,
                      'initial': 30, 'reserved': 5},
            #Customer:
            URLS[3]: {'username': self.username2, 'password': FORM_PASSWORD, 'password2': FORM_PASSWORD, 'providers': FORM_PROVIDER, 
                      'params': {'username': self.username2} },
            #Provider:
            URLS[4]: {'username': self.username2, 'password': FORM_PASSWORD, 'password2': FORM_PASSWORD, 
                                      'params': {'username': self.username2} },
            #basecommand
            URLS[5]: {'pattern': 'just_testing2', 'type': 2, 'account': self.account.pk, 'priority': 1, 'defaultAnswer': body.pk, 
                      'activationDate': '2009-06-26 14:40:15', 'params': {'pattern': 'just_testing2', 'type': 2} }
            }
    
    def test_normal_user_cant_enter_admin_views(self):
        """
         Let's check if an unauthorized user can't enter smadmin views
        """
        testguy = User.objects.create(username="testGuy", password="1234")
        self.assertEqual(False, checkAdmin(testguy) )
        self.assertEqual(False, checkChannelAdmin(testguy) )        
        self.assertEqual(False, checkCustomer(testguy) )
        
    def test_authorized_admin_can_enter_admin_views(self):
        """
         Let's check if an smadmin user can enter everywhere
        """        
        testguy = Provider.objects.create(username="testGuy", password="1234")
        self.assertEqual(True, checkAdmin(testguy) )
        self.assertEqual(True, checkChannelAdmin(testguy) )
        self.assertEqual(True, checkCustomer(testguy) )
        
    def test_customer_can_enter_only_customer_views(self):
        """
         Let's check if an customer user can enter customer views
        """                
        testguy = Customer.objects.create(username="testGuy", password="1234")        
        self.assertEqual(False, checkAdmin(testguy) )
        self.assertEqual(False, checkChannelAdmin(testguy) )
        self.assertEqual(True, checkCustomer(testguy) )

    def test_create_delete_items_and_check(self):
        """
            Iterate all items, and tries to create them, then delete them.
        """
        resp = self.client.post(reverse('root'), {'username': self.admin_name, 'password': self.password} )    # Works!
        self.failUnlessEqual(resp.status_code, 200)                        
            
        for url_name in URLS:            
            # Create the item and check
            resp = self.client.post(reverse('showItem', args=[url_name] ), self.FORM_DATA_LIST[url_name] )
            self.failUnlessEqual(resp.status_code, 200)
                
            obj = ITEM_URL_DICT[url_name]['model']           
            # Special case for user which we dont need to check theirs passwords.
            if 'params' in self.FORM_DATA_LIST[url_name].keys():
                params = self.FORM_DATA_LIST[url_name]['params']
            else:
                params = self.FORM_DATA_LIST[url_name]
            
            objlist = obj.objects.filter(**params)
            
            if not objlist:
                qs = obj.objects.all()                
                self.fail('Object still not created')

            for item in objlist:
                chk_id = item.pk
                            
            resp = self.client.get(reverse('editItem', args=[url_name, chk_id, 'true'] ) )                        
            self.failUnlessEqual(resp.status_code, 302)
            
            try:        
                temp = obj.objects.filter(pk=chk_id)
                self.fail('Object not deleted')
            except:        
                pass
                
        self.assertTrue            
        
    def test_delete_user_and_check(self):
        """
         Let's check if an smadmin user can delete a generic user
        """
        testguy = Customer.objects.create(username=self.username, password=self.password,
                                    last_login='2009-03-23 17:58:47',
                                    date_joined='2009-03-23 17:58:47'                                    
                                     )        
        
        chk_id = testguy.pk
        # Logging the admin                
        resp = self.client.post(reverse('root'), {'username': self.admin_name, 'password': self.password })    # Works!        
        self.failUnlessEqual(resp.status_code, 200)
        name = URLS[3] # Customer
        
        resp = self.client.get(reverse('editItem', args=[ name, chk_id, 'true'] ) )
        self.failUnlessEqual(resp.status_code, 302)
        
        try:        
            obj = Customer.objects.get(username=form.username)
        except:        
            self.assertEqual
            return
            
        self.fail('Object not deleted')
        
    def test_modify_items(self):
        resp = self.client.post(reverse('root'), {'username': self.admin_name, 'password': self.password} )    # Works!
        self.failUnlessEqual(resp.status_code, 200)                        
            
        for url_name in self.MODIFY_FORM_DATA_LIST.keys():            
            # Create the item and check
            resp = self.client.post(reverse('showItem', args=[url_name] ), self.FORM_DATA_LIST[url_name] )
            self.failUnlessEqual(resp.status_code, 200)
                
            modelBase = ITEM_URL_DICT[url_name]['model']           
            # Special case for user which we dont need to check theirs passwords.
            if 'params' in self.FORM_DATA_LIST[url_name].keys():
                params = self.FORM_DATA_LIST[url_name]['params']
            else:
                params = self.FORM_DATA_LIST[url_name]
            
            objlist = modelBase.objects.filter(**params)
            
            if not objlist:
                qs = modelBase.objects.all()                
                    
                self.fail('Object still not created')
            
            chk_id = None
            for item in objlist:
                if chk_id:
                    self.fail('Got more than 1 key filtering an item')
                    
                chk_id = item.pk                
            #Modifying
            resp = self.client.post(reverse('editItem', args=[url_name, chk_id] ), self.MODIFY_FORM_DATA_LIST[url_name] )                              
            self.failUnlessEqual(resp.status_code, 302)            
            # Special case for user who we dont need to check theirs passwords.
            if 'params' in self.MODIFY_FORM_DATA_LIST[url_name].keys():
                params = self.MODIFY_FORM_DATA_LIST[url_name]['params']
            else:
                params = self.MODIFY_FORM_DATA_LIST[url_name]
            
            objlist = modelBase.objects.filter(**params)
            
            if not objlist:
                # DEBUG
                qs = modelBase.objects.all()                
                
                self.fail('Object not modified')
            
            #Delete the item    
            resp = self.client.get(reverse('editItem', args=[url_name, chk_id, 'true'] ) )                        
            self.failUnlessEqual(resp.status_code, 302)
            
            try:        
                temp = obj.objects.filter(pk=chk_id)
                self.fail('Object not deleted')
            except:        
                pass                           
        #endfor
        self.assertTrue
