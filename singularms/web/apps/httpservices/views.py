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
from django.http import HttpResponse
from webservice.aux_funct import *
import simplejson

log = logging.getLogger('galotecnia')

KEY_ERROR = '-10'

SEND_ONE = 0
SEND_MAN = 1
SEND_CHN = 2

keys = (['username', 'password', 'account', 'phoneNumber', 'text'],
        ['username', 'password', 'account', 'phoneList', 'text'],
        ['username', 'password', 'account', 'channel', 'text'],)
       
def check_keys(get_dic, tipo):
    d = {}
    try:
        for k in keys[tipo]:
            d[k] = get_dic[k]
    except KeyError:
        return None
    if get_dic.has_key('activationDate'):
        d['activationDate'] = get_dic['activationDate']
    else:
        d['activationDate'] = datetime.datetime.now()
    return d

def testHTTP(request):
    return HttpResponse('Hello world!')

def sendSMS(request):
    data = check_keys(request.GET, SEND_ONE)
    if not data:
        return HttpResponse(simplejson.dumps(KEY_ERROR))
    if not 'activationDate' in data:
        act_date = None
    else:
        act_date = data['activationDate']
    id = send_sms(data['username'], data['password'], data['account'], data['phoneNumber'], data['text'], act_date)
    return HttpResponse(simplejson.dumps(id))

def sendSMSmany(request):
    data = check_keys(request.GET, SEND_MAN)
    if not data:
        return HttpResponse(KEY_ERROR)
    if not 'activationDate' in data:
        act_date = None
    else:
        act_date = data['activationDate']
    id = send_sms_many(data['username'], data['password'], data['account'], data['phoneList'], data['text'], act_date)
    return HttpResponse(simplejson.dumps(id)) 

def sendSMSToChannel(request):
    data = check_keys(request.GET, SEND_CHN)
    if not data:
        return HttpResponse(KEY_ERROR)
    if not 'activationDate' in data:
        act_date = None
    else:
        act_date = data['activationDate']
    id = send_sms_channel(data['username'], data['password'], data['account'], data['channel'], data['text'], act_date)
    return HttpResponse(simplejson.dumps(id))

def getAccounts(request):
    try:
        acc = get_accounts(request.GET['username'], request.GET['password'])
    except KeyError:
        return HttpResponse(KEY_ERROR)
    return HttpResponse(simplejson.dumps(acc))
    
def getChannels(request):
    try:    
        chn = get_channels(request.GET['username'], request.GET['password'])
    except KeyError:
        return HttpResponse(KEY_ERROR)
    return HttpResponse(simplejson.dumps(chn))    
   
def getCredit(request):
    try:
        credit = get_credit(request.GET['username'], request.GET['password'], request.GET['account'])
    except KeyError:
        return HttpResponse(KEY_ERROR) 
    return HttpResponse(simplejson.dumps(credit))
    
def getStatus(request):
    try:
        sts = get_status(request.GET['username'], request.GET['password'], request.GET['id'])
    except KeyError:
        return HttpResponse(KEY_ERROR)
    return HttpResponse(simplejson.dumps(sts))

def updateIncoming(request):
    try:
        out = update_incoming(request.GET['username'], request.GET['password'], request.GET['last_update'], request.GET['last_id'])
    except KeyError:
        return HttpResponse(KEY_ERROR)
    return HttpResponse(simplejson.dumps(out))
