#!/usr/bin/python3

''' Put this file at subfolder "stacks/". Config screen searches for that folder and loads all modules inside it
i.e:
	- /path/to/project/config.py
	- /path/to/project/stacks/confExample.py
The class name must match the file name
i.e.: If file is called "confExample.py" then the class must be "confExample"
Modify imports, but gettext, as you need, this is only a sample
'''

import sys
import os
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
#Probably you want that
from appconfig.appConfig import appConfig 
#Don't modify this ->
import gettext
_ = gettext.gettext
#Don't modify this <-

class exampleStackParm(QWidget):
	def __init__(self,parameter1=None):
		super().__init__()
		#Debug mode
		self.dbg=True
		#To pass a parm to a stack you must pass it to configScreen (init dict parms {'name':value})
		self.parm="parameter1"
		self.parameter1=None
		#Description shown at "From here you can..." box
		self.menu_description=(_("See an example parametrized stack"))
		#Description shown at config panel
		self.description=(_("Configure Example Stack With Parms"))
		#Icon for the menu item
		self.icon=('dialog-password')
		#Tooltip
		self.tooltip=(_("From here you can see an example parametrized stack"))
		#If enabled=False then the stack is not loaded
		self.enabled=True
		#Index position at menu list
		self.index=6
		#Switch that controls if there's any change
		self.sw_changes=False
		#Configure lib (optional)
		self.config=appConfig()
		#Default config level (one from "user", "system" or "n4d". Needed if you use configure lib)
		self.level='user'
		#Parametrized stacks initialize the screen at apply_parms

	#Those methods must be present at all config stacks ->

	def _debug(self,msg):
		if self.dbg:
			print("ConfExample: %s"%msg)
	#def _debug

	def setTextDomain(self,textDomain):
		gettext.textdomain(textDomain)
	#def set_textDomain

	def setConfigLevel(self,level):
		self.level=level
	#def setConfigLevel
	
	def setRsrcPath(self,rsrc):
		if os.path.isdir(rsrc):
			self.rsrc=rsrc
	#def setRsrcPath

	def getChanges(self):
		return (self.sw_changes)
	#def getChanges

	#Those methods must be present at all config stacks <-
	
	#This method must be present at parametrized config stack ->
	def apply_parms(self,parm):
		self._debug("Set parm %s"%parm)
		self.parm=parm
		self._load_screen()
	#This method must be present at parametrized config stack <-

	def _load_screen(self):
		box=QVBoxLayout()
		lbl_txt=QLabel(_("Example Stack with parm %s"%self.parm))
		lbl_txt.setAlignment(Qt.AlignTop)
		box.addWidget(lbl_txt)
		box_btns=QHBoxLayout()
		btn_ok=QPushButton(_("Apply"))
		btn_ok.clicked.connect(self._save_config)
		btn_cancel=QPushButton(_("Cancel"))
		box_btns.addWidget(btn_ok)
		box_btns.addWidget(btn_cancel)
		box.addLayout(box_btns)
		self.setLayout(box)

	def _save_config(self):
		data=self._get_data()
		key="example"
		#
		#data -> Data to be written
		#level -> Config level (user, system or n4d)
		#key -> Key that will store the data (dict's key for value "data")
		#
		#Call config library
		#self.config.write_config(data,level=self.level,key=key)
		self.sw_changes=False
	#def _save_apps

	def _get_data(self):
		data="Output from a process"
		return(data)
	
