#! /usr/bin/python3
from PySide2.QtWidgets import QApplication
from PySide2.QtQuick import QQuickView
from PySide2.QtCore import QUrl, QObject, Slot, Signal,Property
import os
import subprocess
import sys
import gettext
try:
	confText=gettext.translation("python3-appconfig")
	_ = confText.gettext
except:
	gettext.textdomain('python3-appconfig')
	_ = gettext.gettext


class Tunnel(QObject):

	@Slot(str)
	def on_ticket(self, ticket):
		ticket=ticket.replace(' ','##U+0020##').rstrip()
		print(ticket)
		app.quit()
	#def on_ticket

#class Tunnel

app = QApplication([_("Authentication required")])
tunnel = Tunnel()
view = QQuickView()
view.rootContext().setContextProperty("tunnel", tunnel)
url = QUrl("/usr/share/appconfig/auth/login.qml")
view.setSource(url)
view.show()

sys.exit(app.exec_())
