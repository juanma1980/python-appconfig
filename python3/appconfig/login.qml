import QtQuick 2.6
import Edupals.N4D.Agent 1.0 as N4DAgent

Window {
    id: mainWindow
    visible: true
    width: 640
    height: 480
    Rectangle{
        width: parent.width
        height: 30
        Button{
            text: "Home"
            onClicked: pageLoader.source="home.qml"
            x:0
            y:0
        }
    }

Rectangle {
    width: 400
    height: 250
    anchors.centerIn: parent
    color: "#e9e9e9"

    N4DAgent.Login
    {
        showAddress:false
        address:"localhost"
        showCancel: false
        inGroups:["sudo","admins","teachers"]
        
        anchors.centerIn: parent
        
        onLogged: {
            tunnel.on_ticket(ticket);
        }
    }
}
}
