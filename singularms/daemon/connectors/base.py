
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


from accounting.models import SENT_STATUS, FAIL_STATUS, PROCESSING_STATUS, NONE_STATUS
import logging
import re

MESSAGE_STATUS = {
    "InProgress": {"status": 1, "description": "Message sending in progress"},
    "DeliveredUpstream": {"status": 2, "description": "Message delivered upstream"},
    "DeliveredMobile": {"status": 3, "description": "Message delivered to mobile"},
    "InternalError": {"status": 3, "description": "Internal error"},
    "AuthenticationFailure": {"status": 4, "description": "Authentication failure"},
    "DataNotValid":    {"status": 5, "description": "Data isn't valid"},
    "NoCredit" : {"status": 6, "description": "There isn't enough credit"},
    "NoUpstreamCredit": {"status": 7, "description": "There isn't enough upstream credit"},
    "DailyQuotaExceeded": {"status": 8, "description": "Daily quota exceeded"},
    "UpstreamQuotaExceeded": {"status": 9, "description": "Upstream quota exceeded"},
    "Cancelled": {"status": 10, "description": "Message sending cancelled"},
    "Unroutable": {"status": 11, "description": "Message unroutable"},
    "Blocked": {"status": 12, "description": "Message blocked"},
    "Censored": {"status": 13, "description": "Message failed, it has been censored"},
    "TemporarilyUnavailable": {"status": 14, "description": "Message sending service temporarily unavailable"},
    "GenericDeliveryFailure":    {"status": 15, "description": "Delivery failed due to a generic failure"},
    "PhoneDeliveryFailure": {"status": 16, "description": "Phone delivery failed"},
    "NetworkDeliveryFailure": {"status": 17, "description": "Network delivery failed"},
    "Expired": {"status": 18, "description": "Message expired"},
    "FailureRemoteNetwork": {"status": 19, "description": "Failure on remote network"},
    "FailureRemoreCensored": {"status": 20, "description": "Message censored on remote network"},
    "FailureHandSet": {"status": 21, "description": "Failed due to recipient's handset, SIM full"},
    "TransientUpstreamFailure": {"status": 22, "description": "Transient upstream failure"},
    "UpstreamStatusUpdate": {"status": 23, "description": "Upstream status update"},
    "UpstreamCancelFailed": {"status": 24, "description": "Upstream cancel failed"},
    "QueuedRetry": {"status": 25, "description": "Message queued for retry after temporary failure delivering"},
    "QueuedRetryHandset": {"status": 26, "description": "Message queued for retry after temporary failure due to fault on recipient's handset"},
    "UnknownUpstreamStatus": {"status": 27, "description": "Unknown upstream status"}
}

log = logging.getLogger('singularmsd')

def utf8_to_gsm(cadena):
        conversion = {
                u"á": "a", u"à": "a", u"ä": "a", u"â": "a",
                u"é": "e", u"è": "e", u"ë": "e", u"ê": "e",
                u"í": "i", u"ì": "i", u"ï": "i", u"î": "i",
                u"ó": "o", u"ò": "o", u"ö": "o", u"ô": "o",
                u"ú": "u", u"ù": "u", u"ü": "u", u"û": "u",
                u"Á": "A", u"À": "A", u"Ä": "A", u"Â": "A",
                u"É": "E", u"È": "E", u"Ë": "E", u"Ê": "E",
                u"Í": "I", u"Ì": "I", u"Ï": "I", u"Î": "I",
                u"Ó": "O", u"Ò": "O", u"Ö": "O", u"Ô": "O",
                u"Ú": "U", u"Ù": "U", u"Ü": "U", u"Û": "U",
                u"€": "E", 
        }
        if type(cadena) is not unicode:
                return cadena
        out = ""
        for caracter in cadena:
                if caracter in conversion:
                        out += conversion[caracter]
                else:
                        out += caracter
        out = re.sub("[^\w\xf1\xd1\s\d\*/\\¡¿!?\"$%&()=\|@#~\[\]\{\};,\.\:'-]", " ", out)
        return out

def strip_list(recipients):
    return [x.strip() for x in recipients]

class Connector:
    # STATUS
    SENT = SENT_STATUS
    FAILED = FAIL_STATUS
    PROCESSING = PROCESSING_STATUS
    NONE = NONE_STATUS

    def __init__(self, args):
        """
            Config params will be send in a dictionary
        """
        self.log = log 

    def send_one(self, text, recipient, args):
        """
            Send a sms (text) to a phone (recipient) with some args
        """
        raise NotImplemented
        # Returns [STATUS, STATUS_MSG, ID_REMOTO]

    def send_many(self, text, recipients, args):
        """
            Send a sms (text) to some phones ([recipients]) with some args
        """
        raise NotImplemented
        # Returns [STATUS, STATUS_MSG, ID_REMOTO]

    def get_info(self, id):
        """
            Get the status of a message in the external platform (like BulkSMS, WPR, etc)
        """
        raise NotImplemented
        # Returns [[STATUS, STATUS_MSG], ...]

    def get_credit(self):
        """
            Get external platform credit
        """
        raise NotImplemented
        # Return FLOAT_CREDIT

    def send_mms(self, text, recipient, attachments, args):
        """
            Send a mms (text + attachments) to a phone (recipient) with some args
        """
        raise NotImplemented
        # Return [STATUS, STATUS_MSG, ID_REMOTO]

    def check_code(self, code):
        """
            Recode an external platform message status to a singularms daemon status
        """
        raise NotImplemented
        # Return STATUS

    def encode(self, incoming_msg, **kwargs):
        """
            Parse a incoming message (incoming_msg) and check if matchs with any of
            the SingularMS customer commands. If TRUE, a response msg will be created
        """
        raise NotImplemented
        # No return

    def decode(self, access, **kwargs):
        """
            Receive all incoming messages; an account must be passed in args
            if we want to receive his new messages. If incoming messages have to been
            processed (channel services, web services, etc), a encode call must be done
        """
        raise NotImplemented
        # No return
        
