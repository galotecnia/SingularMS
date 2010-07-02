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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render_to_response 
from django.template import RequestContext

from models import IncomingMessage 
from smlog.views import info 
from manager.menu import setLeftMenu, appendMenu, appendSubmenu
from accounting.views import admin_required

import datetime

def baseItemMenu():
    """ 
        Generates the base item menu
    """        
    m = []    
    logMenu = appendMenu(m, _('Incoming messages'), reverse('showIncomingMessages', args=[]))
    appendSubmenu(m, logMenu, _(u'Incoming messages'), reverse('showIncomingMessages'))
    return m

@admin_required
def showIncomingMessages(request):
    """
        Show general information about an item family
    """
    rc = RequestContext(request)
    context = {'profile': request.session['profile'] }
    context['crumbs'] =  (_('Incoming messages'), reverse('showIncomingMessages')) 
    info(request, 'showIncomingMessages', 'Showing incoming messages specific information')
    setLeftMenu(request, baseItemMenu(), _(u'Summary'))
    context['object_list'] = IncomingMessage.objects.all() 
    return render_to_response('incomingmessage_archive.html', context, rc)
