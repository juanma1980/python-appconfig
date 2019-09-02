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

class exampleStack(QWidget):
	def __init__(self):
		super().__init__()
		#Debug mode
		self.dbg=True
		self.config=appConfig()
		#Description shown at "From here you can..." box
		self.menu_description=(_("See an example stack"))
		#Description shown at config panel
		self.description=(_("Configure Example Stack"))
		#Icon for the menu item
		self.icon=('dialog-password')
		#Tooltip
		self.tooltip=(_("From here you can see an example stack"))
		#If enabled=False then the stack is not loaded
		self.enabled=True
		#Index position at menu list
		self.index=6
		#Switch that controls if there's any change
		self.sw_changes=False
		#Default config level (one from "user", "system" or "n4d")
		self.level='user'
		#
		self._load_screen()

	#Those methods must be present at all config stacks ->

	def _debug(self,msg):
		if self.dbg:
			print("ConfExample: %s"%msg)
	#def _debug

	def set_textDomain(self,textDomain):
		gettext.textdomain(textDomain)
	#def set_textDomain

	def set_confLevel(self,level):
		self.level=level
	
	def get_changes(self):
		return (self.sw_changes)

	#Those methods must be present at all config stacks <-

	def _load_screen(self):
		box=QVBoxLayout()
		lbl_txt=QLabel(_("Example Stack"))
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
		#Call config library
		#self.config.write_config(data,level=self.level,key=key)
		self.sw_changes=False
	#def _save_apps

	def _get_data(self):
		data="Output from a process"
		return(data)
	
