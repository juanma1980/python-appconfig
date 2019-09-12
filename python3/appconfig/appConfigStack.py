#!/usr/bin/env python3
from PyQt5.QtWidgets import QWidget,QHBoxLayout,QPushButton
from PyQt5.QtCore import pyqtSignal
from edupals.ui import QAnimatedStatusBar
import gettext
_ = gettext.gettext
QString=type("")

class appConfigStack(QWidget):
	message=pyqtSignal("PyQt_PyObject")
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
		self.changes=False
		self.add_events=False
		self.statusBar=QAnimatedStatusBar.QAnimatedStatusBar()
		self.statusBar.setStateCss("success","background-color:qlineargradient(x1:0 y1:0,x2:0 y2:1,stop:0 rgba(0,0,255,1), stop:1 rgba(0,0,255,0.6));color:white;")
		self.__init_stack__()
	#def __init__

	def __init_stack__(self):
		raise NotImplementedError()
	#def __init_stack__
	
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
		self.changes=False
		self._debug("Saving to level %s"%level)
		self.appConfig.write_config(data,level=level,key=key)
	#def saveChanges

	def _reset_screen(self):
		self.updateScreen()
		self.setChanged('',False)
	#def _reset_screen

	def updateScreen(self):
		print("updateScreen method not implemented in this stack")
		raise NotImplementedError()
	#def updateScreen
	
	def writeConfig(self):
		print("writeConfig method not implemented in this stack")
		raise NotImplementedError()
	#def updateScreen

	def showEvent(self,event):
		def recursive_add_events(layout):
			for idx in range(0,layout.count()):
				widget=layout.itemAt(idx).widget()
				if widget:
					if "QCheckBox" in str(widget):
						widget.stateChanged.connect(lambda x:self.setChanged(widget))
					elif "QComboBox" in str(widget):
						widget.currentIndexChanged.connect(lambda x:self.setChanged(widget))
					elif "QLineEdit" in str(widget):
						widget.textChanged.connect(lambda x:self.setChanged(widget))
					elif "QPushButton" in str(widget):
						if widget.menu():
							widget.menu().triggered.connect(lambda x:self.setChanged(widget))
					elif "dropTable" in str(widget):
						widget.drop.connect(lambda x:self.setChanged(widget))
						for x in range (0,widget.rowCount()):
							for y in range (0,widget.columnCount()):
								tableWidget=widget.cellWidget(x,y)
								if 'dropButton' in str(tableWidget):
									tableWidget.drop.connect(lambda x:self.setChanged(tableWidget))

				elif layout.itemAt(idx).layout():
					recursive_add_events(layout.itemAt(idx).layout())

		if self.add_events==False:
			self.add_events=True
			layout=self.layout()
			recursive_add_events(layout)
			box_btns=QHBoxLayout()
			btn_ok=QPushButton(_("Apply"))
			btn_ok.clicked.connect(self.writeConfig)
			btn_cancel=QPushButton(_("Cancel"))
			btn_cancel.clicked.connect(self._reset_screen)
			box_btns.addWidget(btn_ok)
			box_btns.addWidget(btn_cancel)
			try:
				layout.addLayout(box_btns)
			except:
				layout.addLayout(box_btns,layout.rowCount(),0,1,layout.columnCount())
		try:
			self.updateScreen()
		except:
			print("updateScreen method is not implemented in this stack")
	#def showEvent

	def setChanged(self,widget,state=True):
		self._debug("State: %s"%state)
		self.changes=state
	#def setChanged

	def getChanges(self):
		return self.changes
	#def getChanges

	def showMsg(self,msg):
		self.message.emit(msg)

#class appConfigStack
