#!/usr/bin/env python3
import socket
import time

from PyQt5 import QtGui
from PyQt5.QtWidgets import QDialog,QApplication,QGridLayout,QWidget,QLineEdit,QLabel,QPushButton,QHBoxLayout
from PyQt5.QtCore import QSize,Qt,pyqtSignal,pyqtSlot
from subprocess import Popen, PIPE
import base64

from edupals.ui import QAnimatedStatusBar

import gettext
_ = gettext.gettext

QString=type("")
N4D=True
try:
	import xmlrpc.client as n4d
except ImportError:
	raise ImportError("xmlrpc not available. Disabling server queries")
	N4D=False
import ssl

class n4dGui(QDialog):
	validateSignal=pyqtSignal('QString','QString','QString',name='validate')
	def __init__(self):
		super().__init__()
		self.setWindowIcon(QtGui.QIcon("/usr/share/icons/hicolor/48x48/apps/x-appimage.png"))
		self.setModal(True)
		self.setWindowTitle(_("Authentication is required"))
		box=QGridLayout()
		self.statusBar=QAnimatedStatusBar.QAnimatedStatusBar()
		self.statusBar.setStateCss("success","background-color:qlineargradient(x1:0 y1:0,x2:0 y2:1,stop:0 rgba(0,0,255,1), stop:1 rgba(0,0,255,0.6));color:white;")
		self.statusBar.setStateCss("error","background-color:qlineargradient(x1:0 y1:0,x2:0 y2:1,stop:0 rgba(255,0,0,1), stop:1 rgba(255,0,0,0.6));color:white;text-align:center;text-decoration:none;")
		box.addWidget(self.statusBar,0,0,1,2)
		icn_auth=QtGui.QIcon.fromTheme("preferences-system-user-sudo.svg")
		lbl_icn=QLabel()
		img=QtGui.QPixmap(icn_auth.pixmap(QSize(64,64)))
		lbl_icn.setPixmap(img)
		box.addWidget(lbl_icn,0,0,2,1)
		lbl_auth=QLabel(_("This action needs authentication against\nthe N4d Server"))
		lbl_auth.setFont(QtGui.QFont("roboto",weight=QtGui.QFont.Bold,pointSize=12))
		lbl_info=QLabel(_("An application is trying to do an action\nthat requires N4d authentication"))
		lbl_info.setFont(QtGui.QFont("roboto",pointSize=10))
		box.addWidget(lbl_auth,0,1,1,1)
		box.addWidget(lbl_info,1,1,1,1)
		txt_username=QLineEdit()
		txt_username.setPlaceholderText(_("Username"))
		txt_password=QLineEdit()
		txt_password.setPlaceholderText(_("Password"))
		txt_server=QLineEdit()
		txt_server.setPlaceholderText(_("Server"))
		box.addWidget(txt_username,2,0,1,2)
		box.addWidget(txt_password,3,0,1,2)
		box.addWidget(txt_server,4,0,1,2)
		btn_ok=QPushButton(_("Accept"))
		btn_ok.clicked.connect(lambda x:self.acepted(txt_username,txt_password,txt_server))
		btn_ko=QPushButton(_("Cancel"))
		btn_ko.clicked.connect(self.close)
		box_btn=QHBoxLayout()
		box_btn.addWidget(btn_ok)
		box_btn.addWidget(btn_ko)
		box.addLayout(box_btn,5,1,1,1,Qt.Alignment(2))
		self.setLayout(box)
	#def __init__

	def acepted(self,*args):
		(txt_username,txt_password,txt_server)=args
		self.validateSignal.emit(txt_username.text(),txt_password.text(),txt_server.text())
	#def acepted

	def showMessage(self,msg,status="error"):
		self.statusBar.setText(msg)
		if status:
			self.statusBar.show(status)
		else:
			self.statusBar.show()
	#def _show_message
#class n4dGui

class appConfigN4d():
	def __init__(self,n4dmethod="",n4dclass="",n4dparms="",username='',password='',server='localhost'):
		self.dbg=True
		self.username=username
		self.password=password
		self.server=server
		self.query=''
		self.n4dClass="FileOperations"
		self.n4dMethod=''
		self.n4dParms=''
		self.result={}
		self.retval=0
		self.n4dAuth=None
	#def __init__

	def _debug(self,msg):
		if self.dbg:
			print("appConfigN4d: %s"%msg)

	def error(self,error):
		print("Error: %s"%error)
	#def error

	def getCredentials(self):
		@pyqtSlot(str,str,str)
		def _qt_validate(user,pwd,srv):
			self._validate(user,pwd,srv)

		#Check X
		p=Popen(["xset","-q"],stdout=PIPE,stderr=PIPE)
		p.communicate()
		if p.returncode==0:
			self.n4dAuth=n4dGui()
			self.n4dAuth.validateSignal.connect(_qt_validate)
			self.n4dAuth.exec_()
		else:
			user=input(_("Username: "))
			password=input(_("Password: "))
			server=input(_("Server: "))
			self._validate(user,password,server)
	#def getCredentials

	def setCredentials(self,username,password,server):
		self.username=username
		self.password=password
		self.server=server
		self._debug("Credentials %s %s"%(username,server))
	#def setCredentials

	def _validate(self,user,pwd,srv):
		ret=[False]
		data={}
		self.setCredentials(user,pwd,srv)
		n4dClient=self._n4d_connect()
		if n4dClient:
			try:
				ret=n4dClient.validate_user(user,pwd)
			except Exception as e:
				self.error(e)
				self.n4dAuth.showMessage(_("Validation error"))

		if (isinstance(ret,bool)):
			#Error Login 
			self.setCredentials('','','')
			self.n4dAuth.showMessage(_("Validation error"))
		elif not ret[0]:
			#Error Login 
			self.setCredentials('','','')
			self.n4dAuth.showMessage(_("Validation error"))
		else:
			data=self._on_validate(n4dClient)
		return(data)

	def _on_validate(self,n4dClient=None):
		if not self.n4dParms:
			self.query="n4dClient.%s([\"%s\",\"%s\"],\"%s\")"%(self.n4dMethod,self.username,self.password,self.n4dClass)
		else:
			parms=self.n4dParms.split(',')
			self.n4dParms=""
			for parm in parms:
				sep=","
				if self.n4dParms=="":
					sep=""
				self.n4dParms=self.n4dParms+"%s\"%s\""%(sep,parm)

			self.query="n4dClient.%s([\"%s\",\"%s\"],\"%s\",%s)"%(self.n4dMethod,self.username,self.password,self.n4dClass,self.n4dParms)
		self.result=self._execQuery(n4dClient)
		if self.n4dAuth:
			self.n4dAuth.close()
	#def _on_validate

	def _execAction(self,auth):
		if not self.username and auth:
			self.getCredentials()
		elif self.username:
			self._validate(self.username,self.password,self.server)
		self._debug(self.result)
		return(self.result)
	#def setClassMethod

	def _execQuery(self,n4dClient):
		data={}
		try:
			data=eval('%s'%self.query)
		except Exception as e:
			print("Syntax error on query %s"%self.query)
			self.retval=3
		if self.retval==0:
			if type(data)==type({}):
				if 'status' in data.keys():
					retval=data['status']
					if data['status']!=True:
						print("Query %s failed,"%(self.query))
					self.retval=4
		return(data)
	#def execQuery

	def writeConfig(self,n4dparms):
		self.n4dParms=n4dparms
		self.n4dMethod="send_file_to_server"
		return(self._execAction(auth=True))
	
	def readConfig(self,n4dparms):
		self.n4dParms=n4dparms
		self.n4dMethod="get_file_from_server"
		return(self._execAction(auth=True))

	def _n4d_connect(self):
		n4dClient=None
		context=ssl._create_unverified_context()
		try:
			socket.gethostbyname(self.server)
		except:
			#It could be an ip
			try:
				socket.inet_aton(self.server)
			except Exception as e:
				print(e)
				self.error("Error creating SSL context")
				self.retval=1
		if self.retval==0:
			try:
				n4dClient = n4d.ServerProxy("https://"+self.server+":9779",context=context,allow_none=True)
			except:
				self.error("Error accesing N4d at %s"%self.server)
				self.retval=2
		return n4dClient
	#def _n4d_connect

