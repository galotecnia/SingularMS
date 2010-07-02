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

from django.utils.translation import ugettext_lazy as _
from accounting.models import NONE_STATUS, SENT_STATUS, PROCESSING_STATUS, FAIL_STATUS

# SENDING MESSAGE TYPES
MESSAGE_TYPE_INDIVIDUAL = 'Individual'
MESSAGE_TYPE_CHANNEL = 'Channel'
MESSAGE_TYPES = {
    MESSAGE_TYPE_INDIVIDUAL: _('Individual'),
    MESSAGE_TYPE_CHANNEL: _('Channel'),
}

MESSAGE_STATUS_NAME = ('Process', 'Pending')
MESSAGE_STATUS = {
    unicode(_(MESSAGE_STATUS_NAME[0])): True,
    unicode(_(MESSAGE_STATUS_NAME[1])): False,
}

# GENERAL STATUS
DELIVERED  = SENT_STATUS
FINAL_FAIL = FAIL_STATUS
TMP_FAIL   = PROCESSING_STATUS
NONE       = NONE_STATUS
STATUS_CHOICES = ( (NONE, _('NONE')), (DELIVERED,_('DELIVERED')), (FINAL_FAIL,_('FATAL ERROR')), (TMP_FAIL,_('PROCESSING')) )

# TEMPLATES
TEMPLATES = {
    'update_channel': 'mt/channel.html',
    'delete_channel': 'mt/channel_confirm_delete.html',
    'delete_message': 'mt/message_confirm_delete.html',
    'create_channel': 'mt/channel.html',
    'send_message': 'mt/send_message.html',
    'ajax_filter': 'mt/table_list.html',
    'sms_types': 'mt/sms_types.html',
    'show_subscriber': 'mt/subscriber.html',
    'ajax_subscriber': 'mt/table_subscriber.html',
    'message_list': 'mt/message_list.html',
    'channel_list': 'mt/channel_list.html',
    'ajax_channel_list': 'mt/table_channel.html',
    'errors': 'base.html'
}

# SENDING ERRORS
ACCOUNT_NO_CREDIT = -40
WRONG_USER_PASS = -100
WRONG_ACCOUNT = -200
MALFORMED_SMS_BODY = -60
SMS_BODY_NOT_FOUND = -70
OUTOFCREDIT_ERROR = _('Not enough credits')

ERROR_MSG = {
    ACCOUNT_NO_CREDIT: _('Account without credits'),
    MALFORMED_SMS_BODY: _('Malformed SMS body'),
    SMS_BODY_NOT_FOUND: _('SMS body not found'),
}

# MOBILE ERRORS
MOBILE_LESS_THAN_9 = -10
MOBILE_MORE_THAN_9 = -20
MOBILE_NOT_VALID   = -30

MOBILE_ERRORS = ( MOBILE_LESS_THAN_9, MOBILE_MORE_THAN_9, MOBILE_NOT_VALID, )

MOBILE_MSG_ERROR = {
    MOBILE_LESS_THAN_9: _("Mobile number doesn't have enough digits"),
    MOBILE_MORE_THAN_9: _("Mobile number has more digits than normal"),
    MOBILE_NOT_VALID  : _("Mobile number is not valid"),
}
     
