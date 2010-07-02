
#!/usr/bin/python

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

import unittest
import coverage
import glob

from mocker import Mocker
from mocker import Mock
from mocker import expect
from mocker import ARGS
from mocker import KWARGS
from mocker import ANY


import smstool_event_handler
 
class SMSToolEventHandlerTests (unittest.TestCase):
 
    def setUp(self):
        self.mocker = Mocker()
        self.event_handler = smstool_event_handler.SmsToolEventHandler ([])
 
    def tearDown(self):
        self.mocker.restore()

    def test_parse_sms_ok_files (self):
        for file in glob.glob ('./sms_test_files/GSM*'):
            self.event_handler.headers = {}
            self.event_handler.text = ''
            self.event_handler.filename = file
            self.event_handler.parse_sms_file ()
            if self.event_handler.text == '':
                self.fail ("Coud not parse %s correctly" % file)

    def test_wrong_files (self):
        for file in glob.glob ('./sms_test_files/BADGSM*'):
            self.event_handler.filename = file
            self.assertRaises (ValueError, self.event_handler.parse_sms_file)

    def test_input_parser_wrong_param_numbers (self):
        wrong_argv = ['one', 'two', 'three', 'four', 'five' ]
        self.event_handler.argv = wrong_argv
        self.assertRaises (ValueError, self.event_handler.input_parser)
        wrong_argv = ['one', 'two', 'three']
        self.event_handler.argv = wrong_argv
        self.assertRaises (ValueError, self.event_handler.input_parser)

    def test_input_parser_wrong_event (self):
        wrong_argv = ['smstool_event_handler', 'WrongEvent', 'filename', 'id']
        self.event_handler.argv = wrong_argv
        self.assertRaises (ValueError, self.event_handler.input_parser)

    def test_input_parser_ok_event_SENT (self):
        argv = ['smstool_event_handler', 'SENT', 'filename', 'id']
        self.event_handler.argv = argv
        self.event_handler.input_parser()
        self.assertEqual (self.event_handler.event, 'SENT')
        self.assertEqual (self.event_handler.filename, 'filename')
        self.assertEqual (self.event_handler.message_id, 'id')

    def test_input_parser_ok_event_FAILED (self):
        argv = ['smstool_event_handler', 'FAILED', 'filename', 'id']
        self.event_handler.argv = argv
        self.event_handler.input_parser()
        self.assertEqual (self.event_handler.event, 'FAILED')
        self.assertEqual (self.event_handler.filename, 'filename')
        self.assertEqual (self.event_handler.message_id, 'id')

    def test_input_parser_ok_event_RECEIVED (self):
        argv = ['smstool_event_handler', 'RECEIVED', 'filename']
        self.event_handler.argv = argv
        self.event_handler.input_parser()
        self.assertEqual (self.event_handler.event, 'RECEIVED')
        self.assertEqual (self.event_handler.filename, 'filename')

    def test_input_parser_ok_event_REPORT (self):
        argv = ['smstool_event_handler', 'REPORT', 'filename', 'id']
        self.event_handler.argv = argv
        self.event_handler.input_parser()
        self.assertEqual (self.event_handler.event, 'REPORT')
        self.assertEqual (self.event_handler.filename, 'filename')
        self.assertEqual (self.event_handler.message_id, 'id')

    def test_load_config_ok (self):
        self.event_handler.config_file = './smstool_event_handler.conf'
        self.event_handler.load_config()
        self.assertEqual ('pepito', self.event_handler.username)
        self.assertEqual ('password', self.event_handler.password)
        self.assertEqual ('TestAccess', self.event_handler.access)
        self.assertEqual ('http://localhost:8080/', self.event_handler.server_url)

    def test_load_config_ko (self):
        self.event_handler.config_file = './smstool_event_handler_test_wrong.conf'
        self.assertRaises (ValueError, self.event_handler.load_config)

    def test_load_config_not_found (self):
        self.event_handler.config_file = './no_config_file.conf'
        self.assertRaises (ValueError, self.event_handler.load_config)

    def test_dispatch_SENT_event (self):
        dummy_SOAPpy= self.mocker.replace('SOAPpy')
        dummy_SOAPpy.SOAPProxy (ANY)
        self.mocker.count (1)
        self.mocker.result (True)
        self.mocker.replay ()

        argv = ['smstool_event_handler', 'SENT', './sms_test_files/singularmszhwabc.sms', '1JyoAT']
        event_handler = smstool_event_handler.SmsToolEventHandler (argv, './smstool_event_handler.conf')
        event_handler.dispatch ()
        self.mocker.verify()


    def test_dispatch_RECEIVED_event (self):
        dummy_server = self.mocker.mock ()
        dummy_SOAPpy= self.mocker.replace('SOAPpy')
        dummy_SOAPpy.SOAPProxy (ANY)
        self.mocker.count (1)
        self.mocker.result (dummy_server)

        dummy_server.receiveSMS(ARGS, KWARGS)
        self.mocker.count (1)
        self.mocker.result (True)
        self.mocker.replay ()

        argv = ['smstool_event_handler', 'RECEIVED', './sms_test_files/GSM1.M1h8yB']
        event_handler = smstool_event_handler.SmsToolEventHandler (argv, './smstool_event_handler.conf')
        event_handler.dispatch ()
        self.mocker.verify()

    def test_dispatch_FAILED_event (self):
        dummy_SOAPpy= self.mocker.replace('SOAPpy')
        dummy_SOAPpy.SOAPProxy (ANY)
        self.mocker.count (1)
        self.mocker.result (True)
        self.mocker.replay ()

        argv = ['smstool_event_handler', 'FAILED', './sms_test_files/GSM1.M1h8yB', '1JyoAT']
        event_handler = smstool_event_handler.SmsToolEventHandler (argv, './smstool_event_handler.conf')
        event_handler.dispatch ()
        self.mocker.verify()

    def test_dispatch_REPORT_event (self):
        dummy_SOAPpy= self.mocker.replace('SOAPpy')
        dummy_SOAPpy.SOAPProxy (ANY)
        self.mocker.count (1)
        self.mocker.result (True)
        self.mocker.replay ()

        argv = ['smstool_event_handler', 'REPORT', './sms_test_files/GSM1.M1h8yB', '1JyoAT']
        event_handler = smstool_event_handler.SmsToolEventHandler (argv, './smstool_event_handler.conf')
        event_handler.dispatch ()
        self.mocker.verify()

if __name__ == '__main__':
    try:
        coverage.use_cache(False)
        coverage.erase()
        coverage.start()
        reload(smstool_event_handler)
        try:
            unittest.main()
        finally:
            coverage.stop()
            coverage.report(smstool_event_handler)
    except ImportError:
        unittest.main()
