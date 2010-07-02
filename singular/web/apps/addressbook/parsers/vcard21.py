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
import logging

log = logging.getLogger('galotecnia')

TIPOS_TEL = {
    'HOME': T_PERSONAL, 'home': T_PERSONAL,
    'WORK': T_TRABAJO, 'work': T_TRABAJO,
    'CELL': M_PERSONAL, 'cell': M_PERSONAL,
}

TELEFONOS = {
    T_PERSONAL: 'HOME',
    T_TRABAJO: 'WORK',
    M_PERSONAL: 'CELL',
    M_TRABAJO: 'CELL',
}

TIPOS_EMAIL = {
    'INTERNET': EM_PERSONAL, 'internet': EM_PERSONAL,
    'X400': EM_PERSONAL, 'x400': EM_PERSONAL,
}

TIPOS_DIR = {
    'HOME': D_PERSONAL, 'home': D_PERSONAL,
    'WORK': D_PROFESIONAL, 'work': D_PROFESIONAL,
    'DOM': D_SERVICIOS, 'dom': D_SERVICIOS,
    'POSTAL': D_SERVICIOS, 'postal': D_SERVICIOS,           
}

DIRECCIONES = {
    D_PERSONAL: 'HOME',
    D_PROFESIONAL: 'WORK',
    D_SERVICIOS: 'POSTAL',
}

DATOS_EXTRA = {
    GTALK : 'X-messaging/gtalk-All',
    MSN   : 'X-messaging/msn-All',
    ICQ   : 'X-messaging/icq-All',
    YAHOO : 'X-messaging/yahoo-All',
    JABBER: 'X-messaging/xmpp-All',
    AIM   : 'X-messaging/aim-All',
}

class vcard21:

    def __init__(self, user, text = "", *args, **kwargs):
        """
            User needed (contacts will be added to him), and optional text with contacts
        """
        self.user = user
        self.data_text = text
        self.index = 0
        self.contacto = -1
        self.total = 0

######################################## IMPORT #######################################

    def parse(self, text=""):
        """
            Import process. Text variable with all contact data
        """
        if text:
            self.data_text = text
        func, args = self.parse_keyword()
        while func:
            func(args)
            func, args = self.parse_keyword()
        return self.total

    def parse_keyword(self):
        """
            Get what kind of data is been processed and his arguments.
            Return related function to this kind of data
        """
        aux_index = self.data_text.find(':', self.index)
        if aux_index == -1:
            # Search finished
            return None, None 
        key = self.data_text[self.index:aux_index].strip()
        self.index = aux_index + 1
        args = []
        if key.find(';') != -1:
            args = key.split(';')
            key = args.pop(0)
        # If for extra data, like msn, icq, yahoo messenger, etc
        # that are not noted in RFC2426
        if key.lower().startswith('x-messaging/'): 
            key = key[key.find('/')+1:key.find('-', key.find('/'))]
        log.debug('vcard21 -> key: %s, args = %s', key, args)
        try:
            func = getattr(self, 'parse_' + key)
        except AttributeError:
            # Tipo de dato desconocido
            func = self.unknown_function
        return func, args

    def parse_initial(self):
        """
            Get value of a kind of data
        """
        tmp_index = self.index
        aux_index = self.data_text.find('\n', self.index)
        self.index = aux_index + 1
        while self.data_text[self.index] == " ":
            aux_index = self.data_text.find('\n', self.index)
            self.index = aux_index + 1
        dato = ''.join(self.data_text[tmp_index:aux_index].splitlines()).strip()
        return dato

    def unknown_function(self, args):
        """
            Parse all unknown kind of data
        """
        dummy = self.parse_initial()

    def apply_char_set(self, dato, encode):
        """
            Support UTF-8 encoding/decoding
        """
        for k,v in dato.items():
            i = v.find('=')
            while i > 0:
                v = v.replace(v[i:i+3], v[i+1:i+3].decode('hex'))   
                i = v.find('=', i)
            dato[k] = v.decode(encode)
        return dato

    def parse_BEGIN(self, args):
        """
            Parse the beggining of a block
        """
        from addressbook.models import Contacto
        card = self.parse_initial()
        self.contacto, self.created = Contacto.objects.get_or_create(nombre = 'TMP_CONTACT', usuario = self.user)

    def parse_END(self, args):
        """
            Parse the ending of a block, and add a new contact
        """
        aux_index = self.data_text.find('\n', self.index)
        card = self.data_text[self.index:aux_index].rstrip()
        self.index = aux_index + 1
        log.debug("vcard21 -> SAVING THIS CONTACT: %s", self.contacto)
        self.contacto = None
        self.total += 1

    def crea_dato(self, datos, args, types, default_type, save_func):
        """
            Function responsible for generating the instance associated with the data received. The
            arguments are:
             * Data: dictionary to store information
             * Args: argument list returned by the parse_keyword
             * Types: dictionary of the different possible types
             * Default_type: default data type (if it does not specify types)
             * Save_func: function with which will be recorded
        """
        tipo = default_type
        encode = None
        for arg in args:
            key, value = arg.split("=")
            if key.lower() == "type":
                for k in types:
                    if k in value.split(','):
                        tipo = types[k]
            elif key.lower() == "charset":
                encode = value
        if encode:
            datos = self.apply_char_set(datos, encode)
        save_func(tipo, **datos)
        log.debug('vcard21 -> NEW CONTACT INFO:  %s', datos)

    def parse_TEL(self, args):
        dato = self.parse_initial()
        self.crea_dato({'dato':dato}, args, TIPOS_TEL, T_PERSONAL, self.contacto.create_data)

    def parse_EMAIL(self, args):
        dato = self.parse_initial()
        self.crea_dato({'dato': dato}, args, TIPOS_EMAIL, EM_PERSONAL, self.contacto.create_data)

    def parse_icq(self, args):
        dato = self.parse_initial()
        self.crea_dato({'dato': dato}, args, {}, ICQ, self.contacto.create_data)

    def parse_msn(self, args):
        dato = self.parse_initial()
        self.crea_dato({'dato': dato}, args, {}, MSN, self.contacto.create_data)
    
    def parse_yahoo(self, args):
        dato = self.parse_initial()
        self.crea_dato({'dato': dato}, args, {}, YAHOO, self.contacto.create_data)
    
    def parse_xmpp(self, args):
        dato = self.parse_initial()
        self.crea_dato({'dato': dato}, args, {}, YAHOO, self.contacto.create_data)
        
    def parse_jabber(self, args):
        self.parse_xmpp(args)

    def parse_gtalk(self, args):
        dato = self.parse_initial()
        self.crea_dato({'dato': dato}, args, {}, GTALK, self.contacto.create_data)

    def parse_aim(self, args):
        dato = self.parse_initial()
        self.crea_dato({'dato': dato}, args, {}, AIM, self.contacto.create_data)
    
    def parse_URL(self, args):
        dato = self.parse_initial()
        self.crea_dato({'dato':dato}, args, {}, W_PERSONAL, self.contacto.create_data)

    def parse_ADR(self, args):
        dato = self.parse_initial()
        codigo_postal, dummy, direccion, poblacion, provincia, zip_code, pais = dato.split(';')
        datos = {'domicilio':direccion, 'codPostal':codigo_postal or zip_code, 'poblacion':poblacion, 'provincia':provincia, 'pais':pais}
        self.crea_dato(datos, args, TIPOS_DIR, D_PERSONAL, self.contacto.create_dir)

    def parse_N(self, args):
        from addressbook.models import Contacto
        split_name = self.parse_initial().split(';')
        encode = None
        for arg in args:
            key, value = arg.split("=")
            if key.lower() == "charset":
                encode = value
        nombre = "%s %s" % (split_name[1], split_name[2]) if len(split_name) == 3 else "%s" % split_name[1]
        datos = {'nombre': nombre, 'apellidos': split_name[0] }
        if encode:
            datos = self.apply_char_set(datos, encode)
        datos['tratamiento'] = TRATAMIENTO_INV[split_name[3]] if split_name[3] in TRATAMIENTO_INV else None
        self.contacto.update(**datos)
      

########################################## EXPORT ########################################### 

    def export(self):
        """
            Export to vcard2.1 process
        """
        from addressbook.models import Contacto
        out = ""
        for contacto in Contacto.objects.filter(usuario = self.user):
            out += u"BEGIN: VCARD\r\n"
            out += u"N;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:%s;%s;;%s\r\n".encode('utf-8') % (contacto.nombre, 
                contacto.apellidos, contacto.get_tratamiento_display())
            for direccion in contacto.direccion():
                out += u"ADR;TYPE=%s;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:%s;;%s;%s;%s;;%s\r\n".encode('utf-8') % (DIRECCIONES[direccion.tipo], 
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
                 
         
