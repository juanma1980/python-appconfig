#!/usr/bin/env python2
import sys
import os
import json
import subprocess

try:
	from xmlrpclib import *
except ImportError:
	raise ImportError("xmlrpc not available. Disabling server queries")

try:
	import xmlrpc.client as n4d
except ImportError:
	raise ImportError("xmlrpc not available. Disabling server queries")
import ssl

class appConfig():
	def __init__(self):
		self.dbg=True
		self.home=os.environ['HOME']
		self.baseDirs={"user":"%s/.config"%self.home}
		self.confFile="app.conf"
		self.passFile="app.pwd"
		self.config={}
		self.n4d=None
	#def __init__

	def _debug(self,msg):
		if self.dbg:
			print("Config: %s"%msg)
	#def _debug

	def set_baseDirs(self,dirs):
		self.baseDirs=dirs.copy()
		self._debug("baseDirs: %s"%self.baseDirs)
	#def set_baseDirs

	def set_configFile(self,confFile):
		self.confFile=confFile
		self._debug("ConfFile: %s"%self.confFile)
	#def set_confFile

	def get_configFile(self,level=None):
		confFile={}
		if level in self.baseDirs.keys():
			confFile.update({level:"%s/%s"%(self.baseDirs[level],self.confFile)})
		else:
			for key,item in self.baseDirs.items():
				confFile.update({key:"%s/%s"%(item,self.confFile)})
		return confFile

	def set_defaultConfig(self,config):
		self.config.update({'default':config})
		self._debug(self.config)
	#def set_defaultConfig

	def get_config(self,level=None):
		self._read_config_from_system(level)
		self._read_config_from_n4d()
		config=self.config.copy()
		self._debug("Data -> %s"%(self.config))
		return (config)

	def _read_config_from_system(self,level=None):
		def _read_file(confFile,level):
			data={}
			self._debug("Reading %s -> %s"%(confFile,level))
			if os.path.isfile(confFile):
				try:
					data=json.loads(open(confFile).read())
				except Exception as e:
					self._debug("Error opening %s: %s"%(confFile,e))
					
			if data:
				self._debug("Updating %s -> %s"%(confFile,level))
				self.config.update({level:data})
		#def _read_file
		confFiles=self.get_configFile(level)
		for confLevel,confFile in confFiles.items():
			_read_file(confFile,confLevel)
	#def read_config_from_system

	def write_config(self,data,level='user',key=None,pk=None):
		self._debug("Writing key %s to %s Polkit:%s"%(key,level,pk))
		retval=True
		if level=='system' and not pk:
			self._debug("Invoking pk")
			try:
				data=json.dumps(data)
				subprocess.check_call(["pkexec","/usr/share/appconfig/bin/appconfig-polkit-helper.py",data,level,key,self.confFile,self.baseDirs[level]])
			except Exception as e:
				self._debug("Invoking pk failed: %s"%e)
				retval=False
		else:
			oldConf=self.get_config(level)
			self._debug("Old: %s"%oldConf)
			newConf=oldConf.copy()
			if key:
				if not level in newConf.keys():
					newConf[level]={key:None}
				if not key in newConf[level].keys():
					newConf[level][key]=None
				newConf[level][key]=data
			else:
				for key in data.keys():
					if not level in newConf.keys():
						newConf[level]={key:None}
					if not key in newConf[level].keys():
						newConf[level][key]=None
					newConf[level][key]=data[key]
			if key=='n4d':
				retval=self._write_config_to_n4d(newConf)
			else:
				retval=self._write_config_to_system(newConf,level)
		return (retval)


	def _write_config_to_system(self,conf,level='user'):
		data={}
		retval=True
		if not level in self.config.keys():
			self.config[level]={}
		self._debug("Writing info %s"%self.config[level])
		if level and level in self.baseDirs.keys():
			confDir=self.baseDirs[level]
		else:
			confDir=self.defaultDir
		if not os.path.isdir(confDir):
			try:
				os.makedirs(confDir)
			except Exception as e:
				print("Can't create dir %s: %s"%(confDir,e))
				retval=False
		if retval:
			confFile=("%s/%s"%(confDir,self.confFile))
			self.config[level]=conf[level]
			self._debug("New: %s"%self.config[level])
			try:
				with open(confFile,'w') as f:
					json.dump(self.config[level],f,indent=4,sort_keys=True)
			except Exception as e:
				retval=False
				print("Error writing system config: %s"%e)
		return (retval)
	#def read_config_from_system

	def set_class_for_n4d(self,n4dclass):
		self.n4dclass=n4dclass
		self._debug("N4d Class: %s"%self.n4dclass)
	#def set_class_for_n4d(self,n4dclass):

	def set_method_for_n4d(self,n4dmethod,n4dclass=None,parms=None):
		self.n4dmethod=n4dmethod
		if parms:
			self.n4dparms[n4dmethod]={'parms':parms}
		if n4dclass:
			self.n4dparms[n4dmethod]={'class':n4dclass}
		else:
			self.n4dparms[n4dmethod]={'class':self.n4dclass}
		self._debug("N4d Method: %s"%self.n4dmethod)
	#def set_method_for_n4d(self,n4dmethod):

	def _read_config_from_n4d(self):
		sw=True
		if self.n4d:
			query="self.n4d.%s(self,credentials,%s"%(self.n4dmethod,self.n4dclass)
			self.config['n4d']=self._execute_n4d_query(query)
		return (self.config)
	#def read_config_from_n4d

	def _write_config_to_n4d(self,conf):
		pass

	def _execute_n4d_query(self):
		retval={}
		try:
			data=eval(query)
		except Exception as e:
			self._debug("Error accessing n4d: %s"%e)
			sw=False
		if 'status' and 'data' in data.keys():
			retval=data
			if data['status']!=True:
				self._debug("Call to method %s of class %s failed,"%(self.n4dmethod,self.n4dclass))
		elif sw:
			self._debug("Unable to get status or data from n4d method. Please update your method")
		return(retval)

	def set_credentials(self,user,pwd,server):
		self.credentials=[user,pwd]
		if server!='localhost':
			self._debug("Connecting to server %s"%server)						
			self.n4d=self._n4d_connect(server)
		else:
			try:
				server_ip=socket.gethostbyname("server")
				self.n4d=self._n4d_connect("server")
			except:
				self.n4d=None
	#def set_credentials
	
	def _n4d_connect(self,server):
		#Setup SSL
		context=ssl._create_unverified_context()
		n4dclient = n4d.ServerProxy("https://"+server+":9779",context=context,allow_none=True)
		return(n4dclient)
	#def _n4d_connect
