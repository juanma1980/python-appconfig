#!/usr/bin/env python3
from PyQt5.QtWidgets import QWidget
import gettext
_ = gettext.gettext

class appConfigStack(QWidget):
	def __init__(self):
		super().__init__()
		self.dbg=True
		self.default_icon='shell'
		self.menu_description=(_("Configure stack"))
		self.description=(_("Configure custom stack"))
		self.icon=('org.kde.plasma.quicklaunch')
		self.tooltip=(_("From here you can configure something"))
		self.index=1
		self.enabled=True
		self.sw_changes=False
		self.level='user'
		self.appConfig=None
		self.config={}
		self.__init_stack__()
	#def __init__

	def __init_stack__(self):
		pass
	
	def _debug(self,msg):
		if self.dbg:
			print("confStack: %s"%msg)
	#def _debug

	def setAppConfig(self,appconfig):
		self.appConfig=appconfig
	#def setAppConfig

	def setTextDomain(self,textDomain):
		gettext.textdomain(textDomain)
	#def set_textDomain(self,textDomain):
	
	def applyParms(self,app):
		self._debug("Set parm %s"%app)
		self.app=app
	#def apply_parms(self,app):

	def getConfig(self):
		data={}
		data=self.appConfig.getConfig('system')
		self._debug("Data: %s"%data)
		self.level=data['system'].get('config','user')
		if self.level!='system':
			data=self.appConfig.getConfig(self.level)
			level=data[self.level].get('config','user')
			if level!=self.level:
				data[self.level]['config']=self.level

		self._debug("Read level from config: %s"%self.level)
		return (data)
	#def get_default_config

	def setConfig(self,config):
		self.config=config.copy()
	#def setConfig
	
	def saveChanges(self,key,data,level=None):
		if not level:
			level=self.level
		self._debug("Saving to level %s"%level)
		self.appConfig.write_config(data,level=level,key=key)
	#def write_config
	
	def updateScreen(self):
		pass
	#def updateScreen
		
	def showEvent(self,event):
		self.updateScreen()
	#def paintEvent
