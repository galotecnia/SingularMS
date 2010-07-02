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

from django.utils.translation import ugettext_lazy as _

TRATAMIENTO = (
    (0, 'Sr.'),
    (1, 'Sra.'),
    (2, 'Dr.'),
    (3, 'Dra.'),
    (4, 'Srta.'),
)
TRATAMIENTO_INV = dict([(clave,valor) for valor, clave in dict(TRATAMIENTO).items()])

# CONTACT DATA OPTIONS
T_PERSONAL = 100
T_TRABAJO = 101
EM_PERSONAL = 102
EM_TRABAJO = 103
F_PERSONAL = 104
F_TRABAJO = 105
M_PERSONAL = 106
M_TRABAJO = 107
W_PERSONAL = 108
W_TRABAJO = 109
GTALK = 110
MSN = 111
ICQ = 112
YAHOO = 113
JABBER = 114
AIM = 115

OPCIONES_CONTACTO = (
    (T_PERSONAL , _(u'Home phone')),
    (T_TRABAJO, _(u'Job phone')),
    (M_PERSONAL, _(u'Private mobile')),
    (M_TRABAJO, _(u'Job mobile')),
    (EM_PERSONAL, _(u'Private email')),
    (EM_TRABAJO, _(u'Job email')),
    (F_PERSONAL, _(u'Private FAX')),
    (F_TRABAJO, _(u'Job FAX')),
    (W_PERSONAL, _(u'Private web')),
    (W_TRABAJO, _(u'Job web')),
    (GTALK, _(u'GTalk')),
    (MSN, _(u'Msn')),
    (ICQ, _(u'ICQ')),
    (YAHOO, _(u'Yahoo MSN')),
    (JABBER, _(u'Jabber')),
    (AIM, _(u'AIM')),
)

# CONTACT DATA SUBOPTIONS
OPCIONES_TELEFONO = OPCIONES_CONTACTO[:4]
OPCIONES_EMAIL = OPCIONES_CONTACTO[4:6]
OPCIONES_FAX = OPCIONES_CONTACTO[6:8]
OTRAS_OPCIONES = OPCIONES_CONTACTO[8:]

TELEFONOS = [T_PERSONAL, T_PERSONAL, T_TRABAJO, T_TRABAJO, M_PERSONAL, M_PERSONAL, M_TRABAJO, M_TRABAJO]
EMAILS = [EM_PERSONAL, EM_PERSONAL, EM_TRABAJO, EM_TRABAJO]
FAXES = [F_PERSONAL, F_PERSONAL, F_TRABAJO, F_TRABAJO]
WEBS = [W_PERSONAL, W_PERSONAL, W_TRABAJO, W_TRABAJO]
OTRAS = [GTALK, MSN, ICQ, YAHOO, JABBER, AIM]

LISTA_DATOS_IMP_CSV = TELEFONOS + EMAILS + FAXES + WEBS + OTRAS 
LISTA_DATOS_EXP_CSV = [T_PERSONAL, T_TRABAJO, M_PERSONAL, M_TRABAJO, EM_PERSONAL, EM_TRABAJO, F_PERSONAL, F_TRABAJO, W_PERSONAL, W_TRABAJO]

OPCIONES_DICT = { 
    # PHONE OPTIONS
    T_PERSONAL : OPCIONES_TELEFONO, T_TRABAJO : OPCIONES_TELEFONO, M_PERSONAL : OPCIONES_TELEFONO, M_TRABAJO : OPCIONES_TELEFONO,
    # EMAIL OPTIONS
    EM_PERSONAL : OPCIONES_EMAIL, EM_TRABAJO : OPCIONES_EMAIL,
    # FAX OPTIONS
    F_PERSONAL : OPCIONES_FAX, F_TRABAJO : OPCIONES_FAX,
    # OTHER OPTIONS
    W_PERSONAL : OTRAS_OPCIONES, W_TRABAJO : OTRAS_OPCIONES, 110 : OTRAS_OPCIONES, 111 : OTRAS_OPCIONES, 112 : OTRAS_OPCIONES, 113 : OTRAS_OPCIONES, 114 : OTRAS_OPCIONES 
}

# ADDRESS OPTIONS
D_PERSONAL = 200
D_PROFESIONAL = 201
D_SERVICIOS = 202

LISTA_DIR_IMP_CSV = [D_PERSONAL, D_PERSONAL, D_PROFESIONAL, D_PROFESIONAL, D_SERVICIOS, D_SERVICIOS]
LISTA_DIR_EXP_CSV = [D_PERSONAL, D_PROFESIONAL, D_SERVICIOS]

OPCIONES_DIRECCION=(
    (D_PERSONAL, _(u'Home address')),
    (D_PROFESIONAL, _(u'Job address')),
    (D_SERVICIOS, _(u'Service address')),
)


# INPORT AND EXPORT OPTIONS
VCARD21 = 50
VCARD3  = 51
CSV     = 52

OPCIONES_IMPORTACION = (
    (VCARD21, _(u'vCARD2.1')),
    (VCARD3, _(u'vCARD3')),
    (CSV, _(u'CSV')),
)

OPCIONES_IMPORTACION_CHANNEL = (
    (CSV, _(u'CSV')),
)

TIPOS_RESPUESTA = {
    VCARD21: 'text/x-vcard',
    VCARD3 : 'text/x-vcard',
    CSV    : 'text/csv',
}
