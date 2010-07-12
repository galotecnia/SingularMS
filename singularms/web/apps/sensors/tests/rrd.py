#!/usr/bin/python

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

import sys
import datetime
import rrdtool, tempfile

RRD = '/tmp/test.rrd'
rrdtool.create (RRD,
		'-b 1212997413',
		'-s 60',
		'DS:t1:GAUGE:60:U:U',
#		'RRA:AVERAGE:0.5:1:10080',
		'RRA:AVERAGE:0.5:20:10080',
		'RRA:HWPREDICT:5440:0.01:0.015:288',
#		'RRA:DEVPREDICT:100:0.5:0.5:20',
	)

for line in open("./mbmon.tsv").readlines():
	line = line.strip()
	if line == "": continue

	t1,t2,t3,rpm,vcore1,vcore2,v3,v5,v12,dt,\
	uptime,users,load5,load15,load60 = line.split("\t")

	t1,t2,t3,vcore1,vcore2,v3,v5,v12,load5,load15,load60 = \
		float(t1), float(t2), float(t3), float(vcore1), \
		float(vcore2), float(v3), float(v5), float(v12), \
		float(load5), float(load15), float(load60)

	rpm, users = int(rpm), int(users)

	dt = ' '.join(dt.split (' ')[:-3]) + " 2008"
	dt = datetime.datetime.strptime(dt, '%a %b %d %H:%M:%S %Y')
	rrdtool.update (RRD, '%s:%f' % (dt.strftime("%s"), t1))

	# falta uptime (x d hh:mm)

DAY = 86400
WEEK = 7 * DAY
YEAR = 365 * DAY
fd,path = tempfile.mkstemp('.png')

rrdtool.graph(path,
		'--imgformat', 'PNG',
		'--width', '1000',
		'--height', '400',
		'--start', "-%i" % DAY * 1,
#		'--end', "-1",
		'--vertical-label', 'Temperatura',
		'--title', 'Temperatura del micro esta semana',
#		'--lower-limit', '20',
		'DEF:temp=%s:t1:AVERAGE' % RRD,
		'DEF:tempSoft=%s:t1:AVERAGE:step=20' % RRD,
		'DEF:pred=%s:t1:HWPREDICT' % RRD,
		'DEF:dev=%s:t1:DEVPREDICT' % RRD,
		'DEF:fail=%s:t1:FAILURES' % RRD,
		'TICK:fail#ffffa0:1.0:Failures Average bits out',
		'CDEF:upper=pred,dev,2,*,+',
		'CDEF:scaledupper=upper,8,*',
		'CDEF:lower=pred,dev,2,*,-',
		'CDEF:scaledlower=lower,8,*',
		'CDEF:scaledtemp=temp,8,*',
		'CDEF:scaledtempSoft=tempSoft,8,*',
#		'DEF:temp2=%s:t1:HWPREDICT' % RRD,
#		'AREA:temp#990033:Temperatura',
		'LINE2:temp#990033:Temperatura',
#		'LINE2:scaledtemp#990033:Temperatura',
#		'LINE2:scaledtempSoft#4400FF:Temperatura',
#		'LINE1:upper#ff0000:upper',
#		'LINE1:scaledupper#00ff00:upper',
#		'LINE1:lower#ff0000:lower',
#		'LINE1:scaledlower#00ff00:lower',
#		'LINE1:temp2#71ff64:Temperatura por dos'
	)

info = rrdtool.info(RRD)
print info['last_update']
print info['ds']['t1']['minimal_heartbeat']
print info
