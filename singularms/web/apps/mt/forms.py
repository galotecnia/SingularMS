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

from django import forms
from django.utils.translation import ugettext as _
from django.utils.datastructures import MultiValueDict
from django.db.models import signals
from datetime import datetime
import string

from mt.models import *
from mt.singular_exceptions import OutOfCredit

from django.db.models import Q
from django.contrib.auth.models import User
from django.http import Http404
from django.conf import settings
from accounting.models import *
from constants import *

def check_mobile(mobile):
     mobile = mobile.strip()
     mobile_int = ''
     try:
         mobile_int = int(mobile)
     except ValueError:
         return MOBILE_NOT_VALID
     except TypeError:
         return MOBILE_NOT_VALID
     if mobile_int <= 0:
         return MOBILE_NOT_VALID
     # Checks the len of the number (without the + prefix)
     l = len(str(mobile_int))
     if l < 9:
         return MOBILE_LESS_THAN_9
     # Case 34600000000
     if mobile.startswith('34') and l == 11:
        return mobile
     national = not mobile.startswith('+')
     if (l > 9 and national) or (l > 13 and not national):
         return MOBILE_MORE_THAN_9
     return mobile

class AttachmentForm(forms.ModelForm):
    """
        Form need in mms type of messages
    """
    class Meta:
        model = Attachment
        exclude = ('contentType','body')

class SendMessageForm(forms.Form):
    """
        Form with shared fields of advance and send to channel form
    """ 
    
    def __init__(self,*args,**kwargs):
        id = kwargs.pop('id')
        self.tipo = kwargs.pop('type') if 'type' in kwargs else "easy"
        super(forms.Form,self).__init__(*args,**kwargs)
        try:
            user = User.objects.get(pk=id)
        except User.DoesNotExist:
            raise Http404
        if checkAdmin(user):
            filter = {}
        else:
            try:
                customer = Customer.objects.get(pk=id)  
                filter = {'customer__exact' : customer}
            except Customer.DoesNotExist:
                raise Http404
        self.accounts = Account.objects.filter(**filter)

        self.accounts_choices = []
        for temp in self.accounts:
            self.accounts_choices.append((temp.id, str(temp)))
        self.date = (datetime.datetime.now() + datetime.timedelta(days = settings.DEFAULT_DEACTIVATION_TIME))

        # Show channel list or mobile input field
        if self.tipo == "channel":
            channels = []
            qs = Channel.objects.filter(**filter)
            for temp in qs.filter(Q(destructionDate__gte = datetime.datetime.now()) | Q(destructionDate__isnull = True)):
                channels.append((temp.id, str(temp)))
            self.fields['channel'] = forms.MultipleChoiceField(label = _(u'Channels'), choices = channels)
        else:
            self.fields['mobile'] = forms.CharField(label = _(u'Mobile'))

        # Show user's account list and dates
        self.fields['account'] = forms.ChoiceField(label=_('Account'), choices = self.accounts_choices)
        self.fields['actiDate'] = forms.DateTimeField(label = _('Activation time'), initial=datetime.datetime.now())
        self.fields['deactiDate'] = forms.DateTimeField(label = _('Deactivation time'),required=False,initial=self.date)

        # Show all kind of msgs that we can use
        capabilities = {}
        for ac in Access.objects.filter(account__in = self.accounts):
            capabilities.update(dict(ac.capabilities.values_list()))
        self.fields['typeMsg'] = forms.ChoiceField(label=_('Type'), choices = capabilities.items())
        self.fields['body'] =  forms.CharField(max_length=160,label= _('Body'), widget=forms.Textarea)

    def clean_mobile(self):
        mobile = self.data.getlist('mobile')
        list = []
        invalid = {}
        for mob in mobile:
            m = check_mobile(mob)
            if m < 0:
                invalid[str(mob)] = MOBILE_MSG_ERROR[m] + ': ' + mob
            else:
                list.append(m)
        self.data.setlist('mobile', list)
        mobile = self.data.getlist('mobile')
        if len(invalid):
            raise forms.ValidationError(invalid.values())
        return mobile

    def clean_deactiDate(self):
        data = self.cleaned_data
        if data['deactiDate']:
            if 'actiDate' in data and data['actiDate'] >= data['deactiDate']:
                raise forms.ValidationError( _("The activation date cant be bigger or same than deactivation date"))
            return data['deactiDate']
        return None

    def clean_account(self):
        data = self.cleaned_data
        if self.tipo == 'easy':
            mobiles = len(self.data.getlist('mobile'))
        else:
            mobiles = 0
            if not 'channel' in data:   
                raise forms.ValidationError(_(u"No channel selected. Please, choose at least one"))
            for c in Channel.objects.filter(id__in = data['channel']):
                mobiles += c.subscriber_set.count()
        self.account = Account.objects.get(id = data['account'])
        if not self.account or self.account.get_real_credit() < mobiles:
            raise forms.ValidationError(OUTOFCREDIT_ERROR)
        return data

    def save(self, commit = True):
        data = self.cleaned_data
        msg_id = None
        if self.tipo == "easy":
            for mobile in self.data.getlist('mobile'):
                try:
                    msg_id = Message.create_one(text = data['body'], mobile = adapt_mobile(mobile), 
                            activationDate = data['actiDate'], deactivationDate = data['deactiDate'], account = self.account)
                except OutOfCredit:
                    return {'result': False, 'error': OUTOFCREDIT_ERROR}
        else:
            for channel in Channel.objects.filter(id__in = data['channel']):
                msg_id = Channel.create_one(text = data['body'], channel_name = channel.name, account = self.account,
                        activationDate = data['actiDate'], deactivationDate = data['deactiDate'])
        return {'result': True, 'id': str(msg_id)}

        
class SetForms:
    
    @staticmethod
    def check_create(*args,**kwargs):
        """
            This method check if the user can send messages with this forms
        """
        id = kwargs['id']
        type = kwargs['type']
        try:
            user = User.objects.get(pk=id)
        except User.DoesNotExist:
            raise Http404

        if checkAdmin(user):
            if not Account.objects.count():
                return {'result': False, 'error': _("Sorry, but you have to create an account")}
            if type == 'channel':
                if not Channel.objects.count():
                   return {'result':False, 'error': _("Sorry, but you have to create a channel")}
        else:
            try:
                elec_customer = Customer.objects.get(pk=id)
            except Customer.DoesNotExist:
                raise Http404
            if not Account.objects.filter(customer__exact = elec_customer).count():
                return {"result":False,"error":_("This user not have any account")}
            if type == 'channel':
                if not Channel.objects.filter(customer__exact = elec_customer).count():
                    return {'result':False,"error":_("This user is not subscriber to any channel")}
        return {'result': True}
    
    def __init__(self,*args,**kwargs):
        self.forms = { 'smsForm':  kwargs['smsForm'],
                       'attchForm': kwargs['attchForm'],
                     }
        self.typesMsg = dict(self.forms['smsForm'].fields['typeMsg'].choices)
        self.typesMsg = dict([(v, k) for (k, v) in self.typesMsg.iteritems()])
        self.type = kwargs['type']

    def getForm(self,form):
        """
            Return the form select with "form"
        """
        return self.forms[form]
    
    def is_valid(self):
        """
            Check the is_valid method for forms
        """
        if (self.forms['smsForm'].is_valid() == False):
            return False
        else:
            if 'mms' in self.typesMsg:
                if (int(self.forms['smsForm'].cleaned_data['typeMsg']) == int(self.typesMsg['mms'])):
                    if (self.forms['attchForm'].is_valid()):
                        return True
                    else:
                        return False
                else:
                    return True
            else:
                return True

    def save(self,commit=True):
        result = self.forms['smsForm'].save()
        if not result['result']:
            return result
        if self.type == "channel":
            msg = ChannelMessage.objects.get(id = result['id'])
            body = msg.message.body
        else:
            msg = Message.objects.get(id = result['id'])
            body = msg.body
        if 'mms' in self.typesMsg:
            if (int(self.forms['smsForm'].cleaned_data['typeMsg']) == int(self.typesMsg['mms'])):
                body.mms = True
                body.save()
                files = self.forms['attchForm'].files
                data =  self.forms['attchForm'].data
                for f in files.getlist('file'):
                    form = AttachmentForm(data,MultiValueDict({'file':[f]}))
                    if form.is_valid():
                        instance = form.save(commit=False)
                        instance.contentType = f.content_type
                        instance.body = body
                        instance.save()
        elif 'Repliable' in self.typesMsg:
            if (int(self.forms['smsForm'].cleaned_data['typeMsg']) == int(self.typesMsg['Repliable'])):
                msg.repliable = True
                msg.save()
        return {'result':True}

class ChannelForm(forms.ModelForm):
    """
        Creates and modifies channels
    """
    class Meta:
        model = Channel
        exclude = ['id']

    def __init__(self,*args,**kwargs):
        self.user=kwargs['user']
        del kwargs['user']
        super(forms.ModelForm,self).__init__(*args,**kwargs)
        if (not checkAdmin(self.user)):
            self.fields.pop('customer')

    def save(self, commit=True):
        item = super(forms.ModelForm, self).save(commit=False)
        if commit:
            if (not checkAdmin(self.user)):
                item.save()
                try:
                    cust = Customer.objects.get(pk=self.user.id)
                    item.customer = [cust]
                except Customer.DoesNotExist:
                    raise Http404
            item.save()
        return item

class BodyForm(forms.ModelForm):
    class Meta:
        model = Body
        
    def __init__(self, user = None, *args, **kwargs):
        self.user = user
        super(forms.ModelForm, self).__init__( *args, **kwargs)

class ChannelChoice(forms.Form):
    channel = forms.ChoiceField(label=_('channel'))
    def __init__(self,user = None, *args,**kwargs): 
        
        if not checkAdmin(user):
            channels = Channel.objects.filter(customer = user, active = True, destructionDate__gte = datetime.datetime.now())
        else:
            channels = Channel.objects.filter(active = True, destructionDate__gte = datetime.datetime.now())
        elec_channel = []
        for temp in channels:
            elec_channel.append((temp.id, str(temp)))
        #del kwargs['channels']
        super(forms.Form,self).__init__(*args,**kwargs)
        self.fields['channel'] = forms.ChoiceField(label=_('channel'), choices =elec_channel)

class SubscriberFullForm(forms.ModelForm):
        
    class Meta:
        model = Subscriber

    def __init__(self, user, *args, **kwargs):
        super(SubscriberFullForm, self).__init__(*args, **kwargs)
        query = Channel.objects.filter( (Q(destructionDate__gte = datetime.datetime.now()) |
                            Q(destructionDate__isnull = True)) & Q(active = True))
        if not checkAdmin(user):
            query = query.filter(customer = user)
        self.fields['channels'].queryset = query
        
    
    def clean_mobile(self):
        data = self.cleaned_data
        mobile = data['mobile']
        mob = check_mobile(mobile)
        if mob in MOBILE_ERRORS:
            raise forms.ValidationError(MOBILE_MSG_ERROR[mob])
        return mob

class SubscriberForm(forms.ModelForm):
    
    class Meta:
        model = Subscriber
        exclude = ['channels']
 
    def clean_mobile(self):
        data = self.cleaned_data
        mobile = data['mobile']
        mob = check_mobile(mobile)
        if mob in MOBILE_ERRORS:
            raise forms.ValidationError(MOBILE_MSG_ERROR[mob])
        return mob

class FilterForm (forms.Form):
    """
        Form for filter message list
    """
    status = forms.MultipleChoiceField(label=_(u'Status'),choices=STATUS_CHOICES,required=False)
    mobile = forms.CharField(label = _(u'Mobile'), required = False)
    initDate = forms.DateTimeField(label = _(u'Created since'), required = False)
    endDate = forms.DateTimeField(label = _(u'Created until'), required = False)
    mms = forms.BooleanField(label = _(u'MMS'), required = False)

    def __init__(self,*args,**kwargs):
        self.type = kwargs['type']
        id = kwargs["id"]
        del kwargs['id']
        del kwargs['type']
        super(forms.Form,self).__init__(*args,**kwargs)
        if (self.type == 'Channel'):
            self.fields.pop('mobile')
            self.fields.pop('status')
            try:
            #get user for id
                user = User.objects.get(pk=id)
            except User.DoesNotExist:
                raise Http404
            if (checkAdmin(user) == False ):
                try:
                    #if not admin, get customer for this id
                    elec_customer = Customer.objects.get(pk=id)
                except Customer.DoesNotExist:
                    raise Http404
            elec_channel = []
            if checkAdmin(user):
                qs = Channel.objects.all()
            else:
                qs = Channel.objects.filter(customer__exact = elec_customer)
            for temp in qs:
                elec_channel.append((temp.id, temp.name))
            #Create field for channel's user
            field = forms.ChoiceField(label=_('Channel'),choices=elec_channel,required=False)
            self.fields.insert(0,'channel',field)

