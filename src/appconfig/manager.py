#!/usr/bin/env python3
import sys
import os
import json
import tempfile

class manager():
	def __init__(self,fileformat="",name="",relativepath="",level=""):
		self.dbg=True
		self.formats=["json"]
		self.basePaths={"system":"/usr/share/","user":os.path.join(os.environ["HOME"],".config")}
		idx=0
		if fileformat!="":
			if fileformat in self.formats:
				idx=self.formats.index(fileFormat)
		self.currentFormat=idx
		if relativepath!="":
			if os.path.exists(relativepath)==False:
				if relativepath.endswith("/")==False:
					if "." in relativepath.split("/")[-1]==True:
						relativepath=os.path.dirname(relativepath)
					relativepath=relativepath+"/"
			elif os.path.isdir(relativepath)==False:
				relativepath=os.path.dirname(relativepath)
				name=os.path.basename(relativepath)
		else:
			relativepath="appconfig"
		if name=="":
			self.fname="{}.{}".format(os.path.basename(relativepath),self.formats[self.currentFormat])
		else:
			self.fname=name
		self.relativepath=os.path.join(relativepath,self.fname)
		if level=="":
			level="user"
		self.level=level
	#def __init__

	def _debug(self,msg):
		if self.dbg==True:
			print("{}".format(msg))
	#def _debug

	def getConfig(self):
		config={}
		if self.formats[self.currentFormat]=="json":
			config=self._readJsonFile()
		elif self.formats[self.currentFormat]=="yaml":
			#config=self._readYamlFile()
			pass
		elif self.formats[self.currentFormat]=="kde":
			#config=self._readKdeFile()
			pass
		elif self.formats[self.currentFormat]=="ini":
			#config=self._readIniFile()
			pass
		return(config)
	#def getConfig

	def _readJsonFile(self):
		fcontent={}
		path=os.path.join(self.basePaths.get(self.level),self.relativepath)
		self._debug("Reading JSON {}".format(path))
		if os.path.exists(path):
			with open(path,"r") as f:
				try:
					fcontent=json.load(f)
				except Exception as e:
					self._debug("Error: {}".format(e))
		return(fcontent)
	#def _readJsonFile

	def writeConfig(self,data):
		if self.formats[self.currentFormat]=="json":
			config=self._writeJsonFile(data)
		elif self.formats[self.currentFormat]=="yaml":
			#config=self._writeYamlFile(data)
			pass
		elif self.formats[self.currentFormat]=="kde":
			#config=self._writeKdeFile(data)
			pass
		elif self.formats[self.currentFormat]=="ini":
			#config=self._writeIniFile(data)
			pass
		return(config)
	#def writeConfig

	def _writeJsonFile(self,data):
		path=os.path.join(self.basePaths.get(self.level),self.relativepath)
		if os.path.exists(os.path.dirname(path))==False:
			os.makedirs(os.path.dirname(path))
		self._debug("Writing JSON {}".format(path))
		if isinstance(data,dict):
			jcontent=self._readJsonFile()
			jcontent.update(data)
			with open(path,"w") as f:
				try:
					json.dump(jcontent,f,indent=4)
				except Exception as e:
					self._debug("Error: {}".format(e))
		else:
			self._debug("Invalid data")
		return(jcontent)
	#def _writeJsonFile
#class appConfig

