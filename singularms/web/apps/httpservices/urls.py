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

urlpatterns = patterns('httpservices.views',
    url(r'^test',           'testHTTP',         name='test_http'),
    url(r'^send',           'sendSMS',          name='send_sms'),
    url(r'^send_many',      'sendSMSmany',      name='send_many'),
    url(r'^send_channel',   'sendSMSToChannel', name='send_channel'),
    url(r'^get_account',    'getAccounts',      name='get_accounts'),
    url(r'^get_channels',   'getChannels',      name='get_channels'),
    url(r'^get_credit',     'getCredit',        name='get_credit'),
    url(r'^get_status',     'getStatus',        name='get_status'),
    url(r'^update_incoming','updateIncoming',   name='update_incoming'),
)

