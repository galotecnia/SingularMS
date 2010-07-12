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
import sys
import ConfigParser
import logging
from logging.handlers import SysLogHandler
import os
from gettext import gettext as _
from gettext import textdomain

logging.basicConfig(format="<%(levelname)s> %(message)s")
formatter = logging.Formatter("<%(levelname)s> %(message)s")
logger = logging.getLogger("smstool_singularms_event_handler")
syslog = SysLogHandler(address = "/dev/log", facility = 'local1')
syslog.setFormatter(formatter)
logger.addHandler(syslog)
logger.setLevel(logging.INFO)



class SmsToolEventHandler:
    ACCEPTED_EVENTS = ('SENT', 'FAILED', 'RECEIVED', 'REPORT')

    def __init__ (self, argv, config_file = '/etc/singularms/smstool_event_handler.conf'):
        self.argv = argv
        self.config_file = config_file

    def load_config (self):
        if not os.path.isfile (self.config_file):
            errmsg = _("Error, config file %(file)s does not exist.") % {'file': self.config_file}
            raise ValueError (errmsg)
        config = ConfigParser.RawConfigParser()
        config.read(self.config_file)
        try:
            self.username = config.get('auth', 'username')
            self.password = config.get('auth', 'password')
            self.access = config.get('server', 'access')
            self.server_url = config.get('server', 'url')
        except ConfigParser.NoOptionError, e:
            errmsg = _("while reading config file: %(error)s") % {'error': e}
            raise ValueError (errmsg)
        except ConfigParser.NoSectionError, e:
            errmsg = _("while reading config file: %(error)s") % {'error': e}
            raise ValueError (errmsg)
        
    def input_parser (self):

        if len (self.argv) < 2:
            raise ValueError ('Less parameters than expected')
        self.event = self.argv[1]

        if self.event == 'RECEIVED':
            if len(self.argv) != 3:
                raise ValueError ('Wrong number of params')
            self.filename = self.argv[2]
            self.message_id = None
            return

        if self.event == 'SENT' and len (self.argv) != 4:
            raise ValueError ('Wrong number of params')
        elif len (self.argv) < 4:
            raise ValueError ('Less parameters than expected')
        if self.event not in SmsToolEventHandler.ACCEPTED_EVENTS:
            raise ValueError ('Wrong event: %(event)s' % {'event': self.event})
        self.filename = self.argv[2]
        self.message_id = self.argv[3]

    def parse_sms_file (self):
        self.headers = {}
        self.text = ''
        reading_header = True
        for line in open(self.filename, 'r').readlines ():
            if reading_header:
                if line.strip() == '':
                    reading_header = False
                else:
                    key_length = line.find(':')
                    key = line[:key_length]
                    value = line[key_length + 1:].strip()
                    self.headers[key] = value.strip()
            else:
                line = line.strip()
                if line != '':
                    self.text += line
        if self.text == '':
            raise ValueError ("There is no message")


    def receive_message (self):
        try:
            date = datetime.datetime.now()
            text = _("%(text)s (%(date)s)") % {'text': self.text, 'date': date.strftime("%H:%M %d/%m/%y")}
            if not self.server.receiveSMS(self.username, self.password, self.headers['From'], self.text, date, self.access):
                #print "Error: access %s does not exist" % access
                logger.error("access %(access)s does not exist" % {'access': acces})
        except TypeError, e:
            #print "Error: incorrect username or password" % self.username
            logger.error("Incorrect username or password")
        except socket.error, (e, s):
            #print "Error# %d creating socket: '%s'" % (e, s)
            logger.error("%(codeError)d creating socket: '%(s)s'" % {'codeError': e, 's': s})


    def dispatch (self):

        self.load_config ()
        self.input_parser ()
        self.parse_sms_file ()
        self.server = SOAPpy.SOAPProxy(self.server_url)
        try:
            if self.event == 'SENT':
                logger.info("Message sent to: %(to)s" % {'to': self.headers['To']})
                #print "Message sent"
                #print "(%s) %s" % (self.headers['To'], self.text)
            elif self.event == 'RECEIVED':
                logger.info("Message received from: %(from)s" % {'from': self.headers['From']})
                #print "(%s) %s" % (self.headers['From'], self.text)
                self.receive_message ()
            elif self.event == 'FAILED':
                logger.info("Message failed")
                #print "Message failed"
                #print "(%s) %s" % (self.headers['From'], self.text)
            elif self.event == 'REPORT':
                logger.info("Message failed")
                #print "Message report"
                #print "(%s) %s" % (self.headers['From'], self.text)
            else:
                print _("Error, event must be SENT, RECEIVED, FAILED or REPORT not '%(event)s'") % {'event': self.event}
                sys.exit (100)
        except socket.error, (e, s):
            logger.error("%s", s)
            sys.exit (1)

def usage():
    usage = _("""
Usage: %(argv0)s $1 is the type of the event wich can be SENT, RECEIVED, FAILED or REPORT.
       $2 is the filename of the sms.
       $3 is the message id. Only used for SENT messages with status report.
       The config is readed from /etc/singularms/smstool_event_handler.conf
""") % {'argv0':sys.argv[0]}
    print usage


if __name__ == "__main__":
    textdomain('daemon_tools')
    logger.info("dispatching event: %(argv)s" % {'argv': sys.argv})
    try:
        event_handler = SmsToolEventHandler (sys.argv)
        event_handler.dispatch ()
    except ValueError, e:
        logger.error("%(event)s" % {'event': e})
        print e
        usage ()
        sys.exit (1)
