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


#!/usr/bin/python

import SOAPpy 

USERNAME = 'USUARIO'
PASSWORD = 'PASSWORD'

server = SOAPpy.WSDL.Proxy('http://demo.galotecnia.com/singularms/ws/service/service.wsdl', config=SOAPpy.SOAPConfig(debug=1))

#server.soapproxy.config.buildWithNamespacePrefix = 0
#for i in server.methods:
#    server.methods[i].namespace = server.wsdl.targetNamespace
#
#for k, v in server.methods.items():
#       print "Nombre del metodo: %s" % k
#       for l in range(len(v.inparams)):
#               print "\t", v.inparams[l].name, v.inparams[l].type
#       print "\t", v.outparams, v.retval
#
#print server.show_methods()
#print dir(server.soapproxy)

greetings = server.say_hello(name = 'Pepe', times = 10)
for g in greetings:
    print g

print "Lista de canales:",
channels = server.getChannels(username = USERNAME, password = PASSWORD)
for c in channels:
    print c,
print

print "Lista de cuentas:",
accounts = server.getAccounts(username = USERNAME, password = PASSWORD)
for c in accounts:
    print c,
print

