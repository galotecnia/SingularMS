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

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from django.db.models.signals import post_save, pre_delete, post_delete

from accounting.models import Provider, Access, Customer, Account, Purchase, NONE_STATUS, SENT_STATUS, PROCESSING_STATUS, FAIL_STATUS
from smlog.models import LOGPRIO_LIST
import datetime
import os
import logging
from constants import *

from singular_exceptions import OutOfCredit

_logger = logging.getLogger('galotecnia')

MONTHS_OPTIONS = (
    (1, _('January')),
    (2, _('February')),
    (3, _('March')),
    (4, _('April')),
    (5, _('May')),
    (6, _('June')),
    (7, _('July')),
    (8, _('August')),
    (9, _('September')),
    (10, _('October')),
    (11, _('November')),
    (12, _('December'))
)

OPERATORS_LIST = (
    (0, 'Vodafone'),
    (1, 'Tempos21'),
    (2, 'Lleida.net'),
    (3, 'SitSMS'),
    (4, 'Arsys'),
)

LOGTYPE_LIST = (
    (1, _('auth')),
    (2, _('message')),
    (3, _('platform')),
    # TODO: completar esto y pensarlo
)

def adapt_mobile(mobile):
    mobile = mobile.strip()
    national = mobile.find('+')
    if national == -1:
        return '+34' + mobile
    # Casos +600000000
    if national == 0 and len(str(mobile)) == 10:
        return '+34' + str(mobile)[1:]
    return mobile

class Body(models.Model):
    """
        The body of a SMS
    """
    plainTxt = models.TextField(verbose_name = _('plain text'), blank = False)
    mms = models.BooleanField(verbose_name = _('MMS'), blank = False, default = False)
    encodedMsg = models.TextField(verbose_name = _('encode Message'), blank = True, null = True)

    def size(self):
        return self.mms and len(self.encodedMsg) or len(self.plainTxt)

    def __unicode__(self):
        return self.plainTxt

    class Meta:
        verbose_name = _('Body')
        verbose_name_plural = _('Bodies')

class Attachment(models.Model):
    """
        An attachment for a MMS
    """
    contentType = models.CharField(verbose_name = _('content type'), max_length = 255, blank = False)
    file = models.FileField(verbose_name = _('file'), upload_to = 'attachments/%Y/%m', blank = False)
    body = models.ForeignKey('Body', blank = False, verbose_name = _('body'))

    def __unicode__(self):
        return self.file.name

    def filename (self):
        return os.path.basename (self.file.name)

    class Meta:
        verbose_name = _('attachment')
        verbose_name_plural = _('attachments')


class Channel(models.Model):
    """
        A tematic channel
    """
    name = models.CharField(verbose_name=_('name'), max_length=255, blank=False, unique=True)
    description = models.CharField (verbose_name = _('description'), max_length = 255, blank = False)
    creationDate = models.DateTimeField(verbose_name= _('creation date'), auto_now_add = True, blank = False)
    destructionDate = models.DateTimeField(verbose_name= _('destruction date'), blank = True, null = True)
    active = models.BooleanField(verbose_name= _('active'), blank = False, default = True)
    customer = models.ManyToManyField(Customer, verbose_name=_('customer'), blank=False)

    CHANNEL_DOES_NOT_EXIST = -2000

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['-creationDate']
        verbose_name = _('channel')
        verbose_name_plural = _('channels')
        permissions = ( ("can_manage", "Can manage"), )

    @staticmethod
    def create_one(text, channel_name, account, activationDate, deactivationDate = None):
        """
            Send a sms to a channel
        """

        # Check if channel_name exist
        try:
            channel = Channel.objects.get (name = channel_name)
        except Channel.DoesNotExist:
            return Channel.CHANNEL_DOES_NOT_EXIST

        # Check if we have enough credits and reserve it
        try:
            account.check_credit(True, channel.subscriber_set.count())
        except OutOfCredit:
            return ACCOUNT_NO_CREDIT

        # Check if account can send messages to channel_name
        b = Body(plainTxt=text, mms=False, encodedMsg=text)
        b.save ()
        m = Message(body=b, activationDate=activationDate, account=account, deactivationDate=deactivationDate)
        m.save ()
        cm = ChannelMessage (message = m, channel = channel)
        cm.save()

        return cm.id

class Subscriber(models.Model):
    """
        Mobile number of a person subscribed to the platform
    """
    mobile = models.CharField(verbose_name = _('mobile phone'), max_length=15, blank=False, unique=True)
    name = models.CharField(verbose_name = _('name'), max_length = 255, blank = True, null = True)
    creationDate = models.DateTimeField(verbose_name = _('creation date'), auto_now_add = True, blank = False)
    channels = models.ManyToManyField(Channel, verbose_name = _('channels'))

    def __unicode__(self):
        return self.mobile

    class Meta:
        verbose_name = _('subscriber')
        verbose_name_plural = _('subscribers')

    @staticmethod
    def create(mobile, channel_id, name):
        mob = adapt_mobile(mobile)
        item, created = Subscriber.objects.get_or_create(mobile = mob)
        item.name = name
        item.save()
        ch = Channel.objects.get(pk = channel_id)
        if ch not in item.channels.all():
            item.channels.add(ch)
            item.save()
        post_save.send(sender=Subscriber, instance=item)
        return created

def save_subsc_handler(sender, **kwargs):
    return sub_handler(sender, 
                       lambda u: u + 1,
                       "Instance error in subscriber save signal",
                       **kwargs)

def del_subsc_handler(sender, **kwargs):
    return sub_handler(sender, 
                       lambda u: u - 1,
                       "Instance error in subscriber del signal",
                       **kwargs)

def sub_handler(sender, function, msg, **kwargs):
    ch_id_list = []
    chmsg_list = []
    subsc = None
    try:
        subsc = kwargs['instance']
    except KeyError:
        _logger.error("Error while try to get a Subscriber instance")
        return
    # Subscriber's channels id list
    try:
        for ch in subsc.channels.values():
            ch_id_list.append(ch['id'])
    except AttributeError:
        _logger.error(msg)
        return    

    # Check each subscriber's channel if there is any unprocessed msg
    for ch in Channel.objects.filter(id__in = ch_id_list):
        for chmsg in ch.channelmessage_set.all():
            if not chmsg.message.processed:
                # Looking for a positive purchase
                for p in chmsg.message.account.purchase_set.all():
                    if p.real_credit() > 0:
                        p.reserved = function(p.reserved)
                        p.save()
                        break    

post_save.connect(save_subsc_handler, sender=Subscriber)
pre_delete.connect(del_subsc_handler, sender=Subscriber)

class MessageBase (models.Model):
    """
        The content of a message (previous form of a SMS)
    """
    processed = models.BooleanField(verbose_name=_('processed'), blank = False, default = False)
    body = models.ForeignKey('Body', verbose_name=_('body'), blank = False, null = False)
    creationDate = models.DateTimeField(verbose_name=_('creation date'), auto_now_add = True, blank = False)

    class Meta:
            abstract = True

class Message (MessageBase):
    """
        The content of a message (previous form of a SMS)
    """
    activationDate = models.DateTimeField(verbose_name=_('activation date'), blank = False)
    deactivationDate = models.DateTimeField(verbose_name=_('deactivation date'), blank = True, null = True)
    firstSentDate = models.DateTimeField(verbose_name=_('first sent date'), blank = True, null = True)
    lastSentDate = models.DateTimeField(verbose_name=_('last sent date'), blank = True, null = True)
    account = models.ForeignKey(Account, verbose_name=_('account'))
    mobile = models.CharField(verbose_name = _('mobile phone'), max_length = 15, blank = True, null = True)
    repliable = models.BooleanField(verbose_name = _('Is this message repliable?'), default=False)

    def __unicode__(self):
         return _("%(body)s (m:%(mobile)s)") % {'body':self.body, 'mobile':self.mobile}

    # Return number of message channel subscriptors
    def num_of_phones(self):
        return self.channelmessage_set.all()[0].channel.subscriber_set.all().count()

    # Return message channel
    def get_channel(self):
        return self.channelmessage_set.all()[0].channel.name

    # Return msg error from SMSHistory related objects
    def get_error(self):
        history = self.smshistory_set.all().order_by("-sentDate")
        if history:
            return history[0].status_info
        return "Status msg not found, please contact SingularMS admin"

    # Return phone number in spanish format
    # otherwise return in current format
    def mobile_formated(self):
        if not self.mobile.find("+34"):
            return self.mobile[3:]
        return self.mobile
    
    def response_left(self):
        return self.responsemessage_set.filter(read = False).count()

    def response_messages(self):
        return self.responsemessage_set.all().order_by('receivedDate')

    def put_in_the_queue (self):
        """
            This function doesn't check all requirements (Balance, Permissions) before send message
        """
        
        list_ids = []
        if self.mobile:
            mq = SMSQueue(message=self, mobile=self.mobile, priority=1, queueDate=datetime.datetime.now())
            mq.save()
            list_ids.append("%(id)s" % {'id': mq.get_id()})
        else:
            # Channel message
            try:
                suscribers = []
                for chmsg in self.channelmessage_set.all():
                    for suscriber in chmsg.channel.subscriber_set.all():
                        mq = SMSQueue(message=self, mobile=suscriber.mobile, priority=0, queueDate=datetime.datetime.now())
                        mq.save()
                        list_ids.append("%(id)s" % {'id': mq.get_id()})
        
            except IndexError:
                _logger.error("This is not a channel message or the channel has not subscribers")
                return []

        # Dont check this message anymore
        self.processed = True
        self.save()
        return list_ids

    class Meta:
        # First older messages
        ordering = ['-creationDate']
        verbose_name = _('message')
        verbose_name_plural = _('messages')

    @staticmethod
    def create_one (text, mobile, activationDate, account, body_id = -1, deactivationDate = None):
        """
            Create one message and left it waiting to be enqueued by the daemon.
        """

        try:
            account.check_credit(True)
        except OutOfCredit:
            return ACCOUNT_NO_CREDIT

        if body_id == -1 :
            # Individual message
            b = Body(plainTxt=text, mms=False, encodedMsg=text)
            try:
                b.save ()
            except IntegrityError:
                return MALFORMED_SMS_BODY
        else:
            # Channel message
            try:
                b = Body.objects.get(id = body_id)
            except Body.DoesNotExist:
                return SMS_BODY_NOT_FOUND
            
        m = Message(body=b, mobile=mobile, activationDate=activationDate,
            account=account, deactivationDate=deactivationDate)
        m.save()
        return m.id

    @staticmethod
    def easy_create(text, mobile, user):
        accounts = []
        try:
            accounts = user.customer.account_set.all()
        except Customer.DoesNotExist:
            if user.is_superuser:
                accounts = Account.objects.all()
        if not accounts:
            return _(u"Sorry, you don't have any related account, you can't send sms.")
        for acc in accounts:
            if acc.get_real_credit():
                d = datetime.datetime.now()
                Message.create_one(text, mobile, d, acc)
                return _(u"Message sent successfully")
        return _(u"Sorry, you don't have enough credit to send sms.")
                
    
    # Check if a message can be deleted. A message can be deleted if:
    #   - Is not processed yet
    #   - Is processed, but it is in the SMSQueue yet
    def can_be_del(self):
        """
            Check if a message can be deleted
        """
        if not self.processed:
            return True
        return False

    def status(self):
        msg = SMSHistory.objects.filter(message = self).order_by('-sentDate')
        if not msg:
            return 0, None
        if not self.channelmessage_set.count():
            return msg[0].local_status, msg[0].server_status
        sent = fail = 0
        for m in msg:
            if FAIL_STATUS == m.local_status or FAIL_STATUS == m.server_status:
                fail += 1
            elif SENT_STATUS == m.server_status:
                sent += 1
        return 0, "Sent(%d)  Fail(%d)" % (sent, fail)           
        
def del_msg_handler(sender, **kwargs):
    msg = None
    try:
        msg = kwargs['instance']
    except KeyError:
        _logger.error("No instance while trying to delete it")
        return
    
    if msg.mobile:
        for p in msg.account.purchase_set.all():
            if p.reserved > 0:
                p.reserved -= 1
                p.save()
                break
    else:
        s = 0
        try:
            chmsg = msg.channelmessage_set.all()[0]
            suscribers = chmsg.channel.subscriber_set.all()
            s = suscribers.count()
            chmsg.delete()
        except IndexError:
            _logger.error("This is not a channel message or channel doesnt have any subscribers")
        if s:
            for p in msg.account.purchase_set.all():
                if p.reserved >= s:
                    p.reserved -= s
                    p.save()
                    break
                elif p.reserved > 0:
                    s -= p.reserved
                    p.reserved = 0
                    if s == 0:
                        break                

pre_delete.connect(del_msg_handler, sender=Message)

class ResponseMessage(models.Model):
    """
        A message response
    """
    
    message = models.ForeignKey(Message, null = True)
    receivedDate = models.DateTimeField(verbose_name=_(u'Received date'))
    body = models.CharField(verbose_name=_(u'Body text'), max_length=160)
    server_id = models.CharField(verbose_name = _(u'Server id'), max_length=255)
    read = models.BooleanField(default = False, verbose_name = _(u'Already read'))

    @staticmethod
    def create_one(message, body, receivedDate, server_id):
        item, created = ResponseMessage.objects.get_or_create(message = message, body = body, receivedDate = receivedDate, server_id = server_id)
        item.save()
        return item

    def __unicode__(self):
        return u"%s" % self.body

    class Meta:
        verbose_name = _('Response Message')
        verbose_name_plural = _('Response Messages')

class SMSHistory (models.Model):
    """
        A message history from a processed message
    """

    message = models.ForeignKey(Message, blank = False, null = False)
    mobile = models.CharField(verbose_name = _('mobile phone'), max_length = 15, blank = False)
    priority = models.IntegerField(verbose_name = _('priority'), blank = False, choices = LOGPRIO_LIST)

    sentDate = models.DateTimeField(verbose_name = _('sent date'), blank = True, null = True)
    local_status = models.IntegerField(verbose_name = _('Msg status on local'), blank = False, choices = STATUS_CHOICES, default = NONE)
    server_status = models.IntegerField(verbose_name = _('Msg status on server'), blank = False, choices = STATUS_CHOICES, default = NONE)
    status_info = models.CharField(verbose_name = _('Status information'), max_length = 255, blank = True)

    local_id = models.CharField(verbose_name = _('local message id'), max_length = 255)
    remote_id= models.CharField(verbose_name = _('remote message id'), max_length = 255)

    def __unicode__(self):
        return _("%(message)s to %(mobile)s") % {'message':self.message, 'mobile':self.mobile}

    class Meta:
        verbose_name = _('SMS History')
        verbose_name_plural = _('SMS Histories')

    @staticmethod
    def check_id (customer, id):
        """
            Get a status information, by a tuple [STATUS (normalized), INFO] for a single SMS, or
            [ Nº SENT SMS, Nº FAIL SMS] for a channel SMS
        """
        # TODO:check if the customer is valid
        h = SMSHistory.objects.filter(
                local_id__startswith="%(id)s_" % {'id': id},
                message__account__in=customer.account_set.all()
            ).order_by('-sentDate')
        if not h:
            return []
        if h.values_list('mobile').distinct().count() == 1:
            if h[0].local_status == SENT_STATUS:
                return [h[0].server_status, h[0].status_info]
            return [h[0].local_status, h[0].status_info]
        else:
            sent = fail = 0
            for m in h:
                if FAIL_STATUS == m.local_status or FAIL_STATUS == m.server_status:
                    fail += 1
                elif SENT_STATUS == m.server_status:
                    sent += 1
            return ["%d" % sent, "%d" % fail] 
            

class SMSQueue (models.Model):
    """
        A message which has been enqueued
    """
    message = models.ForeignKey(Message, blank = False, null = False)
    mobile = models.CharField(verbose_name = _('mobile phone'), max_length = 15, blank = False)
    priority = models.IntegerField(verbose_name=_('priority'), blank = False, choices = LOGPRIO_LIST)
    queueDate = models.DateTimeField(verbose_name=_('queue date'), blank = False, null = True)
    processedDate = models.DateTimeField(verbose_name=_('processed date'), blank = True, null = True)
    nextProcDate = models.DateTimeField(verbose_name =_('Next processed date'), blank = True, null = True)

    def get_id(self):
        return "%(messageId)d_%(id)d" % {'messageId': self.message.id, 'id': self.id}

    def __unicode__(self):
        return _("%(message)s to %(mobile)s") % {'message':self.message, 'mobile':self.mobile}

    class Meta:
        # First more priority SMSs
        ordering = ['priority', '-queueDate']
        verbose_name = _('SMS enqueued')
        verbose_name_plural = _('SMS enqueued')

class ChannelMessage (models.Model):
    """
        A message sent to a channel
    """
    message = models.ForeignKey(Message, verbose_name = _('message'), blank = False, null = False)
    channel = models.ForeignKey(Channel, verbose_name = _('channel'), blank = False, null = False)

    def __unicode__(self):
        return _("%(message)s into %(channel)s") % {'message':self.message, 'channel':self.channel}

    class Meta:
        verbose_name = _('channel message')
        verbose_name_plural = _('channel messages')
    
     
    def can_be_del(self):
        """
            heck if a channelmessage can be deleted
        """
        return self.message.can_be_del()

    def status(self):
        return SENT_STATUS

