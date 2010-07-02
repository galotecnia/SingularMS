# Create your views here.
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

from django.http import Http404
from django.http import HttpResponse
from models import register, sensor
from models import DEFAULT_GRAPH_WIDTH, DEFAULT_GRAPH_HEIGHT
import datetime, time
import os

def send_image (path):
    """
        Send an image to the client's web browser.
    """
	filename = os.path.basename(path)
	fileExtension = filename.split (".")[-1:]
	response = HttpResponse(mimetype='image/%s' % str(fileExtension[0]))
#	response['Content-Disposition'] = 'attachment; filename=%s' % filename
	response.write (open(path, "r").read())
	return response
	
def graphLast (request, period, sensorid, width = DEFAULT_GRAPH_WIDTH, height = DEFAULT_GRAPH_HEIGHT, force = False, adjust = True):
	if width is None:
		width = DEFAULT_GRAPH_WIDTH
	if height is None:
		height = DEFAULT_GRAPH_HEIGHT
	if force == "force/":
		force = True
	if adjust == "float/":
		adjust = False
	else:
		adjust = True
	width = int (width)
	height = int (height)
	s = sensor.objects.get (pk = sensorid)
	if period == "hour":
		path = s.graphRRDLastHour(width = width, height = height)
	elif period == "day":
		path = s.graphRRDLastDay(force = force, width = width, height = height, adjust = adjust)
	elif period == "week":
		path = s.graphRRDLastWeek(force = force, width = width, height = height, adjust = adjust)
	elif period == "month":
		path = s.graphRRDLastMonth(force = force, width = width, height = height, adjust = adjust)
	elif period == "year":
		path = s.graphRRDLastYear (force = force, width = width, height = height, adjust = adjust)
	else:
		raise Http404

	if path is None:
		raise Http404

	return send_image (path)

def graphTime (request, period, sensorid, year, month, day, hour, width = DEFAULT_GRAPH_WIDTH, height = DEFAULT_GRAPH_HEIGHT, force = False, adjust = True):
	if width is None:
		width = DEFAULT_GRAPH_WIDTH
	if height is None:
		height = DEFAULT_GRAPH_HEIGHT
	if force == "force/":
		force = True
	if adjust == "float/":
		adjust = False
	else:
		adjust = True
	width = int (width)
	height = int (height)
	s = sensor.objects.get (pk = sensorid)
	start = datetime.datetime (int(year), int(month), int(day), int(hour))

	if period == "hour":
		end  = start + datetime.timedelta (hours = 1)
	elif period == "day":
		end  = start + datetime.timedelta (days = 1)
	elif period == "week":
		end  = start + datetime.timedelta (weeks = 1)
	elif period == "month":
		end  = start + datetime.timedelta (days = 30)
	elif period == "year":
		end  = start + datetime.timedelta (days = 365)
	else:
		raise Http404

	path = s.graphRRD (str('%s_%s:%s:%s_%s' % (period, year, month, day, hour)), force, width, height, time.mktime(start.timetuple()), time.mktime(end.timetuple()))

	if path is None:
		raise Http404

	return send_image (path)
