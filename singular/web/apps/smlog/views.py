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

import types, syslog
from time import gmtime
from time import strftime
import calendar, datetime
import logging

from django.conf import settings
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.views.generic.list_detail import object_list

from accounting.models import admin_required
from manager.menu import *
from models import Log, LOGPRIO_LIST, DEBUG, INFO, ERROR, WARNING

_logger = logging.getLogger('galotecnia')

def __log_something(priority, objct, message, request = False):
    if request:
        if request.user:
            username = request.user.username
        else:
            username = 'Anonymous'
        if 'REMOTE_ADDR' in request.META:
            message += ' [%(username)s@%(remoteAdd)s]' % {'username': username, 'remoteAdd': request.META['REMOTE_ADDR']}
        else:
            message += ' [%(username)s@testing by django\'s client' % {'username': username, }
        if 'HTTP_USER_AGENT' in request.META:
            message += ' %s' % request.META['HTTP_USER_AGENT']
    if type(objct) is types.FunctionType:
        message = '(%(objName)s) %(message)s' % {'objName': objct.__name__, 'message': message}
    elif type(objct) is types.ClassType:
        message = '(%(type)s) %(message)s' % {'type': type(objct), 'message': message}
    else:
        message = '(%(objct)s) %(message)s' % {'objct': objct, 'message': message}

    _logger.log(priority, message)

    if priority != DEBUG:
        # We shrink the message to fit the model datatype
        l = Log(priority =  priority, text = message[:255])
        l.save()

    if settings.LOG_TO_SYSLOG and priority != DEBUG:
        syslog.syslog(syslog.LOG_LOCAL4 | priority, "[singularms] %(message)s " %{'message': message.encode('utf-8')} )

def error (request, objet, message):
    __log_something (ERROR, object, message, request)

def warning (request, object, message):
    __log_something (WARNING, object, message, request)

def info (request, object, message):
    __log_something (INFO, object, message, request)

def debug (request, object, message):
    __log_something (DEBUG, object, message, request)

def smlogMenu(request):
    m = []
    logMenu = appendMenu (m, _('All messages'), reverse('logIndex') )
    appendSubmenu (m, logMenu, _('Info'), reverse('logPriority', args=[INFO, ] ) )
    appendSubmenu (m, logMenu, _('Warning'), reverse('logPriority', args=[WARNING, ] ) )
    appendSubmenu (m, logMenu, _('Error'), reverse('logPriority', args=[ERROR, ] ) )
    setLeftMenu (request, m, _('Logs') )

@admin_required
def showLogCalendar (request, page=None, priority=None, paginate_by=60, allow_empty=True,
            date_check=None):
    """
       Calendar
    """
    info(request, 'showLog', 'Showing log messages')
    smlogMenu(request)
    
    # Creating the html ouput    
    calhtml = '<table border="0" cellpadding="0" cellspacing="0" class="month"><tr><th colspan="7" class="month">'
    # Checking and transforming the date_check as parameter
    
    #DEBUG: Don't take it very seriously.
    if date_check:
        date_check = datetime.datetime.strptime(str(date_check), '%Y%m%d')        
    else:
        date_check = datetime.date.today()
    # Generate the month and year headers
    calhtml += _(calendar.month_name[ date_check.month ]) + ' '
    calhtml += str(date_check.year)
    #calhtml += calendar.day_name[ calendar.weekday(date_check.year, date_check.month, date_check.day ) ]
    calhtml += '</th></tr>'
    # Showing days header
    calhtml += '<tr>'
    for day in calendar.day_name:
        calhtml += '<th>'
        calhtml += _(day)
        calhtml += '</th>'
    calhtml += '</tr>'
    # Filing the days and adding links
    month_array = calendar.monthcalendar(date_check.year, date_check.month)
    nweeks = len(month_array)
    
    one_day = datetime.timedelta(1)
    for n_week in xrange(0, len(month_array)):
        calhtml += '<tr>'
        for n_day in xrange(0, 7):
            calhtml += '<td>'
            if month_array[n_week][n_day] > 0:                
                # Database check and link if data is present
                #if Log.objects.filter(date = ( date_check.year, date_check.month ,date_check.day) :
                #testdate = str(date_check.year) + '-' + str(date_check.month) + '-' + str(month_array[n_week][n_day] )
                testdate = datetime.date(date_check.year, date_check.month, month_array[n_week][n_day])                
                if Log.objects.filter(date__gt = testdate, date__lt = testdate + one_day):
                    # Generate a new date for checking logs
                    calhtml += '<a href="'
                    #/log/date/'
                    #calhtml +=  reverse("logIndex")
                    calhtml += reverse('logCalendar', args=[testdate.strftime("%Y%m%d") ])
                    #calhtml += testdate.strftime("%Y%m%d")
                    calhtml += '" date_check="'
                    # <a href="/log/" date_check="2009-12-03">                    
                    calhtml += str(testdate)
                    calhtml += '">'
                    calhtml += str(month_array[n_week][n_day])
                    calhtml += '</a>'
                else:
                    #calhtml += '---'
                    calhtml += str(month_array[n_week][n_day])
                
            calhtml += '</td>'
        
        calhtml += '</tr>'            
    # End of the table
    calhtml += '</table>'
    
    # Checking the priority and preparing the object list
    testdate = datetime.date(date_check.year, date_check.month, date_check.day)
    if priority:
        qs = Log.objects.filter (priority__exact=priority,
                                #date__contains = testdate
                                ).order_by ('-date')
                                
        priorityName = dict(LOGPRIO_LIST).get(int(priority))
    else:
        qs = Log.objects.filter(
            date__gt = testdate,
            date__lt = testdate + one_day).order_by ('-date')
        priorityName = None
    
    # End of the view
    return object_list (
            request, queryset=qs,
            #paginate_by =  paginate_by,
            allow_empty=allow_empty,
            page=page,
            extra_context={ 
                    'priority':         priority,
                    'priorityName':     priorityName,
                    'profile':             request.session['profile'],
                    'calhtml':             calhtml,
                    'date_check':         date_check,                     
            })
