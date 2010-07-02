from django.conf import settings

try:
	if settings.RRD_PATH is None:
		RRD_PATH = '/tmp/'
	else:
		RRD_PATH = settings.RRD_PATH
except AttributeError:
	RRD_PATH = '/tmp/'

try:
	if settings.GRAPH_TTL is None:
		GRAPH_TTL = 1
	else:
		GRAPH_TTL = settings.GRAPH_TTL
except AttributeError:
	GRAPH_TTL = 1

# seconds between alarms
try:
	if settings.ALARM_REPEAT_INTERVAL is None:
		ALARM_REPEAT_INTERVAL = 3600
	else:
		ALARM_REPEAT_INTERVAL = settings.ALARM_REPEAT_INTERVAL
except AttributeError:
	ALARM_REPEAT_INTERVAL = 3600

# seconds between malfunctions alarms
try:
	if settings.MALFUNCTION_REPEAT_INTERVAL is None:
		MALFUNCTION_REPEAT_INTERVAL = 3600
	else:
		MALFUNCTION_REPEAT_INTERVAL = settings.MALFUNCTION_REPEAT_INTERVAL
except AttributeError:
	MALFUNCTION_REPEAT_INTERVAL = 3600
