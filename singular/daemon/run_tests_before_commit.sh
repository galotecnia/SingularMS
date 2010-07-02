#!/bin/sh
. /opt/pinax-env/bin/activate
WD=$(pwd)
export DJANGO_SETTINGS_MODULE=settings
export PYTHONPATH=$WD/../web:$WD/../web/apps
echo $PATH
cd ../web/
python manage.py test manager
