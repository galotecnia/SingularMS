#-*- coding: utf-8 -*-

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


from django.core.mail import send_mail
from django.conf import settings
import datetime
import socket

class GalotecniaSupport:

    para = ['you@yourdomain',]
    de = 'singularms@yourdomain'

    def process_exception(self, request, exception, environ = None, subject = "", **args):
        import traceback
        import sys

        def presenta_dict(d, base=""):
            out = "{\n"
            if hasattr(d, 'items'):
                for k, v in d.items():
                    valstr = isinstance(v, dict) and presenta_dict(v, "  ") or repr(v)
                    out += base + "'%s': %s,\n" % (k, valstr)
            else:
                out += repr(d)
            out += "}\n"
            return out

        exc_info = sys.exc_info()
        mail = "SingularMS has failed today at %s\n" % datetime.datetime.now ()
        mail += "Traceback:\n"
        mail += "################################################################\n"
        mail = '\n'.join(traceback.format_exception(*(exc_info or sys.exc_info())))
        mail += "################################################################\n"
        mail += "Http request: \n"
        mail += "%s" % presenta_dict(request)

        if args:
            mail += "\n\nInformacion extra: \n"
            mail += "%s" % presenta_dict(args)

        if not subject:
            subject = "ERROR!!! Exception in SingularMS" 
        ip = hostname = ""
        if environ and 'REMOTE_ADDR' in environ:
            ip = environ['REMOTE_ADDR']
        if request and 'REMOTE_ADDR' in request.META:
            ip = request.META['REMOTE_ADDR']
        if ip: 
            try:
                hostname = socket.gethostbyaddr(ip)[0]
                subject += " (from %s)" % hostname
            except socket.herror:
                subject += " (from %s)" % ip
            mail += "\nOrigen:\n%s\n%s\n\n" % (ip, hostname)

        if environ:
            mail += "\nEnviron:\n%s\n\n" % presenta_dict(environ)

        if settings.SEND_MAIL_ON_EXCEPTION:
            send_mail (subject, mail, self.de, self.para, fail_silently=False)

    def process_error(self, msg):
        mail = "SingularMS has failed today at %s\n" % datetime.datetime.now ()
        mail += "################################################################\n"
        mail += "Error: %s" % msg
        send_mail ("ERROR!!!! Exception in SingularMS", mail, self.de, self.para, fail_silently=False)


