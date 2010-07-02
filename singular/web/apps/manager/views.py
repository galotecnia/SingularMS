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

from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.http import *
from django.template import RequestContext

from accounting.models import *
from accounting.decorators import checkMessageAdmin
from smlog.views import info, error, warning
from smlog.models import LOGPRIO_LIST
from forms import loginForm, DateForm, aweekago, today
from menu import create_header_menu

from time import gmtime, strftime
from os import makedirs

TEMPLATES = {
    'help': { 
        'rol_and_right': 'help/roles.html',
        'web_map': 'help/web_map.html',
        'send_sms': 'help/send_sms.html',
        'acc_and_pay': 'help/acc_and_pay.html',
        'users': 'help/users_help.html',
        'logs': 'help/logs_help.html',
        'info': 'help/info_help.html',
        'receive': 'help/receive_help.html',
        'stats': 'help/stats_help.html',
        'creation_assistant': 'help/creation_assistant.html'
    },
    'statistics': 'statistics.html',
    'root': 'index.html',
    'errors': 'base.html',
    'login': 'login.html'
}

def index(request):
    """
        Login view
    """
    if not request.user or not request.user.is_authenticated():
        # Not autenticate user, show login form
        form = loginForm ()
        if request.method == 'POST':
            form = loginForm (request.POST)
            if form.is_valid ():
                user = authenticate (username = form.data['username'], 
                                     password = form.data['password']
                                    )
                if user is not None:
                    login (request, user)
                    info (request, 'index', 
                          'User %(username)s logged in ' % {'username':user.username}
                         )
                    request.session['profile'] = getProfile (user)
                    menu = request.session['profile']                    
                    if request.GET.has_key ('next'):
                        return HttpResponseRedirect(request.GET['next'])
                    data = {}
                    try:
                        credits = {}
                        u = Customer.objects.get(id=request.user.id)
                        for account in u.account_set.all():
                            credits[account.name] = account
                        data['credit'] = credits
                    except Customer.DoesNotExist:
                        if checkAdmin(user):
                            for account in Account.objects.all():
                                credits[account.name] = account
                            data['credit'] = credits
                    data['profile'] = menu
                    return render_to_response(TEMPLATES['root'], data,
                                                RequestContext (request)
                                             )
                else:
                    warning (request, 'index', 
                             'Invalid username or password'
                            )
                    form.errors['username'] = [
                                            _('Invalid username and password')
                                              ]
            else:
                warning (request, 'index', _('Posted values not valid'))
        else:
            info (request, 'index', 'Showing login form')
        data = {}
        data['form'] = form
        data['profile'] = getProfile(request.user)
        return render_to_response(TEMPLATES['login'], data , RequestContext (request))
    else:
        # Autenticate user
        try:
            data = {}
            try:
                credits = {}
                user = Customer.objects.get(id=request.user.id)
                for account in user.account_set.all():
                    credits[account.name] = account
                data['credit'] = credits
            except Customer.DoesNotExist:
                if (checkAdmin(request.user)):
                    for account in Account.objects.all():
                        credits[account.name] = account
                    data['credit'] = credits
            data['profile'] = request.session['profile']                            
            data['showInfoToUser'] = getOutputMsg(request)

            return render_to_response(TEMPLATES['root'], 
                                      data, 
                                      RequestContext (request)
                                     )            
        except KeyError:
            # Profile not correctly loaded, so we log out
            # and ask for login            
            return logout_view(request)            
                       
def logout_view (request):
    """
        Logout view
    """
    info (request, 'logout_view', 
                    'User %(username)s logged out ' % {'username':request.user.username}
         )
    logout(request)
    #return HttpResponseRedirect("/")
    return HttpResponseRedirect( reverse('root') )

def getOutputMsg(request):
    """
        Checks for a session variable, and
        returns it for template rendering
    """
    output = None
    if "showInfoToUser" in request.session:
        output = request.session['showInfoToUser']
        del request.session['showInfoToUser']
        
    return output    

def show_help(request,help):
    templates_help = {}
    for key in TEMPLATES['help'].keys():
        templates_help[key]=key
    if help in TEMPLATES['help']:
        if 'profile' in request.session:
            return render_to_response(TEMPLATES['help'][help],{'profile':request.session['profile'],'templates_help':templates_help},RequestContext(request))
        else:
            return render_to_response(TEMPLATES['help'][help],{'templates_help':templates_help},RequestContext(request))
    else:
        raise Http404

def getProfile (user):
    """
        Create the user profile. The return value of this functions must be passed to all the templates.
    """
    if not user:
        return {}
    messageAdmin = channelAdmin = admin = customer = False
    if checkAdmin (user):
        messageAdmin = channelAdmin = admin = True
    elif checkChannelAdmin (user):
        channelAdmin = True
    elif checkCustomer (user):
        customer = True

    profile = {}
    profile['admin'] = admin
    profile['channelAdmin'] = channelAdmin
    profile['customer'] = customer
    profile['headerMenu'] = create_header_menu(admin, channelAdmin, customer)
    return profile

def show_statistics(request, id):
    data = {}
    data['profile'] = request.session['profile']                            
    data['showInfoToUser'] = getOutputMsg(request)
    try:
        account = Account.objects.get(pk = id)
    except Account.DoesNotExist:
        raise Http404
    inicio = aweekago()
    fin = today()
    if request.POST:
        form = DateForm(request.POST)
        if form.is_valid():
            inicio = form.cleaned_data['inicio']
            fin = form.cleaned_data['fin']
        data['form'] = form
    else:
        data['form'] = DateForm()
    data['datos'] = account.get_statistics(inicio, fin)
    return render_to_response(TEMPLATES['statistics'], data, RequestContext(request))


