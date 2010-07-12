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
from django.utils import simplejson
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext 
from django.views.generic.create_update import update_object
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.conf import settings

from accounting.models import *
from accounting.decorators import *
from forms import *
from models import *

from manager.menu import *
from menu_utils import *
from constants import *
from manager.templatetags.display_form import display_form

from smlog.views import info, error
import datetime

MESSAGE_CONTEXT = { 
    'mms_size': settings.MMS_SIZE,
    'mms_multi': settings.MMS_MULTI,
    'mms_file_types': settings.MMS_FILE_TYPES,
    'sms_size': settings.SMS_SIZE,
}

SEND_DATA = {
    'easy': { 
        'custom': 'easy',
    },
    'channel': {
        'custom': 'channel',
    },
}
###############################################################################################
# Channel views
###############################################################################################

@channel_admin_required
def channelList(request, allow_empty=True):
    """
        Show a list of channels.
    """
    crumbs = (
        ( _('Home'), reverse('root')),
        ( _('Channel List'), reverse('showList')),
    )
    info(request, 'channelList', 'Listing channels')
    setLeftMenu (request, channelMenu (), _('Channels'))
    kwargs = {'user':request.user}
    newForm = ChannelForm(**kwargs)
    extra_context = { 'profile' : request.session['profile'],
                      'crumbs':crumbs,
                      'channelform': newForm
                    }
    return render_to_response(TEMPLATES['channel_list'],
                              extra_context,
                              RequestContext(request)
)

@channel_admin_required
def updateChannel(request, object_id):
    """
        #TODO
    """

    crumbs = ( ( _('Home') , reverse('root') ),
               ( _('Channel List') , reverse('showList')  ),
               ( _('Update Channel %(objectId)s') % {'objectId': object_id} , 
                        reverse('update_channel',args=[object_id])),
             )
    info (request, 'updateChannel', 'Updating channel')
    setLeftMenu (request, channelMenu (), _('Channels'))
    return update_object(
            request, 
            Channel, 
            object_id = object_id,
            post_save_redirect = reverse('showList'),
            template_name=TEMPLATES['update_channel'],
            extra_context = {'profile' : request.session['profile'],
                             'crumbs':crumbs,
                             'use': 'update'
                             },
        )

@channel_admin_required
def update_subscriber(request, id):
    rc = RequestContext(request)
    info(request, 'update_subscriber', 'Updating subscriber')
    setLeftMenu(request, create_subscriber_menu(), _('Channel\'s Subscriber'))
    crumbs = (  ( _('Home'), reverse('root')),
                ( _('Channel\'s Subscriber'), reverse('showSubscriber')),
                ( _('Update Subscriber'), reverse('update_subscriber', args=[id])),
             )
    item = get_object_or_404(Subscriber, pk = id)
    context = {'object': item}
    if request.POST:
        form = SubscriberFullForm(request.user, request.POST, instance = item)
        if form.is_valid():
            item = form.save()
            return HttpResponseRedirect(reverse('showSubscriber'))
        else:
            context['form'] = form
    else:
        context['form'] = SubscriberFullForm(request.user, instance = item)
    context['crumbs'] = crumbs
    context['profile'] = request.session['profile']
    return render_to_response('mt/subscriber_actions.html', context, rc)

@channel_admin_required
def deleteChannel(request, object_id):
    """
        #TODO
    """
    setLeftMenu (request, channelMenu(), _('Channels'))
    crumbs = ( ( _('Home') , reverse('root') ),
               ( _('Channel List') , reverse('showList')  ),
               ( _('Delete Channel %(objectId)s') % {'objectId': object_id} , 
                        reverse('delete_channel',args=[object_id])),
             )
    info (request, 'deleteChannel', 'enter to delete channel %(object)s' % {'object':object_id})
    try:
        object = Channel.objects.get(pk = object_id)
    except Channel.DoesNotExist:
        error (request, 'deleteChannel', 
                        _('Trying to delete a unexisting channel'))
        object = None   
    if request.POST:
        object.destructionDate = datetime.datetime.now()
        object.active = False
        object.save()
        info(request, 'deleteChannel', 
                _("Channel %(object)s have been deleted" % {'object': object}))
        return HttpResponseRedirect(reverse('showList'))
    else:
        return render_to_response(TEMPLATES['delete_channel'], {
                'object': object,
                'profile' : request.session['profile'],
                'crumbs' : crumbs
            }, RequestContext (request))

@channel_admin_required
def showSubscriber(request):
    info(request, 'showSubscriber', 'Show subscriber')
    setLeftMenu(request, create_subscriber_menu(), _('Channel\'s Subscriber'))
    context = {}
    context['crumbs'] = (
        ( _('Home'), reverse('root')),
        ( _('Channel\'s Subscriber'), reverse('showSubscriber')),
    )
    channels = ChannelChoice(request.user)
    if (len(channels.fields['channel']._choices) == 0):
        channels = None
    newSubscriber = SubscriberForm()
    return render_to_response(TEMPLATES['show_subscriber'],
                                                {
                                                    'channels': channels,
                                                    'subscriber' : newSubscriber,
                                                    'profile': request.session['profile'],
                                                    'crumbs': context['crumbs'],
                                                    'form_empty': display_form(newSubscriber)
                                                },
                                                RequestContext(request)
                                             )

###############################################################################################
# End channel views
###############################################################################################

def channel_msgs_status(request, id):
    rc = RequestContext(request)
    context = {'profile': request.session['profile']}
    crumbs = ( ( _('Home'), reverse('root') ),
               ( _('Channel messages'), reverse('messagelist', args=['Channel']) ),
               ( _('Message status'), reverse('message_status', args=[id]) ),
             )  
    chmsg = get_object_or_404(ChannelMessage, pk=id)
    context['crumbs'] = crumbs
    context['object_list'] = chmsg.message.smshistory_set.all()
    context['channel'] = chmsg.channel.name
    setLeftMenu(request, messageMenu (request), _('Message'))
    return render_to_response('mt/channel_message_status.html', context, rc)

def deleteMessage(request, object_id,type):

    object = None
    msg_object = None
    crumbs = ( ( _('Home') , reverse('root') ),
               ( _('Message List') , reverse('messagelist',args=[type])  ),
               ( _('Delete Message %(objectId)s') % {'objectId': object_id} ,
                        reverse('deletemessage',args=[type,object_id])),
             )
    info (request, 'deleteMessage', 'deleting message')
    setLeftMenu (request, messageMenu (request), _('Message'))
    if type == 'Individual':
        try:
            object = Message.objects.get(pk = object_id)
        except Message.DoesNotExist:
            error (request, 'deleteMessage',
                        _('Trying to delete a unexisting message'))
    elif type == 'Channel':
        try:
            msg_object = Message.objects.get(pk=object_id)
            object = msg_object.channelmessage_set.all()[0]
        except (ChannelMessage.DoesNotExist, Message.DoesNotExist):
            error (request, 'deleteMessage',
                        _('Trying to delete a unexisting message'))
    if request.POST:
        if object.can_be_del():
            object.delete()
            if msg_object: 
                msg_object.delete()
            info (request, 'deleteMessage',
                _('Message %(object)s have been deleted' % {'object': object.__unicode__()}))
            return HttpResponseRedirect(reverse('messagelist',args=[type]))
        else:
            error (request, 'deleteMessage',
                        _('Can not delete message %(objectID)s') %{'objectID':object.id})
            return render_to_response(TEMPLATES['errors'],
                                      {
                                        'profile': request.session['profile'],
                                        'crumbs': crumbs,
                                        'showInfoToUser': _('Can not delete message %(objectID)s') %{'objectID':object.id},
                                        'type': type
                                      },RequestContext (request)
                                      
                    )
    else:
        return render_to_response(TEMPLATES['delete_message'], {
                'object': object,
                'profile' : request.session['profile'],
                'crumbs' : crumbs,
                'type': type
            }, RequestContext (request))

def filterQs(request,type=None):
    info(request,"filterQs","enter in filterQs")
    filters = request.GET['filter'].split(',')
    filter = {}
    status = []
    for f in filters:
        k,v = f.split(':')
        if k == 'creationDateSince':
            v = datetime.datetime.strptime(v, "%Y-%m-%d_%H-%M-%S")
            k = 'creationDate__gte' 
        elif k == 'creationDateUntil':
            v = datetime.datetime.strptime(v, "%Y-%m-%d_%H-%M-%S")
            k = 'creationDate__lte'  
        elif k == 'mms':
            k = 'body__mms'
            v = 1 if v == 'True' else 0
        elif k == 'channel':
            k = 'channelmessage__channel__id'
        elif k == 'mobile':
            k = 'mobile__icontains'
        if k != 'status':
            filter[str(k)] = v
        else:
            status.append(int(v))
    if status:
        filter['smshistory__server_status__in'] = status
    return filter


###############################################################################################
# Message list and send process
###############################################################################################
@customer_required
def messageList2(request,type=None,channel=None):
    """
        Shows a message list
    """
    info(request, 'messageList', 'Listing messages')
    setLeftMenu(request, messageMenu(request), _('Messages'))
    crumbs = ((_('Home'), reverse('root')),)
    extra_context = {}
    if type:
        extra_context['typeName'] = MESSAGE_TYPES[type]
        typeName = MESSAGE_TYPES[type]

        if typeName == MESSAGE_TYPES[MESSAGE_TYPE_INDIVIDUAL]:
            crumbs += ((_('Individual messages'), reverse('messagelist', args = [MESSAGE_TYPE_INDIVIDUAL])),)
            extra_context['type'] = MESSAGE_TYPE_INDIVIDUAL
        elif typeName == MESSAGE_TYPES[MESSAGE_TYPE_CHANNEL]:
            crumbs += ((_('Channel messages'), reverse('messagelist', args = [MESSAGE_TYPE_CHANNEL])),)
            extra_context['type'] = MESSAGE_TYPE_CHANNEL
        else:
            error(request, 'messageList2', 'Trying to list messages of unknown type')
            raise Http404

    if channel:
        extra_context['channel'] = channel
        
    extra_context['profile'] = request.session['profile']
    extra_context['crumbs'] = crumbs
    kwargs = {'type': type, 'id': request.user.id}
    extra_context['filterForm'] = FilterForm(**kwargs)
    return render_to_response(TEMPLATES['message_list'], extra_context, RequestContext(request))

@customer_required
def easySend(request, tipo = "easy", mobile = None):
    """
        Normal and advanced sending message process management
    """
    # Error context
    def make_context(request, context):
        return {
            'profile': request.session['profile'],
            'custom': context['custom'],
            'crumbs': context['crumbs'],
            'showInfoToUser': ret['error']
        }

    # Aditional information context
    def add_context_info(context, request, form):
        context['profile'] = request.session['profile']
        context['form'] = form.getForm('smsForm')
        context['form_file'] = form.getForm('attchForm')
        return context

    # Personalized crumbs, it depends on the kind of message
    def get_crumbs(tipo):
        crumbs = {
            'easy': ((_('Home'), reverse('root')), (_('Individual message'), reverse('easySend')),),
            'channel': ((_('Home'), reverse('root')), ( _('Channel Message') , reverse('easyChannelSend')),),
        }
        return crumbs[tipo]
        
    info(request,'easySend', "Send %s message" % tipo)

    # Menu setup
    m = createMenuMessages(request)
    setLeftMenu(request, m, _('Options'))

    rc = RequestContext(request)
    context = MESSAGE_CONTEXT
    context['crumbs'] = get_crumbs(tipo)
    context['custom'] = SEND_DATA[tipo]['custom']
    kwargs = {'id': request.user.id, 'type': context['custom']}
    ret = SetForms.check_create(**kwargs)
    if not ret['result']:
        return render_to_response(TEMPLATES['errors'], make_context(request, context), rc)
    infoToUser = ""
    kwargs = {'id': request.user.id, 'type': tipo}

    if request.method == 'POST':
        setFormsKwargs = {
            'smsForm': SendMessageForm(request.POST, **kwargs),
            'type': context['custom'],
            'attchForm': AttachmentForm(request.POST, request.FILES),
        }
        instSetForm = SetForms(**setFormsKwargs)
        if instSetForm.is_valid():
            ret = instSetForm.save()
            if not ret['result']:
                return render_to_response(TEMPLATES['errors'], make_context(request, context), rc)
        else:
            warning(request, "easyForm_view", "Form for send message contains invalid data")
            files = []
            if len(instSetForm.getForm('attchForm').files) != 0:
                for f in instSetForm.getForm('attchForm').files.getlist('file'):
                    files.append(str(f.name))
            mobiles = []
            if context['custom'] != "channel":
                if len(instSetForm.getForm('smsForm').data.getlist('mobile')) != 0:
                    for m in instSetForm.getForm('smsForm').data.getlist('mobile'):
                        mobiles.append(str(m))
            context = add_context_info(context, request, instSetForm)
            context['files'] = files
            context['mobiles'] = mobiles 
            return render_to_response(TEMPLATES['send_message'], context, rc)
        
        infoToUser = _('Message sent correctly')

    setFormsKwargs = {
        'smsForm': SendMessageForm(**kwargs),
        'type': context['custom'], 
        'attchForm': AttachmentForm()
    }
    instSetForm = SetForms(**setFormsKwargs)
    context = add_context_info(context, request, instSetForm)
    context['showInfoToUser'] = infoToUser
    return render_to_response(TEMPLATES['send_message'], context, rc)

###############################################################################################
# Ajax views
###############################################################################################

def ajax_filter_typesSms(request):
    info(request,"ajaxFilterTypeSms","view types sms for account")
    if request.is_ajax():
        capabilities = {}
        if ('account' in request.GET):
            access = Access.objects.filter(account__exact =
                            Account.objects.get(id=request.GET['account']))
            
            for acc in access:
                capabilities.update(dict(acc.capabilities.values_list())) 
                
        else:
            capabilities = dict(Capabilities.objects.all().values_list())
               
        return render_to_response(TEMPLATES['sms_types'], {'data':capabilities},
                                          RequestContext(request)) 
    else:
        warning(request,"ajaxFilterTypeSms","this view is only for ajax")
        raise Http404
            
def ajaxSubscriber(request):
    info(request,"ajaxSubscriber","return list of channel's subscriber")
    if not request.is_ajax():
        warning(request,"ajaxSubscriber","this view is only for ajax")
        raise Http404
    if ('channel' in request.GET) and (request.GET['channel'] != 'undefined'):
        chn = Channel.objects.get(id = request.GET['channel'])
        subs = chn.subscriber_set.values()
        return render_to_response(
            TEMPLATES['ajax_subscriber'],
            { 'data': subs, 'pag_index': settings.SUBSCRIBER_PAGINATE, },
            RequestContext(request)
            )
    subs=None
    return render_to_response(
        TEMPLATES['ajax_subscriber'],
        { 'data': subs, 'pag_index': settings.SUBSCRIBER_PAGINATE, },
        RequestContext(request)
     )

def ajaxDeleteSubscriber(request):
    info(request,"ajaxDeleteSubscriber","Deleting subscriber")
    if request.is_ajax():
        if "checked" in request.GET:
            checked = request.GET['checked']
            # Check if there are marked channels
            if checked:
                list = checked.split(",")
                channel = Channel.objects.get(pk = request.GET['channel'])
                subscriber = Subscriber.objects.filter(id__in=list)
                if len(subscriber) == len(list):
                    for s in subscriber:
                        s.channels.remove(channel)
                        if not s.channels.all().count():
                            s.delete()
                else:
                    warning(request,"ajaxDeleteSubscriber","not filter same number of item than items in list")
                    return HttpResponse(simplejson.dumps({'data':False,'ajax':False}))
            return HttpResponse(simplejson.dumps({'data':True,'ajax':False}))
        else:
            warning(request,"ajaxDeleteSubscriber","not select any subscriber to delete")
            return HttpResponse(simplejson.dumps({'data':False,'ajax':False}))
    else:
        warning(request,"ajaxDeleteSubscriber","this view is only access by ajax")
        raise Http404
  
def ajaxNewSubscriber(request):
    info(request,"ajaxNewSubscriber","Creating new Subscriber to channel")  
    if request.is_ajax():
        newForm = SubscriberForm(request.POST)
        if not newForm.is_valid():
            return HttpResponse(simplejson.dumps({'data':False,'ajax':True,'errors':display_form(newForm)}))
        elif 'channel' not in request.POST:
            newForm.errors['__all__'] = u"There was an error while trying to choose a channel. Please, try it again."
            return HttpResponse(simplejson.dumps({'data':False,'ajax':True,'errors':display_form(newForm)}))
        else:
            mobile = request.POST['mobile']
            channel = request.POST['channel']
            name = request.POST['name']
            Subscriber.create(mobile, channel, name)
            return HttpResponse(simplejson.dumps({'data':True,'ajax':True,'errors':False,
                                                      'form':display_form(SubscriberForm())
                                                     }))
    else:
        warning(request,"ajaxNewSubscriber","this view is only for ajax")
        raise Http404

def ajaxNewChannel(request):
    info(request,"ajaxNewChannel","Creating new Channel")
    if request.is_ajax():
        kwargs = {'user':request.user}
        newForm = ChannelForm(request.POST,**kwargs)
        if newForm.is_valid():
            newForm.save()
            return HttpResponse(simplejson.dumps({'data':True,'ajax':True,'errors':False}))
        else:
            warning(request,"ajaxNewChannel","Not valid form")
            return HttpResponse(simplejson.dumps({'data':False,'ajax':True,
                                                  'errors':display_form(newForm)}))

    else:
        warning(request,"ajaxNewSubscriber","this view is only for ajax")
        raise Http404

def ajaxChannelList(request):
    info(request,"ajaxSubscriber","return list of channel")
    if request.is_ajax():
        if checkAdmin(request.user):
            chns = Channel.objects.all()
        else:
            chns = Channel.objects.filter(customer=request.user)

        chns = chns.filter(
                            Q(destructionDate__gte = datetime.datetime.now()) |
                            Q(destructionDate__isnull = True)
                          )
        
        return render_to_response(TEMPLATES['ajax_channel_list'],
                                            {
                                                'data': chns,
                                                'pag_index': settings.SUBSCRIBER_PAGINATE,
                                            },
                                            RequestContext(request)
                                         )
    else:
        warning(request,"ajaxSubscriber","this view is only for ajax")
        raise Http404

def ajaxNumOfSubscribers(request):
    if not request.is_ajax():
        warning(request,"ajaxNumOfSubscribers","this view is only for ajax")
        raise Http404
    if not 'channel' in request.GET:
        return HttpResponse(simplejson.dumps({'data':False}))
    if request.GET['channel'] != 'undefined':
        chn = Channel.objects.get(id = request.GET['channel'])
        subs = chn.subscriber_set.values()
        return HttpResponse(simplejson.dumps({'data':True,'num':len(subs)}))
    return HttpResponse(simplejson.dumps({'data':False}))

def ajax_size_file_upload(request):
    if request.is_ajax:
        if (request.method == 'POST'):
            size = 0
            list = []
            for f in request.FILES.getlist('file'):
                if (((size + f.size)/1024) < settings.MMS_SIZE):
                    size+= f.size
                else:
                    list.append(f.name)
            return HttpResponse(simplejson.dumps({"result": True, 'size':size, 'list':list}))

@customer_required
def ajax_filter(request,type=None):
    info(request,"ajax_filter","create queryset of message list")
    if not request.is_ajax():
        warning(request,"ajax_filter","This view is only for ajax")
        raise Http404
    filter = {}
    if (('filter' in request.GET) & (request.GET['filter'] != '')):
        filter = filterQs(request,type)
    if (checkAdmin(request.user)):
        if type ==  MESSAGE_TYPE_INDIVIDUAL:
            filter['mobile__isnull'] = False
        elif type == MESSAGE_TYPE_CHANNEL:
            filter['mobile__isnull'] = True
        qs = Message.objects.filter(**filter).order_by('-creationDate')
    else:
        if type == MESSAGE_TYPE_INDIVIDUAL:
            accs = Account.objects.filter(customer=Customer.objects.get(id=request.user.id))
            filter['account__in'] = accs
            filter['mobile__isnull'] = False
            qs = Message.objects.filter(**filter).order_by('-creationDate')
        elif type == MESSAGE_TYPE_CHANNEL:
            chnls = Channel.objects.filter(customer=Customer.objects.get(id=request.user.id))
            filter['id__in'] = [q.message.id for q in ChannelMessage.objects.filter(channel__in=chnls).order_by('channel')]
            qs = Message.objects.filter(**filter).order_by('-creationDate')
    data = {'data':qs,'type':type}
    return render_to_response(TEMPLATES['ajax_filter'], data, RequestContext( request ) )

def ajax_gen_filter(request,type):
    """

    """
    info(request,"gen_ajax_filter","generate filter to message_list")
    if not request.is_ajax():
        warning(request,"gen_ajax_filter","This view is only access in Ajax mode")
        raise Http404
    if (request.method != 'POST'):
        warning(request,"gen_ajax_filter","This view is only access in POST method")
        raise Http404

    kwargs = {'type':type, 'id':request.user.id}
    form = FilterForm(request.POST,**kwargs)
    if not form.is_valid():
        return HttpResponse(simplejson.dumps({"result": False,'filter':" ", 'ajax': True, 'errors':display_form(form)}))
    filter = ""
    if type == MESSAGE_TYPE_INDIVIDUAL:
        for status in form.cleaned_data['status']:
            filter += ",status:%s" % status
        if form.cleaned_data['mobile'] != '':
            filter += ",mobile:"+form.cleaned_data['mobile']
    else:
        filter += ",channel:%s" % form.cleaned_data['channel']
    if form.cleaned_data['initDate'] != None:
        filter +=",creationDateSince:"+str(form.cleaned_data['initDate']).replace(' ','_').replace(':','-')
    if form.cleaned_data['endDate'] != None:
        filter +=",creationDateUntil:"+str(form.cleaned_data['endDate']).replace(' ','_').replace(':','-')
    if form.cleaned_data['mms'] != None:
        filter +=",mms:"+str(form.cleaned_data['mms'])
    filter = filter[1:len(filter)]
    info(request,"gen_ajax_filter","generate valid filter")
    return HttpResponse(simplejson.dumps({"result": True,'filter':filter,'ajax':True }))

###############################################################################################
# End ajax views
###############################################################################################

def read_message_responses(self, id = None):
    try:
        m = Message.objects.get(pk = id)
    except Message.DoesNotExist:
        raise Http404
    for r in m.responsemessage_set.filter(read = False):
        r.read = True
        r.save()
    return HttpResponse(simplejson.dumps({}))
