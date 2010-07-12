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
from mt.models import *

admin.site.register(ResponseMessage)

class BodyAdmin(admin.ModelAdmin):
	list_display = ('plainTxt', 'mms')

admin.site.register(Body, BodyAdmin)

class AttachmentAdmin(admin.ModelAdmin):
	list_display = ('contentType', 'file')

admin.site.register(Attachment, AttachmentAdmin)

class MessageAdmin(admin.ModelAdmin):
	list_display = ('account', 'mobile', 'processed', 'body')
	date_hierarchy = 'activationDate'
	list_filter = ['account', 'processed']

admin.site.register(Message, MessageAdmin)

class ChannelAdmin(admin.ModelAdmin):
	#list_display = ('name', 'description', 'active', 'customer')
    list_display = ('name', 'description', 'active')
    list_filter = ['customer', 'active']

admin.site.register(Channel, ChannelAdmin)

class SubscriberAdmin(admin.ModelAdmin):
	list_display = ('mobile', 'creationDate', 'name')
	search_fields = ['mobile']
	date_hierarchy = 'creationDate'
#	list_filter = ['customer']

admin.site.register(Subscriber, SubscriberAdmin)

class SMSHistoryAdmin(admin.ModelAdmin):
	list_display = ('message', 'mobile', 'sentDate', 'local_status', 'server_status', 'local_id', 'remote_id')
	search_fields = ['mobile', 'sentDate', 'message__body__plainTxt']
	date_hierarchy = 'sentDate'
	list_filter = ['priority', 'mobile', 'local_status', 'server_status']

admin.site.register(SMSHistory, SMSHistoryAdmin)

class SMSQueueAdmin(admin.ModelAdmin):
	list_display = ('message', 'mobile', 'priority', 'queueDate', 'processedDate', 'nextProcDate')
	list_filter = ['mobile', 'priority']

admin.site.register(SMSQueue, SMSQueueAdmin)

class ChannelMessageAdmin(admin.ModelAdmin):
	list_display = ('message', 'channel', )
	list_filter = ['channel']

admin.site.register(ChannelMessage, ChannelMessageAdmin)

#class ChannelStatsAdmin (admin.ModelAdmin):
#    list_display = (
#        'channel', 'numSent', 'numMessages', 'numJoins',
#        'numLeaves', 'numSubscribers', 'month', 'year'
#    )
#    search_fields = ['channel', ]
#    list_filter = [ 'channel', 'year', 'month'] 

#admin.site.register(ChannelStats, ChannelStatsAdmin)

