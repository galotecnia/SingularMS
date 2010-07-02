#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, time, datetime
import rrdtool

os.environ['DJANGO_SETTINGS_MODULE'] = "celajes.settings"
from celajes.sensors.models import *

def __createRRD__ (sensor):
	RRD = os.path.join ('.', '%s.rrd' % sensor.id)
	description = [str(i).strip() for i in sensor.type.rrd_description.split ('\n')]
	r = register.objects.filter (sensor = sensor.pk).order_by ('time')[0]
	description.append ("-b %s" % (int (r.time.strftime ("%s")) - 20))
	rrdtool.create (RRD, *description)

def __updateRRD__ (sensor, t, value):
	RRD = os.path.join ('.', '%s.rrd' % sensor.id)
	if not os.path.isfile (RRD):
		__createRRD__ (sensor)
	try:
		rrdtool.update (RRD, '%s:%s' % (t.strftime("%s"), value))
	except Exception, e:
		print e

if __name__ == '__main__':

	try:
		s = sys.argv[1]
	except IndexError:
		print "tienes que pasar el id de un sensor...."
		sys.exit (1)

	try:
		s = sensor.objects.get (pk = s)
	except sensor.DoesNotExist:
		print "El sensor este no existe"
		sys.exit (1)

	print "Sensor: %s" % s
	for r in register.objects.filter (sensor = s.pk):
		__updateRRD__ (s, r.time, r.value)
	print "Listo"

