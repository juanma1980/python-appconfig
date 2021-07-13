import QtQuick 2.6
import "LoginAuth" as N4dLogin 
import Edupals.N4D.Agent 1.0 as N4DAgent

Rectangle {
    id: dialog
    width: 400
    height: 320
	property string address: qsTr("%1").arg(server)

    N4dLogin.Login
    {
		id: root
        showCancel: false
        inGroups:["sudo","admins","teachers"]
        address:dialog.address
        
        onLogged: {
            tunnel.on_ticket(ticket);
			if (address != 'localhost')
			{
				dialog.address='localhost'
/*			 	console.log("Address selected: " + address)*/
            	proxy.requestTicket(address,user,pwd,inGroups);
			}
        }



    }
}
