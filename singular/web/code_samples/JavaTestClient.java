/*
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
 */

import org.apache.axis.client.Call;
import org.apache.axis.client.Service;
import javax.xml.namespace.QName;

import com.galotecnia.www.soap.*;

public class JavaTestClient {
        public static void main(String [] args) 
                throws java.rmi.RemoteException, javax.xml.rpc.ServiceException
        {
                SingularService_ServiceLocator serviceLocator = new SingularService_ServiceLocator();
                serviceLocator.setSingularServiceEndpointAddress("http://demo.galotecnia.com/singularms/ws/");
                SingularService_PortType singularService = serviceLocator.getSingularService();
                String[] out = singularService.say_hello("Test", 10);
                for (int i = 0; i < out.length; i++) {
                        System.out.println(out[i]);
                }
                /*
                int iout = singularService.sendSMS("username", "password", "account", "34000000000", "Test desde Axis usando WWSS");
                System.out.println("Salida: " + iout);
                */
        }
}
