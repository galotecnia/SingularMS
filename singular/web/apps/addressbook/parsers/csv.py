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

from addressbook.constants import *
from mt.models import Channel, Subscriber
import logging

log = logging.getLogger('galotecnia')

HEADER = '"nombre", "apellidos", "tratamiento", "dom_casa_1", "pob_casa_1", "prov_casa_1", "cod_casa_1", "pais_casa_1", "dom_casa_2", "pob_casa_2", "prov_casa_2", "cod_casa_2", "pais_casa_2", "dom_trab_1", "pob_trab_1", "prov_trab_1", "cod_trab_1", "pais_trab_2", "dom_trab_2", "pob_trab_2", "prov_trab_2", "cod_trab_2", "pais_trab_2", "dom_serv_1", "pob_serv_1", "prov_serv_1", "cod_serv_1", "pais_serv_1", "dom_serv_2", "pob_serv_2", "prov_serv_2", "cod_serv_2", "pais_serv_2", "tlf_pers_1", "tlf_pers_2", "tlf_trab_1", "tlf_trab_2", "mov_pers_1", "mov_pers_2", "mov_trab_1", "mov_trab_2", "email_per_1", "email_per_2", "email_trab_1", "email_trab_2", "fax_pers_1", "fax_pers_2", "fax_trab_1", "fax_trab_2", "url_pers_1", "url_pers_2", "url_trab_1", "url_trab_2", "gtalk", "msn", "icq", "yahoo", "jabber", "aim"'

class csv:

    def __init__(self, user, channel = None, text = "", *args, **kwargs):
        """
            User needed (contact will be added to him), optional text with contacts
        """
        self.user = user
        self.data_text = text
        self.index = 0
        self.contacto = -1
        self.total = 0
        self.channel = channel

######################################## IMPORT #######################################

    def parse(self, text=""):
        if text:
            self.data_text = text
        for linea in text.splitlines()[1:]:
            self.parse_contacto(linea)
        return self.total

    def parse_contacto(self, linea):
        from addressbook.models import Contacto
        self.index = 0
        nombre, apellidos = self.get_datos(linea, 2)
        self.contacto, self.created = Contacto.objects.get_or_create(nombre = nombre, apellidos = apellidos, usuario = self.user)
        if self.channel:
            if self.contacto.tlf_movil():
                Subscriber.create(self.contacto.tlf_movil(), self.channel.id, nombre)
        self.parse_data(linea)
        self.total += 1

    def get_datos(self, datos, num = 1):
        out = []
        for i in range(num):
            aux_index = datos.find('"', self.index) + 1
            self.index = datos.find('"', aux_index) + 1
            out.append(datos[aux_index:self.index-1])
        if num == 1:
            return out[0]
        return out   
    
    def parse_data(self, linea):
        for tipo in LISTA_DIR_IMP_CSV:
            domicilio, poblacion, provincia, postal, pais = self.get_datos(linea, 5)
            if domicilio or poblacion or provincia or postal or pais:
                self.contacto.create_dir(tipo, domicilio, postal, poblacion, provincia, pais)
        for clase in LISTA_DATOS_IMP_CSV:
            dato = self.get_datos(linea)
            if dato:
                self.contacto.create_data(clase, dato) 
         

########################################## EXPORT ########################################### 

    def export(self):
        from addressbook.models import Contacto
        out = HEADER + "\n"
        for contacto in Contacto.objects.filter(usuario = self.user):
            out += '"%s", "%s", "%s", ' % (contacto.nombre, contacto.apellidos, contacto.get_tratamiento_display())
            for tipo in LISTA_DIR_EXP_CSV:
                d = contacto.direccion().filter(tipo = tipo)
                if not d:
                    out += '"", '*10
                elif d.count() == 1:
                    out += '"%s", '*5 % (d[0].domicilio, d[0].poblacion, d[0].provincia, d[0].codPostal, d[0].pais) + '"", '*5 
                else:
                    for d_p in d[:2]: 
                        out += '"%s", '*5 % (d_p.domicilio, d_p.poblacion, d_p.provincia, d_p.codPostal, d_p.pais)
            for clase in LISTA_DATOS_EXP_CSV: 
                d = contacto.get_datos().filter(clase = clase)
                if not d:
                    out += '"", '*2
                elif d.count() == 1:
                    out += '"%s", ' % d[0].dato + '"", ' 
                else:
                    for d_p in d[:2]: 
                        out += '"%s", ' % d_p.dato
            for clase in OTRAS:
                d = contacto.get_datos().filter(clase = clase)
                if d:
                    out += '"%s", ' % d[0].dato
                else:
                    out += '"", '
            out = out[:len(out)-2] + '\n'
        return out
                 
         
