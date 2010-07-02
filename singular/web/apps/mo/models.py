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
from django.db.models import signals, Q

from accounting.models import Customer, Account 
from smlog.models import LOGPRIO_LIST 
from mt.models import MONTHS_OPTIONS, Message
from mt.models import MessageBase, Body, Channel, Subscriber
from django.db.models.signals import post_save, pre_delete, post_delete
from django.core.mail import send_mail
from django.conf import settings
from suds.client import Client

import datetime
import string
import logging

log = logging.getLogger('singularms')

ADMIN_COMMAND_LIST_CHOICES = (
    (1, 'join'),   
    (2, 'leave'),  
    (3, 'info')   
)

ADMIN_COMMAND_TRANSLATION = {
                             'es': {'join': 'alta', 'leave': 'baja', 'info': 'info'}                             
                             }

EXTERNAL_COMMAND_TYPE_LIST = (
    (1, _('Web Service')),
    (2, _('HTTP get')),
)

REPLY    = 1
ADMIN    = 2
EXTERNAL = 3

COMMAND_TYPE_LIST = (
    (REPLY, 'reply'),
    (ADMIN, 'admin'),
    (EXTERNAL, 'external'),
)

PRIORITY_LIST = (
    (0, 'Low'),
    (1, 'Medium'),
    (2, 'High'),
    (3, 'Now!'),
)

COMMAND_SUCCESSFUL = _("ALL OK")

HELP_DATES = str(_('Format is ') ) + str(_('YYYY-MM-DD HH:MM:SS') )

def getNameFromTuple(tuple, index):
    """
        Given a number from a list of tuples, get the name associated to such number
        Useful for choice list's tuples.
    """
    for row in tuple:
        if row[0] is index:
            return row[1]
    else:
        return None

def getDefaultDeactivationDate():
    return datetime.datetime.now() + datetime.timedelta(weeks=8)

class IncomingMessage(MessageBase):
    """
        The content of a message (previous form of a SMS)
    """
    receivedDate = models.DateTimeField(verbose_name=_(u'Received date'))
    processedDate = models.DateTimeField(verbose_name=_('Processed date'), blank=True, null=True)    
    mobile = models.CharField(verbose_name = _('Mobile phone'), max_length = 15, blank=True, null=True)
    account = models.ForeignKey(Account, verbose_name=_('Account'))

    def __unicode__(self):
         return _("%(body)s (m:%(mobile)s)") % {'body':self.body, 'mobile':self.mobile}

    class Meta:
        # First older messages
        ordering = ['-creationDate']
        verbose_name = _('incoming message')
        verbose_name_plural = _('incoming messages')

    @staticmethod
    def create_one (mobile, text, date, account, body = None):
        """
            Create one message and left it waiting to be processed by the daemon
        """
        if not body:
            body = Body(plainTxt=text, mms=False, encodedMsg=text)
            body.save ()
        m = IncomingMessage(body=body, mobile=mobile, account=account, receivedDate = date, creationDate = datetime.datetime.now())
        m.save()
        return m

    def process(self):
        cmd = Command.get_command(self.body.plainTxt)
        if cmd:
            [cmd, args] = cmd
            text = cmd.process(self.mobile,args)
            self.processedDate = datetime.datetime.now()
            self.processed = True
            self.save()
            return text, cmd
        self.processed = True
        self.save()
        response = self.account.args()['response'] if 'response' in self.account.args() else settings.FROM_EMAIL_ADDRESS
        if settings.WRONG_INCOMMING_MESSAGE_EMAIL:
            send_mail(
                _('Wrong incomming message from: %s' % self.mobile),
                _('%(mobile)s: %(full)s' % {'mobile': self.mobile, 'full': self.body.plainTxt}),
                settings.FROM_EMAIL_ADDRESS,
                [response],
                fail_silently=True)
        # Not command found o more than one command found
        error_msg = "%s not matched with commands" % self.body.plainTxt
        return None, error_msg
        
 
class Command (models.Model):
    """
        A command in the platform
    """
    pattern = models.CharField (verbose_name = _('pattern'), max_length=160, blank=False, unique=True)
    type = models.IntegerField(verbose_name=_('type'), blank=False, choices=COMMAND_TYPE_LIST)
    active = models.BooleanField(verbose_name= _('active'), blank=False, default=True)
    creationDate = models.DateTimeField(verbose_name= _('creation date'), auto_now_add=True, blank=False)
    activationDate = models.DateTimeField(verbose_name=_('activation date'), default=datetime.datetime.now,
                                          blank=False, help_text=HELP_DATES )
    
    deactivationDate = models.DateTimeField(verbose_name=_('deactivation date'), blank=True, null=True, 
                                            default=getDefaultDeactivationDate,
                                             help_text=HELP_DATES )
    
    defaultAnswer = models.ForeignKey(Body, blank=True, null=True, verbose_name = _('default answer') )
    account = models.ForeignKey(Account, verbose_name=_('account') )
    priority = models.IntegerField(_('priority'), blank=False, choices=PRIORITY_LIST)
    
    default_fields = ('pattern', 'type',  'defaultAnswer', 'activationDate', 'deactivationDate')
    
    class Meta:
        verbose_name = _('base command')
        verbose_name_plural = _('base commands')
    
    def __unicode__(self):
         return "<%(pattern)s>" % {'pattern':self.pattern}

    def prepare_args(self, args):
        out = args
        for p in self.pattern.split():
            out = out.replace(p, '')
        return out.strip()

    @staticmethod
    def search(search, instant = None):
        """
            Search a given pattern in the command list.
        """
        if not instant:
            instant = datetime.datetime.now
        return Command.objects.filter(pattern__istartswith = search, activationDate__lt = instant,
                                   deactivationDate__gt = instant)
    
    def get_foreign_cmd(self, opt, instant = None):
        if not instant:
            instant = datetime.datetime.now
        if opt == REPLY:
            return self.replycommand_set.filter(Q(startTime__lt = instant) & 
                                   ( Q(endTime__gt = instant) | Q(endTime__isnull = True) )
                                   )[0]
        elif opt == ADMIN:
            return self.admincommand_set.all()[0]
        elif opt == EXTERNAL:
            return self.externalcommand_set.all()[0]
        return None

    @staticmethod
    def get_command(pattern):
        """
            Search for a command parsing the pattern.
        """
        if not pattern:
            return None
        args = None
        try:
            s1, args = pattern.split(" ", 1)
        except ValueError:
            s1 = pattern
        search = s1
        cmd = Command.search(search)
        if not cmd.count():
            log.info("El texto %s no casa con ningun comando", pattern)
            return None
        elif cmd.count() == 1:
            return cmd[0].get_foreign_cmd(cmd[0].type), cmd[0].prepare_args(args)
        else:
            try:
                s1,s2,args = pattern.split(" ",2)
            except ValueError:
                s1,s2 = pattern.split(" ",2)
            search = string.join([s1,s2])
            cmd = Command.search(search)
            if not cmd.count():
                log.info("El texto %s no casa con ningun comando", pattern)
                return None
            elif cmd.count() == 1:
                return cmd[0].get_foreign_cmd(cmd[0].type), cmd[0].prepare_args(args)
            else:
                try:
                    s1,s2,s3,args = pattern.split(" ",3)
                except ValueError:
                    s1,s2,s3 = pattern.split(" ",3)
                search = string.join([s1,s2,s3])
                cmd = Command.search(search)
                if cmd.count() == 1:
                    return cmd[0].get_foreign_cmd(cmd[0].type), comd[0].prepare_args(args)
                log.info("El texto %s no casa con ningun comando", pattern)
        return None
    
class AdminCommand (models.Model):
    """
        Used primarily for handling phone numbers into channels
    """
    command = models.ForeignKey('Command', verbose_name= _('command'), blank = False, null = False)    
    action = models.IntegerField(verbose_name=_('action'), blank=False, choices=ADMIN_COMMAND_LIST_CHOICES)
    channel = models.ForeignKey(Channel, verbose_name= _('channel'), blank=True, null=True)
    
    CHANNEL_DOESNT_EXIST    = _("CHANNEL DOESNT EXIST")
    CHANNEL_NOT_DEFINED    = _("CHANNEL NOT DEFINED")
    ACTION_NOT_DEFINED      = _("ACTION NOT DEFINED")
    SUBSCRIBER_ALREADY_EXISTS   = _("SUBSCRIBER ALREADY EXITS")
    SUBSCRIBER_DOESNT_EXISTS    = _("SUBSCRIBER DOESNT EXIST")
    
    channelObj = None

    class Meta:
        verbose_name = _('admin command')
        verbose_name_plural = _('admin commands')
        
    def process(self, mobile, args = None):        
        if not self.channel:
            return self.CHANNEL_NOT_DEFINED
        try:
            self.channelObj = Channel.objects.get(pk=self.channel.id)
        except Channel.DoesNotExist:
            return self.CHANNEL_DOESNT_EXIST
        
        GET_FUNCTION_FROM_TYPE = {1: self.doJoin, 2: self.doLeave, 3: self.doInfo}
        try:
            function = GET_FUNCTION_FROM_TYPE[self.action]            
        except KeyError:
            return ACTION_NOT_DEFINED
        return function(mobile, self.channelObj)
    
    def getSubscriber(self, mobile):
        try:
            subscriber = Subscriber.objects.get(mobile=mobile)
        except Subscriber.DoesNotExist:
            subscriber = Subscriber(mobile=mobile)
            subscriber.save()
        return subscriber        
    
    def doLeave(self, mobile, channel_id):
        subscriber = self.getSubscriber(mobile)
        subscriber.channels.remove(self.channelObj)
        subscriber.save()
        return _("LEAVING %s") % self.channel.name
    
    def doJoin(self, mobile, channel_id):
        subscriber = self.getSubscriber(mobile)
        subscriber.channels.add(self.channelObj)
        subscriber.save()        
        signals.post_save.send(sender=Subscriber, instance=subscriber)
        return _("JOINING %s") %self.channel.name
    
    def doInfo(self, mobile, *args):
        body_id = self.command.defaultAnswer.id        
        # Channel means body_id. Would be wise to change it.
        Message.create_one('', mobile, datetime.datetime.now(), self.command.account, body_id=body_id)
        # create_one doesnt return any values.
        return _("INFO %s") % self.channel.name

def del_admin_cmd_handler(sender, **kwargs):
    """
        Post delete Admin Command signal, delete the linked command
    """
    admin = None
    try:
        admin = kwargs['instance']
    except KeyError:
        return
    try:
        cmd = admin.command
    except Command.DoesNotExist:
        return
    cmd.delete() 

post_delete.connect(del_admin_cmd_handler, sender=AdminCommand)

class ReplyCommand (models.Model):
    """
        For a pattern in a incoming message, a sms is sent
    """
    command = models.ForeignKey('Command', verbose_name= _('command'), blank = False, null = False)
    startTime = models.DateTimeField(verbose_name=_('start date'), default=datetime.datetime.now,
                                          blank = False, help_text=HELP_DATES )
    endTime = models.DateTimeField(verbose_name=_('end date'), blank = True, null = True,
                                   default=getDefaultDeactivationDate)
    answer = models.ForeignKey(Body, blank = False, verbose_name = _('answer') )
    
    default_fields = ('command', 'answer', 'startTime', 'endTime')

    class Meta:
        verbose_name = _('reply command')
        verbose_name_plural = _('reply commands')
        unique_together = ['id', 'answer']
    
    def process(self, mobile, args = None):
        if self.answer and self.answer.plainTxt:
            return str(self.answer.plainTxt)
        return _("RECEIVED OK")

def del_reply_cmd_handler(sender, **kwargs):
    """
        Post delete Reply Command signal, delete the linked command
        if it is posible (if there is only one reply command left)
    """
    reply = None
    try:
        reply = kwargs['instance']
    except KeyError:
        return
    try:
        cmd = reply.command
    except Command.DoesNotExist:
        return
    # If there is only one ReplyCommand left, delete his Command
    if cmd.replycommand_set.all().count() < 1:
        cmd.delete() 

post_delete.connect(del_reply_cmd_handler, sender=ReplyCommand)

class ExternalCommand (models.Model):
    """
        An external command in the platform
    """
    command = models.ForeignKey('Command', verbose_name= _('command'), blank = False, null = False)
    email = models.EmailField (verbose_name = _('admin\'s email'), blank = False)
    type = models.IntegerField(verbose_name=_('type'), blank = False, choices = EXTERNAL_COMMAND_TYPE_LIST)
    username = models.CharField (verbose_name = _('user name'), max_length = 255, blank = True)
    password = models.CharField (verbose_name = _('password'), max_length = 255, blank = True)
    url = models.URLField (verbose_name = _('url'), null = False)

    default_fields = ('command', 'email', 'url') 
    
    class Meta:
        verbose_name = _('external command')
        verbose_name_plural = _('external commands')

    def process(self, mobile, text = None):
        try:
            client = Client(self.url)
        except Exception, e:
            log.error("Error en el proceso del webservice %s en el servidor %s", self.command, self.url)
            return "ERROR IN WEBSERVICE"
        if client:
            for s in self.servicecore_set.all():
                msg = "client.service." + s.serv_name + "("
                if text:
                    kwargs = text.split()
                    kwargs.reverse()
                args_left = False
                for arg in s.servicearg_set.all():
                    if len(arg.content) > 0:
                        msg += arg.name + "='" + arg.content + "',"
                    else:
                        if len(kwargs) > 0:
                            msg += arg.name + "='" + kwargs.pop() + "',"
                        else:
                            args_left = True
                msg = msg[0:len(msg)-1] + " )"
                if args_left:
                    log.error("There are arguments left in %s service on %s server.", s.serv_name, self.url) 
                    return "THERE ARE ARGUMENTS LEFT"
                try:
                    log.info("External command: %s", msg)
                    a = eval(msg)
                    return str(a)[:160]
                except TypeError:
                    return "ERROR WHILE EXECUTING SERVICE %s ON SERVER" %s.serv_name
                return "WRONG SMS"
            log.error("Service doesnt not exist on %s server.", self.url)
            return "NOT SERVICES FOUND"
        else:
            return "SERVER NOT WORKING"
            
def del_ext_cmd_handler(sender, **kwargs):
    """
        Post delete External Command signal, delete the linked command
    """
    ext = None
    try:
        ext = kwargs['instance']
    except KeyError:
        return
    try:
        cmd = ext.command
    except Command.DoesNotExist:
        return
    cmd.delete() 

post_delete.connect(del_ext_cmd_handler, sender=ExternalCommand)

class ServiceCore (models.Model):
    """
        Service linked to an external commmand
    """
    ext_comm = models.ForeignKey('ExternalCommand', verbose_name= _('external command'), blank = False, null = False)
    serv_name = models.CharField(verbose_name = _('service name'), max_length = 255, blank = False, null = False)
    
    class Meta:
        verbose_name = _('service core')
        verbose_name_plural = _('service cores')

class ServiceArg (models.Model):
    """
        Arguments of a service
    """
    name = models.CharField(verbose_name = _('name'), max_length = 255, blank = False, null = False)
    type = models.CharField(verbose_name = _('type'), max_length = 255, blank = False, null = False)
    content = models.CharField(verbose_name = _('content'), max_length = 255, null = True, blank = True)
    service = models.ForeignKey('ServiceCore', verbose_name = _('service'), null = False)

    class Meta:
        verbose_name = _('service argument')
        verbose_name_plural = _('service arguments')

class CommandStats (models.Model):
    """
        Statistics for a command
    """
    command = models.ForeignKey('Command', verbose_name= _('command'), blank = False, null = False)
    numRecvd = models.PositiveIntegerField(verbose_name = _('no. recvd SMS\'s'), blank = False, default = 0)
    month = models.IntegerField(verbose_name = _('month'), choices = MONTHS_OPTIONS, blank = False)
    year = models.PositiveIntegerField(verbose_name = _('year'), blank = False)

    class Meta:
        ordering = ['-year', '-month']
        verbose_name = _('command stat')
        verbose_name_plural = _('command stats')
