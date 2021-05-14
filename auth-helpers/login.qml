import QtQuick 2.6
import QtQuick.Dialogs 1.2
import Edupals.N4D.Agent 1.0 as N4DAgent

Dialog {
    id: dialog
    width: 400
    height: 250
	modality: Qt.ApplicationModal
	visible: true
	standardButtons: StandardButton.NoButton
	property string address: "localhost"

    N4DAgent.Login
    {
        showAddress:false
        showCancel: false
        inGroups:["sudo","admins","teachers"]
        anchors.centerIn: dialog
        address:dialog.address
        
        onLogged: {
            tunnel.on_ticket(ticket);
			if (address != 'localhost')
			{
				address: "localhost"
            	tunnel.on_ticket(ticket);
			}
        }
    }
}
