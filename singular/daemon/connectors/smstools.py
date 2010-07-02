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


from connectors.base import Connector
from connectors.base import utf8_to_gsm
import time
import datetime
import random
import tempfile


class SmsToolConnector(Connector):
    SPOOL = "/var/spool/sms/"
    SMSTemplate = """To: %s

%s
"""
    def __init__(self, args):
        self.out_dir = args['out_dir']
        self.in_dir = args['in_dir']

    def send_one(self, text, recipient, args):
        filename = tempfile.mktemp('.sms', 'singularms', self.out_dir)
        open(filename, 'w').write(utf8_to_gsm (SmsToolConnector.SMSTemplate % (recipient, text)))
        id = filename[len (self.out_dir + "/singularms"):-1 * len ('.sms')]
        return self.PROCESSING, id

    def send_many(self, text, recipients, args):
        for r in recipients:
            self.send_one (text, r)
        return self.PROCESSING, random.randrange(1, 999999999999999)

    def get_info(self, id):
        status = random.choice ([self.SENT, self.FAILED, self.PROCESSING])
        if status == self.PROCESSING:
            return (status, None)
        return (status, datetime.datetime.now ())

    def get_credit(self):
        return 999
