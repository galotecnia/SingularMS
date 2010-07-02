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

from django import template

register = template.Library()

@register.simple_tag
def display_form(form):
    html=""
    if '__all__' in form.errors:
        html += unicode(form.errors['__all__'])

    for field in form:
        # Field errors display
        if len(field.errors):
            html += "<b>" + unicode(field.errors) + "</b>"
        html += '<p>'
        # Field label display
        if field.field.required:
            html += "<label for=\"id_%(name)s\" class=\"required\">" % \
                {
                    'name': unicode(field.name)
                }
    	else:
            html += "<label for=\"id_%(name)s\">" % \
                {
                    'name': unicode(field.name)
                }

        # Field content display
        html += "%(field)s: </label> %(value)s" % \
                { 'field': unicode(field.label), 
                  'value': unicode(field)
                }
        # Field help display
        html += unicode(field.help_text)

        html += "</p>\n"
    return html
