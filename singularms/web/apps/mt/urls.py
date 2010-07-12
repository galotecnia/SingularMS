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

from django.conf.urls.defaults import *

urlpatterns = patterns('mt.views',
    
    # Channel stuff
    url(r'^channel/list/$',                      'channelList',      name='showList'),
    url(r'^channel/list/page(?P<page>[0-9]+)/$', 'channelList',      name='showListPage'),
    url(r'^channel/(?P<object_id>\d+)/update/$', 'updateChannel',    name='update_channel'),
    url(r'^channel/(?P<object_id>\d+)/delete/$', 'deleteChannel',    name='delete_channel'),
    url(r'^channel/subscriber/$',                'showSubscriber',   name='showSubscriber'),
    url(r'^channel/subscriber/(?P<id>\d+)/$',    'update_subscriber',name='update_subscriber'),

    # Sending messages views
    url(r'^send_message/$',                      'easySend',         name='easySend'),
    url(r'^send_to_channel/$',                   'easySend', {'tipo': 'channel'}, name='easyChannelSend'),

    # Ajax views
    url(r'^ajax_sms_types/$',                                'ajax_filter_typesSms', name='ajaxFilterSms'),
    url(r'^ajax_subscriber/$',                               'ajaxSubscriber',       name='ajaxSubscriber'),
    url(r'^ajax_delete_subscriber/$',                        'ajaxDeleteSubscriber', name='ajaxDeleteSubscriber'),
    url(r'^ajax_new_subscriber/$',                           'ajaxNewSubscriber',    name='ajaxNewSubscriber'),
    url(r'^ajax_size_file_upload/$',                         'ajax_size_file_upload',name='ajaxSizeFileUpload'),
    url(r'^ajax_filter/(?P<type>Individual|Channel)/$',      'ajax_filter',          name='ajaxFilter'),
    url(r'^ajax_gen_filter/(?P<type>Individual|Channel)/$',  'ajax_gen_filter',      name='ajaxGenFilter'),
    url(r'^ajax_num_of_subs/$',                              'ajaxNumOfSubscribers', name='ajaxNumOfSubscribers'),
    url(r'^ajax_channel_list/$',                             'ajaxChannelList',      name='ajaxChannelList'),
    url(r'^ajax_new_channel/$',                              'ajaxNewChannel',       name='ajaxNewChannel'),

    # Other views
    url(r'^message/list/type(?P<type>Individual|Channel)/$', 'messageList2',         name='messagelist'),
    url(r'^message/list/status/(?P<id>\d+)/$',               'channel_msgs_status',  name='message_status'),
    url(r'^message/type(?P<type>Individual|Channel)/(?P<object_id>\d+)/delete/$', 'deleteMessage', name='deletemessage'),
    url(r'^message/read/(?P<id>\d+)/$',                      'read_message_responses', name='read_message_responses'),
    url(r'^message/read/$',                      'read_message_responses', name='read_message_responses'),
)

