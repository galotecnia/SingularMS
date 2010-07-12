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

from django.conf.urls.defaults import *

urlpatterns = patterns('views',
	# Example:
	# (r'^celajes/', include('celajes.foo.urls')),
	url(r'^graphLast/(?P<period>(hour|day|week|month|year))/(?P<sensorid>\d+)/((?P<width>\d+)/(?P<height>\d+)/)?(?P<force>(force)/)?(?P<adjust>(float)/)?$', 'graphLast', name='sensors_graph_last'),
	url(r'^graphTime/(?P<period>(hour|day|week|month|year))/(?P<sensorid>\d+)/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<hour>\d+)/((?P<width>\d+)/(?P<height>\d+)/)?(?P<force>(force)/)?(?P<adjust>(float)/)?$', 'graphTime', name='sensors_graph_time'),
)
