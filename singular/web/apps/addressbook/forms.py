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

from django.forms import ModelForm
from django import forms
from models import *
from mt.models import Channel
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import AdminDateWidget
from django.conf import settings

class ContactoForm(ModelForm):
    
    class Meta:
        model = Contacto
        exclude = ['id', 'usuario']

    def save(self, user):
        try:
            return Contacto.objects.get(nombre = self.cleaned_data['nombre'], apellidos = self.cleaned_data['apellidos'],
                tratamiento = self.cleaned_data['tratamiento'], usuario = user)
        except Contacto.DoesNotExist:
            item = super(ContactoForm, self).save(commit=False)
            item.usuario = user
            item.save()
            return item

class SearchForm(forms.Form):

    search_field = forms.CharField(max_length = 25, required = False, label = _(u'Search field'))

class DireccionForm(ModelForm):

    class Meta:
        model = Direccion
        exclude = ['id', 'contacto']

    def save(self, user):
        item = super(DireccionForm, self).save(commit=False)
        item.contacto = user
        item.save()
        return item

class DatoContactoForm(ModelForm):

    class Meta:
        model = DatoContacto
        exclude = ['id', 'contacto']

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['clase'].required = False
        self.fields['dato'].required = False
    
    def save(self, user):
        item = super(DatoContactoForm, self).save(commit=False)
        item.contacto = user
        item.save()
        return item


class MultiDatoForm(forms.Form):
    
    clase = forms.ChoiceField(required=False, choices=OPCIONES_TELEFONO, label=_(u'Phone type'))
    phone = forms.CharField(max_length=13, required=False, label=_(u'Phone'))
    email = forms.EmailField(required=False)


class FileTypeForm(forms.Form):
   
    type = forms.ChoiceField(label=_(u'File type'), choices=OPCIONES_IMPORTACION)

class FileDirForm(FileTypeForm):

    file = forms.FileField(label=_(u'Import file'))

class ChannelFileDirForm(FileDirForm):
    
    channel = forms.ModelChoiceField(queryset = Channel.objects.filter(active = True), empty_label=None)

    def __init__(self, *args, **kwargs):
        super(ChannelFileDirForm, self).__init__(*args, **kwargs)
        self.fields['type'].choices = OPCIONES_IMPORTACION_CHANNEL
          
class DynamicForm(forms.Form):
    """
       Dynamic form
    """
    def setFields(self, kwds):
        """
           Set the fields in the form.
        """
        keys = kwds.keys()
        for k in keys:
            self.fields[k] = kwds[k]

    def setData(self, kwds):
        """
           Set the data to include in the form
        """
        keys = kwds.keys()
        for k in keys:
            self.data[k] = kwds[k]
        self.is_bound = True

    def validate(self, post):
        """
        Validate the contents of the form
        """
        for name,field in self.fields.items():
            try:
                field.clean(post[name])
            except ValidationError, e:
                self.errors[name] = e.messages

