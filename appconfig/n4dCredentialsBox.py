#! /usr/bin/python3
#It's not pretty but works
#This class creates an authentication dialog against a N4d server using qml n4dAgent
#Works with both qt and non qt apps

from PySide2.QtWidgets import QDialog,QApplication,QMainWindow,QGridLayout,QWidget
from PySide2.QtQuick import QQuickView
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtCore import Qt,QUrl, QObject, Slot, Signal,QEventLoop, QSize
import time
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

#Tunnel for qml
class Tunnel(QObject):
	onQmlTicket=Signal(str)

	@Slot(str)
	def on_ticket(self, ticket):
		ticket=ticket.replace(' ','##U+0020##').rstrip()
		self.onQmlTicket.emit(ticket)
		return True
	#def on_ticket
#class Tunnel

####
#This class implements the modal dialog
#It creates a Qt Window and a QApplication if they don't exist
###
class n4dDialog(QDialog):
	onTicket=Signal(list)
	def __init__(self,server='localhost',app=None):
		super(n4dDialog, self).__init__()
		if len(sys.argv)==2:
			server=sys.argv[1]
		if app:
			self.mw=self._createMainWindow()
			self.setParent(self.mw)
		self.server=server
		self.setModal=True
		self.tunnel = Tunnel()
		self.tunnel.onQmlTicket.connect(self._onTicket)
		self.tickets=[]
		self.dbg=False
		self.loginBox(app)
		self.createWinId()
		self._debug("Login launched on server: {}".format(self.server))
	#def __init__
	
	def _debug(self,msg):
		if self.dbg:
			print("N4dCredentials: {}".format(msg))
	#def _debug(self,msg):

	def _createMainWindow(self):
		mw=QMainWindow()
		return(mw)
	#def _createMainWindow

	def loginBox(self,app):
		self.tickets=[]
		self.qview = QQuickView()
		self.qview.setResizeMode(self.qview.SizeRootObjectToView)
		self._debug("Accesing server: {}".format(self.server))
		root=self.qview.rootContext()
		root.setContextProperty("server", str(self.server))
		root.setContextProperty("tunnel", self.tunnel)
		self._debug("Values setted")
		url = QUrl("/usr/share/appconfig/auth/login.qml")
		self.qview.setSource(url)
		self._debug("Source setted")
		root=self.qview.rootObject()
		qml=self.createWindowContainer(self.qview,self,Qt.FramelessWindowHint)
		self._debug("Container ready")
		qml.setFixedSize(self.qview.sizeHint())
		qml.show()
		if app:
			self._debug("Container ready")
			sys.exit(app.exec_())
	#def loginBox

	@Slot(str)
	def _onTicket(self,*args):
		ticket=args[0]
		self._debug("Server: {}".format(self.server))
		self._debug("Ticket: {}".format(ticket))
		if ticket not in self.tickets:
			self.tickets.append(ticket)
			self._debug("Emit {}".format(self.tickets))
		if self.server=='localhost' or  len(self.tickets)==2:
			self.onTicket.emit(self.tickets)
			self.accept()
	#def _onTicket
#class n4dDialog

class n4dCredentials():
	onTicket=Signal(list)
	def __init__(self,server='localhost'):
		super(n4dCredentials, self).__init__()

		self.sw=False
		app=QApplication.instance()
		if app==None:
			app=QApplication()
		app=None
		self.dialog=n4dDialog(server,app)
	#def __init__
#class n4dCredentials
