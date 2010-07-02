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

function toggleStatus(id, url) {
    var texto = document.getElementById('list_' + id).value;
    $.ajax({
        type: "POST",
        url: url,
        data: { 'value': texto},
        success: function () {
        },
        error: function (xhr, ajaxOptions, thrownError) {
            alert("Unknown error, please contact SingularMS admin.");
        } 
    });
}

function toggleStatus2(valor) {
    if (valor == 0) {
        $('#formulario').removeAttr('style');
        $('#mensaje').attr('style', 'display: none');
    }
    else {
        $('#mensaje').removeAttr('style');
        $('#formulario').attr('style', 'display: none');
    }
}
