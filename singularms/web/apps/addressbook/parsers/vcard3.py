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
from vcard21 import *
import logging

log = logging.getLogger('galotecnia')

class vcard3(vcard21):

    def export(self):
        from addressbook.models import Contacto
        out = ""
        for contacto in Contacto.objects.filter(usuario = self.user):
            out += u"BEGIN: VCARD\r\n"
            out += u"N:%s;%s;;%s\r\n".encode('utf-8') % (contacto.nombre, 
                contacto.apellidos, contacto.get_tratamiento_display())
            for direccion in contacto.direccion():
                out += u"ADR;TYPE=%s:%s;;%s;%s;%s;;%s\r\n".encode('utf-8') % (DIRECCIONES[direccion.tipo], 
                    direccion.codPostal, direccion.domicilio, direccion.poblacion, direccion.provincia, direccion.pais)
            for dato in contacto.get_datos():
                if dato.clase in TELEFONOS:       
                    out += u"TEL;TYPE=%s:%s\r\n" % (TELEFONOS[dato.clase], dato.dato)
                elif dato.clase in [EM_PERSONAL, EM_TRABAJO]:
                    out += u"EMAIL:%s\r\n" % dato.dato
                elif dato.clase in [F_PERSONAL, F_TRABAJO]:
                    out += u"FAX:%s\r\n" % dato.dato
                elif dato.clase in [W_PERSONAL, W_TRABAJO]:
                    out += u"URL:%s\r\n" % dato.dato
                else:
                    out += u"%s:%s\r\n" % (DATOS_EXTRA[dato.clase], dato.dato)
            out += u"END: VCARD\r\n\r\n"
        return out
                 
         
