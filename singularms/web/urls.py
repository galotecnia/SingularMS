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
from django.conf import settings
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$',                  'manager.views.index', name='root'),
    url(r'^accounts/login/$',   'manager.views.index', name='login'),
    url(r'^accounts/logout/$',  'manager.views.logout_view', name="logout"),

    url(r'^manager/',           include('manager.urls')),
    url(r'^accounting/',        include('accounting.urls')),
    url(r'^mt/',                include('mt.urls')),
    url(r'^mo/',                include('mo.urls')),
    url(r'^smlog/',             include('smlog.urls')),
    url(r'^ws/',                include('webservice.urls')),
    url(r'^http/',              include('httpservices.urls')),
    url(r'^addressbook/',       include('addressbook.urls')),

    url(r'^admin/(.*)',         admin.site.root),

    url(r'^site_media/(.*)$',   'django.views.static.serve', {'document_root': './media', 'show_indexes': True}),
    url(r'^attachments/(.*)$',  'django.views.static.serve', {'document_root': './media/attachments', 'show_indexes': True}),
)

