
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
	Exception tree to signal any problem involved with SMS sending.
"""
__author__ = "Juan Gregorio Regalado Pacheco <goyo.regalado@galotecnia.com>"
__version__= "0.1"

class SMSException(Exception):
	message = "Generic SMS Exception"
	def __str__(self):
		return self.message

class ServerInternalErrorException(SMSException):
	message = "Server internal error, messages couldn't be sent"

class AuthenticationFailureException(SMSException):
	message = "Authentication failure, please check your username and password values"

class PhoneValidationFailureException(SMSException):
	message = "Phone validation failure, please check your number"

class DataValidationFailureException(SMSException):
	message = "Data validation failure, please check your data"

class CreditFailureException(SMSException):
	message = "Credit failure, you haven't enough credit to send messages with this server"

class UpstreamCreditNotAvailableException(SMSException):
	"""
		I don't know what in the hell is the upstream credit
	"""
	message = "Upstream credits not available, please check your upstream credit"


class DailyQuotaExceededException(SMSException):
	message ="Daily quota exceeded, you can't send more messages today"

class UpstreamQuotaExceededException(SMSException):
	message ="Upstream quota exceeded, please check your upstream quota"

class MessageSendingCancelledException(SMSException):
	message ="Message sending has been cancelled"

class TemporarilyUnavailableException(SMSException):
	message = "Service temporarily unavailable"

class ServerCommunicationException(SMSException):
	"""
		It will be raised when there is any problem communicating with the server.
	"""
	message = "Server communication error: We could't reach the SMS sending service."

class UnknownErrorException(SMSException):
	"""
		Represents the improbable situation in which the server send us an unknown error code.
	"""
	message = "Unknown error exception: This is a really extrange problem. We don't understand the server's response"

