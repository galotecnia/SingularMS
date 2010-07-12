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

DJANGOBIN=../../django/django_src-20070223/django/bin

all: syncdb runserver

syncdb:
	python manage.py syncdb

runserver:
	python manage.py runserver

translate: locale/es/LC_MESSAGES/django.mo

# The first step is to create a message file for a new language.
# To create or update a message file, run this command:
#
# ${DJANGOBIN}/make-messages.py -l LANGUAGECODE
# http://www.djangoproject.com/documentation/i18n/#message-files

locale/es/LC_MESSAGES/django.po: *.py manager/models/*.py manager/*.py
	${DJANGOBIN}/make-messages.py -a

locale/es/LC_MESSAGES/django.mo: locale/es/LC_MESSAGES/django.po
	${DJANGOBIN}/compile-messages.py

shell:
	python manage.py shell

load_xml:
	python manage.py loaddata base_data.xml

graph:
	python manage.py graph_models -g mt accounting mo -o graph.png

.PHONY: syncdb runserver shell
