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
from django.utils.translation import ugettext as _

register = template.Library()

@register.simple_tag
def jquery_calendar (id):
    script='$("#'
    script+=str(id)
    script+='''").datepicker({ 
                            dayNames        : [\''''
    script+=_('Sunday') 
    script+='\',\''
    script+=_('Monday')
    script+='\',\''
    script+=_('Tuesday')
    script+='\',\''
    script+=_('Wednesday')
    script+='\',\''
    script+=_('Thursday')
    script+='\',\''
    script+=_('Friday')
    script+='\',\''
    script+=_('Saturday')    
    script+='''\'],
                               dayNamesMin     : [\''''
    script+=_('Su')
    script+='\',\''
    script+=_('Mo')
    script+='\',\''
    script+=_('Tu')
    script+='\',\''
    script+=_('We')
    script+='\',\''
    script+=_('Th')
    script+='\',\''
    script+=_('Fr')
    script+='\',\''
    script+=_('Sa')  
    script+='''\'],
                               firstDay        : 1,
                               monthNames      : [\''''
    script+=_('January')
    script+='\',\''
    script+=_('February')
    script+='\',\''
    script+=_('March')
    script+='\',\''
    script+=_('April')
    script+='\',\''
    script+=_('May')
    script+='\',\''
    script+=_('June')
    script+='\',\''
    script+=_('July')
    script+='\',\''
    script+=_('August')
    script+='\',\''
    script+=_('September')
    script+='\',\''
    script+=_('October')
    script+='\',\''
    script+=_('November')
    script+='\',\''
    script+=_('December')
    script+='''\'                                      ],      
                                 monthNamesShort : [\''''
    script+=_('Jan') 
    script+='\',\''
    script+=_('Feb') 
    script+='\',\''
    script+=_('Mar') 
    script+='\',\''
    script+=_('Apr') 
    script+='\',\''
    script+=_('May')
    script+='\',\''
    script+=_('Jun') 
    script+='\',\''
    script+=_('Jul') 
    script+='\',\''
    script+=_('Aug') 
    script+='\',\''
    script+=_('Sep') 
    script+='\',\''
    script+=_('Oct') 
    script+='\',\''
    script+=_('Nov') 
    script+='\',\''
    script+=_('Dec')
    script+='''\'                                              ]       

                             });'''
    return script
