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


__author__ = "Juan Carlos Castillo Cano <juancarlos@galotecnia.com>"
__version__= "1.1"

import logging
from connectors.base import Connector, utf8_to_gsm
from connectors.smsexceptions import *
from mt.constants import ACCOUNT_NO_CREDIT, WRONG_USER_PASS, WRONG_ACCOUNT, MOBILE_LESS_THAN_9, MOBILE_MORE_THAN_9
from mt.constants import MOBILE_NOT_VALID, MALFORMED_SMS_BODY, SMS_BODY_NOT_FOUND 
from xml.parsers.expat import ExpatError
from socket import error
from suds.client import Client
from mo.models import IncomingMessage
from mt.models import Message, SMSHistory, ResponseMessage
import datetime
from django.core.mail import send_mail

log = logging.getLogger('singularmsd.connectors.singular')

WSDL = "http://singularms.galotecnia.com/ws/service.wsdl"

msg_error = {
    ACCOUNT_NO_CREDIT: u'Singular Connector Error: run out of credit',
    WRONG_USER_PASS: u'Singular Connector Error: wrong user/pass',
    WRONG_ACCOUNT: u'Singular Connector Error: account doesnt not exist or is incorrect', 
    MOBILE_LESS_THAN_9: u'Singular Connector Error: phone number with less than 9 digits', 
    MOBILE_MORE_THAN_9: u'Singular Connector Error: phone number with more than 9 digits',
    MOBILE_NOT_VALID: u'Singular Connector Error: phone number not valid',
    MALFORMED_SMS_BODY: u'Singular Connector Error: malformed sms body',
    SMS_BODY_NOT_FOUND: u'Singular Connector Error: sms body not found',
    }   

REPLACEMENT_DICT = {'>':'*',  '<':'*', '&': '', ';': '%3B'}

def parse_text(text):
    for k in REPLACEMENT_DICT: text = text.replace(k,REPLACEMENT_DICT[k])
    return text

class SingularConnector(Connector):
    
    def __init__(self, args):
        self.username = args['username']
        self.password = args['password']
        self.server = None
        self.process = False
        self.url = args['url'] if 'url' in args else WSDL
        try:
            self.server = Client(self.url)
            log.info("Server %s available", self.url)
        except Exception, e:
            log.warn("Server %s not available (reason: %s)", self.url, e)
        if 'process' in args:
            self.process = args['process']
    
    def send_one(self, text, phone, args):
        phone = phone.strip()
        try:
            id = self.server.sendSMS(username = self.username, password = self.password, account = args['account'], phoneNumber = phone, text = parse_text(text))
        except KeyError:    
            msg = "Account argument needed in user %s params in order to send a msg." % self.username
            log.error(msg)
            return self.FAILED, msg, ''
        except (error, AttributeError, ExpatError):
            msg = "Cannot connect with %s server while sending a msg." % self.url
            log.warn(msg)
            return self.NONE, msg, ''
        except Exception, e:
            log.error(e)
            return self.FAILED, e, ''
        if id > 0:
            log.debug("Sending %s msg to %s" % (text, phone))
            return self.PROCESSING, 'Sent', str(id)
        if id in msg_error:
            return self.FAILED, msg_error[id], ''
        log.error("Not matched error: %d", id)
        return self.FAILED, "Error in Singular Connector: error (%s) not matched." % id, ''

    def send_many(self, text, phones, args):
        """
            Sends the same text to a list of recipients
        """
        phones = [p.strip() for p in phones]
        try:
            id_list = self.server.sendSMSmany(username = self.username, password = self.password, account = args['account'], phoneList = phones, text = text)
        except KeyError:
            msg = "Account argument needed in user %s params in order to send many msgs." % self.username
            log.error(msg)
            return self.FAILED, msg, ''
        except (error, AttributeError, ExpatError):
            msg = "Cannot connect with %s server while sending many msgs." % self.url
            log.warn(msg)
            return self.NONE, msg, ''
        except Exception, e:
            log.error(e)
            return self.FAILED, e, ''
        if id > 0:
            log.debug("Sending %s msg to %s" % (text, phones))
            return self.PROCESSING, 'Sent', str(id_list)
        if id in msg_error:
            return self.FAILED, msg_error[id], ''
        log.error("Not matched error: %d", id)
        return self.FAILED, "Error in Singular Connector: error (%s) not matched." % id, ''

    def get_info(self, id):
        """
            Obtains info about the message sent with id. The id value is returned by bulk
            when you achieve the sending proccess.

            Returns a dictionary with two keys, the id and a list o tuples with the status
            of the individual messages of the batch.
        """
        try:
            l = self.server.getStatus(username=self.username, password=self.password, id=id)
        except (error, AttributeError, ExpatError):
            msg = "Cannot connect to %s server while checking %s msg status." % (self.url, id)
            log.warn(msg)
            return [[self.NONE, msg], ]
        if l:
            log.info("Updating %s msg status: %s %s" % (id, l[0][0], l[0][1]))
            return l
        msg = "Received no %s msg status from %s" % (id, self.url)
        log.error(msg)
        return [[self.FAILED, msg], ]

    def get_credit(self, account):
        """
            Returns the credits availables for the account represented.
        """
        credit = None
        try:
            credit = self.server.getCredit(username = self.username, password = self.password, account = account)
            log.debug("%s account credit: %s" %(account, str(credit)))
        except (error, AttributeError, ExpatError):
            msg = "Cannot connect to % server while checking %s account credit" % (self.url, account)
            log.error(msg)
        return credit

    def encode(self, incoming_msg, **kwargs):
        answer, cmd = incoming_msg.process()
        if answer and cmd:
            if cmd.command.account.customer.user_ptr == incoming_msg.access.account_set.all()[0].customer.user_ptr:
                id = Message.create_one(answer, incoming_msg.mobile, datetime.datetime.now(), cmd.command.account)
                if id < 0:
                    log.error("Error while trying to create a msg response: info = %s", kwargs)
                else:
                    log.debug("Response mesage %s to %s: %s", id, incoming_msg.mobile[1:], answer)
            else:
                log.error("% user cannot receive msgs from %s access", cmd.command.account.customer.user_ptr, incoming_msg.access)
        else:
            log.error(cmd)
                

    def decode(self, access, **kwargs):
        # Get previous_date from last incoming msg in DDBB
        try: 
            previous_date = IncomingMessage.objects.filter(account__in = access.account_set.all()).order_by('-receivedDate')[0].receivedDate
        except IndexError:
            previous_date = datetime.datetime.now() - datetime.timedelta(60)
        last = previous_date.strftime('%d/%m/%Y %H:%M:%S')
        log.debug("Checking incoming messages from %s to now in %s", last, access)
        try:
            last_id = ResponseMessage.objects.filter(message__account__access = access).order_by('-receivedDate')[0].server_id
        except IndexError:
            last_id = 0
        log.debug("Checking incoming messages with id > %s", last_id)
        try:
            log.info("username=%s", self.username)
            log.info("password=%s", self.password)
            log.info("last_update=%s", last)
            log.info("last_id=%s", last_id)
            incoming_msgs = self.server.updateIncoming(username = self.username, password = self.password, last_update = last, last_id = last_id)
        except KeyError:    
            msg = "Some arguments left while trying to update %s user's incoming message list." % self.username
            log.error(msg)
            return
        except (error, AttributeError):
            msg = "Cannot connect to %s server while trying to update incoming message list." % self.url
            log.warn(msg)
            return
        except Exception, e:
            log.error("Unhandled error while trying to update %s user's incoming message list: %s", self.username, e)
            return
        if not incoming_msgs:
            log.debug("There are no new messages in %s access.", access)
            return
        self.parse_incoming(incoming_msgs, access)

    def prerare_list(self, m_list):
        """
            Recoder SOAPLIB array method. This is because SOAPLIB and suds have problems
            to understand arrays data.
        """
        try:
            if type(m_list) == list:
                # Normally instance
                return m_list
            elif type(m_list[0]) == list:
                # Normally list
                return m_list[0]
            log.warn("No format matched with incoming message list %s. Anything wrong?", m_list)
        except TypeError:
            log.error("List with incoming messages has wrong format: %s", m_list)
        return []
        
        
    def parse_incoming(self, msgs, access):
        lineas = self.prerare_list(msgs)
        for linea in lineas:
            phone, received, text, msg_id  = linea.split('$')
            date = datetime.datetime.strptime(received, '%Y-%m-%d %H:%M:%S')
            if msg_id:
                try:
                    m = SMSHistory.objects.filter(remote_id = msg_id)[0].message
                except IndexError:
                    log.error("Incoming message %s external to this platform (phone %s, id = %s)", text, phone, msg_id)
                    item = ResponseMessage.create_one(None, text, date, msg_id)
                    continue
                item = ResponseMessage.create_one(m, text, date, msg_id)
                log.debug("Incoming message to %s received: %s", m, item)
                args = m.account.args()
                if 'to' in args:
                    to_reply = [p.strip() for p in args['to'].split(',')]
                    from_reply = args['from'] if 'from' in args else 'no-reply@galotecnia.com'
                    subject = u"Reply message received from %s" % phone
                    mail = "Received on: %s\nMobile: %s\nText: %s" % (date, phone, text)
                    log.debug("Sending mail %s to %s", mail, to_reply)
                    send_mail(subject, mail, from_reply, to_reply, fail_silently=False)
            else:
                item = IncomingMessage.create_one(phone, text, date, access.account_set.all()[0], None)
                log.info("Received %s msg on %s from %s mobile to %s access.", text, received, phone, access)
                if self.process:
                    self.encode(item)
