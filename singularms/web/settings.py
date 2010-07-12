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


# Django settings for SingularMS project.

from django.utils.translation import ugettext_lazy as _
import logging

DEBUG = True
TEMPLATE_DEBUG = DEBUG
FILE_CHARSET = 'utf-8'

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'           # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = '/tmp/singular.db'             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. All choices can be found here:
# http://www.postgresql.org/docs/current/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
TIME_ZONE = 'Atlantic/Canary'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en'

LANGUAGES = (    
    ('en', _('English') ),
    ('es', _('Spanish') ),
)

SITE_ID = 1

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '!d5xg(7jgb%wnh4m%bl$n)d^em2yeec0ix3-!&x*fjt-q^=81v'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.csrf.CsrfResponseMiddleware',
    'email_support.EmailSupport',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates".
    # Always use forward slashes, even on Windows.
	"templates",
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    )

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'manager',
    'accounting',
    'smlog',
    'mt',
    'mo',
    #'django_extensions',
    'pagination',
    'webservice',
    'httpservices',
    'addressbook',
)

#AUTH_PROFILE_MODULE = 'accounting.Provider'

# Send mail on app exception
SEND_MAIL_ON_EXCEPTION = True

# Sender email for all app emails
FROM_EMAIL_ADDRESS = 'singularms-noreply@galotecnia.com'
EMAIL_FROM = FROM_EMAIL_ADDRESS
EMAIL_TO = ['desarrollo@galotecnia.com']

# Send mail on bad incoming message
WRONG_INCOMMING_MESSAGE_EMAIL = 'desarrollo@galotecnia.com'

# Maximun MMS size in KB
MMS_SIZE = 300

# Enable the upload of multiple files in the MMS send form
MMS_MULTI = True

# Extension list of allowed file types for MMS
MMS_FILE_TYPES = ['gif', 'jpg', 'jpeg', 'jpe', 'jfif', 'jfi', 'jif', 'mid', 'midi', \
                  'amr', 'mpeg', '3gpp', 'jad', 'java', 'jar', 'sis', 'rm',]

# Maximun SMS size in characters
SMS_SIZE = 160

# Maximum wait time in seconds for a semaphore
MAX_SEMAPHORE_WAIT = 5.0

# paginate in subscriber
SUBSCRIBER_PAGINATE = 10

# Seconds to resend a message (tmp status)
DEFAULT_DEACTIVATION_TIME = 300

# Days to allow check server status
DEFAULT_CHECK_DAYS = 4

# Secs. to resend in case of connector temp fail
DEFAULT_RETRY_TIME_CONNECTOR_TEMP_FAIL = 300

# Log messages to syslog
LOG_TO_SYSLOG = True

# Credit limits. If any account reach those limits, an email will be sent to EMAIL_CREDIT_LIMIT
MINIMAL_CREDIT_LIMIT = 100
CRITICAL_CREDIT_LIMIT = 10
EMAIL_CREDIT_LIMIT = ['desarrollo@galotecnia.com']

# Log settings
LOG_FILENAME = '/var/log/singularms.log'
LOG_FORMAT = "%(asctime)-15s [%(levelname)s] %(filename)s:%(lineno)s %(message)s"

# Activate addressbook application
ACTIVE_ADDRESS_BOOK = True

TEST_RUNNER = 'xmlrunner.extra.djangotestrunner.run_tests'
TEST_OUTPUT_VERBOSE = True
TEST_OUTPUT_DESCRIPTIONS = True
TEST_OUTPUT_DIR = 'xmlrunner'

PINAX_ROOT = '/opt/galotecnia/pinax/pinax/'
import os
PROJECT_ROOT = os.getcwd()

try:
    from settings_local import *
except ImportError:
    # Not module, so dont load it.
    pass

log = logging.getLogger('galotecnia')
fh = logging.FileHandler(LOG_FILENAME)
fh.setFormatter(logging.Formatter(LOG_FORMAT))
log.addHandler(fh)
log.setLevel(logging.DEBUG)

