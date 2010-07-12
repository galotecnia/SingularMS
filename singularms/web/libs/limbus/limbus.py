# -*- encoding: utf-8 -*-

####################################################################
from limbus_client import LimbusSudsClient, LimbusSOAPpyClient
from limbus_server import LimbusSoaplibServer
####################################################################
    
CLIENT_TYPES_DICT = {
    # Put your limbus client class here
    'suds': LimbusSudsClient,
    'soappy': LimbusSOAPpyClient,
}

def get_limbus_client(client_type = 'suds'):
    if client_type.lower() in CLIENT_TYPES_DICT:
        return CLIENT_TYPES_DICT[client_type.lower()]
    return None

SERVER_TYPES_DICT = {
    # Put your limbus server class here
    'soaplib': LimbusSoaplibServer,
}

def get_limbus_server(server_type = ''):
    if server_type.lower() in SERVER_TYPES_DICT:
        return SERVER_TYPES_DICT[server_type.lower()]
    return None
