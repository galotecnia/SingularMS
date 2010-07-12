
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

"""
    Test connector
"""

from connectors.base import Connector, utf8_to_gsm
from mo.models import IncomingMessage
from mt.models import Message
import time
import datetime
import random
from django.core.mail import send_mail
import logging
log = logging.getLogger('singularmsd')

DEFAULT_DE = 'galotecnia@galotecnia.com'
DEFAULT_PARA = 'desarrollo@galotecnia.com'

def gen_id(mult = 1000):
    return int(random.random()*mult)

display = { 0: u'NONE', 1: u'SENT', 2: u'FAIL', 3: u'PROCESSING', 4: u'PROCESSING', }

choices = { 0: [Connector.NONE, u'Cannot connect to Dummy, try later', ''],
            1: [Connector.SENT, u'Ok', str(gen_id())],
            2: [Connector.FAILED, u'Error in Dummy', ''],
            3: [Connector.PROCESSING, u'Temporal error in Dummy', str(gen_id())],
            4: [Connector.PROCESSING, u'Temporal error in external Dummy platform', str(gen_id())],
          }

class DummyConnector(Connector):

    def __init__(self, args):
        try:
            self.de = args['de']
            self.para = [args['para'],]
        except (AttributeError, KeyError):
            self.de = DEFAULT_DE
            self.para = [DEFAULT_PARA]
        self.subject = u'Dummy SMS'

    def send_one(self, text, recipient, args):
        acc = args['account_name'] if 'account_name' in args else 'Unknown'
        text = utf8_to_gsm(text).encode('latin1')
        status = gen_id(100)
        if status < 90:
            status = 4
        elif status < 95:
            status = 0
        else:
            status = 2
        mail = 'Msg "%s" sent' % text
        mail += ' to %s from %s account. Status: %s.' % (str(recipient), str(acc), str(display[status]))
        send_mail (self.subject, mail, self.de, self.para, fail_silently=False)
        log.info('Sending a mail from %s to %s', self.de, self.para[0])
        return choices[status]
 
    def send_mms(self, text, recipient, attachments, args):
        return choices[1]

    def send_many(self, text, recipients, args):
        return choices[1]

    def get_info(self, id):
        status = gen_id(100)
        if status < 85:
            status = 1
        elif status < 90:
            status = 2
        elif status < 95:
            status = 3
        else:
            status = 0
        return [choices[status][:2], ]
        
    def get_credit(self):
        return 1000
 
    def check_code(self, code = 0):
        return self.SENT

    def encode(self, incoming_msg, **kwargs):
        answer, cmd = incoming_msg.process()
        if answer and cmd:
            if cmd.command.account.customer.user_ptr == incoming_msg.account.customer.user_ptr:
                id = Message.create_one(answer, incoming_msg.mobile, datetime.datetime.now(), cmd.command.account)
                if id < 0:
                    log.error("Error whiel trying to create a response message. Info = %s", kwargs)
                else:
                    log.debug("Dummy message %d created to %s phone, text: %s", id, incoming_msg.mobile[1:], answer)
            else:
                log.error("DUMMY: %s user cannot receive from account %s", cmd.command.account.customer.user_ptr, incoming_msg.account)
        else:
            log.error("DUMMY COMMAND ERROR: %s", cmd)

    def decode(self, access, **kwargs):
        if random.randint(0,100) > 90:
            item = IncomingMessage.create_one(str(random.randrange(600000000, 699999999)), "DummySMS Received", datetime.datetime.now(), access.account_set.all()[0], None)
            self.encode(item)
