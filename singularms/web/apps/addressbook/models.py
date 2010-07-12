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

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from django.utils.datastructures import SortedDict
from django import forms
import operator

from constants import *
from parsers import *

TIPOS_PARSERS = {
    VCARD21 : vcard21,
    VCARD3  : vcard3,
    CSV     : csv,
}

class Contacto(models.Model):
    """
        Data related to a person: name, surname, date of birth, etc
    """
    nombre = models.CharField(
            verbose_name=_(u'Nombre'),
            max_length = 50,
    )
    apellidos = models.CharField(
            verbose_name=_(u'Apellidos'),
            max_length = 100, blank = True, null = True,
    )
    tratamiento = models.IntegerField(
            verbose_name = _(u'Tratamiento'),
            choices = TRATAMIENTO, blank = True, null = True,
    )
    usuario = models.ForeignKey(User,
            verbose_name = _(u'Usuario'),
    )

    def __unicode__(self):
        if not self.tratamiento == None:
            return u"%s %s %s" % (dict(TRATAMIENTO)[self.tratamiento], self.nombre, self.apellidos)
        return u"%s %s" % (self.nombre, self.apellidos)

    def update_data(self, kwargs):
        for d in self.get_datos():
            if kwargs['%d_del' % d.id]:
                d.delete()
            elif d.clase != int(kwargs['%d_clase' % d.id]) or d.dato != kwargs['%d' % d.id]:
                d.dato = kwargs['%d' % d.id]
                d.clase = int(kwargs['%d_clase' % d.id])
                d.save() 

    def create_data(self, clase, dato):
        self.datocontacto_set.get_or_create(clase = clase, dato = dato)

    def create_dir(self, tipo, domicilio, codPostal, poblacion, provincia, pais):
        self.direccion_set.get_or_create(tipo=tipo, domicilio=domicilio, codPostal=codPostal, poblacion=poblacion, provincia=provincia, pais=pais)

    def update(self, nombre, apellidos, tratamiento):
        self.nombre = nombre
        self.apellidos = apellidos
        self.tratamiento = tratamiento
        self.save()
        
    def get_datos(self):
        return self.datocontacto_set.all()

    @staticmethod
    def datos_contacto(contacto):
        """
            Return a t-uple with all needed data to be used in forms
        """
        if contacto.direccion_set.all():
            direccion = contacto.direccion_set.all()[0]
        else:
            direccion = ""
        telefono = self.tlf_movil()
        if not telefono:
            telefono = self.tlf_casa()
        if not telefono:
            telefono = self.tlf_trabajo()
        correo = self.email()
        return (direccion, telefono, correo)

    def tlf_casa(self):
        try:
            return self.datocontacto_set.filter(clase = T_PERSONAL)[0].dato
        except IndexError:
            return ""

    def tlf_movil(self):
        try:
            return self.datocontacto_set.filter(clase=M_PERSONAL)[0].dato
        except IndexError:
            try:
                return self.datocontacto_set.filter(clase=M_TRABAJO)[0].dato
            except IndexError:
                return ""

    def moviles(self):
        return self.datocontacto_set.filter(clase__in = [M_PERSONAL, M_TRABAJO])
        
    def emails(self):
        return self.datocontacto_set.filter(clase__in = [EM_PERSONAL, EM_TRABAJO])

    def tlf_trabajo(self):
        try:
            return self.datocontacto_set.filter(clase = M_TRABAJO)[0].dato
        except IndexError:
            try:
                return self.datocontacto_set.filter(clase = T_TRABAJO)[0].dato
            except IndexError:
                return ""

    def email(self):
        try:
            return self.datocontacto_set.filter(clase = EM_PERSONAL)[0].dato
        except IndexError:
            try:
                return self.datocontacto_set.filter(clase = EM_TRABAJO)[0].dato
            except IndexError:
                return ""

    def fax(self):
        try:
            return self.datocontacto_set.filter(clase = F_PERSONAL)[0].dato
        except IndexError:
            try:
                return self.datocontacto_set.filter(clase = F_TRABAJO)[0].dato
            except IndexError:
                return ""

    @staticmethod
    def search (query, user):
        datos_contactos = DatoContacto.objects.filter (
                reduce (operator.or_, [ models.Q(dato__icontains = bit, contacto__usuario = user) for bit in query.split() ])
            )

        search_fields = ['domicilio', 'codPostal', 'poblacion', 'provincia', 'pais']
        direccion_contactos = QuerySet(Direccion)
        for bit in query.split (): 
            or_queries = [models.Q(**{'%s__icontains' % field_name: bit, 'contacto__usuario': user}) for field_name in search_fields]
            other_qs = QuerySet(Direccion)
            other_qs.dup_select_related(direccion_contactos)
            other_qs = other_qs.filter(reduce(operator.or_, or_queries))
            direccion_contactos = direccion_contactos & other_qs
        
        search_fields = ['nombre', 'apellidos', ] # your search fields here
        personasEncontradas = QuerySet(Contacto)
        for bit in query.split (): 
            or_queries = [models.Q(**{'%s__icontains' % field_name: bit, 'usuario': user}) for field_name in search_fields]
            other_qs = QuerySet(Contacto)
            other_qs.dup_select_related(personasEncontradas)
            other_qs = other_qs.filter(reduce(operator.or_, or_queries))
            personasEncontradas = personasEncontradas & other_qs

        pe = []
        for p in personasEncontradas:
            pe.append(p)
        for c in datos_contactos:
            if c.contacto not in pe:
                pe.append(c.contacto)
        for d in direccion_contactos:
            if d.contacto not in pe:
                pe.append(d.contacto)

        return pe

    def direccion(self):
        return self.direccion_set.all()

    def get_direccion(self):
        """
            Return a dictionary with all relative address data.
        """
        direccion = ""
        codigo_postal = ""
        poblacion = ""
        provincia = ""
        pais = ""
        direcciones = self.direccion_set.all()
        if direcciones:                                                                       
            d = direcciones[0]
            if d.domicilio: 
                direccion = d.domicilio
            if d.codPostal:
                codigo_postal = d.codPostal
            if d.poblacion:
                poblacion = d.poblacion
            if d.provincia:
                provincia = d.provincia
            if d.pais:
                pais = d.pais
        out = {}
        out['direccion'] = direccion
        out['codigo_postal'] = codigo_postal
        out['poblacion'] = poblacion
        out['provincia'] = provincia
        out['pais'] = pais
        return out

    def datos_form(self):
        from forms import DynamicForm
        kwargs = SortedDict()
        for dat in self.datocontacto_set.all():
            ind = str(dat.id) + '_clase'
            eli = str(dat.id) + '_del'
            kwargs[ind] = forms.ChoiceField(choices=OPCIONES_DICT[dat.clase], label=_(u'Type'), initial=dat.clase)
            kwargs[str(dat.id)] = forms.CharField(max_length=80, label=_(u'Data'), initial=dat.dato)
            kwargs[eli] = forms.BooleanField(required=False, initial=False, label=_(u'Delete?'))
        form = DynamicForm()
        form.setFields(kwargs)
        return form 

    def direccion_form(self):
        from forms import DynamicForm
        kwargs = SortedDict()
        for dir in self.direccion_set.all():
            kwargs['%d_tip' % dir.id] = forms.ChoiceField(choices=OPCIONES_DIRECCION, label=_(u'Type'), initial=dir.tipo)
            kwargs['%d_dom' % dir.id] = forms.CharField(required=False, max_length = 100, label=_(u'Address'), initial=dir.domicilio)
            kwargs['%d_cod' % dir.id] = forms.CharField(required=False, max_length = 5, label=_(u'Post Code'), initial=dir.codPostal)
            kwargs['%d_pob' % dir.id] = forms.CharField(required=False, max_length = 50, label=_(u'City'), initial=dir.poblacion)
            kwargs['%d_pro' % dir.id] = forms.CharField(required=False, max_length = 50, label=_(u'Province'), initial=dir.provincia)
            kwargs['%d_pai' % dir.id] = forms.CharField(required=False, max_length = 50, label=_(u'Country'), initial=dir.pais)
            kwargs['%d_del' % dir.id] = forms.BooleanField(required=False, initial=False, label=_(u'Delete?'))
        form = DynamicForm()
        form.setFields(kwargs)
        return form

    def update_dir(self, kwargs):
        for d in self.direccion():
            if kwargs['%d_del' % d.id]:
                d.delete()
            elif d.tipo != kwargs['%d_tip'%d.id] or d.domicilio != kwargs['%d_dom'%d.id] or d.codPostal != kwargs['%d_cod'%d.id] \
                or d.poblacion != kwargs['%d_pob'%d.id] or d.provincia != kwargs['%d_pro'%d.id] or d.pais != kwargs['%d_pai'%d.id]:
                d.tipo = kwargs['%d_tip' % d.id]
                d.domicilio = kwargs['%d_dom' % d.id]
                d.codPostal = kwargs['%d_cod' % d.id]
                d.poblacion = kwargs['%d_pob' % d.id]
                d.provincia = kwargs['%d_pro' % d.id]
                d.pais = kwargs['%d_pai' % d.id]
                d.save()

    @staticmethod
    def importar(user, args, channel = False):
        file = args['file']
        tipo = args['type']
        if channel and 'channel' in args:
            channel = args['channel']
        info = file.read()
        parser = TIPOS_PARSERS[int(tipo)](user, channel)
        return parser.parse(info)

    @staticmethod
    def exportar(user, tipo):
        parser = TIPOS_PARSERS[int(tipo)](user)
        return parser.export()

class Direccion(models.Model):
    """
        Address model
    """
    tipo = models.IntegerField(
            verbose_name = _(u'Kind of address'),
            choices = OPCIONES_DIRECCION, blank = True, null = True,
    )
    domicilio = models.CharField(
            verbose_name = _(u'Address'),
            max_length = 100, blank = True, null = True,
    )
    codPostal = models.CharField(
            verbose_name = _(u'Zip code'),
            max_length = 5, blank = True, null = True
    )
    poblacion = models.CharField(
            verbose_name = _(u'City'), 
            max_length = 50, blank = True, null = True
    )
    provincia = models.CharField(
            verbose_name = _(u'Province/State'),
            max_length = 50, blank = True, null = True
    )
    pais = models.CharField(
            verbose_name = _(u'Country'),
            max_length = 50, blank = True, null = True
    )
    contacto = models.ForeignKey(
            Contacto,
            verbose_name = _(u'Person')
    )

    def __unicode__(self):
        cad = u""
        if self.domicilio:
            cad += self.domicilio + " "
        if self.poblacion:
            cad += self.poblacion + " "
        if self.codPostal:
            cad += "CP: " + self.codPostal + " "
        if self.provincia:
            cad += "- " + self.provincia + " "
        if self.pais:
            cad += "(" + self.pais.capitalize() + ")" 
        return cad.rstrip()

    class Meta:
        verbose_name = _(u'Address')
        verbose_name_plural = _(u'Addresses')

class DatoContacto(models.Model):
    """
        Contact data
    """
    clase = models.IntegerField(
            verbose_name = _(u'Kind'),
            choices=OPCIONES_CONTACTO
    )
    dato = models.CharField(
            verbose_name = _(u'Data'),
            max_length = 80
    )
    contacto = models.ForeignKey(
            Contacto,
            verbose_name = _(u'Contact')
    )

    def __unicode__(self):
        return u"%s: %s" %( dict(OPCIONES_CONTACTO)[self.clase], self.dato)

    class Meta:
        unique_together = [['dato', 'clase', 'contacto']] 
    
    def get_dato_corto(self):
        return self.dato[:15] 

    def show(self):
        return '(Trab.)' if self.clase % 2 else '(Priv.)' 
