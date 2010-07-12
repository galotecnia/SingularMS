/*
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
*/

var estado = 0;

function cambia_movil(id) {
    var et = "#list_" + id;
    var value = $(et).val();
    var label = "#mobile_" + id;
    $(label).attr('value', value);
}

function get_email(id) {
    var et = "#email_" + id;
    return $(et).val();
}

function toggleStatus(id) {
    if (estado == 0) {
        $('#etiqueta_' + id).removeAttr('style');
        estado = 1;
    }
    else {
        $('#etiqueta_' + id).attr('style', 'display: none');
        estado = 0;
    }
}
