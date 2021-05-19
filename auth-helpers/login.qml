import QtQuick 2.6
import QtQuick.Dialogs 1.2
import Edupals.N4D.Agent 1.0 as N4DAgent
import "Login" as N4dLogin 

Dialog {
    id: dialog
    width: 400
    height: 250
	modality: Qt.ApplicationModal
	visible: true
	standardButtons: StandardButton.NoButton
	property string address: "localhost"

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
			 	console.log("Address selected: " + address)
            	proxy.requestTicket(address,user,"lliurex",inGroups);
				localadress:""
			}
        }



    }
}
