# -*- encoding: utf-8 -*-

# Include all server libraries here
from soaplib.wsgi_soap import SimpleWSGISoapApp as SoaplibServer

# Generic Limbus Server
class LimbusServer:
    pass
    
# Soaplib Server Adaption
class LimbusSoaplibServer(SoaplibServer, LimbusServer): 
    pass

