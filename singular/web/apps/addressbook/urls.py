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

from django.conf.urls.defaults import *

# place app url patterns here
urlpatterns = patterns('addressbook.views',
    # Contacts
    url(r'^contactos/$',                    'lista_contactos', name='contacto_listar'),
    url(r'^contactos/crear/$',              'gestion_contactos', name='contacto_crear'),
    url(r'^contactos/(?P<id>\d+)/$',        'gestion_contactos', name='contacto_editar'),
    url(r'^contactos/del/(?P<id>\d+)/$',    'eliminar_contactos', name='contacto_eliminar'),
    url(r'^contactos/buscar/$',             'buscar_contactos', name='contacto_buscar'),
    url(r'^contactos/datos/(?P<id>\d+)/$',  'gestion_datos_contacto', name='contacto_datos'),
    url(r'^contactos/direccion/(?P<id>\d+)/$',  'gestion_direcciones', name='contacto_direcciones'),
    # Import/Export
    url(r'^import/$',                       'importar', name='importar_agenda'),
    url(r'^export/$',                       'exportar', name='exportar_agenda'),
)
