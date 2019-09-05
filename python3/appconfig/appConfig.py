#!/usr/bin/env python3
import sys
import os
import json
import tempfile
import subprocess
N4D=True
try:
	import xmlrpc.client as n4d
except ImportError:
	raise ImportError("xmlrpc not available. Disabling server queries")
	N4D=False
import ssl

class appConfig():
	def __init__(self):
		self.dbg=True
		self.home=os.environ['HOME']
		self.confFile="appconfig.conf"
		self.baseDirs={"user":"%s/.config"%self.home,"system":"/usr/share/%s"%self.confFile.split('.')[0],"n4d":"/usr/share/%s"%self.confFile.split('.')[0]}
		self.config={}
		self.n4dcredentials=[]
		self.server="172.20.9.174"
		self.n4d=None
		self.n4dclass=None
		self.n4dmethod=None
		self.n4dparms={}
	#def __init__

	def _debug(self,msg):
		if self.dbg:
			print("Config: %s"%msg)
	#def _debug

	def set_baseDirs(self,dirs):
		self.baseDirs=dirs.copy()
		if 'nd4' not in self.baseDirs.keys():
			self.baseDirs['n4d']=self.baseDirs['system']
		self._debug("baseDirs: %s"%self.baseDirs)
	#def set_baseDirs

	def set_configFile(self,confFile):
		self.confFile=confFile
		self._debug("ConfFile: %s"%self.confFile)
	#def set_confFile

	def get_configFile(self,level=None):
		confFile={}
		if level in self.baseDirs.keys():
			conf=os.path.join(self.baseDirs[level],self.confFile)
			confFile.update({level:conf})
		else:
			for level,item in self.baseDirs.items():
				if key=='n4d':
					continue
				conf=os.path.join(item,self.confFile)
				confFile.update({level:conf})
		return confFile
	#def get_configFile

	def set_defaultConfig(self,config):
		self.config.update({'default':config})
		self._debug(self.config)
	#def set_defaultConfig

	def set_level(self,level):
		self.level=level
	#def set_level

	def get_level(self):
		config=get_config()
		#N4d wons over all
		#User wons over system
		level=config['n4d'].get('enabled','user')
		if level=='user':
			level=config['user'].get('enabled','system')
			if level=='system':
				level=config['system'].get('enabled','user')
				if level!='system':
					level='system'
			else:
				level='user'
		else:
			level='n4d'
		self.set_level(level)
		return(level)
	#def get_level

	def get_config(self,level=None):
		self.config={}
		if N4D==False and level=='n4d':
			level='system'
		if level=='n4d':
			self._read_config_from_n4d()
		else:
			self._read_config_from_system(level)

		config=self.config.copy()
		self._debug("Data -> %s"%(self.config))
		return (config)
	#def get_config

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

	def write_config(self,data,level=None,key=None,pk=None,create=True):
		self._debug("Writing key %s to %s Polkit:%s"%(key,level,pk))
		retval=True
		if level==None:
			level=self.get_level()
		if N4D==False and level=='n4d':
			level='system'
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
			if 'enabled' not in newConf[level].keys():
				data['enabled']=True
			if level=='n4d':
				if not self.n4d:
					self.n4d=self._n4d_connect(self.server)
				self._debug("Sending config to n4d")
				retval=self._write_config_to_n4d(newConf)
			else:
				retval=self._write_config_to_system(newConf,level)
		return (retval)
	#def write_config

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
	#def _write_config_to_system

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

	def _write_config_to_n4d(self,conf,level='n4d'):
		retval=True
		self.n4dcredentials={'user':'','password':'','server':''}
		if not self.n4dcredentials:
			retval=False
		if retval:
			if not self.n4dclass:
				#create tmp file (will be sended to n4d server)
				confFile=tempfile.mkstemp()[1]
				self.config[level]=conf[level]
				try:
					with open(confFile,'w') as f:
						json.dump(self.config[level],f,indent=4,sort_keys=True)
				except Exception as e:
					retval=False
					print("Error writing system config: %s"%e)
				self.n4dclass="ScpManager"
				self.n4dmethod="send_file"
				self.n4dparms.update({self.n4dmethod:["\"%s\""%self.n4dcredentials['user'],"\"%s\""%self.n4dcredentials['password'],"\"%s\""%self.n4dcredentials['server'],"\"%s\""%confFile,"\"%s/%s\""%(self.baseDirs['system'],self.confFile)]})
				query="self.n4d.%s([self.n4dcredentials['user'],self.n4dcredentials['password']],\"%s\",%s)"%(self.n4dmethod,self.n4dclass,",".join(self.n4dparms.get(self.n4dmethod,[])))
				retval=self._execute_n4d_query(query)
		return retval
	#def _write_config_to_n4d

	def _execute_n4d_query(self,query):
		retval=True
		data={}
		try:
			self._debug("Executing query %s"%query)
			data=eval(query)
		except Exception as e:
			self._debug("Error accessing n4d: %s"%e)
			retval['status']=False
		if type(data)==type({}):
			if 'status' in data.keys():
				retval=data['status']
#				data=data['status']
				if data['status']!="True":
					self._debug("Call to method %s of class %s failed,"%(self.n4dmethod,self.n4dclass))
					self._debug("%s"%data)
		self._debug(data)
		return(retval)
	#def _execute_n4d_query(self,query):

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
