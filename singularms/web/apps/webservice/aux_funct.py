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

import datetime
import logging
from mt.models import Customer, Message, Channel, ResponseMessage
from accounting.models import Purchase, Access, Account, Capabilities
from accounting.models import NONE_STATUS, FAIL_STATUS
from mt.models import SMSHistory
from mt.forms import check_mobile
from mt.singular_exceptions import *
from mt.constants import ACCOUNT_NO_CREDIT
from mo.models import IncomingMessage

log = logging.getLogger('galotecnia')

def test_simple():
    return "Test ok"

def send_sms(username, password, account, phoneNumber, text, activationDate = None):
    """
        Send a text msg to a phone over an account given
    """
    try:
        account = Customer.check_customer_and_credit(username, password, account)
    except OutOfCredit:
        return ACCOUNT_NO_CREDIT 
    if account < 0:
        return account
    if not activationDate:
        activationDate = datetime.datetime.now()
    phoneNumber = check_mobile(phoneNumber)
    if phoneNumber < 0:
        return phoneNumber
    return Message.create_one(text, phoneNumber, activationDate, account)

def send_sms_many(username, password, account, phoneList, text, activationDate = None):
    """
        Send a text msg to a many phones over an account given
    """
    try:
        account = Customer.check_customer_and_credit (username, password, account, len(phoneList))
    except OutOfCredit:
        return [ACCOUNT_NO_CREDIT]
    if account < 0:
        return [account]
    activationDate = datetime.datetime.now ()
    idlist = []
    for phone in phoneList:
        if check_mobile(phone) < 0:
            return [-50] # FIXME: cambiar esto por MobileErrorException cuando se implemente
    for phone in phoneList:
        phone = phone.strip()
        idlist.append(Message.create_one (text, phone, activationDate, account))
    return idlist

def send_sms_channel(username, password, account, channel, text, activationDate = None):
    """
        Send a msg to a channel, with a account given        
    """
    try:
        account = Customer.check_customer_and_credit (username, password, account)
    except OutOfCredit:
        return ACCOUNT_NO_CREDIT
    if account < 0:
        return account
    if activationDate is None:
        activationDate = datetime.datetime.now ()
    chmsg_id = Channel.create_one (text, channel, account, activationDate)
    return Message.objects.get(channelmessage__id = chmsg_id).id

def get_accounts(username, password):
    """
        Get all accounts for a given user after check him
    """
    customer = Customer.get_customer (username, password)
    if customer < 0:
        return customer

    acc = []
    for i in customer.get_accounts ():
        acc.append (i.name)
    return acc

def get_channels (username, password):
    """
        Return all channels for this user
    """
    customer = Customer.get_customer (username, password)
    if customer < 0:
        return customer

    channels = []
    for i in customer.get_channels ():
        channels.append (i.name)
    return channels

def get_credit (username, password, account):
    """
        Return credit for an user and an account given
    """

    account = Customer.check_customer_and_credit (username, password, account)
    if account < 0:
        if account == Purchase.INSUFFICIENT_CREDIT:
            return 0
        return account #Error
    return account.get_real_credit ()

def get_status(username, password, id):
    """
        Return msg status given by his id
    """
    customer = Customer.get_customer (username, password)
    if customer < 0:
        return [str(FAIL_STATUS), "Customer error, please check your customer id and password"]
    l = SMSHistory.check_id (customer, id)
    if l:
        return [str(l[0]), str(l[1])]
    return [str(NONE_STATUS), "Msg %s not found on system, try it later" % id]

def update_incoming(username, password, last_update, last_id):
    customer = Customer.get_customer (username, password)
    access = Access.objects.filter(capabilities__in = Capabilities.objects.filter(typeSMS = 'Repliable'), account__customer = customer)
    last = datetime.datetime.strptime(last_update, '%d/%m/%Y %H:%M:%S')
    out = []
    for imsg in IncomingMessage.objects.filter(account__access__in = access, receivedDate__gt = last):
        imsg.processedDate = datetime.datetime.now()
        imsg.processed = True
        imsg.save()
        out.append("%s$%s$%s$" % (imsg.mobile, imsg.receivedDate, imsg.body.plainTxt))
    for rmsg in ResponseMessage.objects.filter(message__account__access__in = access, id__gt = last_id):
        out.append("%s$%s$%s$%s" % (rmsg.message.mobile, rmsg.receivedDate, rmsg.body, rmsg.message.id))
    return out
