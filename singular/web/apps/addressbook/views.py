# -*- coding:utf-8 -*-

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

from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.conf import settings
from django.contrib.auth.decorators import login_required

from smlog.views import info, error
from models import *
from forms import *
from manager.menu import *
from mt.models import Message, adapt_mobile
from mt.constants import ERROR_MSG

def contactMenu(request):
    """
        Creates the Contact list left menu
    """
    m = []
    list = appendMenu(m, _('Contacts'), reverse('contacto_listar'))
    appendSubmenu(m, list, _('New contact'), reverse('contacto_crear'))
    appendSubmenu(m, list, _('Contact list'), reverse('contacto_listar'))
    appendSubmenu(m, list, _('Search contact'), reverse('contacto_buscar')),
    return m

def actionMenu(request):
    """
        Creates the Contact list left menu
    """
    m = []
    list = appendMenu(m, _('Import/Export'), reverse('importar_agenda'))
    appendSubmenu(m, list, _('Import'), reverse('importar_agenda'))
    appendSubmenu(m, list, _('Export'), reverse('exportar_agenda'))
    appendSubmenu(m, list, _('Import to channel'), reverse('importar_canal')),
    return m

@login_required
def lista_contactos(request):
    rc = RequestContext(request)
    context = {'profile': request.session['profile'] }
    context['crumbs'] = ( ( _('Home') , reverse('root') ),
                          ( _('Contact list') , reverse('contacto_listar') ),
                        )
    info(request, 'lista_contactos', 'Listing contacts')
    setLeftMenu(request, contactMenu(request), _(u'Summary'))
    context['object_list'] = request.user.contacto_set.all()
    if request.POST:
        data = request.POST
        msg = Message.easy_create(data['text'], adapt_mobile(data['mobile']), request.user)
        context['msg'] = msg
    return render_to_response('addressbook/listar_contactos.html',context, rc)

@login_required
def importar(request, channel = False):
    rc = RequestContext(request)
    context = {'profile': request.session['profile'] }
    rev = reverse('importar_agenda')
    if channel:
        rev = reverse('importar_canal')
    context['crumbs'] = ( ( _('Home') , reverse('root') ),
                          ( _('Import') , rev ),
                        )
    info(request, 'importar', 'Import process')
    setLeftMenu(request, actionMenu(request), _(u'Database actions'))
    if request.method == "POST":
        if channel:
            form = ChannelFileDirForm(request.POST, request.FILES)
        else:
            form = FileDirForm(request.POST, request.FILES)
        if form.is_valid():
            result = Contacto.importar(request.user, form.cleaned_data, channel)
            if result:
                context['msg'] = _(u'Import process done. Total new contacts: %d' % result)
            else:
                context['msg'] = _(u'There were errors in import process.')
        else:
            context['form'] = form
    if not 'form' in context:
        if channel:
            context['form'] = ChannelFileDirForm()
        else:
            context['form'] = FileDirForm()
    context['label'] = _(u'Import')
    return render_to_response('addressbook/importar.html', context, rc) 

@login_required
def exportar(request):
    rc = RequestContext(request)
    context = {'profile': request.session['profile'] }
    context['crumbs'] = ( ( _('Home') , reverse('root') ),
                          ( _('Export') , reverse('exportar_agenda') ),
                        )
    info(request, 'exportar', 'Export process')
    setLeftMenu(request, actionMenu(request), _(u'Database actions'))
    if request.method == "POST":
        form = FileTypeForm(request.POST)
        if form.is_valid():
            tipo = form.cleaned_data['type']
            result = Contacto.exportar(request.user, tipo)
            if result:
                return HttpResponse(result, mimetype=TIPOS_RESPUESTA[int(tipo)])
            else:
                context['msg'] = _(u'There were errors in export process.')
        else:
            context['form'] = form
    if not 'form' in context:
        context['form'] = FileTypeForm()
    context['label'] = _(u'Export')
    return render_to_response('addressbook/importar.html', context, rc)

@login_required
def buscar_contactos(request):
    rc = RequestContext(request)
    context = {'profile': request.session['profile'] }
    context['crumbs'] = ( ( _('Home') , reverse('root') ),
                          ( _('Search contact') , reverse('contacto_buscar') ),
                        )
    info(request, 'buscar_contactos', 'Searching contacts')
    setLeftMenu(request, contactMenu(request), _(u'Summary'))
    if request.POST:
        form = SearchForm(request.POST)
        if form.is_valid():
            context['object_list'] = Contacto.search(form.cleaned_data['search_field'], request.user)
            return render_to_response('addressbook/listar_contactos.html',context, rc)
        else:
            context['form'] = form
    else:
        context['form'] = SearchForm()
    return render_to_response('addressbook/buscar_contactos.html', context, rc)

@login_required
def eliminar_contactos(request, id):
    rc = RequestContext(request)
    context = {'profile': request.session['profile'] }
    context['crumbs'] = ((_('Home'), reverse('root')), (_('Delete contact'), reverse('contacto_eliminar', args=[id])),)
    info(request, 'eliminar_contactos', 'Deleting a contact')
    setLeftMenu(request, contactMenu(request), _(u'Summary'))
    item = get_object_or_404(Contacto, pk = id)
    if request.method == 'POST':
        item.delete()
        return HttpResponseRedirect(reverse('contacto_listar'))
    context['object'] = item
    return render_to_response('addressbook/eliminar_contacto.html', context, rc)
    
@login_required
def gestion_datos_contacto(request, id=None):
    rc = RequestContext(request)
    context = {'profile': request.session['profile'] }
    context['crumbs'] = ((_('Home'), reverse('root')), (_('Contact data'), reverse('contacto_datos', args=[id])),)
    info(request, 'gestion_datos_contacto', 'Management contact data')
    setLeftMenu(request, contactMenu(request), _(u'Summary'))
    item = get_object_or_404(Contacto, pk=id)
    form = None
    if request.POST:
        form = item.datos_form()
        form.setData(request.POST)
        new_form = DatoContactoForm(request.POST)
        if form.is_valid() and new_form.is_valid():
            item.update_data(form.cleaned_data)
            if new_form.cleaned_data['clase']:
                dato = new_form.save(item)
        else:
            context['form'] = form
            context['new_form'] = form
    if not 'form' in context:
        context['form'] = item.datos_form()
        context['new_form'] = DatoContactoForm() 
    context['object'] = item 
    context['label'] = _(u'data')
    return render_to_response('addressbook/gestion_datos.html', context, rc)

@login_required
def gestion_direcciones(request, id=None):
    rc = RequestContext(request)
    context = {'profile': request.session['profile'] }
    context['crumbs'] = ((_('Home'), reverse('root')), (_('Contact address'), reverse('contacto_direcciones', args=[id])),)
    info(request, 'gestion_direcciones', 'Management contact address')
    setLeftMenu(request, contactMenu(request), _(u'Summary'))
    item = get_object_or_404(Contacto, pk=id)
    form = None
    if request.POST:
        form = item.direccion_form()
        form.setData(request.POST)
        new_form = DireccionForm(request.POST)
        if form.is_valid() and new_form.is_valid():
            item.update_dir(form.cleaned_data)
            if new_form.cleaned_data['tipo']:
                dato = new_form.save(item)
        else:
            context['form'] = form
            context['new_form'] = form
    if not 'form' in context:
        context['form'] = item.direccion_form()
        context['new_form'] = DireccionForm() 
    context['object'] = item 
    context['label'] = _(u'address')
    return render_to_response('addressbook/gestion_datos.html', context, rc)

@login_required
def gestion_contactos(request, id = None):
    rc = RequestContext(request)
    context = {'profile': request.session['profile'] }
    item = None
    if id:
        context['crumbs'] = ((_('Home'), reverse('root')), (_('Edit contact'), reverse('contacto_editar', args=[id])),)
        info(request, 'gestion_contactos', 'Edition a contact')
        item = get_object_or_404(Contacto, pk = id)
        context['label'] = _(u'Edit')
        context['object'] = item
    else:
        context['crumbs'] = ( (_('Home'), reverse('root')), (_('New contact'), reverse('contacto_crear')),)
        info(request, 'gestion_contactos', 'Adding a new contact')
        context['label'] = _(u'New')
    setLeftMenu(request, contactMenu(request), _(u'Summary'))
    if request.POST:
        form = ContactoForm(request.POST, instance = item) if item else ContactoForm(request.POST)
        if not item:
            dato_form = MultiDatoForm(request.POST)
            dir_form = DireccionForm(request.POST)
        if form.is_valid(): 
            item = form.save(request.user)
        if item and not id and dato_form.is_valid() and dir_form.is_valid():
            data = dato_form.cleaned_data   
            if 'clase' in data and 'phone' in data:
                item.create_data(data['clase'], data['phone'])
            if 'email' in data:
                item.create_data(EM_PERSONAL, data['email']) 
            if dir_form.cleaned_data['tipo']:
                dir = dir_form.save(item)
            return HttpResponseRedirect(reverse('contacto_listar'))
        else:
            context['form'] = form
            if not id:
                context['dato_form'] = dato_form
                context['dir_form'] = dir_form
    else:
        context['form'] = ContactoForm(instance = item) if item else ContactoForm()
        if not id:
            context['dato_form'] = MultiDatoForm() 
            context['dir_form'] = DireccionForm(instance = item.direccion()) if item and item.direccion() else DireccionForm() 
    return render_to_response('addressbook/gestion_contactos.html', context, rc)

