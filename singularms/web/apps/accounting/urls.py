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
from accounting.forms import customerFormWizard, accountForm, lite_purchaseForm
from mo.forms import *

urlpatterns = patterns('accounting.views',
    #TODO: Change name to urlname
    url(r'^summary/(?P<name>\w+)/$', 	'showItemSummary',	name="showItemSummary"),    
    url(r'^(?P<name>\w+)/$', 					'showItem', name="showItem"),
    url(r'^(?P<name>\w+)/(?P<id>[0-9]+)/$',		'editItem', name="editItem"),
    url(r'^(?P<name>\w+)/(?P<id>[0-9]+)/(?P<delete>true)/$', 'editItem', name="editItem"),
    
)
