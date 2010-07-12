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

import types

# Here we can't use ugettext_lazy because the header menu is stored in the 
# session. The session data is saved to disk using serialization (pickle 
# module) and this module can't serialize a Proxy object
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.conf import settings
from mt.constants import MESSAGE_TYPE_CHANNEL, MESSAGE_TYPE_INDIVIDUAL

def appendMenu(menu, name, url):
	"""
		Add a menu
	"""
	m = (name, {'url' : url, 'selected' : False, 'subMenu' : []})
	menu.append (m)
	return m

def appendSubmenu(mainMenu, menuTitle, subMenuTitle, url, selected = False):
	"""
		Add a submenu in the given menu
	"""
	if type(menuTitle) != types.TupleType:
		if (dict(mainMenu).get(menuTitle) == None):
			return {}
		m = dict(mainMenu).get(menuTitle)['subMenu']
	else:
		m = menuTitle[1]['subMenu']

	s = {
        'title': subMenuTitle,
		'url': url,
		'selected': selected,
	}
	m.append(s)
	return s

def setLeftMenu(request, menu, title):
	"""
		Set the menu and the title
	"""
	request.session['profile']['leftMenu'] = menu
	request.session['profile']['leftMenuTitle'] = title

def setRightMenu(request,menu,title):
    request.session['profile']['rightMenu'] = menu
    request.session['profile']['rightMenuTitle'] = title

def clearLeftMenu(request):
	request.session['profile']['leftMenu'] = None

def create_header_menu(admin, channelAdmin, customer):
    """
        This method creates the header menu
    """
    m = []
    #TODO: Define menu to role exactly
    appendMenu(m, _('Start'), reverse('root') )

    if customer or admin or channelAdmin:
        # Send menu
        sendMenu = appendMenu(m, _('Send'), '#')
        appendSubmenu(m, sendMenu, _('Send messages'), reverse('easySend'))
        appendSubmenu(m, sendMenu, _('Outgoing message list'),
            reverse ('messagelist', args = [MESSAGE_TYPE_INDIVIDUAL]))
 
    if admin:
        # MO menu
        receptionMenu = appendMenu(m, _('Reception'), '#')
        appendSubmenu(m, receptionMenu, _('Commands'),
            reverse('showItemSummary', args=['advcommands']))
        appendSubmenu(m, receptionMenu, _("Command's assistants"),
            reverse('showItemSummary', args=['normalcommands']))
        appendSubmenu(m, receptionMenu, _(u'Incoming messages'),
            reverse('showIncomingMessages', ))   

    if channelAdmin or admin:
        # Channel menu
        channelMenu = appendMenu(m, _('Channels'), '#')
        appendSubmenu(m, channelMenu, _('Channels list'), reverse('showList'))
        appendSubmenu(m, channelMenu, _('Subscribers'), reverse('showSubscriber'))

    if admin:
        # Administration menu
        appendMenu(m, _('Administration'), '#')        
        appendSubmenu(m, _('Administration'), _('Accounts & Payments'),
            reverse('showItemSummary', args = ['accpay']))        
        appendSubmenu(m, _('Administration'), _('Users'),
            reverse('showItemSummary', args = ['users']))
        appendSubmenu(m, _('Administration'), _('Assistants for creation'),
            reverse('showItemSummary', args = ['assistants']))
        appendSubmenu(m, _('Administration'), _('Logs'), reverse('logIndex'))

    if settings.ACTIVE_ADDRESS_BOOK and (customer or admin or channelAdmin):
        # AddressBook
        addressBook = appendMenu(m, _(u'Address Book'), '#')
        appendSubmenu(m, addressBook, _(u'Contact list'), reverse('contacto_listar', args=[]))
        appendSubmenu(m, addressBook, _(u'Import/Export'), reverse('importar_agenda', args=[]))

    # Help menu
    # aboutMenu = appendMenu(m, _('Help'), '#')
    # appendSubmenu(m, aboutMenu, _('Profiles and rights'), reverse('help', args=['rol_and_right']))
    # appendSubmenu(m, aboutMenu, _('Web Map'), reverse('help', args=['web_map']))
    # appendSubmenu(m, aboutMenu, _('Send sms'), reverse('help', args=['send_sms']))
    # appendSubmenu(m, aboutMenu, _('Account & Payments'), reverse('help', args=['acc_and_pay']))
    # appendSubmenu(m, aboutMenu, _('Users'), reverse('help', args=['users']))
    # appendSubmenu(m, aboutMenu, _('Logs'), reverse('help',  args=['logs']))
    # appendSubmenu(m, aboutMenu, _('Message and channel list'), reverse('help', args=['info']))
    # appendSubmenu(m, aboutMenu, _('Receive'), reverse('help', args=['receive']))
    # appendSubmenu(m, aboutMenu, _('Creation assistant'), reverse('help', args=['creation_assistant']))
    return m

