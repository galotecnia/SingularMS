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
from mo.models import *

class IncomingMessageAdmin(admin.ModelAdmin):
    list_display = ('account', 'mobile', 'processed', 'body')
    list_filter = ['account', 'processed']
    date_hierarchy = 'creationDate'

admin.site.register(IncomingMessage, IncomingMessageAdmin)

class CommandAdmin(admin.ModelAdmin):
    list_display = (
            'pattern', 'type', 'active', 'creationDate',
            'activationDate', 'deactivationDate', 'defaultAnswer',
         )
    list_filter = [ 'type', 'active', ]
    search_fields = ['command', ]
    date_hierarchy = 'creationDate'

admin.site.register(Command, CommandAdmin)

class AdminCommandAdmin(admin.ModelAdmin):
    list_display = (
            'command', 'action', 'channel',
         )
    list_filter = [ 'channel', 'action', ]
    search_fields = ['command', 'channel', ]

admin.site.register(AdminCommand, AdminCommandAdmin)

class ReplyCommandAdmin(admin.ModelAdmin):
    list_display = (
            'command', 'startTime', 'endTime', 'answer',
         )
    search_fields = ['command', 'answer',  ]

admin.site.register(ReplyCommand, ReplyCommandAdmin)

class ExternalCommandAdmin(admin.ModelAdmin):
    list_display = (
            'command', 'email', 'url',
         )
    search_fields = ['command', 'email', 'type',  ]
    list_filter = [ 'type', ]

admin.site.register(ExternalCommand, ExternalCommandAdmin) 

class ServiceCoreAdmin(admin.ModelAdmin):
    list_display = (
            'serv_name', 'ext_comm', 
         )
    search_fields = ['ext_comm', 'serv_name', ]
    list_filter = ['ext_comm', ]
  
admin.site.register(ServiceCore, ServiceCoreAdmin)

class ServiceArgAdmin(admin.ModelAdmin):
    list_display = (
            'name', 'type', 'content', 'service',
         )
    search_fields = ['name', 'type', 'service', ]
    list_filter = ['service', ]

admin.site.register(ServiceArg, ServiceArgAdmin)

class CommandStatsAdmin(admin.ModelAdmin):
    list_display = (
            'command', 'numRecvd', 'month', 'year'
         )
    search_fields = ['command', ]
    list_filter = [ 'command', 'year', 'month']

admin.site.register(CommandStats, CommandStatsAdmin)  
