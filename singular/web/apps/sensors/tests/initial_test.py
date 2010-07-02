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

import unittest, logging, datetime, time, rrdtool, os
from sensors.models import sensorType
from sensors.models import sensor
from sensors.models import alarm
from sensors.models import alarmLog
from sensors.models import register
from django.db import IntegrityError
from django.test import TestCase

class sensorTest (TestCase):
    name = 'testSensoráéíóñäü'
    descriptionText = 'üñí¢ôðé "D€scription"'
    setup_done = False

    def setUp(self):
        self.sensorType = sensorType.objects.create(
                model = sensorTest.name,
                description = sensorTest.descriptionText,
                unit = "Centigrade degrees",
                minAcceptedValue = 19.99,
                maxAcceptedValue =  31.0,
                rrd_description = '''-b 1212997413
-s 1
DS:sensor:GAUGE:60:U:U
RRA:AVERAGE:0.5:20:10080''',
            )

        self.sensorType2 = sensorType.objects.create(
                model = sensorTest.name + "2",
                description = sensorTest.descriptionText,
                rrd_description = '''-b 1212997413
-s 1
DS:sensor:GAUGE:60:U:U
RRA:AVERAGE:0.5:100:10080''',
            )

        self.sensorOne = sensor.objects.create (
                name = sensorTest.name,
                description = sensorTest.descriptionText,
                type = self.sensorType,
                statusUpdateTime = datetime.datetime.now()
            )

        self.sensorTwo = sensor.objects.create (
                name = "no database storage",
                description = sensorTest.descriptionText,
                type = self.sensorType,
                storeAllData = False,
                statusUpdateTime = datetime.datetime.now ()
            )

        self.alarmOne = alarm.objects.create (
                sensor = self.sensorOne,
                minValue = 20,
                maxValue = 29.5,
            )

    def tearDown (self):
        for f in ('/tmp/1.rrd', '/tmp/2.rrd'):
            if os.path.isfile (f):
                try:
                    os.unlink (f)
                except OSError, e:
                    print e

    def testSensorType (self):
        self.assertEquals(self.sensorType.model, sensorTest.name)
        self.assertEquals(self.sensorType.description, sensorTest.descriptionText)
#       self.assertEquals (self.sensorType.__unicode__(), '%s [-9999999.999990, 9999999.999990]' % sensorTest.name)

        self.assertEquals(self.sensorOne.name, sensorTest.name)
        self.assertEquals(self.sensorOne.description, sensorTest.descriptionText)

    def test_incomplete_sensor (self):
        self.assertRaises(IntegrityError, sensor.objects.create, name = "peta", description = "hola")
        self.assertRaises(IntegrityError, sensor.objects.create, description = "hola", type = self.sensorType)
        self.assertRaises(IntegrityError, sensor.objects.create, name = "peta", description = "hola")
        self.assertRaises(IntegrityError, sensor.objects.create, description = "hola", type = self.sensorType)

    def test_register_without_sensor_ko (self):
#       Insertar un registro sin sensor (KO)
        self.assertRaises(TypeError, register.addData, value = 2.3, t0 = 1234)

    def test_register_with_sensor_ok (self):
#       Insertar un registro    con el identificador numérico del sensor (OK)
        self.assertRaises(TypeError, register.addData, value = 2.3, t0 = 1234)

    def test_register_without_value_ko (self):
#       Insertar un registro con valor no numérico (KO)
        self.assertRaises(ValueError, register.addData, selSensor = 1, value = "hola", t0 = 1234)

    def test_register_empty_value_ko (self):
#       Insertar un registro con valor vacío (KO)
        self.assertRaises(ValueError, register.addData, selSensor = 1, t0 = 1234)

    def test_register_none_value_ko (self):
#       Insertar un registro con valor Nulo (KO)
        self.assertRaises(ValueError, register.addData, selSensor = 1, value = None, t0 = 1234)

    def test_register_incorrect_sensor_name_ko (self):
#       Insertar un registro    con el identificador textual del sensor incorrecto (K0)
        self.assertRaises (sensor.DoesNotExist, register.addData, selSensor = sensorTest.name + "wrong", value = 3.04, t0 = 23423)

    def test_load_values_ok(self):
        self.insertTestData (1)
        self.insertTestData (2)
        self.assertEquals (len (register.objects.all ()), 199)
        
#       Insertar un registro con fecha en el futuro (WARNING)
        t1 = time.time () + 120
        register.addData (selSensor = 1, value = 23.14, t0 = t1)
        r1 = register.objects.get (sensor__pk = 1, time = datetime.datetime.fromtimestamp (t1))
        self.assertEquals (r1.value, 23.14)
#       Insertar un registro con fecha en el pasado (OK)
        t1 = time.time () - 120
        register.addData (selSensor = 1, value = 23.24, t0 = t1)
        r1 = register.objects.get (sensor__pk = 1, time = datetime.datetime.fromtimestamp (t1))
        self.assertEquals (r1.value, 23.24)
#       Insertar un registro    con el identificador textual del sensor correcto (OK)
        t2 = time.time ()
        register.addData (selSensor = sensorTest.name, value = 23.34, t0 = t2)
        r2 = register.objects.get (sensor__name = sensorTest.name, time = datetime.datetime.fromtimestamp(t2))
        self.assertEquals (len (register.objects.all ()), 202)

        alarmsLaunched = len (alarmLog.objects.all ())
        self.assertEquals (alarmsLaunched, 2)

        sensor.objects.get (pk = 1).graphRRD(name = 'testGraph', force = True, width = 500, height = 150)
        sensor.objects.get (pk = 2).graphRRD(name = 'testGraph', force = True, width = 500, height = 150)
        sensor.objects.get (pk = 2).graphRRDLastDay (force = True, width = 500, height = 150)
        sensor.objects.get (pk = 2).graphRRDLastWeek (force = True, width = 500, height = 150)
        sensor.objects.get (pk = 2).graphRRDLastMonth (force = True, width = 500, height = 150)
        sensor.objects.get (pk = 2).graphRRDLastYear (force = True, width = 500, height = 150)

    def insertTestData (self, sensor):
        t0 = time.time() - 4981 * 60
        for line in open("./apps/sensors/tests/mbmon.tsv").readlines():
            line = line.strip()
            if line == "": continue
        
            t1,t2,t3,rpm,vcore1,vcore2,v3,v5,v12,dt,\
            uptime,users,load5,load15,load60 = line.split("\t")
        
            t1,t2,t3,vcore1,vcore2,v3,v5,v12,load5,load15,load60 = \
                float(t1), float(t2), float(t3), float(vcore1), \
                float(vcore2), float(v3), float(v5), float(v12), \
                float(load5), float(load15), float(load60)
        
            rpm, users = int(rpm), int(users)
        
#           dt = ' '.join(dt.split (' ')[:-3]) + " 2008"
#           dt = datetime.datetime.strptime(dt, '%a %b %d %H:%M:%S %Y')
            t0 += 60
            #register.addData (sensor, float(t1), float(dt.strftime("%s")))
            register.addData (sensor, float(t1), t0)
