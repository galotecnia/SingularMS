#!/usr/local/bin/python
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

from django.db import models, IntegrityError
from django.db.models import Q
from config import *
import logging
import datetime
import time
import rrdtool
import os

_logger = logging.getLogger('galotecnia')

# funciones de conveniencia
debug = _logger.debug
info = _logger.info
warn = _logger.warning
error = _logger.error
crit = _logger.critical

DEFAULT_GRAPH_WIDTH = 550
DEFAULT_GRAPH_HEIGHT = 200

class contactPerson (models.Model):
	name = models.CharField(
        max_length = 50,
        verbose_name="Contact person's name",
        blank = False, null = False, default = None
        )
	description = models.TextField (blank = True)
	email = models.EmailField (null = True, blank = True)
	cellPhone = models.CharField (max_length = 20, null = True, blank = True)

	def __unicode__(self):
		return self.name

class alarmLog (models.Model):
	time = models.DateTimeField (auto_now_add = True)
	description = models.TextField (verbose_name="Alarm description")
	
	
	def __unicode__(self):
		return "[%s] %s" % (self.time, self.description)


class sensorType (models.Model):
	model = models.CharField(
        max_length = 50,
        verbose_name="Vendor model",
        null = False, blank = False, unique = True
        )
	description = models.TextField (
        verbose_name="Sensor type description",
        null = True, blank = True)
	rrd_description = models.TextField (
        verbose_name="RRD description",
        null = False, blank = False,
        help_text="We'll use this information to create the RRD file for this kind of sensor. You need to call \"sensor\" your data source. The default value takes one measure each 60 seconds and stores values for a day, a week, a month and a year",
        default='''-s 60
DS:sensor:GAUGE:120:U:U
RRA:AVERAGE:0.5:1:1440
RRA:AVERAGE:0.5:10:1008
RRA:AVERAGE:0.5:30:1440
RRA:AVERAGE:0.5:360:1460''')
	color = models.CharField(
        max_length=10,
        verbose_name="Graph color",
        null = False, blank = False, default = "0612ff")
	unit = models.CharField(max_length = 50, verbose_name="Unit measured")
	minAcceptedValue = models.FloatField (verbose_name="Minium possible value", null = True, blank = True)
	maxAcceptedValue = models.FloatField (verbose_name="Maximum value", null = True, blank = True)

	def __unicode__(self):
		if self.minAcceptedValue:
			min = str(self.minAcceptedValue)
		else:
			min = "Undefined"
		if self.maxAcceptedValue:
			max = str(self.maxAcceptedValue)
		else:
			max = "Undefined"
		return "%s [%s, %s]" % (self.model, min, max)


class sensor (models.Model):
	name = models.CharField(
        max_length = 50,
        verbose_name="Sensor's name",
        null = False, blank = False, unique = True, default = None
        )
	description = models.TextField (verbose_name="Sensor description")
	type = models.ForeignKey(sensorType, verbose_name="The type of this sensor")
	storeAllData = models.BooleanField (default = True, null = False, blank = False)
	NORMAL = 0
	ALARM = 1
	ERROR = 2	
	status = models.IntegerField (
			choices=(
					(NORMAL, 'Normal'),
					(ALARM, 'Alarm'),
					(ERROR, 'Malfunction')
			),
			default = 0,
			null = False,
			blank = False
		)
	statusUpdateTime = models.DateTimeField ()

	HOUR = 3600
	DAY = HOUR * 24
	WEEK = DAY * 7
	MONTH = WEEK * 4
	YEAR = MONTH * 12

	def __createRRD__ (self):
		RRD = os.path.join (RRD_PATH, '%s.rrd' % self.id)
		rrdtool.create (RRD, *[str(i) for i in self.type.rrd_description.split ('\n')])
#				'-s 1',
#				'DS:t1:GAUGE:60:U:U',
##				'RRA:AVERAGE:0.5:1:10080',
#				'RRA:AVERAGE:0.5:20:10080',
##				'RRA:HWPREDICT:5440:0.01:0.015:288',
##				'RRA:DEVPREDICT:100:0.5:0.5:20',
#			)

	def __updateRRD__ (self, time, value):
		RRD = os.path.join (RRD_PATH, '%s.rrd' % self.id)
		if not os.path.isfile (RRD):
			self.__createRRD__ ()
		try:
			rrdtool.update (RRD, '%s:%f' % (time.strftime("%s"), value))
#			error("Actualizando: %s con '%s:%f'" % (self.id, time.strftime("%s"), value))
		except Exception, e:
			warn (e.message)

	def graphRRDLastHour (self, force = False, width = DEFAULT_GRAPH_WIDTH, height = DEFAULT_GRAPH_HEIGHT, adjust = True):
		return self.graphRRDTillNow ('LastHour', force, width, height, sensor.HOUR, adjust)

	def graphRRDLastDay (self, force = False, width = DEFAULT_GRAPH_WIDTH, height = DEFAULT_GRAPH_HEIGHT, adjust = True):
		return self.graphRRDTillNow ('LastDay', force, width, height, sensor.DAY, adjust)

	def graphRRDLastWeek (self, force = False, width = DEFAULT_GRAPH_WIDTH, height = DEFAULT_GRAPH_HEIGHT, adjust = True):
		return self.graphRRDTillNow ('LastWeek', force, width, height, sensor.WEEK, adjust)

	def graphRRDLastMonth (self, force = False, width = DEFAULT_GRAPH_WIDTH, height = DEFAULT_GRAPH_HEIGHT, adjust = True):
		return self.graphRRDTillNow ('LastMonth', force, width, height, sensor.MONTH, adjust)

	def graphRRDLastYear (self, force = False, width = DEFAULT_GRAPH_WIDTH, height = DEFAULT_GRAPH_HEIGHT, adjust = True):
		return self.graphRRDTillNow ('LastYear', force, width, height, sensor.YEAR, adjust)

	def graphRRDTillNow (self, name = '', force = False, width = DEFAULT_GRAPH_WIDTH, height = DEFAULT_GRAPH_HEIGHT, secondsBack = None, adjust = True):
		if secondsBack is None:
			raise ValueError
		now = time.time ()
		if adjust: now += secondsBack - (now % secondsBack)
		return self.graphRRD ( name = name, force = force, width = width, height = height, start = now - secondsBack, end = now)

	def graphRRD (self, name = '', force = False, width = DEFAULT_GRAPH_WIDTH, height = DEFAULT_GRAPH_HEIGHT, start = None, end = None):
		if start is None:
			start = '-%s' % sensor.DAY
		else:
			start = str(int (start))
		if end is None:
			end = '-1'
		else:
			end = str(int (end))
		RRD = os.path.join (RRD_PATH,'%s.rrd' % self.id)
		if os.path.isfile (RRD):
			RRD_GRAPH = os.path.join (RRD_PATH, '%s_%s_%sx%s.png' % (self.id, name, width, height))
			if not force:
				try:
					if os.path.getctime (RRD_GRAPH) >= time.time() - GRAPH_TTL:
						info ("Return cached graph")
						return RRD_GRAPH
				except OSError:
					pass
			info ("Creating graph png")
			try:
				rrdtool.graph(
						RRD_GRAPH,
						'--imgformat', 'PNG',
						'--width', str(width),
						'--height', str(height),
						'--start', start,
						'--end', end,
						'--vertical-label', self.type.unit.encode ('utf-8'),
						'--title',  self.name.encode ('utf-8'),
#						'--lower-limit', '20',
						'DEF:data=%s:sensor:AVERAGE' % RRD,
#						'DEF:tempSoft=%s:t1:AVERAGE:step=20' % RRD,
#						'DEF:pred=%s:t1:HWPREDICT' % RRD,
#						'DEF:dev=%s:t1:DEVPREDICT' % RRD,
#						'DEF:fail=%s:t1:FAILURES' % RRD,
#						'TICK:fail#ffffa0:1.0:Failures Average bits out',
#						'CDEF:upper=pred,dev,2,*,+',
#						'CDEF:scaledupper=upper,8,*',
#						'CDEF:lower=pred,dev,2,*,-',
#						'CDEF:scaledlower=lower,8,*',
#						'CDEF:scaledtemp=temp,8,*',
#						'CDEF:scaledtempSoft=tempSoft,8,*',
#						'DEF:temp2=%s:t1:HWPREDICT' % RRD,
						'AREA:data#%s' % str (self.type.color),
#						'LINE2:data#990033',
#						'LINE2:scaledtemp#990033:Temperatura',
#						'LINE2:scaledtempSoft#4400FF:Temperatura',
#						'LINE1:upper#ff0000:upper',
#						'LINE1:scaledupper#00ff00:upper',
#						'LINE1:lower#ff0000:lower',
#						'LINE1:scaledlower#00ff00:lower',
#						'LINE1:temp2#71ff64:Temperatura por dos'
					)
#			except BaseException, e:
			except Exception, e:
				print e
				error (e)
			return RRD_GRAPH
		else:
			return None

	def error (self, text):
		if self.status == sensor.ERROR:
			if self.statusUpdateTime > datetime.datetime.now () - datetime.timedelta(0, ALARM_REPEAT_INTERVAL):
				return
		error (text)

	def __unicode__(self):
		return "%s: %s (%s)" % (self.id, self.name, self.type.model)


class alarm (models.Model):
	sensor = models.ForeignKey (sensor)
	minValue = models.FloatField (verbose_name="Minium possible value")
	maxValue = models.FloatField (verbose_name="Maximum possible value")
	contactPersons = models.ManyToManyField (contactPerson)
	alertByEmail = models.BooleanField ()
	alertByCellPhone = models.BooleanField ()

	def launch (self, value, time):
		if self.sensor.status == sensor.ALARM:
			if self.sensor.statusUpdateTime > datetime.datetime.now () - datetime.timedelta(0, ALARM_REPEAT_INTERVAL):
				return
		self.sensor.status = sensor.ALARM
		self.sensor.statusUpdateTime = datetime.datetime.now()
		self.sensor.save ()
		if value > self.maxValue:
			text = "Value: %s, for time: %s greater than %s, alarm maximum value for sensor: %s" % (value, time, self.maxValue, self.sensor)
		elif value < self.minValue:
			text =  "Value: %s, for time: %s lower than %s, alarm minimum value for sensor: %s" % (value, time, self.minValue, self.sensor)
		warn (text)
		alarmLog.objects.create (description = text)

	def ok (self, value):
		if ((value >= self.minValue) and (value <= self.maxValue) and (self.sensor.status != sensor.NORMAL)):
			self.sensor.status = sensor.NORMAL
			alarmLog.objects.create (description = "Value: %s is in the correct interval for sensor: %s" % (value, self.sensor))
			self.sensor.save ()

	def __unicode__(self):
		return "%s min: %s, max: %s" % (self.sensor.id, self.minValue, self.maxValue)


class register (models.Model):
	sensor = models.ForeignKey (sensor, null = False, blank = False)
	time = models.DateTimeField (null = False, blank = False)
	value = models.FloatField (null = False, blank = False)


	@staticmethod
	def addData (selSensor, value = None, t0 = None):
		if value is None: raise ValueError
		f = float (value)
		try:
			try:
				selSensorID = int (selSensor)
				selSensor = sensor.objects.get (pk = selSensorID)
			except ValueError:
				selSensor = sensor.objects.get (name = selSensor)
		except sensor.DoesNotExist:
			selSensor = sensor.objects.get (name = selSensor)
		try:
			t0 = datetime.datetime.fromtimestamp (t0)
		except TypeError:
			t0 = datetime.datetime.now()
		if t0 > datetime.datetime.now ():
			warn ("Data in the future")
		if selSensor.storeAllData:
			register.objects.create (sensor = selSensor, value = f, time = t0)
		selSensor.__updateRRD__(t0, f)
		for a in alarm.objects.filter (Q(sensor = selSensor) & ( Q(minValue__gt = value) | Q(maxValue__lt = value))):
			a.launch (value, t0)
		for a in alarm.objects.filter (
				Q(sensor = selSensor) &
				Q(minValue__lte = value) &
				Q(maxValue__gte = value)):
			if a.sensor.status != sensor.NORMAL:
				a.ok(value)
		if (value < selSensor.type.minAcceptedValue):
			selSensor.error ('Sensor malfunction, value %s lower than minimum possible: %s' % (value, selSensor.type))
		elif (value > selSensor.type.maxAcceptedValue):
			selSensor.error ('Sensor malfunction, value %s higher than maximum possible: %s' % (value, selSensor.type))

	def __unicode__(self):
		return "%s %s = %f" % (self.time, self.sensor.name, self.value)

	class Meta:
		get_latest_by = 'time'
		unique_together = (('time', 'sensor'),)


class sensorGroup (models.Model):
	name = models.CharField(max_length = 50, verbose_name="Sensor's group name", null = False, blank = False, unique = True, default = None)
	sensors = models.ManyToManyField (sensor)

	def __unicode__(self):
		return self.name

