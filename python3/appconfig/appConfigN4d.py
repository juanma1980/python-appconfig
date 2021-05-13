#!/usr/bin/env python3
import socket
import time
import json
from PySide2.QtWidgets import QApplication
from PySide2.QtQuick import QQuickView
from PySide2.QtCore import QUrl,QObject, Slot, Signal, Property,QThread
from PySide2.QtQuick import QQuickView
from subprocess import Popen, PIPE
import base64
import os,subprocess,sys
sys.path.insert(1, '/usr/lib/python3/dist-packages/appconfig')
import n4dCredentialsBox as login

import gettext
_ = gettext.gettext

QString=type("")
N4D=True
import n4d.client 
import n4d.responses
#try:
#	import xmlrpc.client as n4d
#except ImportError:
#	raise ImportError("xmlrpc not available. Disabling server queries")
#	N4D=False
#import ssl
USERNOTALLOWED_ERROR=-10

class appConfigN4d():
	def __init__(self,n4dmethod="",n4dclass="",n4dparms="",username='',password='',server='server'):
		self.dbg=True
		#No more global vars for credentials or methods, etc but server
		self.server=server
		self.username=username
		self.password=password
		self.query=''
		self.n4dClass="VariablesManager"
		self.n4dMethod=''
		self.n4dParms=''
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

	def writeConfig(self,n4dparms):
		#OLD CODE. Call to _execAction it's unnnecessary so we can delete
		#all this ugly code
		self.retval=True
		return(self.retval)
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
		################# -> And all is all. Call to nd4client.set_variable it's enough
		return(self.retval)
	#def writeConfig
	
	def readConfig(self,n4dparms,exclude=[]):
		if self.n4dClient==None:
			self.n4dClient=self._n4d_connect()
		self.retval=0
		tmp=n4dparms.split(",")
		self.varName=tmp[0].upper()
		self.varData=""
		self.varDepends=[]
		self.n4dParms=n4dparms
		self.n4dMethod="get_variable"
		#ret=self._execAction(auth=False)
		try:
			ret=self.n4dClient.get_variable(self.varName)
		except:
			return({})
		if ret['status']!=0:
			return{}
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

	def n4dQuery(self,n4dClass,n4dMethod,*args):
		client=""
		def setCredentials(ticket):
			client=self._n4d_connect(ticket)
			result=self._launch(client,n4dClass,n4dMethod,*args)
			
		result={'status':-1,'return':''}
		if self.n4dClient==None:
			self.n4dClient=self._n4d_connect()
		#Launch and pray. If there's validation error ask for credentials
		try:
			result=self._launch(self.n4dClient,n4dClass,n4dMethod,*args)
		except n4d.client.UserNotAllowedError as e:
			#User not allowed, ask for credentials and relaunch
			result={'status':-1,'code':USERNOTALLOWED_ERROR}
			#Get credentials
			self.loginBox=login.n4dCredentials()
			self.loginBox.loginBox(self.server)
			self.loginBox.onTicket.connect(setCredentials)
		except n4d.client.InvalidServerResponseError as e:
			print("Response: {}".format(e))
		except Exception as e:
			print(e)
		self._debug("N4d response: {}".format(result))
		return(result)
	#def n4dQuery(self,n4dclass,n4dmethod,*args):

	def n4dGetVar(self,client=None,var=''):
		if not client:
			client=self.n4dClient
		print(client)
		result={'status':-1,'return':''}
		#Launch and pray. If there's validation error ask for credentials
		try:
			result=client.get_variable(var)
		except n4d.client.InvalidServerResponseError as e:
			print("Response: {}".format(e))
		except Exception as e:
			print(e)
		return(result)
	#def n4dQuery(self,n4dclass,n4dmethod,*args):


	def _launch(self,n4dClient,n4dClass,n4dMethod,*args):
		proxy=n4d.client.Proxy(n4dClient,n4dClass,n4dMethod)
		try:
			self._debug("Call client: {}".format(n4dClient))
			self._debug("Call class: {}".format(n4dClass))
			self._debug("Call method: {}".format(n4dMethod))
			if len(args):
				self._debug("Call Args: {}".format(*args))
				result=proxy.call(*args)
			else:
				result=proxy.call()
		except Exception as e:
			print(e)
			raise e
		return result

	def _n4d_connect(self,ticket=''):
		self.n4dClient=None
		self._debug("Connecting to n4d at {}".format(self.server))
		client=""
		if ticket:
			ticket=ticket.replace('##U+0020##',' ').rstrip()
			tk=n4d.client.Ticket(ticket)
			client=n4d.client.Client(ticket=tk)
			self._debug("N4d Object2: {}".format(client.credential.auth_type))
		else:
			try:
				socket.gethostbyname(self.server)
			except:
				#It could be an ip
				try:
					socket.inet_aton(self.server)
				except Exception as e:
					self.error(e)
					self.error("No server found. Reverting to localhost")
					self.server='https://localhost:9779'
			if not self.server.startswith("http"):
				self.server="https://{}".format(self.server)
			if len(self.server.split(":")) < 3:
					self.server="{}:9779".format(self.server)
				
			if self.username:
				client=n4d.client.Client(self.server,self.username,self.password)
			else:
				client=n4d.client.Client(self.server)
		self.n4dClient=client
		self._debug("N4d Object2: {}".format(self.n4dClient.credential.auth_type))
		return(client)
	#def _n4d_connect

