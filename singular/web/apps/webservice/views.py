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

import logging

from soaplib_handler import DjangoSoapApp, soapmethod, soap_types, catchWsExceptions
from soaplib.serializers.primitive import String, Integer, Array
from aux_funct import *

log = logging.getLogger('galotecnia')

class SingularService(DjangoSoapApp):

    # __tns__ = 'http://www.galotecnia.com/soap/'
    __tns__ = "http://www.w3.org/2003/05/soap-encoding"

    @catchWsExceptions
    @soapmethod(soap_types.String, soap_types.String, soap_types.String, soap_types.String, soap_types.String, soap_types.String, _returns=soap_types.Integer)
    def sendSMS(self, username, password, account, phoneNumber, text, activationDate = None):
        """
            Send a text msg to a phone over an account given
        """
        log.debug(u'sendSMS: %s "password" "%s" "%s" "%s" "%s" by webservice', username, account, phoneNumber, text, activationDate) 
        return send_sms(username, password, account, phoneNumber, text, activationDate)

    @catchWsExceptions
    @soapmethod(soap_types.String, soap_types.String, soap_types.String, Array(soap_types.String), soap_types.String, soap_types.String, _returns=Array(soap_types.Integer))
    def sendSMSmany(self, username, password, account, phoneList, text, activationDate = None):
        """
            Send a text msg to many phones over an account given
        """
        log.debug(u'sendSMSmany: %s "password" "%s" "%s" "%s" "%s by webservice"', username, account, str(phoneList), text, activationDate) 
        return send_sms_many(username, password, account, phoneList, text, activationDate)

    @catchWsExceptions
    @soapmethod(soap_types.String, soap_types.String, soap_types.String, soap_types.String, soap_types.String, soap_types.String, _returns=soap_types.Integer)
    def sendSMSToChannel(self, username, password, account, channel, text, activationDate = None):
        """
            Send a text msg to a channel over an account given
        """
        log.debug(u'sendSMStoChannel: %s "%s" "%s" "%s" by webservice"', username, account, channel, text)
        return send_sms_channel(username, password, account, channel, text, activationDate)
 
    @catchWsExceptions
    @soapmethod(soap_types.String, soap_types.String, _returns=Array(soap_types.String))
    def getAccounts(self, username, password):
        """
            Return all acces for this user
        """
        log.debug(u'getAccounts: %s by webservice"', username)
        return get_accounts(username, password)

    @catchWsExceptions
    @soapmethod(soap_types.String, soap_types.String, _returns=Array(soap_types.String))
    def getChannels (self, username, password):
        """
            Return all channels for this user
        """
        log.debug(u'getChannels: %s by webservice"', username)
        return get_channels(username, password)

    @catchWsExceptions
    @soapmethod(soap_types.String, soap_types.String, soap_types.String, _returns=soap_types.Integer)
    def getCredit (self, username, password, account):
        """
            Return left credit for an user and an account given
        """
        log.debug(u'"getCredit: %s %s by webservice"', username, account)
        return get_credit(username, password, account)

    @catchWsExceptions
    @soapmethod(soap_types.String, soap_types.String, soap_types.String , _returns=soap_types.Array(soap_types.String))
    def getStatus(self, username, password, id):
        """
            Return msg status given by his id
        """
        log.debug(u'"getStatus: %s %s by webservice"', username, id)
        return get_status(username, password, id)

    @catchWsExceptions
    @soapmethod(soap_types.String, soap_types.Integer, _returns=soap_types.Array(soap_types.String))
    def say_hello(self, name, times):
        results = []
        for i in range(0, times):
            results.append('Hello, %s'%name)
        return results

    @catchWsExceptions
    @soapmethod(soap_types.String, soap_types.String, soap_types.String, soap_types.String,_returns=soap_types.Array(soap_types.String))
    def updateIncoming(self, username, password, last_update, last_id): 
        """
            Return last incoming messages (upper last_update date)
        """
        return update_incoming(username, password, last_update, last_id) 

singular_service = SingularService()

