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

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.contrib.auth.decorators import user_passes_test
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from mt.singular_exceptions import *

import types
import datetime
import logging

from sem_utils import Sem
from signal_handlers import save_purchase_handler
from django.core.mail import send_mail

log = logging.getLogger('galotecnia')

DUMMY = 0
BULKSMS = 1
CANARYSOFT = 2
SMSTOOLS = 3
LLEIDA = 4
SINGULAR = 5

# This must be sync with singularms/daemon/singularmsd.py 
BACKEND_LIST = (
    (DUMMY, 'Dummy'),
    (BULKSMS, 'BulkSMS'),
    (CANARYSOFT, 'Canarysoft'),
    (SMSTOOLS, 'SmsTools'),
    (LLEIDA, 'Lleida.net'),
    (SINGULAR, 'Singular'),
)

# Mensaje enviado correctamente
SENT_STATUS = 1
# Error definitivo
FAIL_STATUS = 2
# Error temporal
PROCESSING_STATUS = 3
# NO estado
NONE_STATUS = 0

def getDefaultFutureDate():
    return datetime.date.today() + datetime.timedelta(weeks=8)

dateformat_help = _('Format is YYYY-MM-DD')

def checkAdmin(user):
    if not user:
        return False
    try:
        if user.is_superuser:
            return True
    except AttributeError:
        return False
    if user.username == '':
        return False
    try:
        Provider.objects.get(username=user.username)
        return True
    except Provider.DoesNotExist:
        return False
    
def checkCustomer(user):
    if checkAdmin(user):
        return True
    try:
        Customer.objects.get(username=user.username)
        return True
    except Customer.DoesNotExist:
        return False

def checkChannelAdmin(user):
    if checkAdmin(user):
        return True
    try:
        if user.has_perm('mt.can_manage'):
            return True
    except AttributeError:
        pass
    return False    	
	
# Decorators:           
admin_required = user_passes_test(checkAdmin)
admin_required.__doc__ = (
	"""
		Checks if the user is an admin == provider
	"""
	)

customer_required = user_passes_test(checkCustomer)
customer_required.__doc__ = (
    """
        Checks if the user is an customer
    """
    )

channel_admin_required = user_passes_test(checkChannelAdmin)
channel_admin_required.__doc__ = (
	"""
		Check if the user is an channel admin
	"""
	)

class Capabilities(models.Model):
    """
        Types of messages
    """
    typeSMS = models.CharField(verbose_name = _('Sms type'), max_length = 255, blank = False)    
    class Meta:
        verbose_name = _('Capabality')
        verbose_name_plural = _('Capabalities')
        
    def __unicode__(self):
        return self.typeSMS

class Provider(User):
    """
        A system user who resells messaging service to Customers
    """
    class Meta:
        verbose_name = _('Provider')
        verbose_name_plural = _('Providers')
    
    def __unicode__(self):
        return _("%(name)s") % {'name': self.username}
    
class Access(models.Model):
    """
        Backends which providers have for sending messages
    """
    provider = models.ForeignKey(Provider, related_name="Provider", verbose_name=_('provider') )
    name = models.CharField(_('name'), unique=True, max_length=40)
    description = models.CharField(_('description'), max_length=150)
    backend = models.IntegerField(_('backend'), blank=False, choices=BACKEND_LIST)
    args1 = models.CharField(_('access arguments'), max_length=100, blank = True)
    capabilities = models.ManyToManyField(Capabilities, related_name= "Capabilities",
                                          verbose_name= _('capabilities'), blank= False)
    

    def __unicode__(self):
        return _("%(name)s: %(provider)s --> %(backend)s") % {'name':self.name, 
                                               'provider':self.provider, 
                                               'backend':BACKEND_LIST[self.backend][1] }

    class Meta:
        verbose_name = _('Access')
        verbose_name_plural = _('Accesses') 

    def args(self):
        try:
            d = dict([(arg.split('=')[0],arg.split('=')[1]) for arg in self.args1.split(';')])
            return d
        except IndexError:
            return {}

class Customer(User):
    """
        A system user who uses the services of a provider (or several providers)
    """
    providers = models.ManyToManyField(Provider, related_name="Providers", 
                                       verbose_name=_('providers'), blank=False)    
    
    WRONG_USERNAME_OR_PASSWORD = -100
    WRONG_ACCOUNT = -200
    
    default_fields = ('username', 'last_login')

    def __unicode__(self):
        return _("%(username)s") % {'username':self.username}

    class Meta:
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')

    def get_accounts (self):
        """
            Get all accounts for this custommer
        """
        return self.account_set.all ()

    def get_channels (self):
        """
            Get all channels for this custommer
        """
        return self.channel_set.all ()

    @staticmethod
    def check_customer_and_credit(username, password, account, messageno = 1):
        """
            Check if the username and password are valid and if the account is related
            to the username and there is credit available to send messageno messages
        """
        customer = Customer.get_customer(username, password)
        if customer < 0:
            return customer

        try:
            account = Account.objects.get(name=account, customer=customer)
        except Account.DoesNotExist:
            return Customer.WRONG_ACCOUNT

        account.check_credit(False, messageno)
        return account

    @staticmethod
    def get_customer (username, password):
        """
            Get a valid customer.
        """       
        try:
            customer = Customer.objects.get(username=username)
            
        except Customer.DoesNotExist:           
            return Customer.WRONG_USERNAME_OR_PASSWORD

        if not customer.check_password(password):
            return Customer.WRONG_USERNAME_OR_PASSWORD
           
        return customer
              
    @staticmethod
    def can_send_to_channel( customer, channel ):
     	"""
    		Does this customer have this channel?
    	"""             
        if not customer:
            return False
        if checkAdmin(customer):
            return True
        chnlist = customer.channel_set.filter( name = channel )
        for item in chnlist:
        	if item.name in channel:
        		return True
        	
        return False                     
        
class Account(models.Model):
    """
        A Provider gives access at his backends to the Customer 

    """
    customer = models.ForeignKey(Customer, verbose_name=_('customer'))
    name = models.CharField(_('account name'), max_length=40, unique=True)
    access = models.ForeignKey(Access, verbose_name=_('access'))
    args2 = models.CharField(_('account arguments'), max_length=100, default='sender=singularms', blank = True)
    num_threads = models.PositiveIntegerField(_('number of threads'), default=1)

    def args(self):
        out = {}
        if self.access.args1:
            for kv in self.access.args1.split(';'): # whatever=whatever
                (k, v) = kv.split("=")
                out[k] = v
        if self.args2:
            for kv in self.args2.split(';'): # username=username;password=password
                (k, v) = kv.split("=")
                out[k] = v
        return out

    def __unicode__(self):
        return "%(name)s" % {'name':self.name}

    class Meta:
        verbose_name = _('Account')
        verbose_name_plural = _('Accounts')
        unique_together = ['customer', 'name']

    def get_statistics(self, inicio, fin):
        """
            Returns the statistics for an account to draw
            graphs on the Home screen SingularMS. Format:
            ('Name': Name of account
              # List of values to display on the graphics, the fields are displayed
              # Individual messages and channel, as well as total messages sent,
              # Those who have been sent successfully and which have failed at some point
              'Ind', 'can', 'tot', 'env', 'false': [[Day 1, value1], [Day2, value2], ...]
              # Global statistics of all time
              'Individual', 'channel', 'total', 'sent', 'failed': total_value

        """
        today = datetime.date.today()
        actual = inicio
        # Return values dict
        out = {'ind':[], 'can':[], 'tot':[], 'env':[], 'fal':[], 'name': self.name, 
               'totales': 0, 'enviados': 0, 'fallidos': 0, 'individuales': 0, 'canal': 0 }
        # Shorts keys to long keys dict
        xchg = {'ind':'individuales', 'tot': 'totales', 'env': 'enviados', 'can': 'canal', 'fal': 'fallidos'}
        while actual <= fin and actual <= today:
            sum = {'ind':0, 'can':0, 'tot':0, 'env':0, 'fal':0} # Days statistics counter
            dia = int(actual.strftime('%s') + '000')
            filter = {'lastSentDate__day': actual.day, 'lastSentDate__month': actual.month, 'lastSentDate__year': actual.year}
            mlist = self.message_set.filter(lastSentDate__day = actual.day, lastSentDate__month = actual.month, lastSentDate__year = actual.year)
            sum['can'] = mlist.filter(mobile = '').count()
            sum['ind'] = mlist.count() - sum['can']
            for m in mlist:
                hlist = m.smshistory_set.filter(sentDate__day = actual.day, sentDate__month = actual.month, sentDate__year = actual.year)
                sum['tot'] += hlist.count()
                sum['env'] += hlist.filter(server_status = SENT_STATUS).count()
                sum['fal'] += hlist.filter(models.Q(local_status = FAIL_STATUS) | models.Q(server_status = FAIL_STATUS)).count()
            for k,v in sum.items():
                out[k].append([dia, v]) # Saving days statistics
                out[xchg[k]] += v # Adding to total statistics
            actual += datetime.timedelta(1)
        # Finally insert a special day with 0 for the correct statistics displayed in the graphs of the previous days
        for k in xchg:
            out[k].append([int(actual.strftime('%s') + '000'), 0])
        return out

    def get_real_credit(self):
        """
            Get the credit of an account.
        """
        real_credit = 0
        for p in self.purchase_set.filter(available__gt = 0):
            real_credit += p.real_credit()
        log.debug("Real credit for account %d: %d", self.id, real_credit)
        return real_credit            
 
    def get_real_reserved(self):
        """
            Get reserved credit for an account
        """
        real_reserved = 0
        for p in self.purchase_set.filter(reserved__gt = 0):
            real_reserved += p.reserved
        return real_reserved

    def get_available_credit(self):
        """
            Get available credit of an account at the moment
        """
        available_credit = 0
        for p in self.purchase_set.filter(available__gt = 0):
            available_credit += p.available
        return available_credit            

    def check_credit(self, reserve = False, num_msgs = 1):
        #
        # Checks if there are enough credit to send the number of messages specified 
        # in the num_msgs argument
        #
        sem = Sem("singular_account_%d" % self.id)
        real_credit = self.get_real_credit()
        if real_credit < num_msgs:
            sem.destroy()
            raise OutOfCredit()
        msg = None
        if real_credit - num_msgs < settings.CRITICAL_CREDIT_LIMIT <= real_credit:
            msg = settings.CRITICAL_CREDIT_LIMIT
        elif real_credit - num_msgs < settings.MINIMAL_CREDIT_LIMIT <= real_credit:
            msg = settings.MINIMAL_CREDIT_LIMIT
        if msg:
            msg = "¡There are left than %d credits on %s account! Please purchase more credit." % (msg, self)
            send_mail(
                '[SingularMS] Warning: raise less than a minimal credit on %s account.' % self,
                msg,
                settings.FROM_EMAIL_ADDRESS,
                settings.EMAIL_CREDIT_LIMIT,
                fail_silently=False)
        if reserve:
            self._reserve_credit(num_msgs)

        # Freeing semaphore
        sem.destroy()

    def _reserve_credit(self, credits = 1):
        """
            Reserve the credits argument across the differents purchases
            associated to this account

            Returns the number of credits reserved (this method don't check
            if there is enough credit to sent the total of credits requested)
        """
        credits_remaining = credits
        for p in self.purchase_set.filter(available__gt = 0):
            credits_reserved = p.reserve(credits_remaining)
            p.save()
            credits_remaining = credits_remaining - credits_reserved
            if (not credits_remaining):
                break
        return credits - credits_remaining

    def balance_credit(self):
        """
            This method tries to fix errors in the logic of reserving and 
            decrementing credits 
            In the case that a purchase has remaining reserved credit and not
            available credit this code scatter the reserved credit in others
            purchases
        """
        # 
        purchases_w_credit = self.purchase_set.filter(available__gt = 0)
        for p in self.purchase_set.filter(reserved__gt = 0, available = 0):
            purchases_w_credit.reserved += p.reserved
            p.reserved = 0
            p.save()

    def spend_credit(self, credits, use_available = True):
        """
            Decrement credit and/or reserved
            WARNING: This method is not thread safe
        """
        log.debug("Spending credit")

        sem = Sem("singular_account_%d" % self.id)

        reserved_credits_remaining = credits
        available_credits_remaining = credits
        for p in self.purchase_set.filter(available__gt = 0).order_by('-reserved'):
            credits_unreserved = p.unreserve(reserved_credits_remaining)
            reserved_credits_remaining -= credits_unreserved
            log.debug("Reversed credits: %d", credits_unreserved)

            if use_available:
                if not credits_unreserved:
                    credits_spent = p.spend(available_credits_remaining)
                else:
                    credits_spent = p.spend(credits_unreserved)
                available_credits_remaining -= credits_spent
                log.debug("Spent credits: %d", credits_spent)

            if (not reserved_credits_remaining) and \
               (not use_available or not available_credits_remaining):
                break

        # Freeing semaphore
        sem.destroy()

        if reserved_credits_remaining:
            log.warning("Reversed credit process not susccessfully ended: %d credits left", reserved_credits_remaining)

        if available_credits_remaining and use_available:
            log.error("Trying to spend %s credits that I dont have.", available_credits_remaining)
            raise OutOfCredit("No available credit")

class Purchase(models.Model):
    """
        A Provider gives to the Customer a number of credits for spending with a backend
    """
    account = models.ForeignKey(Account, verbose_name=_('account') )
    startDate = models.DateField(_('valid from date'), auto_now=False, auto_now_add=False, 
                                 help_text=dateformat_help, blank=False, 
                                 default=datetime.date.today )
    
    endDate = models.DateField(_('valid until date'), auto_now=False, auto_now_add=False, 
                                 help_text=dateformat_help, blank=False,
                                 default=getDefaultFutureDate)
    initial = models.PositiveIntegerField(_('initial number of messages'))
    available = models.PositiveIntegerField(_('number of messages available'), default=10)
    reserved = models.PositiveIntegerField(_('number of messages reserved'), default=0)
    price = models.DecimalField(_('price'), max_digits=8, decimal_places=2, default=1)
            
    INSUFFICIENT_CREDIT = -1100

    default_fields = ('account', 'startDate', 'endDate', 'initial', 'available', 'reserved')

    def __unicode__(self):
        return "%(available)d (+%(reserved)d) / %(initial)d for %(account)s" % {'available': self.available,
                                                                               'reserved':self.reserved, 'initial':self.initial, 
                                                                               'account':self.account}
    
    class Meta:
        verbose_name = _('Purchase')
        verbose_name_plural = _('Purchases')

    def real_credit(self):
        """
            Checks if the credit is still valid
            Returns the actual available credits
        """
        today = datetime.date.today()
        if (self.endDate < today) or (self.startDate > today):
            return 0
        return self.available - self.reserved

    def spend(self, credits = 1):
        """
            This method tries to spend the number of credits specified in 
            the argument in this purchase

            Returns the actual number of credits spend
        """
        available_credit = self.available
        if (available_credit >= credits):
            to_spend = credits
        else:
            to_spend = available_credit

        self.available -= to_spend
        self.save()
        return to_spend

    @staticmethod
    def caducates():
        now = datetime.date.today()
        return [p.id for p in Purchase.objects.filter(endDate__lt = now)]

    @staticmethod
    def no_available():
        return [p.id for p in Purchase.objects.filter(available = 0)]

    def unreserve(self, credits = 1):
        """
            This method tries to unreserve the number of credits specified in 
            the argument in this purchase

            Returns the actual number of credits unreserved
        """
        reserved_credit = self.reserved
        if (reserved_credit >= credits):
            to_unreserve = credits
        else:
            to_unreserve = reserved_credit

        self.reserved -= to_unreserve
        self.save()
        return to_unreserve

    def reserve(self, credits = 1):
        """
            This method tries to reserve the number of credits specified in 
            the argument in this purchase

            Returns the actual number of credits reserved
        """
        #if (self.available >= credits):
        real_credit = self.real_credit()
        if (real_credit >= credits):
            to_reserve = credits
        else:
            to_reserve = real_credit

        self.reserved += to_reserve
        self.save()
        return to_reserve

pre_save.connect(save_purchase_handler, sender=Purchase)

