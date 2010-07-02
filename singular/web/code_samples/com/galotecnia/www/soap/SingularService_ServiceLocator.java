/**
 * SingularService_ServiceLocator.java
 *
 * This file was auto-generated from WSDL
 * by the Apache Axis 1.4 Apr 22, 2006 (06:55:48 PDT) WSDL2Java emitter.
 */

package com.galotecnia.www.soap;

public class SingularService_ServiceLocator extends org.apache.axis.client.Service implements com.galotecnia.www.soap.SingularService_Service {

    public SingularService_ServiceLocator() {
    }


    public SingularService_ServiceLocator(org.apache.axis.EngineConfiguration config) {
        super(config);
    }

    public SingularService_ServiceLocator(java.lang.String wsdlLoc, javax.xml.namespace.QName sName) throws javax.xml.rpc.ServiceException {
        super(wsdlLoc, sName);
    }

    // Use to get a proxy class for SingularService
    private java.lang.String SingularService_address = "http://singularms/singularms/ws/service";

    public java.lang.String getSingularServiceAddress() {
        return SingularService_address;
    }

    // The WSDD service name defaults to the port name.
    private java.lang.String SingularServiceWSDDServiceName = "SingularService";

    public java.lang.String getSingularServiceWSDDServiceName() {
        return SingularServiceWSDDServiceName;
    }

    public void setSingularServiceWSDDServiceName(java.lang.String name) {
        SingularServiceWSDDServiceName = name;
    }

    public com.galotecnia.www.soap.SingularService_PortType getSingularService() throws javax.xml.rpc.ServiceException {
       java.net.URL endpoint;
        try {
            endpoint = new java.net.URL(SingularService_address);
        }
        catch (java.net.MalformedURLException e) {
            throw new javax.xml.rpc.ServiceException(e);
        }
        return getSingularService(endpoint);
    }

    public com.galotecnia.www.soap.SingularService_PortType getSingularService(java.net.URL portAddress) throws javax.xml.rpc.ServiceException {
        try {
            com.galotecnia.www.soap.SingularService_BindingStub _stub = new com.galotecnia.www.soap.SingularService_BindingStub(portAddress, this);
            _stub.setPortName(getSingularServiceWSDDServiceName());
            return _stub;
        }
        catch (org.apache.axis.AxisFault e) {
            return null;
        }
    }

    public void setSingularServiceEndpointAddress(java.lang.String address) {
        SingularService_address = address;
    }

    /**
     * For the given interface, get the stub implementation.
     * If this service has no port for the given interface,
     * then ServiceException is thrown.
     */
    public java.rmi.Remote getPort(Class serviceEndpointInterface) throws javax.xml.rpc.ServiceException {
        try {
            if (com.galotecnia.www.soap.SingularService_PortType.class.isAssignableFrom(serviceEndpointInterface)) {
                com.galotecnia.www.soap.SingularService_BindingStub _stub = new com.galotecnia.www.soap.SingularService_BindingStub(new java.net.URL(SingularService_address), this);
                _stub.setPortName(getSingularServiceWSDDServiceName());
                return _stub;
            }
        }
        catch (java.lang.Throwable t) {
            throw new javax.xml.rpc.ServiceException(t);
        }
        throw new javax.xml.rpc.ServiceException("There is no stub implementation for the interface:  " + (serviceEndpointInterface == null ? "null" : serviceEndpointInterface.getName()));
    }

    /**
     * For the given interface, get the stub implementation.
     * If this service has no port for the given interface,
     * then ServiceException is thrown.
     */
    public java.rmi.Remote getPort(javax.xml.namespace.QName portName, Class serviceEndpointInterface) throws javax.xml.rpc.ServiceException {
        if (portName == null) {
            return getPort(serviceEndpointInterface);
        }
        java.lang.String inputPortName = portName.getLocalPart();
        if ("SingularService".equals(inputPortName)) {
            return getSingularService();
        }
        else  {
            java.rmi.Remote _stub = getPort(serviceEndpointInterface);
            ((org.apache.axis.client.Stub) _stub).setPortName(portName);
            return _stub;
        }
    }

    public javax.xml.namespace.QName getServiceName() {
        return new javax.xml.namespace.QName("http://www.galotecnia.com/soap/", "SingularService");
    }

    private java.util.HashSet ports = null;

    public java.util.Iterator getPorts() {
        if (ports == null) {
            ports = new java.util.HashSet();
            ports.add(new javax.xml.namespace.QName("http://www.galotecnia.com/soap/", "SingularService"));
        }
        return ports.iterator();
    }

    /**
    * Set the endpoint address for the specified port name.
    */
    public void setEndpointAddress(java.lang.String portName, java.lang.String address) throws javax.xml.rpc.ServiceException {
        
if ("SingularService".equals(portName)) {
            setSingularServiceEndpointAddress(address);
        }
        else 
{ // Unknown Port Name
            throw new javax.xml.rpc.ServiceException(" Cannot set Endpoint Address for Unknown Port" + portName);
        }
    }

    /**
    * Set the endpoint address for the specified port name.
    */
    public void setEndpointAddress(javax.xml.namespace.QName portName, java.lang.String address) throws javax.xml.rpc.ServiceException {
        setEndpointAddress(portName.getLocalPart(), address);
    }

}
