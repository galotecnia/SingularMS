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

from datetime import datetime

from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from django.contrib.formtools.wizard import FormWizard
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Permission 

from models import Provider, Account, Customer, Access, Purchase

MAX_CREDITS = 10000000
CUSTOMER_CAN_MANAGE_CHANNELS = 'can_manage'
FULLNAME_CUSTOMER_CAN_MANAGE_CHANNELS = 'mt.' + CUSTOMER_CAN_MANAGE_CHANNELS
    
def getAdminChannelPerm():
    p = Permission.objects.get(codename=CUSTOMER_CAN_MANAGE_CHANNELS)            
    return p

def getAdminChannelPerm_fullname():
    return FULLNAME_CUSTOMER_CAN_MANAGE_CHANNELS

class providerForm(forms.ModelForm):
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)    
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput)    
    class Meta:
        model = Provider
        fields = ['username'] 

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(providerForm, self).__init__(*args, **kwargs)
        
    def clean_password2(self):
        password = self.cleaned_data.get("password", "")
        password2 = self.cleaned_data["password2"]
        if password != password2:
            raise forms.ValidationError(_("The two password fields didn't match.") )        
        return password2

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username = username):
            raise forms.ValidationError(_("This user already exists.") )
        return username
            
   
    def save(self, commit=True):
        item = super(providerForm, self).save(commit=False)
        item.set_password(self.cleaned_data["password"])        
        if commit:
            item.save()
            p = getAdminChannelPerm()
            item.user_permissions.add(p)
            self.save_m2m()                
        return item

class edit_providerForm(providerForm):
    
    def clean_username(self):
        return self.cleaned_data['username']

# Customer forms    
class customerForm(providerForm):
    canManage = forms.BooleanField(label=_("Can manage channels"), 
                                   required=False, initial=None) 
    class Meta:
        model = Customer
        fields = ['username', 'providers']        
        
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(providerForm, self).__init__(*args, **kwargs)
        try:
            instance = kwargs['instance']
        except KeyError:
            instance = None
        if instance:            
            # This seems to be the only way right for django
            # for asking perms...
            if instance.has_perm(getAdminChannelPerm_fullname() ):
                self.fields['canManage'].initial=True
            else:
                self.fields['canManage'].initial=None
        
    def save(self, commit=True):
        item = super(customerForm, self).save(commit=False)
        item.set_password(self.cleaned_data["password"])
        if commit:
            item.save()
            p = getAdminChannelPerm()      
            if self.cleaned_data["canManage"]:
                item.user_permissions.add(p)
            else:
                item.user_permissions.remove(p)
        self.save_m2m()        
        return item

class edit_customerForm(customerForm):
    
    def clean_username(self):
        return self.cleaned_data['username']

class assistantCustomerForm(customerForm):

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(providerForm, self).__init__(*args, **kwargs)        
        # Gets item from other models        
        for field_name, field_type in lite_accountForm().fields.iteritems():
            self.fields[field_name] = field_type
        
        for field_name, field_type in lite_purchaseForm().fields.iteritems():
            self.fields[field_name] = field_type        
        
    def save(self, commit=True):
        item = super(customerForm, self).save(commit=False)
        item.set_password(self.cleaned_data["password"])
        account = Account(name=self.cleaned_data["name"], access=self.cleaned_data["access"],
                           args2=self.cleaned_data["args2"], num_threads=self.cleaned_data["num_threads"])
        purchase = Purchase(startDate=self.cleaned_data["startDate"], endDate=self.cleaned_data["endDate"],
                            initial=self.cleaned_data["initial"], available=self.cleaned_data["initial"])
        if commit:            
            item.save()
            self.save_m2m()
            
            account.customer = item
            account.save()
            
            purchase.account = account
            purchase.save()    
        return item
            
class accountForm(forms.ModelForm):

    class Meta:
        model = Account
        exclude = ['id']
        
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(forms.ModelForm, self).__init__(*args, **kwargs)

class lite_accountForm(accountForm):

    class Meta:
        model = Account
        exclude = ['customer']
        
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(accountForm, self).__init__(*args, **kwargs)
    
class accessForm(forms.ModelForm):    
    class Meta:
        model = Access
        exclude = ['id']
        
    def __init__(self, user = None, *args, **kwargs):
        self.user = user
        super( accessForm, self).__init__( *args, **kwargs)

class purchaseForm(forms.ModelForm):

    initial = forms.IntegerField(max_value=MAX_CREDITS, min_value=0, initial="10", label=_(u'Initial'))
    startDate = forms.DateTimeField(label=_(u'Initial date'))
    endDate = forms.DateTimeField(label=_(u'End date'))

    class Meta:
        model = Purchase
        exclude = ['id', 'available', 'reserved', 'price', 'startDate', 'endDate']
        
    def __init__(self, user = None, *args, **kwargs):
        self.user = user
        super(forms.ModelForm, self).__init__( *args, **kwargs)
    
    def save(self, commit=True):
        item = super(purchaseForm, self).save(commit=False)
        # New purchase
        if not item.pk:
            item.available = item.initial
        item.startDate = self.cleaned_data['startDate'].date()
        item.endDate = self.cleaned_data['endDate'].date()
        if commit:
            item.save()
            self.save_m2m()        
        return item
    
class edit_purchaseForm(forms.ModelForm):

    class Meta:
        model = Purchase
        exclude = ['id', 'available', 'price', 'initial']
        
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(forms.ModelForm, self).__init__( *args, **kwargs)
        
class lite_purchaseForm(purchaseForm):

    class Meta:
        model = Purchase
        exclude = ['account', 'id', 'available','reserved', 'price']
        
    def __init__(self, user = None, *args, **kwargs):
        self.user = user
        super(purchaseForm, self).__init__( *args, **kwargs)

# Hooks for the wizard
class customer_wizardhook(customerForm):

    def __init__(self, *args, **kwargs):
        super(providerForm, self).__init__(*args, **kwargs)
        
class account_wizardhook(lite_accountForm):

    def __init__(self, *args, **kwargs):
        super(accountForm, self).__init__(*args, **kwargs)
        
class purchase_wizardhook(lite_purchaseForm):
    def __init__(self, *args, **kwargs):
        super(purchaseForm, self).__init__(*args, **kwargs)

# Wizards
class customerFormWizard(FormWizard):
    def get_template(self, step):
        """
            Hook for specifying the name of the template to use for a given step.
        """
        if 'template' in self.extra_context:            
            return self.extra_context['template']
        return 'forms/wizard.html'
    
    def done(self, request, form_list):
        customer = form_list[0].save()
        account  = form_list[1].save(commit=False)
        purchase  = form_list[2].save(commit=False)
        account.customer = customer
        account.save()        
        purchase.account = account
        purchase.save()
        return None
