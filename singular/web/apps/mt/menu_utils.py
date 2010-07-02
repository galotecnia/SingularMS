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

from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from accounting.models import checkAdmin
from manager.menu import *
from constants import MESSAGE_TYPE_INDIVIDUAL, MESSAGE_TYPE_CHANNEL

#
# Left menus
#
def messageMenu(request):
    """
        Creates the Message list left menu
    """
    m = []
    list = appendMenu(m, _('List messages'), '#')
    appendSubmenu(m, list, _('Individual messages'), reverse('messagelist', args=[MESSAGE_TYPE_INDIVIDUAL]))
    appendSubmenu(m, list, _('Channel messages'), reverse('messagelist', args=[MESSAGE_TYPE_CHANNEL]))
    return m

def createMenuMessages(request):
    """
        Creates the Send Message left menu
    """
    m = []
    m1 = appendMenu(m, _('Destinations'), reverse('easySend'))
    appendSubmenu(m, m1, _('Individual'), reverse('easySend'))
    if request.user.has_perm('mt.can_manage'):
        appendSubmenu(m, m1, _('Channel'), reverse('easyChannelSend'))
    return m 

def create_subscriber_menu():
    """
        Create the Suscribers management left menu
    """
    m = []
    appendMenu(m, _('Subscriber\'s list'), reverse('showSubscriber'))
    return m

def channelMenu ():
    """
        Create the Channel management left menu
    """
    m = []
    appendMenu(m, _('All channels'), reverse('showList'))
    return m

