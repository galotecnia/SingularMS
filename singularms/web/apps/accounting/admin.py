# -*- encoding: utf-8 -*-

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

from django.contrib import admin
from accounting.models import *
from smlog.models import Log

class ProviderAdmin(admin.ModelAdmin):
	#list_display = ('name', 'user', )
	list_display = ('id', 'username')

admin.site.register(Provider, ProviderAdmin)

class AccessAdmin(admin.ModelAdmin):
	list_display = ('name', 'description', 'provider', 'backend')
	list_filter = [ 'provider', 'backend', ]

admin.site.register(Access, AccessAdmin)

class CustomerAdmin(admin.ModelAdmin):
	list_display = ('id', 'username')

admin.site.register(Customer, CustomerAdmin)

class AccountAdmin(admin.ModelAdmin):
	list_display = ('customer', 'name', 'access', 'args2') #, 'num_threads')

admin.site.register(Account, AccountAdmin)

class PurchaseAdmin(admin.ModelAdmin):
	#list_display = ('account', 'available', 'reserved', 'initial', 'price', 'startDate', 'endDate')
    list_display = ('account', 'available', 'reserved', 'initial', 'price', 'startDate', 'endDate')
    list_filter = [ 'account', ]

admin.site.register(Purchase, PurchaseAdmin)

class CapabilitiesAdmin(admin.ModelAdmin):
    list_display = ('typeSMS',)

admin.site.register(Capabilities, CapabilitiesAdmin)
