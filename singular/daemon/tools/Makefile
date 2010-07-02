FILES2TRANS = singularms_client smstool_event_handler.py 
POTFILE = locale/es/LC_MESSAGES/message.pot
POFILE = locale/es/LC_MESSAGES/daemon_tools.po
MOFILE = locale/es/LC_MESSAGES/daemon_tools.mo
EXTRACT = xgettext
EXTARGS = -L Python --from-code=UTF-8
UPDATE = msgmerge
COMPILE = msgfmt

all: translate

translate: extract update compile

extract: $(FILES2TRANS)
	$(EXTRACT) $(EXTARGS) -o $(POTFILE) $?

update: $(POTFILE)
	$(UPDATE) -U  $(POFILE) $?
	rm $(POTFILE)

compile: $(POFILE)
	$(COMPILE) -o $(MOFILE) $?
