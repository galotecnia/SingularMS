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
from django.contrib.formtools.wizard import FormWizard
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from smlog.views import debug

from mo.models import IncomingMessage, Command, AdminCommand, ReplyCommand, ExternalCommand, ServiceCore, ServiceArg
from mo.models import ADMIN_COMMAND_TRANSLATION, ADMIN_COMMAND_LIST_CHOICES, getNameFromTuple, EXTERNAL_COMMAND_TYPE_LIST
from mo.models import REPLY, ADMIN, EXTERNAL
from mt.models import Body, Channel

import copy
import string
from libs.limbus.limbus import get_limbus_client
from xml.parsers.expat import ExpatError
from django.utils.datastructures import SortedDict
import datetime

import logging
log = logging.getLogger('galotecnia')

SMS_MAX_LENGTH = 130
ASCII_SPACE = ' '

class bodyTxtField(forms.CharField):
    """
    For a given text, creates a new body instance
    """
    def __init__(self, max_length=SMS_MAX_LENGTH, min_length=None, *args, **kwargs):
        self.max_length, self.min_length = max_length, min_length
        self.widget = forms.Textarea
        super(forms.CharField, self).__init__(*args, **kwargs)

    def clean(self, text):        
        if text is u'':
            return None
        itemTxt = Body(plainTxt=text, mms=False)
        itemTxt.save()
        return itemTxt

# For debug processes only. Should be deleted 
class incomingMsgForm(forms.ModelForm):     
    class Meta: 
        model = IncomingMessage 
               
    def __init__(self, user=None, *args, **kwargs): 
        self.user = user 
        super(forms.ModelForm, self).__init__(*args, **kwargs)

class commandForm(forms.ModelForm):
    defaultAnswer = bodyTxtField(label=_("Default answer"), required=False)
    class Meta:
        model = Command
        exclude = ['id', 'defaultAnswer']
        
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        
class replyCommandForm(forms.ModelForm):
    answer = bodyTxtField(label=_("Answer") )
    class Meta:
        model = ReplyCommand
        exclude = ['id']

    def clean(self):
        data = self.cleaned_data
        start = data['startTime']
        end = data['endTime']
        if start >= end:
            raise forms.ValidationError( _("The activation date cant be bigger or same than \
                                            deactivation date") )
        all = ReplyCommand.objects.filter(command = data['command']).order_by('startTime')
        if not all:
            return data
        pre = None
        for rc in all:
            if rc.startTime > end:
                if not pre or start > pre.endTime:
                    return data
            pre = rc
        if start > pre.endTime:
            return data
        raise forms.ValidationError( _("There is a conflict in dates with anothers Reply Commands") )
                    
        
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(forms.ModelForm, self).__init__(*args, **kwargs)        
        
class newCompleteReplyCommandForm(forms.ModelForm):
    """
        Creates both a reply command and a base command
    """
    answer = forms.CharField(label=_("Answer"), widget=forms.Textarea)    
    class Meta:        
        exclude = ['id', 'type', 'defaultAnswer']
        model = Command
        
    def __init__(self, user=None, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)        
        self.user = user
        # TODO: Load of bodies needed to be discussed first. 
        #This is perfectly safe for deleting.

    def clean(self):
        data = self.cleaned_data
        start = data['activationDate']
        end = data['deactivationDate']
        if start >= end:
            raise forms.ValidationError( _("The activation date cant be bigger or same than \
                                            deactivation date") )
        cmd = None
        try:
            cmd = Command.objects.get(pattern = data['pattern'])
        except Command.DoesNotExist:
            return data
        all = ReplyCommand.objects.filter(command = cmd.id).order_by('startTime')
        if not all:
            return data
        pre = None
        for rc in all:
            if rc.startTime > end:
                if not pre or start > pre.endTime:
                    return data
            pre = rc
        if start > pre.endTime:
            return data
        raise forms.ValidationError( _("There is a conflict in dates with anothers Reply Commands") )
 
    def save(self, commit=True):
        try:
            itemCommand = Command.objects.get(pattern = self.cleaned_data['pattern'])
            if itemCommand.activationDate > self.cleaned_data['activationDate']:
                itemCommand.activationdate = self.cleaned_data['activationDate']
            if itemCommand.deactivationDate < self.cleaned_data['deactivationDate']:
                itemCommand.deactivationDate = self.cleaned_data['deactivationDate']
        except Command.DoesNotExist:
            itemCommand = super(forms.ModelForm, self).save(commit=False)
        itemCommand.type = REPLY    #type: ReplyCommand
        itemCommand.defaultAnswer = None
        if commit:
            itemCommand.save()
            itemTxt = Body(plainTxt=self.cleaned_data['answer'], mms=False)
            itemTxt.save()
            itemReplyCommand = ReplyCommand(command=itemCommand, startTime=self.cleaned_data['activationDate'], 
                                            endTime=self.cleaned_data['deactivationDate'], answer=itemTxt)
            itemReplyCommand.save()
        return itemCommand

# Admin forms ------------------------------------------------------------------------------        
class adminCommandForm(forms.ModelForm):
    class Meta:
        model = AdminCommand
    
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(adminCommandForm, self).__init__(*args, **kwargs)
        
class singleAdminCommandForm(forms.ModelForm):
    """
        Creates both an admin command and a base command. Handles the language correctly.
    """
    action = forms.ChoiceField(choices=ADMIN_COMMAND_LIST_CHOICES, label=_('Action') )
    language = None
    channel = forms.ChoiceField()
    answer = forms.CharField(label=_("Default Answer"), widget=forms.Textarea, max_length = 160, required=False)    
    
    class Meta:
        model = Command
        exclude = ['pattern', 'type', 'defaultAnswer']
        
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        try:
            self.language = kwargs['language']
            del kwargs["language"]
        except KeyError:
            pass
        super(singleAdminCommandForm, self).__init__(*args, **kwargs)               
        self.channelChoices = []
        for channel in Channel.objects.filter(active=True):
            self.channelChoices.append((channel.id, channel.name) )            
        self.fields['channel'] = forms.ChoiceField(choices=self.channelChoices)
 
    def clean(self):
        data = self.cleaned_data
        deactiDate = data['deactivationDate']
        if not deactiDate:
           return data
        actiDate = data['activationDate']
        if actiDate >= deactiDate:
            raise forms.ValidationError( _("The activation date cant be bigger or same than \
                                            deactivation date") )
        return data      
 
    def save(self, commit=True):
        instance = super(singleAdminCommandForm, self).save(commit=False)
        instance.type = ADMIN
        ans = Body(plainTxt = self.cleaned_data['answer'])
        ans.save()
        instance.defaultAnswer = ans
        # Getting a translation if available
        try:
            index = int(self.cleaned_data['action'])            
            actionName = getNameFromTuple(ADMIN_COMMAND_LIST_CHOICES, index)
            translatedCommandType = ADMIN_COMMAND_TRANSLATION[self.language][actionName]
        except KeyError:
            translatedCommandType = actionName
             
        channel = Channel.objects.get(pk=self.cleaned_data['channel'])
        instance.pattern = translatedCommandType + ASCII_SPACE + channel.name                
        if commit:
            # Already existing commands are deleted
            try:
                oldcommand = Command.objects.get(pattern=instance.pattern)
                oldcommand.delete()
            except Command.DoesNotExist:
                pass            
            instance.save()            
            adminInstance = AdminCommand()
            adminInstance.command = instance
            adminInstance.channel = channel
            adminInstance.action = self.cleaned_data['action']
            adminInstance.save()            
        return instance
# --------------------------------------    
class ExternalCommandForm(forms.ModelForm):
    class Meta:
        model = ExternalCommand
        
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(forms.ModelForm, self).__init__(*args, **kwargs)

class CommandAuxForm(forms.ModelForm):
    class Meta:
        model = Command
        exclude = ['id', 'type', 'defaultAnswer',]
 
    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
 
    def clean(self):
        data = self.cleaned_data
        deactiDate = data['deactivationDate']
        if not deactiDate:
           return data
        actiDate = data['activationDate']
        if actiDate >= deactiDate:
            raise forms.ValidationError( _("The activation date cant be bigger or same than \
                                            deactivation date") )
        return data      

class ExtCommForm(CommandAuxForm):
   
    default_answer = forms.CharField(label = _('Default answer'), max_length = 255, required = False)
    email = forms.EmailField(label = _('Email'))
    type = forms.ChoiceField(label = _('Type'), choices = EXTERNAL_COMMAND_TYPE_LIST)
    username = forms.CharField(label = _('Username'), max_length = 255, required = False)
    password = forms.CharField(label = _('Password'), max_length = 255, required = False)
    url = forms.URLField(label = _('Server\'s URL'))    

    def __init__(self, *args, **kwargs):
        super(CommandAuxForm, self).__init__(*args, **kwargs)

class ServCoreForm(forms.Form):
    url = ''
    serv_list = []
    serv = forms.ChoiceField(label = _('Services'))

    def __init__(self, *args, **kwargs):
        self.url = ''
        super(forms.Form, self).__init__(*args, **kwargs)
        if kwargs.has_key('initial') and kwargs['initial'] and kwargs['initial'].has_key('url'):
            self.url = str(kwargs['initial']['url'])
        else:
            self.url = args[0]['0-url']
        self.serv_list = []
        client = get_limbus_client()(self.url)
        if client:
            for serv in client.get_service_list():
                self.serv_list.append((serv, serv))
            if not self.serv_list:
                self.serv_list = [('error',_("not services found")),]
        else:
            self.serv_list = [('error',_("not server found")),]
        self.fields['serv'].choices = self.serv_list 

class ServArgForm(forms.Form):

    arg = forms.MultipleChoiceField(label = _('Arguments by system'),required=False)
    bas = forms.MultipleChoiceField(label = _('Arguments by user'), required=False)
    arg_list = []
    url = ''
    serv = ''

    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)
        if kwargs.has_key('initial') and kwargs['initial'] and kwargs['initial'].has_key('serv'):
            self.serv = str(kwargs['initial']['serv'])
            self.url = str(kwargs['initial']['url'])
        else:
            self.serv = args[0]['1-serv']
            self.url = args[0]['0-url']
        self.arg_list = []
        client = get_limbus_client()(self.url)
        if client:
            inparam = client.get_argument_list(self.serv)
            if inparam:
                for name, tipo in inparam.items():
                    argument = str(name) + " (" + str(tipo) + ")"
                    self.arg_list.append(((str(name),str(tipo)),argument))
            else:
                self.arg_list = [('error',_('NOT SERVICE FOUND'))]
        else:
            self.arg_list = [('error',_('NOT SERVER FOUND')),]
        self.fields['arg'].choices = self.arg_list 
        self.fields['bas'].choices = self.arg_list

class ServArgListForm(forms.Form):
 
    kwds = {}

    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)
        if kwargs.has_key('initial') and kwargs['initial'] and kwargs['initial'].has_key('kwds'):
            self.kwds = kwargs['initial']['kwds']
        else:
            self.kwds = {}
        self.setFields()

    def setFields(self):
        keys = self.kwds.keys()
        keys.sort()
        for k in keys:
            self.fields[k] = self.kwds[k]

        

class ExtCommWizardForm(FormWizard):
    InitialFormStep = 0
    ServiceStep = 1
    ServiceArgsStep = 2
    ServiceArgsSysStep = 3

    NoWSServerStep = 1
    NoSystemArgsStep = 3

    url = '' 

    def no_server(self):
        return ExtCommWizardForm.NoWSServerStep

    def no_arg_sys(self):
        return ExtCommWizardForm.NoSystemArgsStep

    def parse_params(self, request, *args, **kwargs):
        if request.method != 'POST':
            return
        current_step = self.determine_step(request, *args, **kwargs)
        if current_step == ExtCommWizardForm.InitialFormStep:
            form = self.get_form(current_step, request.POST)
            if form.is_valid():
                self.url = form.cleaned_data['url']
                self.initial[(current_step + 1)] = {
                    'url': form.cleaned_data['url'],
                }
                try:
                    server = get_limbus_client()(self.url)
                except Exception, e:
                    # Many exceptions: URLError, ExpatError, SAXParseError ...
                    log.warn("No server found, service wont be created. Server raised %s", e)
                    server = None
                if not server:
                    # No service, so we dont create service neither arguments
                    self.num_steps = self.no_server
                    self.form_list = self.form_list[:self.no_server()]
        elif current_step == ExtCommWizardForm.ServiceStep:
            form = self.get_form(current_step, request.POST) 
            if form.is_valid():
                old_form = self.get_form(current_step-1,request.POST)
                if old_form.is_valid():
                    self.url = old_form.cleaned_data['url']
                self.initial[(current_step + 1)] = {
                    'url' : self.url,
                    'serv' : form.cleaned_data['serv'],
                }
        elif current_step == ExtCommWizardForm.ServiceArgsStep:
            form = self.get_form(current_step, request.POST)
            if form.is_valid():
                kwds = {}
                for a in form.cleaned_data['arg']:
                    for val in form.fields['arg'].choices:
                        if str(val[0]) == str(a):
                            l = "Argument " + str(val[0][0])
                            kwds[val[0][0]] = forms.CharField(label=l, max_length = 255)
                            break
                if not kwds:
                   self.num_steps = self.no_arg_sys
                   self.form_list = self.form_list[:self.no_arg_sys()]
                else:
                    self.initial[(current_step + 1)] = {
                        'kwds' : kwds,
                    }
    
    def done(self, request, form_list):
        form = form_list[0]
        command = None
        extcom = None
        sercor = None
        # Formulario 1: Command 
        command = form.save(commit=False)
        command.defaultAnswer, created = Body.objects.get_or_create(plainTxt = form.cleaned_data['default_answer'])
        command.type = 3 #ExternalCommand
        command.save()
        # Formulario 1: External Command
        extcom = ExternalCommand()
        extcom.command = command
        extcom.email = form.cleaned_data['email']
        extcom.type = form.cleaned_data['type']
        extcom.username = form.cleaned_data['username']
        extcom.password = form.cleaned_data['password']
        extcom.url = form.cleaned_data['url']
        extcom.save()
        # No more forms...
        if len(form_list) < 2:
            return
        # Form 2: ServiceCore
        form = form_list[1]
        sercor = ServiceCore()
        sercor.serv_name = form.cleaned_data['serv'].split('*')[0].strip()
        sercor.ext_comm = extcom
        sercor.save()
        # Form 3: Split between system and user args
        form = form_list[2]
        arg_by_sys = []
        for val in form.fields['bas'].choices:
            by_user = True
            for a in form.cleaned_data['arg']:
                if str(val[0]) == str(a):
                    arg_by_sys.append((val[0][0],val[0][1]))
                    by_user = False
                    break
            if by_user:
                    user_arg = ServiceArg(name = val[0][0], type = val[0][1], content = '', service = sercor)
                    user_arg.save()
                    by_user = False
        # No system args
        if not arg_by_sys:
            return
        # Form 4: system args
        form = form_list[3]
        for key in request.POST:
             if not string.find(key,"3-"):
                 for arg in arg_by_sys:
                     if not string.find(arg[0],key[2:]):
                         content = str(request.POST[key])
                         sys_arg = ServiceArg(name = arg[0], type = arg[1], content = content, service = sercor)
                         sys_arg.save()
        return None
    
    def get_template(self, step):
        """
        Hook for specifying the name of the template to use for a given step.

        Note that this can return a tuple of template names if you'd like to
        use the template system's select_template() hook.
        """
        if 'template' in self.extra_context:            
            return self.extra_context['template']
        return 'forms/wizard.html'
# -------------------------------------------------------------------
class newCompleteAdminCommandForm(commandForm):
    """
        Creates both a admin command and a base command
    """
    channel = forms.ChoiceField()
    info = forms.CharField(label=_("Channel's information") )
    
    channelChoices = []
    language = None
    
    class Meta:        
        exclude = ['id', 'type', 'pattern', 'defaultAnswer']
        model = Command
        
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        try:
            self.language = kwargs['language']
            del kwargs["language"]
        except KeyError:
            pass

        super(commandForm, self).__init__(*args, **kwargs)
        try:
            instance = kwargs['instance']
        except KeyError:
            instance = None
        
        self.channelChoices = []
        for channel in Channel.objects.all():
            self.channelChoices.append((channel.id, channel.name) )
            
        self.fields['channel'] = forms.ChoiceField(choices=self.channelChoices)
               
    def save(self, commit=True):
        instanceditemCommand = super(commandForm, self).save(commit=False)
        instanceditemCommand.type = 2
        instanceditemCommand.defaultAnswer = Body() #debugging                    
        channel = Channel.objects.get(pk=self.cleaned_data['channel'])
        for adminType in ADMIN_COMMAND_LIST_CHOICES:
            try:
                translatedCommandType = ADMIN_COMMAND_TRANSLATION[self.language][adminType[1] ]
            except KeyError:
                translatedCommandType = adminType[1]
                 
            pattern = translatedCommandType + ASCII_SPACE + channel.name
            instanceditemCommand.pattern = pattern            
            #if instanceditemCommand.pattern is pattern:
                # Treating the instancied command
             #   continue            
            # Creating new one
            try:
                newCommand = Command.objects.get(pattern=pattern)
            except Command.DoesNotExist:
                newCommand = Command(pattern=pattern)
            except MultipleObjects:
                pass
            newCommand = copy.copy(instanceditemCommand)                
            newCommand.save()
        # return instanceditemCommand
        return None
