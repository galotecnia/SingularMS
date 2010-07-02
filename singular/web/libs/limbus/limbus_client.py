# -*- encoding: utf-8 -*-

# Include all client libraries here
from suds.client import Client as SudsClient
from SOAPpy.WSDL import Proxy as SOAPpyClient

# Generic Limbus Client
class LimbusClient:
    
    def get_service_list(self):
        """
            List all services
        """
        pass

    def get_argument_list(self, service):
        """
            List all arguments and types of a given service
        """
        pass
    
    def get_argument_type(self, service, argument):
        """
            Get argument type given an argument and a service
        """
        pass
    
    def get_return_type(self, service):
        """
            Get the return type of a given service
        """
        pass
    
# Suds Client Adaption
class LimbusSudsClient(SudsClient, LimbusClient): 

    def __init__(self, *args, **kwargs):
        super(LimbusSudsClient, self).__init__(*args, **kwargs)
        # Setup methods 
        self.__set_call_methods()

    ####################
    # Override methods #
    ####################
    def get_service_list(self):
        """
            Given a suds client, get methods list from wsdl.
        """
        out = []
        for p in self.sd[0].ports:
            for m in p[1]:
                out.append('%s' % m[0])
        return out 

    def get_argument_list(self, service):
        """
            List all arguments of a given service
        """
        out = {}
        for p in self.sd[0].ports:
            for m in p[1]:
                # Check service name
                if m[0] == service:
                    for a in m[1]:
                        out[u'%s' % a[0]] = a[1].type[0]
                    return out
        return out
    
    def get_argument_type(self, service, argument):
        """
            Get argument type given an argument an a service
        """
        for k,v in self.get_argument_list(service):
            if argument == k:
                return v
        return None


    ################################
    # Setup and adaptation methods #
    ################################
    def __set_call_methods(self):
        """
            First get all client methods in order to set them as
            class methods
        """
        for method_name in self.get_service_list():
            method = self.service.__getattr__(method_name)
            setattr(LimbusSudsClient, method_name, method)

class LimbusSOAPpyClient(SOAPpyClient, LimbusClient):
        
    ####################
    # Override methods #
    ####################
    def get_service_list(self):
        """
            Given a suds client, get methods list from wsdl.
        """
        out = [k for k in self.methods]
        return out
