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

from posix_ipc import Semaphore, O_CREAT, BusyError
from django.conf import settings
import logging

log = logging.getLogger('galotecnia')

class Sem(Semaphore):
    def __init__(self, name):
        super(Sem, self).__init__(name = name, flags = O_CREAT, mode = 0666, initial_value = 1)
        try:
            self.acquire(settings.MAX_SEMAPHORE_WAIT)
        except BusyError:
            log.warning ("Max wait time reached for %s", name)

    def destroy(self):
        self.release()
        self.close()

