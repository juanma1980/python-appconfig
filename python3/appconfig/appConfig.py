#!/usr/bin/env python3
import sys
import os
import json
import tempfile
import base64
import subprocess
from appconfig.appConfigN4d import appConfigN4d

class appConfig():
	def __init__(self):
		self.dbg=False
		self.confFile="appconfig.conf"
		self.home=os.environ.get('HOME',"/usr/share/{}".format(self.confFile.split('.')[0]))
		self.localConf=self.confFile
		self.n4dConf="n4d-%s"%self.confFile
		self.baseDirs={"user":"{}/.config".format(self.home),"system":"/usr/share/{}".format(self.confFile.split('.')[0]),"n4d":"/usr/share/{}".format(self.confFile.split('.')[0])}
		self.config={'user':{},'system':{},'n4d':{}}
		self.n4dcredentials=[]
		self.server="172.20.9.174"
		self.n4d=appConfigN4d()
	#def __init__

	def _debug(self,msg):
		if self.dbg:
			print("Config: {}".format(msg))
	#def _debug

	def set_baseDirs(self,dirs):
		self.baseDirs=dirs.copy()
		if 'nd4' not in self.baseDirs.keys():
			self.baseDirs['n4d']=self.baseDirs['system']
		self._debug("baseDirs: %s"%self.baseDirs)
	#def set_baseDirs

	def set_configFile(self,confFile):
		self.confFile=confFile
		self.localConf=self.confFile
		self.n4dConf=self.confFile.split('.')[0]
		self._debug("ConfFile: %s"%self.confFile)
	#def set_confFile

	def get_configFile(self,level=None):
		confFile={}
		if level in self.baseDirs.keys():
			conf=os.path.join(self.baseDirs[level],self.confFile)
			confFile.update({level:conf})
		else:
			for level,item in self.baseDirs.items():
				if level=='n4d':
					continue
				conf=os.path.join(item,self.confFile)
				confFile.update({level:conf})
		return confFile
	#def get_configFile

	def set_defaultConfig(self,config):
		self.config.update({'default':config})
#		self._debug(self.config)
	#def set_defaultConfig

	def set_level(self,level):
		self.level=level
#		if level=='n4d':
#			self.confFile=self.n4dConf
#		else:
#			self.confFile=self.localConf
	#def set_level

	def getLevel(self):
		config=self.getConfig('system')
		level=config['system'].get('config','user')
		self.set_level(level)
		return(level)
	#def getLevel

	def getConfig(self,level=None,exclude=[]):
		self.config={'user':{},'system':{},'n4d':{}}
		if level=='n4d':
#			self.confFile=self.n4dConf
			self._read_config_from_n4d(exclude)
		else:
			self.confFile=self.localConf
			if self._read_config_from_system(level,exclude)==False:
#				self.confFile=self.n4dConf
				self._read_config_from_n4d(exclude)
				self.config['system']['config']='n4d'

		if self.config[level]=={}:
			self.config[level]['config']=level
		config=self.config.copy()
#		self._debug("Data -> %s"%(self.config))
		return (config)
	#def getConfig

	def _read_config_from_system(self,level=None,exclude=[]):
		def _read_file(confFile,level):
			data={}
			self._debug("Reading %s -> %s"%(confFile,level))
			if os.path.isfile(confFile):
				try:
					data=json.loads(open(confFile).read())
				except Exception as e:
					self._debug("Error opening %s: %s"%(confFile,e))
					
			if data:
				if not 'config' in data.keys():
					data['config']=level
				for excludeKey in exclude:
					if excludeKey in list(data.keys()):
						del data[excludeKey]
				self._debug("Updating %s -> %s"%(confFile,level))
				self.config.update({level:data})
		#def _read_file
		fileRead=False
		confFiles=self.get_configFile(level)
		for confLevel,confFile in confFiles.items():
			if os.path.isfile(confFile):
				fileRead=True
				_read_file(confFile,confLevel)
		return fileRead

	#def read_config_from_system

	def write_config(self,data,level=None,key=None,pk=None,create=True):
		self._debug("Writing key %s to %s Polkit:%s"%(key,level,pk))
		retval=True
		if level==None:
			level=self.getLevel()
#		if level=='n4d':
#			self.confFile=self.n4dConf
#		else:
#			self.confFile=self.localConf
		if level=='system' and not pk:
			self._debug("Invoking pk")
			try:
				data=json.dumps(data)
				subprocess.check_call(["pkexec","/usr/share/appconfig/auth/appconfig-polkit-helper.py",data,level,key,self.confFile,self.baseDirs[level]])
			except Exception as e:
				self._debug("Invoking pk failed: %s"%e)
				retval=False
		else:
			oldConf=self.getConfig(level)
#			self._debug("Old: %s"%oldConf)
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
			if level=='n4d':
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
#		self._debug("Writing info %s"%self.config[level])
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
#			self._debug("New: %s"%self.config[level])
			try:
				with open(confFile,'w') as f:
					json.dump(self.config[level],f,indent=4,sort_keys=True)
			except Exception as e:
				retval=False
				print("Error writing system config: %s"%e)
		return (retval)
	#def _write_config_to_system

	def _write_config_to_n4d(self,conf):
		ret=self.n4d.writeConfig(n4dparms="%s,%s"%(self.confFile,conf['n4d']))
		self._debug("N4d returns: %s"%ret)
		return(ret)
	#def _write_config_to_n4d
	
	def _read_config_from_n4d(self,exclude=[]):
		tmpStr="{}"
		ret=self.n4d.readConfig(n4dparms="%s"%self.confFile,exclude=exclude)
		self.config.update({'n4d':ret})
		return(ret)
	#def _read_config_from_n4d

	def n4dGetVar(self,client=None,var=''):
		ret=self.n4d.n4dGetVar(client,var)
		return(ret)
	#def n4dQuery
	
	def n4dSetVar(self,client=None,var='',val={}):
		ret=self.n4d.n4dSetVar(client,var,val)
		return(ret)
	#def n4dQuery

	def n4dQuery(self,n4dclass,n4dmethod,*args,**kwargs):
		ret=self.n4d.n4dQuery(n4dclass,n4dmethod,*args,**kwargs)
		return(ret)
