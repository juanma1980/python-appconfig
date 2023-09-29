#!/usr/bin/env python3
import traceback
from PySide2.QtWidgets import QDialog,QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QGridLayout,QLabel,QPushButton,QLineEdit,QRadioButton,QCheckBox,QComboBox,QTableWidget,QSlider,QScrollArea
from PySide2 import QtGui
#from PySide2.QtWidgets import QApplication
from PySide2.QtCore import Qt,QUrl,QObject, Slot, Signal, Property,QThread,QSize
import logging
import notify2
import gettext
try:
	confText=gettext.translation("python3-appconfig")
	_ = confText.gettext
except:
	gettext.textdomain('python3-appconfig')
	_ = gettext.gettext
#_ = nullTrans.gettext

class appConfigStack(QWidget):
	requestWindowTitle=Signal(str)
	def __init__(self,stack):
		super().__init__()
		self.dbg=True
		self.default_icon='shell'
		self.menu_description=(_("Configure stack"))
		self.description=(_("Configure custom stack"))
		self.icon=('org.kde.plasma.quicklaunch')
		self.tooltip=(_("From here you can configure something"))
		self.index=1
		self.enabled=True
		self.changes=False
		self.level='user'
		self.appConfig=None
		self.config={}
		self.changes=False
		self.add_events=False
		self.refresh=False
		self.stack=stack
		self.textdomain='python3-appconfig'
		self.force_change=False
		self.btn_ok=QPushButton(_("Apply"))
		self.btn_cancel=QPushButton(_("Undo"))
		self.__init_stack__()
		self.writeConfig=self.decorator_writeConfig(self.writeConfig)
		self.updateScreen=self.decorator_updateScreen(self.updateScreen)
	#def __init__

	def __init_stack__(self):
		raise NotImplementedError()
	#def __init_stack__
	
	def _debug(self,msg):
		if self.dbg:
			print("Stack {0}: {1}".format(self.description,msg))
	#def _debug

	def initScreen(self):
		self._debug("No init values")

	def setAppConfig(self,appconfig):
		self.appConfig=appconfig
	#def setAppConfig

	def translate(self,msg=""):
		translated=gettext.dgettext(self.textdomain,msg)
		return(translated)

	def setTextDomain(self,textDomain):
			#gettext.textdomain(textDomain)
		gettext.textdomain('{}'.format(textDomain))
		_ = gettext.gettext
	#def set_textDomain(self,textDomain):
	
	def applyParms(self,app):
		self._debug("Set parm %s"%app)
		self.app=app
	#def apply_parms(self,app):

	def getConfig(self,level=None,exclude=[]):
		self._debug("Getting config for level {}".format(level))
		self._debug("Exclude keys: {}".format(exclude))
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.setCursor(cursor)
		data={'system':{},'user':{},'n4d':{}}
		self._debug("Refresh: {}".format(self.refresh))
		self._debug("Changes: {}".format(self.changes))
		if self.refresh or self.changes:
			if level:
				data=self.appConfig.getConfig(level,exclude)
			else:
				data=self.appConfig.getConfig('system',exclude)
#				self._debug("Data: %s"%data)
				self.level=data['system'].get('config','user')
				if self.level!='system':
					data=self.appConfig.getConfig(self.level,exclude)
					level=data[self.level].get('config','user')
					if level!=self.level:
						self.level=level
						data=self.appConfig.getConfig(level,exclude)
						data[self.level]['config']=self.level
		else:
			if self.config.get(self.level):
				data[self.level]=self.config[self.level].copy()
		self._debug("Read level from config: {}".format(self.level))
		self.refresh=False
		cursor=QtGui.QCursor(Qt.PointingHandCursor)
		self.setCursor(cursor)
		return (data)
	#def get_default_config

	def setConfig(self,config):
		if self.config and self.config==config:
			self.refresh=False
		else:
			if self.config:
				self.refresh=True
			self.config=config.copy()
	#def setConfig

	def setLevel(self,level):
		self.level=level
	#def setLevel

	def setWindowTitle(self,title):
		self.requestWindowTitle.emit("{}".format(title))
	#def setWindowTitle
	
	def _reset_screen(self):
		self.updateScreen()
		#self.setChanged(False)
	#def _reset_screen

	def decorator_updateScreen(self,func):
		def states(*args):
			self._debug("Updating screen: Disconnecting signals")
			layout=self.layout()
			if layout:
				self.recursive_add_events(layout,False)
			func(*args)
			self.force_change=True
			self.changes=False
			self._debug("Updated screen: Connecting signals")
			if layout:
				self.recursive_add_events(layout)
		return (states)
	#def decorator_updateScreen

	def updateScreen(self):
		print("updateScreen method not implemented in this stack")
		raise NotImplementedError()
	#def updateScreen

	def saveChanges(self,key,data,level=None):
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.setCursor(cursor)
		retval=False
		if not level:
			self.getConfig()
			level=self.level
		self._debug("Saving to level {}".format(level))
		retval=True
		if not self.appConfig.write_config(data,level=level,key=key):
			self.btn_ok.setEnabled(True)
			self.btn_cancel.setEnabled(True)
			self.refresh=False
			self.changes=True
			retval=False
			self.showMsg(_("Not enough permissions. Operation failed"))
		cursor=QtGui.QCursor(Qt.PointingHandCursor)
		self.setCursor(cursor)
		return retval
	#def saveChanges
	
	def decorator_writeConfig(self,func):
		def states():
			cursor=QtGui.QCursor(Qt.WaitCursor)
			self.setCursor(cursor)
			self.setEnabled(False)
			func()
			self.refresh=True
			self.changes=False
			self.setEnabled(True)
			self.btn_ok.setEnabled(False)
			self.btn_cancel.setEnabled(False)
			cursor=QtGui.QCursor(Qt.PointingHandCursor)
			self.setCursor(cursor)
		return states
	#def decorator_writeConfig

	def writeConfig(self):
		print("writeConfig method not implemented in this stack")
		raise NotImplementedError()
	#def writeConfig


	def recursive_add_events(self,layout,connect=True):
			
		def recursive_explore_widgets(widget):
			if widget==None or widget in [self.btn_ok,self.btn_cancel]:
				return
			if connect==False:
				widget.blockSignals(True)
			else:
				widget.blockSignals(False)
				if self.add_events==False:
					if isinstance(widget,QCheckBox):
						#widget.stateChanged.connect(self.setChanged,Qt.UniqueConnection)
						widget.stateChanged.connect(lambda x: self.setChanged(True,widget),Qt.UniqueConnection)
					if isinstance(widget,QRadioButton):
						widget.toggled.connect(lambda x: self.setChanged(True,widget),Qt.UniqueConnection)#self.setChanged,Qt.UniqueConnection)
					elif isinstance(widget,QComboBox):
						widget.currentTextChanged.connect(lambda x: self.setChanged(True,widget),Qt.UniqueConnection)#(self.setChanged,Qt.UniqueConnection)
					elif isinstance(widget,QLineEdit):
						widget.textChanged.connect(lambda x: self.setChanged(True,widget),Qt.UniqueConnection)#(self.setChanged,Qt.UniqueConnection)
					elif isinstance(widget,QSlider):
						widget.valueChanged.connect(lambda x: self.setChanged(True,widget),Qt.UniqueConnection)#(self.setChanged,Qt.UniqueConnection)
					#elif isinstance(widget,QTableWidget):
					#	widget.cellChanged.connect(lambda x: self.setChanged(True,widget),Qt.UniqueConnection)#(self.setChanged,Qt.UniqueConnection)
					elif isinstance(widget,QPushButton):
						if widget.menu():
							widget.menu().triggered.connect(lambda x: self.setChanged(True,widget),Qt.UniqueConnection)#(self.setChanged,Qt.UniqueConnection)
						else:
							widget.clicked.connect(lambda x: self.setChanged(True,widget),Qt.UniqueConnection)#(self.setChanged,Qt.UniqueConnection)
					elif 'dropButton' in str(widget):
						widget.drop.connect(lambda x: self.setChanged(True,widget),Qt.UniqueConnection)#(self.setChanged,Qt.UniqueConnection)
					elif isinstance(widget,QTableWidget):
						widget.cellChanged.connect(lambda x: self.setChanged(True,widget),Qt.UniqueConnection)#(self.setChanged,Qt.UniqueConnection)
			if isinstance(widget,QTableWidget):
				for x in range (0,widget.rowCount()):
					for y in range (0,widget.columnCount()):
						tableWidget=widget.cellWidget(x,y)
						recursive_explore_widgets(tableWidget)
			if isinstance(widget,QScrollArea):
				wdg=widget.widget()
				if wdg:
					recursive_explore_widgets(wdg)
				else:
					lay=widget.layout()
					if lay:
						recursive_explore_widgets(lay)
			else:
				if type(widget) in [QGridLayout,QVBoxLayout,QHBoxLayout]:
					self.recursive_add_events(widget,connect)
				else:
					try:
						if widget.layout():
							self.recursive_add_events(widget.layout(),connect)
					except:
							self.recursive_add_events(widget,connect)
			#def recursive_explore_widgets(widget):
		self._debug("Settting events from layout {0} to {1}".format(layout,connect))
		for idx in range(0,layout.count()):
			widget=layout.itemAt(idx).widget()
			if isinstance(widget,QWidget):
				recursive_explore_widgets(widget)

			elif layout.itemAt(idx).layout():
				self.recursive_add_events(layout.itemAt(idx).layout(),connect)
		#recursive_add_events

	def showEvent(self,event):

		if self.add_events==False:
			layout=self.layout()
			if layout:
				self.recursive_add_events(layout,False)
				box_btns=QHBoxLayout()
				box_btns.insertStretch(0)
				self.btn_ok.clicked.connect(self.writeConfig)
				#self.btn_ok.setFixedWidth(self.btn_ok.sizeHint().width())
				self.btn_cancel.clicked.connect(self._reset_screen)
				#self.btn_cancel.setFixedWidth(self.btn_ok.sizeHint().width())
				box_btns.addWidget(self.btn_ok)#,1,Qt.AlignRight)
				box_btns.addWidget(self.btn_cancel)#,1,Qt.AlignRight)
				try:
					layout.addLayout(box_btns,Qt.AlignRight)
				except:
					layout.addLayout(box_btns,layout.rowCount(),0,1,layout.columnCount())
				self.recursive_add_events(layout,True)
			self.add_events=True
		self.btn_ok.setEnabled(False)
		self.btn_cancel.setEnabled(False)
		try:
			self.updateScreen()
		except NotImplementedError as e:
			print("updateScreen method is not implemented in this stack")
		except Exception as e:
			print("{}".format(e))
			traceback.print_exc()
		self.setChanged(False)
	#def showEvent

	def hideControlButtons(self):
		self.btn_ok.hide()
		self.btn_cancel.hide()
	#def hideControlButtons(self):

	def setChanged(self,state=True,*args):
		self._debug("State: {}".format(state))
		self._debug("State: {}".format(type(state)))
		self._debug("Force State: {}".format(self.force_change))
		if self.force_change!=True:
			if isinstance(state,int):
				state=True
			elif isinstance(state,str) and len(str)>0:
				state=True
			elif not isinstance(state,bool):
				state=False
		if self.btn_ok.isHidden()==True:
			state=False

		#if self.btn_ok.isHidden()==False or self.force_change==True:
		#	if self.force_change==True:
		#		state=True
		#else:
		#	state=False
		self.btn_ok.setEnabled(state)
		self.btn_cancel.setEnabled(state)
		self.changes=state
		self.force_change=False
		self._debug("New State: {}".format(state))
	#def setChanged

	def getChanges(self):
		self._debug("Read state: {}".format(self.changes))
		return self.changes
	#def getChanges

	def setParms(self,parms):
		return
	#def setParms

	def showMsg(self,msg,title='',state=None):
		self._debug("Sending {}".format(msg))
		if title=='':
			title=self.description
		try:
			notify2.init(title)
			notice = notify2.Notification(msg)
			notice.show()
		except:
			print(msg)
		return
	#def showMsg

	def n4dGetVar(self,client=None,var=''):
		ret=self.appConfig.n4dGetVar(client,var)
		return(ret)
	#def n4dQuery
	
	def n4dSetVar(self,client=None,var='',val={}):
		ret=self.appConfig.n4dSetVar(client,var,val)
		return(ret)
	#def n4dQuery

	def n4dDelVar(self,client=None,var=''):
		ret=self.appConfig.n4dDelVar(client,var)
		return(ret)
	#def n4dQuery

	def n4dQuery(self,n4dclass,n4dmethod,*args,**kwargs):
		ret=self.appConfig.n4dQuery(n4dclass,n4dmethod,*args,**kwargs)
		return(ret)
	#def n4dQuery

#class appConfigStack
