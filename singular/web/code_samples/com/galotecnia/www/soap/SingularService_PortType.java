/**
 * SingularService_PortType.java
 *
 * This file was auto-generated from WSDL
 * by the Apache Axis 1.4 Apr 22, 2006 (06:55:48 PDT) WSDL2Java emitter.
 */

package com.galotecnia.www.soap;

public interface SingularService_PortType extends java.rmi.Remote {
    public java.lang.String[] say_hello(java.lang.String name, int times) throws java.rmi.RemoteException;

    /**
     * EnvÃ­a un mensaje de texto a un nÃºmero un texto, con una cuenta
     * determinada
     */
    public int sendSMS(java.lang.String username, java.lang.String password, java.lang.String account, java.lang.String phoneNumber, java.lang.String text) throws java.rmi.RemoteException;
}
