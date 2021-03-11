#! /usr/bin/python3
from PySide2.QtWidgets import QApplication
from PySide2.QtQuick import QQuickView
from PySide2.QtCore import QUrl, QObject, Slot, Signal,Property
import os
import subprocess
import sys

class Tunnel(QObject):

	@Slot(str)
	def on_ticket(self, ticket):
		ticket=ticket.replace(' ','##U+0020##').rstrip()
		app.quit()
	#def on_ticket

#class Tunnel

app = QApplication([])
tunnel = Tunnel()
view = QQuickView()
view.rootContext().setContextProperty("tunnel", tunnel)
url = QUrl("/usr/lib/python3/dist-packages/bellscheduler/rsrc/login.qml")
view.setSource(url)
view.show()

sys.exit(app.exec_())
