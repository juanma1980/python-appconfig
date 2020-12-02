#!/usr/bin/env python3
import socket
import time
import json
from PyQt5 import QtGui
from PyQt5.QtWidgets import QDialog,QApplication,QGridLayout,QWidget,QLineEdit,QLabel,QPushButton,QHBoxLayout
from PyQt5.QtCore import QSize,Qt,pyqtSignal,pyqtSlot,QThread
from subprocess import Popen, PIPE
import base64
import os

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
	def __init__(self,forceServer=None):
		import getpass
		super().__init__()
		self.setWindowIcon(QtGui.QIcon("/usr/share/icons/hicolor/48x48/apps/x-appimage.png"))
		self.setModal(True)
		self.setWindowTitle(_("Authentication is required"))
		box=QGridLayout()
		self.statusBar=QAnimatedStatusBar.QAnimatedStatusBar()
#		self.statusBar.setStateCss("success","background-color:qlineargradient(x1:0 y1:0,x2:0 y2:1,stop:0 rgba(0,0,255,1), stop:1 rgba(0,0,255,0.6));color:white;")
#		self.statusBar.setStateCss("error","background-color:qlineargradient(x1:0 y1:0,x2:0 y2:1,stop:0 rgba(255,0,0,1), stop:1 rgba(255,0,0,0.6));color:white;text-align:center;text-decoration:none;")
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
		self.txt_username=QLineEdit()
		self.txt_username.returnPressed.connect(self.acepted)
		self.txt_username.setPlaceholderText(_("Username"))
		self.txt_username.setText(getpass.getuser())
		self.txt_password=QLineEdit()
		self.txt_password.returnPressed.connect(self.acepted)
		self.txt_password.setEchoMode(QLineEdit.Password)
		self.txt_password.setPlaceholderText(_("Password"))
		self.txt_server=QLineEdit()
		self.txt_server.returnPressed.connect(self.acepted)
		self.forceServer=forceServer
		server=self._get_default_server()
		self.txt_server.setPlaceholderText(server)
#		if server=='localhost':
#			self.txt_server.hide()
		box.addWidget(self.txt_password,3,0,1,2)
		box.addWidget(self.txt_username,2,0,1,2)
		box.addWidget(self.txt_server,4,0,1,2)
		btn_ok=QPushButton(_("Accept"))
		btn_ok.clicked.connect(self.acepted)
		btn_ok.setAutoDefault(False)
		btn_ok.setDefault(False)
		btn_ko=QPushButton(_("Cancel"))
		btn_ko.clicked.connect(self.close)
		btn_ko.setAutoDefault(False)
		btn_ko.setDefault(False)
		box_btn=QHBoxLayout()
		box_btn.addWidget(btn_ok)
		box_btn.addWidget(btn_ko)
		box.addLayout(box_btn,5,1,1,1,Qt.Alignment(2))
		self.setLayout(box)
	#def __init__

	def _get_default_server(self):
		if self.forceServer:
			return(self.forceServer)
		import socket
		server='server'
		try:
			server_ip=socket.gethostbyname(server)
		except:
			server='localhost'
		return(server)
	#def _set_default_server(self):

	@pyqtSlot()
	def acepted(self):
		self.txt_username.setReadOnly(True)
		self.txt_password.setReadOnly(True)
		self.txt_server.setReadOnly(True)
		user=self.txt_username.text()
		pwd=self.txt_password.text()
		server=self.txt_server.text()
		if not server:
			server=self._get_default_server()
			self.txt_server.setPlaceholderText(server)
		self.validateSignal.emit(user,pwd,server)
	#def acepted

	def setNewCursor(self,newCursor):

		if (newCursor=="wait"):
			arr_cursor=QtGui.QCursor(Qt.WaitCursor)
			bea_cursor=QtGui.QCursor(Qt.WaitCursor)
		else:
			arr_cursor=QtGui.QCursor(Qt.ArrowCursor)
			bea_cursor=QtGui.QCursor(Qt.IBeamCursor)
			self.txt_username.setReadOnly(False)
			self.txt_password.setReadOnly(False)
			self.txt_server.setReadOnly(False)
		self.txt_username.setCursor(bea_cursor)
		self.txt_password.setCursor(bea_cursor)
		self.txt_server.setCursor(bea_cursor)
		self.setCursor(arr_cursor)

	def showMessage(self,msg,status="error"):
		x=self.x()
		y=self.y()
		move=5
		for i in range(10):
			self.move(x+move,y)
			move=move*(-1)
			time.sleep(0.05)
		self.move(x,y)
		self.statusBar.setText(msg)
		self.statusBar.show("error")
	#def _show_message
#class n4dGui

class appConfigN4d():
	def __init__(self,n4dmethod="",n4dclass="",n4dparms="",username='',password='',server='server'):
		self.dbg=False
		self.username=username
		self.password=password
		self.server=server
		self.query=''
		self.n4dClass="VariablesManager"
		self.n4dMethod=''
		self.n4dParms=''
		self.result={}
		self.retval=0
		self.n4dAuth=None
		self.n4dClient=None
		self.varName=''
		self.uptime=0
	#def __init__

	def _debug(self,msg):
		if self.dbg:
			print("appConfigN4d: %s"%msg)

	def error(self,error):
		print("Error: %s"%error)
	#def error

	def getCredentials(self):
		validate=False
		@pyqtSlot(str,str,str)
		def _qt_validate(user,pwd,srv):
			nonlocal validate
			self.n4dAuth.setNewCursor("wait")
			if self._validate(user,pwd,srv)==False:
				self.n4dAuth.showMessage(_("Validation error"))
			else:
				validate=True
				self.n4dAuth.close()
			self.n4dAuth.setNewCursor("arrow")

		#Check X
		p=Popen(["xset","-q"],stdout=PIPE,stderr=PIPE)
		p.communicate()
		if p.returncode==0:
			self.n4dAuth=n4dGui(self.server)
			self.n4dAuth.validateSignal.connect(_qt_validate)
			self.n4dAuth.exec_()
		else:
			user=input(_("Username: "))
			password=input(_("Password: "))
			server=input(_("Server: "))
			validate=self._validate(user,password,server)
		return validate
	#def getCredentials

	def setCredentials(self,username,password,server):
		self.username=username
		self.password=password
		self.server=server
		self._debug("Credentials %s %s"%(username,server))
	#def setCredentials

	def writeConfig(self,n4dparms):
		self.retval=0
		self.n4dMethod="set_variable"
		tmp=n4dparms.split(",")
		parms=tmp[1:]
		#Empty the variable data
		self.varName=tmp[0].upper()
		self.varData="{}"
		self.retval=self._execAction(auth=True).get('status',False)
		#On error create variable
		if self.retval!=True:
			self.error("Ret: %s"%self.retval)
			self._debug("Adding non existent variable")
			tmp=[]
			tmp=n4dparms.split(",")
			self.varData=self.varData+"\",\"%s configuration\","%self.varName
			self.varData=self.varData+"\"stores %s configuration"%self.varName
			self.n4dMethod="add_variable"
			self._execAction(auth=True)
		#Else put the value
		else:
			self.varData=",".join(tmp[1:])
			self.varDepends=[]
			self._execAction(auth=True)
		if self.retval==0:
			self.retval=True
		self.varName=''
		return(self.retval)
	#def writeConfig
	
	def readConfig(self,n4dparms,exclude=[]):
		self.retval=0
		tmp=n4dparms.split(",")
		self.varName=tmp[0].upper()
		self.varData=""
		self.varDepends=[]
		self.n4dParms=n4dparms
		self.n4dMethod="get_variable"
		ret=self._execAction(auth=False)
		tmpStr=ret
		if isinstance(ret,str):
			tmpStr=ret.replace("'","\"")
		if ret==None:
			tmpStr=""
		if "False" in tmpStr:
			if "False," in tmpStr:
				tmpStr=tmpStr.replace("False,","\"False\",")
			elif "False}" in tmpStr:
				tmpStr=tmpStr.replace("False}","\"False\"}")
		if "True" in tmpStr:
			if "True," in tmpStr:
				tmpStr=tmpStr.replace("True,","\"True\",")
			elif "True}" in tmpStr:
				tmpStr=tmpStr.replace("True}","\"True\"}")
		try:
			data=json.loads(tmpStr)
		except Exception as e:
			self._debug("Error reading n4d values: %s"%e)
			self._debug("Dump: %s"%tmpStr)
			data={}
		for excludeKey in exclude:
			self._debug("Search exclude %s in %s"%(excludeKey,data.keys()))
			if excludeKey in list(data.keys()):
				del data[excludeKey]
		self.varName=''
		return(data)
	#def readConfig(self,n4dparms):

	def n4dQuery(self,n4dclass,n4dmethod,n4dparms=''):
		auth=True
		if os.path.isfile("/etc/n4d/conf.d/%s"%n4dclass):
			with open("/etc/n4d/conf.d/%s"%n4dclass,'r') as f:
				for line in f.readlines():
					if line.startswith(n4dmethod):
						if 'anonymous' in line or '*' in line:
							auth=False
		self.n4dParms=n4dparms
		self.n4dClass=n4dclass
		self.n4dMethod=n4dmethod
		return(self._execAction(auth))

	def _execAction(self,auth):
		if self.n4dClient==None:
			self._n4d_connect()
		validate=False
		self.result={}
		#Check session
		if self.uptime!=0:
			if ((int(time.time())-self.uptime)>59):
				self.username=''
				self.password=''
				self.uptime=0
		if not self.username and auth:
			validate=self.getCredentials()
		elif self.username:
			validate=self._validate(self.username,self.password,self.server)
		else:
			self.username=''
			self.password=''
			validate=True
		if validate:
			if (self.uptime==0):
				self.uptime=int(time.time())
			self._on_validate()
#		self._debug(self.result)
		return(self.result)
	#def _execAction
	
	def _validate(self,user,pwd,srv):
		ret=[False]
		validate=False
		self.setCredentials(user,pwd,srv)
		if self.n4dClient==None:
			self._n4d_connect()
		try:
			ret=self.n4dClient.validate_user(user,pwd)
		except Exception as e:
			self.error(e)

		if (isinstance(ret,bool)):
			#Error Login 
			self.setCredentials('','','')
		elif not ret[0]:
			#Error Login 
			self.setCredentials('','','')
		else:
			validate=True
		return(validate)
	#def _validate

	def _on_validate(self,):
		if not self.n4dParms:
			if self.username:
				self.query="self.n4dClient.%s([\"%s\",\"%s\"],\"%s\")"%(self.n4dMethod,self.username,self.password,self.n4dClass)
			else:
				self.query="self.n4dClient.%s(\"\",\"%s\")"%(self.n4dMethod,self.n4dClass)
		else:
			if self.username:
				if self.varName:
					self.query="self.n4dClient.%s([\"%s\",\"%s\"],\"%s\",\"%s\")"%(self.n4dMethod,self.username,self.password,self.n4dClass,self.varName)
					if self.varData:
						self.query="self.n4dClient.%s([\"%s\",\"%s\"],\"%s\",\"%s\",\"%s\",\"%s\")"%(self.n4dMethod,self.username,self.password,self.n4dClass,self.varName,self.varData,self.varDepends)
				else:
					self.query="self.n4dClient.%s([\"%s\",\"%s\"],\"%s\",%s)"%(self.n4dMethod,self.username,self.password,self.n4dClass,self.n4dParms)
			else:
				if self.varName:
					self.query="self.n4dClient.%s(\"\",\"%s\",\"%s\")"%(self.n4dMethod,self.n4dClass,self.varName)
					if self.varData:
						self.query="self.n4dClient.%s(\"\",\"%s\",\"%s\",\"%s\",\"%s\")"%(self.n4dMethod,self.n4dClass,self.varName,self.varData,self.varDepends)
				else:
					self.query="self.n4dClient.%s(\"%s\",%s)"%(self.n4dMethod,self.n4dClass,self.n4dParms)
		self.result=self._execQuery()
		if self.n4dAuth:
			self.n4dAuth.close()
	#def _on_validate

	def _execQuery(self):
		data={}
		try:
			data=eval('%s'%self.query)
		except Exception as e:
			self.error("Syntax error on query %s"%self.query)
			self.retval=3
		if self.retval==0:
			if type(data)==type({}) or type(data)==type([]):
				if type(data)==type([]):
					tmp=data
					data={'status':tmp[0],'data':tmp[1:]}
				if 'status' in data.keys():
					retval=data['status']
					if data['status']!=True and data['status']!=0:
						self.error("Query %s failed,"%(self.query))
						self.retval=4
		return(data)
	#def execQuery

	def _n4d_connect(self):
		self.n4dClient=None
		self._debug("Connecting to n4d")
		context=ssl._create_unverified_context()
		try:
			socket.gethostbyname(self.server)
		except:
			#It could be an ip
			try:
				socket.inet_aton(self.server)
			except Exception as e:
				self.error(e)
				self.error("No server found. Reverting to localhost")
				self.server='localhost'
		self._debug("Retval: %s"%self.retval)
		if self.retval==0:
			try:
				self.n4dClient = n4d.ServerProxy("https://"+self.server+":9779",context=context,allow_none=True)
			except:
				self.error("Error accesing N4d at %s"%self.server)
				self.retval=2
	#def _n4d_connect

