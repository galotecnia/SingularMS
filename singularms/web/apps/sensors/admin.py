# -*- encoding: utf-8 -*-

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

from django.contrib import admin

from models import *


class contactPersonAdmin (admin.ModelAdmin):
	list_display = ('name', 'description', 'email', 'cellPhone')
	search_fields = ('name', 'description', 'email', 'cellPhone',)


admin.site.register(contactPerson, contactPersonAdmin)

class alarmLogAdmin (admin.ModelAdmin):
	list_display = ('time', 'description')

admin.site.register(alarmLog, alarmLogAdmin)

class sensorTypeAdmin (admin.ModelAdmin):
	list_display = ('model', 'description', 'minAcceptedValue', 'maxAcceptedValue')

admin.site.register(sensorType, sensorTypeAdmin)

class sensorAdmin (admin.ModelAdmin):
	list_display = ('id', 'name','type', 'description', 'status')
	list_display_links = ('id', 'name')
	list_filter = ('type', )

admin.site.register(sensor, sensorAdmin)


class alarmAdmin (admin.ModelAdmin):
	list_display = ('sensor', 'minValue', 'maxValue', 'alertByEmail', 'alertByCellPhone')

admin.site.register(alarm, alarmAdmin)

class registerAdmin (admin.ModelAdmin):
	list_display = ('sensor', 'time', 'value')
	list_filter = ('sensor', )
	date_hierarchy = 'time'
	fieldsets = (
		(None, {
			'fields': ('sensor', ('time', 'value')),
			}),
		)

admin.site.register(register, registerAdmin)

class sensorGroupAdmin (admin.ModelAdmin):
	list_display = ('name', )

admin.site.register(sensorGroup, sensorGroupAdmin)

