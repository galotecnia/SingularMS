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
from django.utils.translation import ugettext_lazy as _

from accounting.models import Account 

from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL

# Homogenizando con los niveles de logging
##ALERT     = 1
#CRITICAL  = 2
#DEBUG     = 3
##EMERGENCY = 4
#ERROR     = 5
#INFO      = 6
##NOTICE    = 7
#WARNING   = 8

# The less the integer, the more the priority
LOGPRIO_LIST = (
    #(ALERT, 'alert'),
    (CRITICAL, 'crit'),
    (DEBUG, 'debug'),
    #(EMERGENCY, 'emerg'),
    (ERROR, 'err'),
    (INFO, 'info'),
    #(NOTICE, 'notice'),
    (WARNING, 'warning'),
    # TODO: documentar esto para saber que significa cada uno
)

class Log(models.Model):
    """
        An entry of log
    """
    date = models.DateTimeField(verbose_name=_('date'), auto_now_add = True, blank = False)
    priority = models.IntegerField(verbose_name=_('priority'), blank = False, choices = LOGPRIO_LIST)
    text = models.CharField (verbose_name=_('text'), max_length = 255, blank = False)
    account = models.ForeignKey(Account, verbose_name=_('account'), null = True, blank = True)

    def __unicode__(self):
        return _("%(date)s (%(priority)s) %(text)s") % {'date':self.date, 'priority':self.priority, 'text':self.text}

    class Meta:
        ordering = ['date']
        verbose_name = _('Log')
        verbose_name_plural = _('Logs')
