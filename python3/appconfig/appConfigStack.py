#!/usr/bin/env python3
from PyQt5.QtWidgets import QWidget
from appconfig.appConfig import appConfig 

class appConfStack(QWidget):
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
		self.config=appConfig()
	#def __init__
	
	def _debug(self,msg):
		if self.dbg:
			print("confStack: %s"%msg)
	#def _debug

	def set_textDomain(self,textDomain):
		gettext.textdomain(textDomain)
	#def set_textDomain(self,textDomain):
	
	def apply_parms(self,app):
		self._debug("Set parm %s"%app)
		self.app=app
	#def apply_parms(self,app):

	def get_default_config(self):
		data={}
		data=self.config.get_config('system')
		self.level=data['system'].get('config','user')
		self._debug("Read level from config: %s"%self.level)
		return (data)
	#def get_default_config
	
	def getChanges(self):
		return (self.sw_changes)
	#def getChanges
