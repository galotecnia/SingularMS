#!/usr/bin/python2.5
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

# Python modules
import sys
import signal
import traceback
import threading
import getopt
import logging
import datetime
import optparse
import Queue
import os
import time
from logging.handlers import SysLogHandler
import time

# Django modules
from accounting.models import Account, Purchase, SENT_STATUS, FAIL_STATUS, PROCESSING_STATUS, NONE_STATUS, Access, Capabilities
from mt.models import Message, ChannelMessage, Body, SMSQueue, SMSHistory
from mt.singular_exceptions import OutOfCredit
from mo.models import IncomingMessage
from galotecnia_support import GalotecniaSupport
from connectors.smsexceptions import SMSException
from connectors.smstools import SmsToolConnector
from connectors.dummy import DummyConnector
from connectors.bulk import BulkConnector
from connectors.canarysoft import CanarySoftConnector
from connectors.lleida import LleidaConnector
from connectors.singular import SingularConnector
from django.contrib.auth.models import User
from django.db.models import Q
from django.conf import settings

# Global logger
log = logging.getLogger('singularmsd')

# This must be sync with singularms/web/accounting/models.py
backends = {
    0: DummyConnector,
    1: BulkConnector,
    2: CanarySoftConnector,
    3: SmsToolConnector,
    4: LleidaConnector,
    5: SingularConnector,
}

SMS_CREDIT = 1
MMS_CREDIT = 2

# Days it takes to forward a message when the account has no balance
NEXT_SEND = 1

# Minimum number of seconds that must elapse between retries of message forwarding. 
# This time should never be used, but is defined for the case of finding a message in 
# the queue with a defined ProcessedDate but without NexProcDate
MIN_TIME_TO_RETRY = 600

# If by some chance, we relive more than 10 threads, we will terminate the application.
# By this we avoid, for example, a infinite loop sending SMS
MAX_REVIVED_THREADS = 10

revived_threads = 0 

# Argument parser
def _parse_args():
        usage = "usage: %prog [options]"
        parser = optparse.OptionParser(usage, version="%prog 0.0")
        parser.add_option('-d', '--daemon', dest="daemonMode", action="store_false",
                help="Launch registerd in daemon mode", default = True
            )
        parser.add_option('-v', '--verbose', dest="verbose", action="store_true",
                help="Turn on verbose mode", default = False
            )
        parser.add_option('-p', '--pid-file', dest="pidFile", help="Pid file",
                action="store", type="string", default = '/var/run/singularmsd.pid'
            )
        parser.add_option('-l', '--log-file', dest="logFile", help="Absolute path to log file",
                action="store", type="string", default = '/var/log/singularmsd.log'
            )
        
        return parser.parse_args()

options, args = _parse_args()

def check_revived_treads():
    """
        Super restrictive mode. We control how many threads relive, and if we overcome a threshold, 
        daemon will be killed.
    """
    if revived_threads > MAX_REVIVED_THREADS:
        msg = "ERROR: Raise MAX_REVIVED_THREADS threads: revived_threads: %d" % revived_threads
        log.error(msg)
        g = GalotecniaSupport()
        g.process_error(msg)
        pf = file(options.pidFile, 'r')
        pid = int(pf.read().strip())
        pf.close()
        try:
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(1)
        except IOError, err:
            err = str(err)
            if err.find("No such process") > 0:
                log.info("Leaving daemon...")
                os.remove(options.pidFile)
                sys.exit(0)
            else:
                log.error(str(err))
                sys.exit(1)

def get_traceback(exception):
    exc_info = sys.exc_info()
    msg = "Not managed exception in SingularMs daemon\n"
    msg += '\n'.join(traceback.format_exception(*(exc_info or sys.exc_info())))
    log.error(msg)

class AccountThread(threading.Thread):
    """
        Class for sending. This thread doesn't check perms, only send SMSs and catch exceptions.
    """
    current_threads = 0
    
    def __init__(self, account, parent):
        """
            Constructor, the account and a signal are needed.
        """
        self.account = account
        self.parent = parent
        self.running = True
        AccountThread.current_threads += 1
        self.num_threads = AccountThread.current_threads
        threading.Thread.__init__(self)
        log.info("Initialize AccountThread of account %s", self.account)
        
    def _send_message(self, connector, credit, sq):
        """
            Send a SMS or a MMS using the connector
        """
        args = self.account.args()
        args['account_name'] = "%s" % self.account
        if sq.message.repliable:
            args['repliable'] = "1"
        if credit == MMS_CREDIT:
            return connector.send_mms(sq.message.body.encodedMsg, sq.mobile, sq.message.body.attachment_set.all(), args)
        return connector.send_one(sq.message.body.encodedMsg, sq.mobile, args)

    def _update_credit(self, sq, status):
        # Modify credit
        if status == PROCESSING_STATUS:
            # Keep in the queue
            return
        try:
            if status == FAIL_STATUS:
                self.account.spend_credit(credits = 1, use_available = False)
            else:
                self.account.spend_credit(credits = 1)
        except OutOfCredit, e:
            log.error("Your account doesn't have purchase availables: %s", e)

    def run(self):
        """
            Send sms method. It sends SMS over a given connector (by SMS's account)
        """
        log.info("starting thread in AccountThread")
        n = 0
        while self.parent.running:
            log.info("Waiting for tasks")
            try:
                sq = self.parent.work.get(True, 10)
                n += 1
            except Queue.Empty:
                log.info("No more tasks, empty queue")
                break

            log.info("id %s: start sending %d" % (sq.get_id(), n)) 
            try:
                # KIND OF MESSAGE: SMS | MMS
                credit = SMS_CREDIT
                if sq.message.body.mms:
                    credit = MMS_CREDIT

                local_status = NONE_STATUS
                server_status = NONE_STATUS
                status_info = ''
                batch_id = ''
                today = datetime.datetime.now()
                available_credit = self.account.get_available_credit()
                if not available_credit:
                    # Run out of credit, delay sending process
                    sq.nextProcDate = today + datetime.timedelta(0,settings.DEFAULT_DEACTIVATION_TIME)
                    sq.save()
                    status_info = "Run out of credit, delayed %d day(s)" % NEXT_SEND
                    local_status = PROCESSING_STATUS
                else:
                    if sq.message.activationDate > today:
                        # This message is not active yet
                        sq.nextProcDate = sq.message.activationDate
                        sq.save()
                        status_info = "Sending delayed until activation date"
                        local_status = PROCESSING_STATUS
                    else:
                        # Active message
                        if sq.message.deactivationDate and today > sq.message.deactivationDate:
                            # Expired
                            status_info = "Sending date expired"
                            local_status = FAIL_STATUS
                        else:
                            # Not deactivation date or not sent, we create an instance
                            # of backend (connector) related to this message.
                            GenericConnector = backends[self.account.access.backend]
                            connector = GenericConnector(self.account.args())
                            log.debug("Account connector = %s (%d) is %s", self.account, self.account.id, connector)

                            # Send message
                            server_status, status_info, batch_id = self._send_message(connector, credit, sq)
                            if server_status != NONE_STATUS:
                                local_status = SENT_STATUS
                            else:
                                local_status = PROCESSING_STATUS
                                sq.nextProcDate = today + datetime.timedelta(0,settings.DEFAULT_RETRY_TIME_CONNECTOR_TEMP_FAIL)
                                log.warn("Cannot send the message over his defined connector, it will be retried in a few minutes.") 
                                sq.save()

                log.debug("Status of message %d = (local = %d, server = %d)" % (sq.message.id, local_status, server_status))
                self._update_credit(sq, local_status)
                # Status message updated
                if not sq.message.firstSentDate:
                    sq.message.firstSentDate = datetime.datetime.now()
                sq.message.lastSentDate = datetime.datetime.now()
                sq.message.save()

            except Exception, e:
                #
                # !!PANIC MODE!!
                #
                # Unhandled error. Activate a panic mode. It will mark the local error message 
                # and will be removed from the queue. For this to work the code below should return no exception. 
                # If you enter this code strange things can happen, for example, may have failed to 
                # update the credit and yet having sent the message to the operator. To try to prevent 
                # something worse going to delete the problem message. Also possible that the error is 
                # software that will be marked with all error messages.
                log.error('Fatal error in sending on AccountThread: %s' % e)
                # Forzamos el borrado del mensaje problemático
                local_status = FAIL_STATUS
                if not status_info:
                    status_info = "A falta error has happened when daemon tried to send %s over this AccountThread" % sq
                g = GalotecniaSupport()
                g.process_exception('Sending process over singularms daemon', e)
                get_traceback(e)
            
            # MessageID_smsqueueID saved before object will be deleted
            id = sq.get_id()

            # Delete smsqueue (if it doesn't have to be fowarded again)
            if local_status != PROCESSING_STATUS:
                log.info("Deleting SMSQueue object id: %d" % sq.id)
                sq.delete()
            
            # Temporal SMSHistory data
            message = sq.message
            mobile = sq.mobile
            priority = sq.priority

            # SMSHistory object creation. Write errors, sent time, sq.id and local_id about it
            sh = SMSHistory(message = message, mobile = mobile, priority = priority, 
                sentDate = datetime.datetime.now(), local_id = id, remote_id = batch_id, 
                local_status = local_status, status_info = status_info[:255], server_status = server_status)
            sh.save()

            # Task done. If this thread die before now, when parent thread calls join() method it will
            # be blocked
            self.parent.work.task_done()          

            # Main loop can continue
            log.debug("id %s: end sending" % id)
 
        log.info("ending thread (sent %d messages)" % n)

class AccountGroup(threading.Thread):
    """
        Sending threads (and their status) of a given account. Dont check perms
    """
    
    def __init__(self, account):
        """
            An account needed if we want to create his children thread.
        """
        self.account = account
        self.event = threading.Event()
        self.running = True
        self.work = Queue.Queue()
        self.lock = threading.Lock()
        log.info("Starting AccountGroup %s", self.account)
        self.threads = [None] * self.account.num_threads
        threading.Thread.__init__(self)
    
    def process_from_queue(self):
        """
            Extract up to 20 messages.
        """
        today = datetime.datetime.today()
        # Check account messages wich process date has not been defined or it has already happend.
        query = SMSQueue.objects.filter(
                Q(message__account = self.account.id) &
                (Q(nextProcDate__isnull = True) | Q(nextProcDate__lte = today))                      
            ).order_by('queueDate')
        n = min(20, len(query))
        if n == 0:
            log.info("All taks queued in AccountGroup")
            return False
        log.debug("Queueing (sent %d messages) in AccountGroup" % n)
        for m in query[:n]:
            m.processedDate = datetime.datetime.now()
            m.save()
            self.work.put(m)
        return True

    def check_account_updates(self):
        """
            Check if there was any changes on DDBB for this Account.
            In a positive case, a data update will be done.
        """
        try:
            acc_in_db = Account.objects.get(id = self.account.id)
        except Account.DoesNotExist:
            # Account doesn't not exist
            log.error("Se ha eliminado la cuenta %s mientras se estaba ejecutando el AccountGroup", self.account)
            return False

        # Thread number changes
        if acc_in_db.num_threads != self.account.num_threads or \
           acc_in_db.args2 != self.account.args2 or \
           acc_in_db.access != self.account.access:
            # Queue argument changes
            log.info("Account %s has changed in DDBB", acc_in_db)
            if acc_in_db.num_threads < self.account.num_threads:
                # Killing the remaining threads... 
                num_threads = len(self.threads)
                remaining_threads = num_threads - acc_in_db.num_threads
                log.info("%d threads killed on account %s", remaining_threads, self.account)
                for i in range(remaining_threads):
                    # FIXME: check if thread is dead if we dont want to leave system 
                    # in an inconsistent status.
                    del self.threads[-1]

            self.account = acc_in_db
        
    def create_accountThreads(self):
        """
            Create AccountThread group configured for this account.
            Num_threads variable controls the number of threads to create.
        """
        # We won't want to do this here anymore
        # self.check_account_updates()
        for i in range(self.account.num_threads):
            if not self.threads[i] or not self.threads[i].isAlive():
                self.threads[i] = AccountThread(self.account, self)
                log.info("Starting thread %d in AccountGroup" % self.threads[i].num_threads)
                self.threads[i].start()
            else:
                log.info("Reusing thread %d in AccountGroup" % self.threads[i].num_threads)

    def stop_threads(self):
        for h in self.threads:
            if h and h.isAlive():
                h.join()

    def watchdog(self):
        """
            We ensure that no one thread is dead. If this occurs, it has to be
            ensured that the work he had taken is marked as done because
            if we do not block the call work.join ().
            normally this is a very serious mistake, because it probably becomes
            to create the thread to exit the loop and we will be cycling to infinity.
        """
        global revived_threads
        while self.work.qsize() > 0 or self.work.unfinished_tasks > 0:
            count = 0
            time.sleep(0.5)
            # FIXME:
            # - There are no work unfinished: 
            #   -> DO NOTHING
            # - There are work unfinished:
            #   * All threads are dead:
            #     -> TODO: Relive at least one of the threads to finish left tasks, or
            #     -> TODO: Mark all tasks as done
            #   * At least one thread alive:
            #     -> continue
            if self.work.qsize() == 0 and self.work.unfinished_tasks > 0:
                # We have no finish taks, check if all threads are dead.
                for h in self.threads:
                    if not h.isAlive():
                       count += 1
                if count != len(self.threads):
                    continue
                # If all threads are dead
                for i in range(self.work.unfinished_tasks):
                    log.error('Mark task as done by thread dead. Qsize: %d. Unfinished tasks: %d', self.work.qsize(), self.work.unfinished_tasks)
                    self.work.task_done()
                    log.error("Reliving AccountThread")
                    revived_threads += 1
                    check_revived_treads()

    def run(self):
        """
            Start a worker thread to send an sms, if permitted. Returns True if you have to retry.
        """
        while self.running:
            log.info("Waiting for new messages in AccountGroup")

            # Block until schedule wants to wake this up (call event.set())
            self.event.wait()
            # Set flag to FALSE, so next call to wait() won't block this thread
            self.event.clear() 

            # Stop set running to FALSE, so it wakes this thread up
            if not self.running: break

            # Check if anyone sent a stop signal while thread was alive
            while self.running:

                # Check if account arguments have changed since last call
                self.check_account_updates()

                # Pop a task row from the queue
                if not self.process_from_queue():
                    log.debug("No hay trabajo, hay que esperar por mas trabajo")
                    # No more tasks. Wait for new tasks
                    break
    
                # Awake threads to run all new tasks
                self.create_accountThreads()

                # Check if all threads are alive        
                log.debug("si hay trabajo, por lo que esperamos a que el trabajo se cumpla")
                self.watchdog()

                # Wait until all threads mark their jobs as done
                log.debug("Wait until all threads mark their jobs as done in %s AccountGroup", self.account)
                self.work.join()
                log.debug("All threads marked their jobs as done in %s AccountGroup", self.account) 

            log.info("Waiting in AccountGroup for childs job's finalization")

            # Wait until AccountThreads finish their job
            self.work.join()

        # Stop signal received. We stop (self.running to FALSE)
        self.stop_threads()

    def stop(self):
        self.running = False
        self.event.set()

class AccessConsulter(threading.Thread):

    def __init__(self, access):
        self.access = access
        threading.Thread.__init__(self)
        self.conector = backends[self.access.backend](self.access.args())

    def update_incoming_list(self):
        # PANIC MODE: This function cannot be blocked
        try:
            # Process unprocessed messages (because a daemon fail happended)
            self.process_unprocessed_msgs()
            log.debug("Checking if there are new incoming messages in %s", self.access)
            # Updating incoming message list and start to process new messages
            self.conector.decode(self.access)
        except Exception, e:
            # An unhandled exception in process message happened
            log.error("Access thread %s has failed trying to update incoming messages because %s", self.access, e)
            get_traceback(e)
            g = GalotecniaSupport()
            g.process_exception('Updating incoming messages', e)

    def process_unprocessed_msgs(self):
        """
            Processes associated messages that were not processed
            Useful in cases where, after devil fails, we want to retrieve the state in which
            stayed (in the event that access is required to process the incoming messages)
        """
        if 'process' in self.access.args():
            for no_proc_imsg in IncomingMessage.objects.filter(account__in = self.access.account_set.all(), processed = False):
                try:
                    self.conector.encode(no_proc_imsg)
                except Exception, e:
                    log.error("Error: trying to process %s message in %s access, %s", no_proc_imsg, self.access, e)
                    get_traceback(e)
                    g = GalotecniaSupport()
                    g.process_exception('Error while processing a incoming message', e)
                # If there is no fault to be processed by the system load is not generated more
                # and is marked as processed without processing date, so you can
                # retrieve the messages that failed because they have no processing time
                if not no_proc_imsg.processed:
                    no_proc_imsg.processed = True
                    no_proc_imsg.save()

    def run(self):
        log.info("AccessConsulter for access %s started", self.access)
        self.running = True
        while self.running:
            self.update_incoming_list()
            time.sleep(120) # Update each 2 minutes

    def stop(self):
        self.running = False
        
class MessageReceiver(threading.Thread):
    """
        This class awake all threads in order to receive incoming messages
    """

    def __init__(self):
        self.access_groups = {}
        threading.Thread.__init__(self)

    def create_access_groups(self):
        # Consult the list of incoming configured accesses
        db_accs = Access.objects.filter(capabilities__in = [Capabilities.objects.get(typeSMS = 'Repliable')])
        for access in db_accs:
            # If there are not created an AccessConsulter for the current access or 
            # the thread is dead or args have changed
            if access.id not in self.access_groups.keys() or \
               not self.access_groups[access.id].isAlive() or \
               access.args1 != self.access_groups[access.id].access.args1:
                ac = AccessConsulter(access)
                ac.start()
                self.access_groups[access.id] = ac
                log.info("Access %d: startert in MessageReceiver", access.id)
        if db_accs.count() < len(self.access_groups):
            db_ids = [a.id for a in db_accs]
            for k,v in self.access_groups.items():
                if k not in db_ids:
                    log.info("Access thread %s is going to be deleted", v.access)
                    v.stop()
                    del self.access_groups[k]

    def run(self):
        log.info("MessageReceiver started")
        self.running = True
        while self.running:
            self.create_access_groups()
            time.sleep(300) # Checking thread status each 5 minutes

    def stop (self):
        self.running = False

class MessageScheduler(threading.Thread):
    """
        This class sleeps for one minute, then check if there is any new accounts to be created.
        Then, check if there is any message waiting to be sent. If there is any message to be sent the class
        activate the proper account_groups to do the job.
    """

    def __init__(self, account_groups):
        # account_groups must be a dictionary with all account ids (by default, empty)
        self.account_groups = account_groups
        threading.Thread.__init__(self)

    def create_account_groups(self):
        db_accs = Account.objects.all()
        for account in db_accs:
            if account.id not in self.account_groups.keys() or not self.account_groups[account.id].isAlive():
                ag = AccountGroup(account)
                ag.start()
                self.account_groups[account.id] = ag
                log.info("Group %d: started in MessageScheduler" % ag.account.id)

        if db_accs.count() < len(self.account_groups):
            db_ids = [a.id for a in db_accs]
            for k,v in self.account_groups.items():
                if k not in db_ids:
                    log.info("Account thread %s is going to be deleted", v.account)
                    v.stop()
                    del self.account_groups[k]

    def enqueue_messages(self):
        """
            We need to search channel messages to create new SMSQueue objects.
        """
        now = datetime.datetime.now()
        ag_to_awake = []

        # If daemon fails while is sending messages it is posible some of the messages
        # stay in the queue like processed but no sent, so they must be putted in the queue
        # again.
        account_list = SMSQueue.objects.filter(
            (Q(nextProcDate__isnull = True) | Q(nextProcDate__lt = now))                      
            ).values_list('message__account', flat = True)
        for a in account_list:
            a = int(a)
            if not a in ag_to_awake:
                log.info('The account %s has some SMS pending in the queue' % a)
                ag_to_awake.append(a)

        # Check message list, putting those new or active messages in the queue. Also
        # we awake the group of threads for each account.
        for message in Message.objects.filter(Q(processed = False) & Q(activationDate__lte = now) & 
                (Q(deactivationDate__isnull = True) | Q(deactivationDate__gt = now))):
            log.debug("Calling put_in_the_queue")
            ids = message.put_in_the_queue()
            log.debug("Messages in the queue: %d" % len(ids))
            if not message.account.id in ag_to_awake:
                ag_to_awake.append(message.account.id)

        for account in ag_to_awake:
            try:
                # PANIC MODE!!!
                if self.account_groups[account].event.isSet():
                    continue
                # Awaking AccountGroup thread
                log.info("Awaiking the Account Group for the account: %d" % account)
                self.account_groups[account].event.set()
            except AttributeError:
                # PANIC MODE!!!
                # If AccountGroup has not been created yet, we take care in MessageScheduler
                log.error("Intentando despertar un hilo que no tiene evento creado para la cuenta %s", account)
                

    def run(self):
        log.info("MessageScheduler started")
        self.running = True
        while self.running:
            self.create_account_groups()
            self.enqueue_messages()
            time.sleep(10)

    def stop (self):
        self.running = False

class MessageConsulter(threading.Thread):
    """
        This class check all message sent status, looking for them in SMSHistory 
        msg status equals to PROCESS_STATUS
    """

    def __init__(self):
        threading.Thread.__init__(self)

    def check_processing_msg_list(self):
        connectors_dict = {}
        now = datetime.datetime.now()
        top = now - datetime.timedelta(settings.DEFAULT_CHECK_DAYS)

        # Obtenemos la lista de mensajes que tienen estado temporal en el servidor
        query = SMSHistory.objects.filter(server_status__in = [NONE_STATUS, PROCESSING_STATUS], local_status = SENT_STATUS, 
                    sentDate__gte = top).order_by('sentDate')
        log.info("MessageConsulter: Consulting a list of %d messages" % len(query))
        i = 0
        for msg in query:
            status = NONE_STATUS
            try:
                # PANIC MODE!!!
                log.debug("History %d: updating status" % msg.id)
                acc_id = msg.message.account.id
                
                # Checking if message account is on memory, otherwise we add it
                if not connectors_dict.has_key(acc_id):
                    backend = msg.message.account.access.backend
                    GenericConnector = backends[backend]
                    connector = GenericConnector(msg.message.account.args())
                    connectors_dict[acc_id] = connector
                con = connectors_dict[acc_id]

                # Checking msg status, we only take first object
                [status, info] = con.get_info(msg.remote_id)[0]
                msg.server_status = status
                msg.status_info = info

                # If we got a valid status, we update send date field of msg
                if status != NONE_STATUS and status != PROCESSING_STATUS:
                    msg.sentDate = datetime.datetime.now()
                log.debug("History %s: setting server status to %s" %(msg.id, msg.server_status))
                msg.save()

            except Exception, e:
                # PANIC MODE!!!
                # If checking status proccess fails (because connector error, status
                # consult error, or while saving the msg), we continue with next task
                log.error("Error al consultar el estado del mensaje %s", msg.id)
                get_traceback(e)
                g = GalotecniaSupport()
                g.process_exception('Actualizacion del estado de mensajes', e)
    
            # Not a valid status
            if status == PROCESSING_STATUS:
                i += 1
                # Every 25 not valid consults, we wait a while
                if i % 25 == 0: 
                    time.sleep(30)

    def run(self):
        log.info("Check status of sent messages process started")
        self.running = True
        while self.running:
            self.check_processing_msg_list()
            time.sleep(300)

    def stop (self):
        self.running = False


class SingularMSD:
    pidfile = options.pidFile
    stdin = "/dev/null"
    stdout = options.logFile

    def __init__(self):
        pass

    def run(self):
        log.info("Starting SingularMSD...")
        try:
            ags = {}
            receiver = MessageReceiver()
            receiver.start()
            consulter = MessageConsulter()
            consulter.start()
            scheduler = MessageScheduler(ags)
            scheduler.start()
        except KeyboardInterrupt:
            log.info("Quitting main thread in SingularMSD...")
        except:
            log.critical("Fatal Exception: %s", traceback.format_exc())

if __name__ == "__main__":

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(filename)s:%(lineno)s [%(thread)d] %(message)s")
    fh = logging.FileHandler(options.logFile)
    fh.setFormatter(fmt)
    log.addHandler(fh)

    handler = SysLogHandler('/dev/log')
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(fmt)
    log.addHandler(handler)

    log.setLevel(logging.INFO)
    if options.verbose:
        log.setLevel(logging.DEBUG)
    log.debug('Setting up logging system...')
    
    s = SingularMSD()
    if options.daemonMode:
        import daemon
        daemon.Daemon(s)
    else:
        s.run()

