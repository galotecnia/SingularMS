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

from soaplib.wsgi_soap import SimpleWSGISoapApp
from soaplib.service import soapmethod
from soaplib.serializers import primitive as soap_types

from django.http import HttpResponse
import StringIO

import inspect
import traceback
import sys
import re
import logging
from xml.etree import ElementTree
from soaplib.soap import make_soap_fault

from galotecnia_support import GalotecniaSupport

log = logging.getLogger('galotecnia')
 
class DumbStringIO(StringIO.StringIO):
    def read(self, n):
        return self.getvalue()
 
def catchWsExceptions(func):
    """
        Soaplib's exception catcher decorador
    """
    def wrapped(*args, **kwargs):
        try:
            result = func(*args, **kwargs)        
            return result
        except Exception,  e:
            tb = sys.exc_info()[2]
            tpl = traceback.extract_tb(tb)
            failedCall = str(tpl[-1][0])
            if re.search("soaplib", failedCall):
                log.error("Unknown error in SOAPLIB, %s", e)
                raise # this is not an exception within the functio but before calling the actual function
            if type(e) == type(TypeError):
                raise # API mistmach exception should not be filtered
            msg = ""
            if hasattr(e, "message"):
                msg = e.message
            log.error("Unknown error: %s", e)
            return e.__doc__
    wrapped.__doc__ = func.__doc__
    wrapped.func_name = func.func_name
    wrapped._is_soap_method = True
    return wrapped

class DjangoSoapApp(SimpleWSGISoapApp):

    # We have to override the original __call__ method because in Django is called 
    # with 2 arguments instead of 3
        
    def __call__(self, request):
        django_response = HttpResponse()

        def start_response(status, headers):
            status, reason = status.split(' ', 1)
            django_response.status_code = int(status)
            for header, value in headers:
                django_response[header] = value

        environ = request.META.copy()
        body = ''.join(['%s=%s' % v for v in request.POST.items()])
        environ['CONTENT_LENGTH'] = len(body)
        environ['wsgi.input'] = DumbStringIO(body)
        environ['wsgi.multithread'] = False
       
        response = SimpleWSGISoapApp.__call__(self, environ, start_response)
        django_response.content = "\n".join(response)

        return django_response

    def onWsdlException(self, environ, exc, resp):
        super(DjangoSoapApp, self).onWsdlException(environ, exc, resp)
        log.error("Excepcion in SingularMS wsdl soaplib: %s", exc)
        g = GalotecniaSupport()
        g.process_exception({}, exc, environ = environ, subject = "Exception in SingularMS wsdl generation", resp=resp) 
        # correo_excepcion("Exception in SingularMS wsdl generation", exc, environ, resp=resp)
        return resp


    def onException(self, environ, exc, resp):
        super(DjangoSoapApp, self).onException(environ, exc, resp)
        log.error("Excepcion in SingularMS soaplib: %s", exc)
        g = GalotecniaSupport()
        g.process_exception({}, exc, environ = environ, subject = "Exception in SingularMS webservice soap library", resp=resp) 
        # correo_excepcion("Excepcion in SingularMS webservice soap library", exc, environ, resp=resp)
        return resp
