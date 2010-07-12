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

import calendar, datetime
from datetime import date

from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.list_detail import object_list
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.models import User, Group
from django.forms.models import modelformset_factory
from django.forms import ModelForm

from models import admin_required
from manager.menu import *

from smlog.views import info, warning, error
from smlog.models import LOGPRIO_LIST, Log

from mo.models import IncomingMessage, Command, ReplyCommand, AdminCommand, ExternalCommand, COMMAND_TYPE_LIST 
from mo.models import ADMIN_COMMAND_LIST_CHOICES, ExternalCommand, getNameFromTuple

from mo.forms import *

from mt.models import Body, Channel
from mt.forms import ChannelForm, BodyForm

from accounting.models import * 
from accounting.forms import *

#NOTE:Deprecated means it will disappear, but isn't the time for dropping it yet.

#Templates:
SUMMARY_ITEM_TEMPLATE = "item_summary.html"
ITEM_TEMPLATE = "item.html"
EDIT_ITEM_TEMPLATE = "edit_item.html"
BASE_ITEM_LIST_TEMPLATE = "base_item_list.html"

GROUPS_URL_FULLNAMES = {'accpay': _('Accounts & Payment'),
                        'users': _('Users'),
                        'assistants': _('Assistants for creation'),
                        'messages': _('Messages'),
                        'advcommands': _('Commands'),
                        'normalcommands': _('Assistants for commands') }

URL_GROUPS = ['accpay', 'users']

URL_GROUP_ITEMS = { 'accpay': ('account', 'access', 'purchase'),
                    'users': ('customer', 'provider'),
                    'assistants': ['customerwizard'],
                    'messages': ('msgbody', 'incomingmsg', 'channel'),
                    'advcommands': ('basecommand', 'admincommand', 'replycommand', 'externalcommand'),
                    'normalcommands': ('easyreplycomm', 'easyadmincomm', 'extcommwizard') }

# Used for following many to many relationships.
SPECIAL_KEYFIELDS = {'account_id': Account, 'customer_id': Customer, 
                     'access_id': Access, 'provider_id': Provider,
                     'body_id': Body, 'command_id': Command,
                     'channel_id': Channel,
                     'defaultAnswer_id': Body,
                     'answer_id': Body}

CHOICE_FIELDS = {'type': COMMAND_TYPE_LIST,
                 'backend': BACKEND_LIST}

#DEPRECATED
VERBOSE_KEYS = {'account_id' : _('account'), 
                'endDate': _('ending Date'), 
                'customer_id': _('customer'), 
                'access_id': _('access'), 
                'last_login': _('last login'),
                'body_id': _('text'),
                'creationDate': _('creation date'),
                'command_id': _('pattern'),
                'channel_id': _('channel'),
                'provider_id': _('provider'),
                'defaultAnswer_id': _('default answer'), }

# Indexes item's data through its urls
ITEM_URL_DICT = {
 'account':    {'model': Account,  'form': accountForm,  'group': 'accpay', 
              'keys': ('name', 'customer', 'access'), 'depencies': Access },
 'access':   {'model': Access,   'form': accessForm,   'group': 'accpay', 'keys': ('name', 'provider', 'backend') },
 'purchase': {'model': Purchase, 'form': purchaseForm, 'editform': edit_purchaseForm, 'group': 'accpay', 'depencies': Account},
 'customer': {'model': Customer, 'form': customerForm, 'editform': edit_customerForm, 'group': 'users', 'keys': ('username', 'last_login') },
 'asist_customer': {'model': Customer, 'form': assistantCustomerForm, 'group': 'assistants', 
                    'label': _("Customer, account and purchase"), 'args': ['no_links']},
 
 'provider': {'model': Provider, 'form': providerForm, 'editform': edit_providerForm, 'group': 'users', 'keys': ('username', 'last_login') }, 
 'msgbody': {'model': Body, 'form': BodyForm, 'group': 'messages'},
 # mo
 'incomingmsg': {'model': IncomingMessage, 'form': incomingMsgForm, 'group': 'messages'},
 'basecommand': {'model': Command, 'form': commandForm, 'group': 'advcommands'},
 'admincommand': {'model': AdminCommand, 'form': adminCommandForm, 'group': 'advcommands', },
                  # 'depencies': Command, 'args': ['cascade_delete']},
 'replycommand': {'model': ReplyCommand, 'form': replyCommandForm, 'group': 'advcommands', 'depencies': Command }, 
 'externalcommand': {'model': ExternalCommand, 'form': ExternalCommandForm, 'group': 'advcommands', },
                    # 'args': ['cascade_delete'], 'depencies': Command}, 
 'easyreplycomm': {'model': Command, 'form': newCompleteReplyCommandForm, 
                   'group': 'normalcommands', 'label': _('Full reply command'), 'keys': ('pattern', 'activationDate', 'deactivationDate') },
 'easyadmincomm': {'model': Command, 'form': singleAdminCommandForm, 'form_args': ('language'), 
                   'group': 'normalcommands', 'label': _('Single admin command') },
 # Wizards
 'extcommwizard': {'model': ExternalCommand, 'form': ExtCommWizardForm, 'group': 'normalcommands', 
                   'label': _('External command wizard'), 'form_args': ('wizard'), 'args': ['no_links'],
                   'formlist': [ExtCommForm, ServCoreForm, ServArgForm, ServArgListForm] },
 'customerwizard': {'model': Customer, 'form': customerFormWizard, 'group': 'assistants', 
                    'label': _("Customer wizard"), 'form_args': ['wizard'], 'args': ['no_links'],
                    'formlist': [customer_wizardhook, account_wizardhook, purchase_wizardhook ] },                   
 }

ITEM_URL_QUERY = {'easyreplycomm': {'type': 1 },
                  'easyadmincomm': {'type': 2 }  }

def getGroupname_from_urlname(urlname):
    for group in URL_GROUP_ITEMS.keys():
        if urlname in URL_GROUP_ITEMS[group]:
            return group
    return None

def getGroupFullname(urlname):
    if urlname in GROUPS_URL_FULLNAMES.keys():
        return GROUPS_URL_FULLNAMES[urlname]
    return _(urlname).title()    

def baseItemMenu(request, name=None):
    """ 
        Generates the base item menu
    """        
    m = []  
    if name in URL_GROUP_ITEMS.keys():
        group = name                
    elif name in ITEM_URL_DICT:
        group = getGroupname_from_urlname(name)
    else:
        warning(request, 'baseItemMenu', "Requested an url which doesn't exist: %(name)s" % {'name': name} )
        raise Http404
    
    logMenu = appendMenu(m, getGroupFullname(group), reverse('showItemSummary', args=[group] ) )
            
    for url in URL_GROUP_ITEMS[group]:
        if 'label' in ITEM_URL_DICT[url].keys():
            appendSubmenu (m, logMenu, ITEM_URL_DICT[url]['label'],
                       reverse('showItem', args=[url]))
        else:
            appendSubmenu (m, logMenu, ITEM_URL_DICT[url]['model']._meta.verbose_name,
                       reverse('showItem', args=[url]))            
    setLeftMenu (request, m, _('Summary') )

def getObj(request, name="Unk", id=None):
    """
        Returns a object list according the url specified, 
        or a defined object trough an id.
    """
    try:
        data = ITEM_URL_DICT[name]            
    except KeyError:
        warning (request, 'getObj', "Requested an item which doesn't exist: %(name)s" % {'name': name}) 
        raise Http404      
    if id:
        item = get_object_or_404(data['model'], id=id)        
        return item        
    objlist = getListFromQuery(request, objModel=data['model'], id=id, name=name)
    return objlist

def getReadyForm(request, form=[], obj=None, urlname=None):
    """
        Decides whenever if a POST form is needed or not.
    """    
    info (request, 'getReadyForm', 'Decides whenever if a POST form is needed or not.')
    kwargs = {}    
    if obj:
        kwargs = {'instance': obj}        
    try:
        if 'language' in ITEM_URL_DICT[urlname]['form_args']:
            kwargs['language'] = request.LANGUAGE_CODE
    except KeyError:
        pass
    if request.method == "POST":
        item = form(request.user.id, request.POST, **kwargs)
    else:
        item = form(request.user.id, **kwargs)    
    return item

def getForm(request, name='', obj=None, editing=False):
    """
        Returns a form according an url
    """
    info (request, 'getForm', 'Getting a form')
    if editing:
        try:
            form = getReadyForm(request, form=ITEM_URL_DICT[name]['editform'],
                                obj=obj, urlname=name)
            return form
        except KeyError:
            pass
    try:
        form = getReadyForm(request, form=ITEM_URL_DICT[name]['form'], obj=obj, urlname=name)         
    except KeyError:
        error(request, 'getForm', "Form not found for this url: %(name)s" % {'name': name} )
        raise Http404    
    return form

@admin_required
def editItem(request, name, id, form=None, template_name=EDIT_ITEM_TEMPLATE, delete=False):
    """
        Edit an user item profile
    """    
    info (request, 'editItem', 'Editing an item')
    try:        
        obj = getObj(request, name, id)
    except Http404:
        warning (request, 'editItem', "Requested an item which doesn't exist: %s" % name)
        raise Http404
    if delete:
        obj.delete()
        return HttpResponseRedirect(reverse("showItem", args=[name]))    
    baseItemMenu(request, name)    
    form = getForm(request, name, obj, editing=True)
    
    if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse("showItem", args=[name]))
    
    return render_to_response(template_name, { "form": form,
                                                "name": name,
                                                "id": id,
                                                'profile':    request.session['profile'],
                                            }, context_instance=RequestContext(request))
        
@admin_required
def showItem(request, name, template_name=ITEM_TEMPLATE, showMenu=True, showLinks=True):    
    """
        Show general information about an item family
    """
    info (request, 'showItem', 'Showing item specific information')
    try:
        if 'no_links' in ITEM_URL_DICT[name]['args']:
            showLinks = None
    except KeyError:
        pass    
    if showMenu:
        baseItemMenu(request, name)
    # Handling the depencies
    try:
        model = ITEM_URL_DICT[name]['depencies']
        objlist = model.objects.all()[:1]
    except KeyError:
        objlist = model = None
    if not objlist and model:
        # The form is't displayed. Instead a message is shown
        items = getObj(request, name)
        output = _("A new instance cannot be created without a previous instance of")
        output += " " + _(model._meta.verbose_name)
        request_context = { "group": items,
                    "profile" : request.session['profile'],
                    "name":    name,
                    "form":    None,
                    'form_wizard': None,
                    "object_list": items[2],
                    'showInfoToUser': output,
                    "showLinks": showLinks}
        return render_to_response(template_name, request_context, 
                                context_instance=RequestContext(request))
    # Handling the wizard
    try:
        formlist = ITEM_URL_DICT[name]['formlist']
        formwizard = ITEM_URL_DICT[name]['form']        
    except KeyError:
        formwizard = None
    if formwizard:
        items = getObj(request, name)        
        request_context = { "group": items,
                        "profile" : request.session['profile'],
                        "name":    name,
                        'form_wizard': True,
                        "object_list": items[2],
                        "showLinks": showLinks,
                        'template': template_name }        
        response = formwizard(formlist).__call__(request, extra_context=request_context)
        if response:
            return response
        group = getGroupname_from_urlname(name)
        if not group:
            return HttpResponseRedirect(reverse("root", args=[] ) )
        return HttpResponseRedirect(reverse("showItemSummary", args=[group] ) )
    # Normal form.
    form = getForm(request, name)                
    if form.is_valid():
        form.save(commit=True)
        if not showLinks:
            group = getGroupname_from_urlname(name)
            return HttpResponseRedirect(reverse("showItemSummary", args=[group] ) )            
        
    items = getObj(request, name)
    request_context = { "group": items,
                        "profile" : request.session['profile'],
                        "name":    name,
                        "form":    form,
                        'form_wizard': None,
                        "object_list": items[2],
                        "showLinks": showLinks}   
    if name == "purchase":
        request_context['caducate'] = Purchase.caducates()
        request_context['no_available'] = Purchase.no_available()
    return render_to_response(template_name, request_context, context_instance=RequestContext(request) )

def getRow(request, block, keyfield, obj, urlname=None):    
    # Special cases:    
    # Handling choicefields.
    if keyfield in CHOICE_FIELDS.keys():
        fullname = getNameFromTuple(CHOICE_FIELDS[keyfield], obj[keyfield])
        if fullname:
                block.append(fullname)
                return None
        else:
            warning (request, 'getRow', "Requested field: %s, which doesn't exist for %s. Fields are: %s"
                  % (keyfield, urlname, obj) )            
    if keyfield in 'action':        
        num = obj[keyfield]
        for item in ADMIN_COMMAND_LIST_CHOICES:
            if item[0] is num:
                block.append(item[1])
                return None
        else:
            warning (request, 'getRow', "Requested field: %s, which doesn't exist for %s. Fields are: %s"
                  % (keyfield, urlname, obj) )
    # Adding the field by default            
    try:    
        block.append(obj[keyfield])
        return None
    except KeyError:
        pass
    new_keyfield = keyfield + '_id'
    try:
        primaryKey = obj[new_keyfield]
    except KeyError:    
        warning (request, 'getRow', "Requested field: %s, which doesn't exist for %s. Fields are: %s"
                  % (keyfield, urlname, obj) )        
        raise Http404  
    # Lets get the unicode data  
    if new_keyfield in SPECIAL_KEYFIELDS.keys():
        model = SPECIAL_KEYFIELDS[new_keyfield]
        try:
            data = model.objects.get(pk=primaryKey)
        except model.DoesNotExist:
            data = None
        block.append(data)
        return None    
    return None
    
def getKeys(objModel, urlname=None):
    try:        
        return ITEM_URL_DICT[urlname]['keys']
    except KeyError:
        pass    
    try:
        return objModel.default_fields        
    except AttributeError:
        pass        
    #Nothing found, so get all the keys by default.
    fkeys = []
    for field in objModel._meta.fields:
        if field.name is not 'id':
            fkeys.append(field.name)
    return fkeys

def getListFromQuery(request, objModel, id=None, name=None):
    """
        Generates a list from a object, ready for template using.   
        
        A list is returned to the template, containing for every index:
        - Global name of the item
        - Name of the fields
        - Data contained on a list
        
        It is assumed that all the variables which are sent doesn't have any errors.
        This is checked before in the previous view.
    """
    info(request, 'showItem', 'Getting a list from a query')
    if 'label' in ITEM_URL_DICT[name].keys():
        globalname = ITEM_URL_DICT[name]['label']
    else:
        globalname = _(objModel._meta.verbose_name)
    # Get special queries if available.
    if name in ITEM_URL_QUERY.keys():
        allobj = objModel.objects.filter(**ITEM_URL_QUERY[name]).values()
    else:
        allobj = objModel.objects.values()        
    if not allobj:        
        return [globalname, None, None, name]
    
    fkeys = getKeys(objModel, urlname=name)
    cappedObj = []
                        
    for obj in allobj:
        # The django's id is always sent on first place
        block = []
        # Then append the rest of fields.
        # This is done because we want to keep the right order between the keys and the data.
        block.append(obj['id'])        
        for keyfield in fkeys:
            getRow(request, block, keyfield, obj, urlname=name)        
        cappedObj.append(block)
    # Get a better name for a key if available, and translate it    
    pretty_keys = []
    for key in fkeys:
        if key in VERBOSE_KEYS.keys():             
            pretty_keys.append(VERBOSE_KEYS[key] )
            continue                            
        for itemtest in objModel._meta.fields:                
            if key in itemtest.name:
                tempvar = itemtest.verbose_name
                pretty_keys.append(tempvar)
                break
            # Checking fields with '_id'            
        else:
            pretty_keys.append(str(_(key) ) )
    item = [globalname, pretty_keys, cappedObj, name]    
    return item

@admin_required
def showItemSummary(request, name, template_name=SUMMARY_ITEM_TEMPLATE):
    """
        Show general information about an item family
    """
    info (request, 'showItemSummary', 'Showing showItemSummary')    
    baseItemMenu(request, name)    
    try:
        list = URL_GROUP_ITEMS[name]    
    except KeyError:
        error(request, 'showItemSummary', "Requested a url group which doesn't exist: %s" % name)
        raise Http404
    item = []    
    for url in list:
        item.append(getObj(request, name=url) )
        
    return render_to_response(template_name,
        { "item": item, "name": name, "fullname": getGroupFullname(name),
        "profile" : request.session['profile']},
        context_instance=RequestContext(request))
