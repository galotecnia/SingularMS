#!/usr/bin/python
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

import SOAPpy
import socket
import datetime
import time
import getopt
import sys
import getpass
import random
import string

server_url = 'http://localhost:9000/'
username = "stresstest"
password = "1234"
account = "accounttest"
mobile = '654321098'

def GenDummySMS(length=160, chars=string.letters + string.digits + '                ,;?:!' ):
    return ''.join([random.choice(chars) for i in range(length)])

def send_message (server, username, password, account, mobile, text):
    try:
        text +=  GenDummySMS(length = random.randrange(10, 150))
        date = datetime.datetime.now()
        text = ("%(text)s (%(date)s)") % {'text': text, 'date': date.strftime("%H:%M %d/%m/%y")}
        id = server.sendSMS(username, password, account, mobile, text)
        print ("Message id: %(id)s") % {'id': id}
        return id
    except TypeError, e:
        print ("You don't have access with user %(username) and password") % {'username': username}
    except socket.error, (e, s):
        print ("Error# %(codeError)d creating socket: '%(text)s'") % {'codeError': e, 'text': s}
    return None


if __name__ == "__main__":
    server = SOAPpy.SOAPProxy(server_url)
    print "Enviando 1000 mensajes a toda castaña"
    ids = []
    for sms in range (256):
        id = send_message (server, username, password, account, mobile, '%d: ' % sms)
        if id:
            ids.append(id)

    print "Consultando el status de los 1000 mensajes"
    for id in ids:
        print id

    print "Enviando 100 mensajes por segundo cada 5 segundos durante 10 minutos"
    ids = []
    for i in range (60 * 10 / 5):
        num_messages = 100
        delay = 5 / num_messages
        for m in range (num_messages):
            id = send_message (server, username, password, account, mobile, '%d-%d: ' % (i, m))
            if id:
                ids.append(id)
            time.sleep (delay)
            
    print "Consultando el status de los 1000 mensajes"
    for id in ids:
        print id

