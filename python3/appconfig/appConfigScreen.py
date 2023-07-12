#!/usr/bin/env python3
import sys
import os
from urllib.request import Request,urlopen,urlretrieve
from pathlib import Path
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,\
				QDialog,QGridLayout,QHBoxLayout,QFormLayout,QLineEdit,QComboBox,\
				QStatusBar,QFileDialog,QDialogButtonBox,QScrollBar,QScrollArea,QListWidget,\
				QListWidgetItem,QStackedWidget,QButtonGroup,QComboBox,QTableWidget,QTableWidgetItem,\
				QHeaderView,QMessageBox,QAbstractItemView
from PySide2 import QtGui
from PySide2.QtCore import QSize,Slot,Qt, QPropertyAnimation,QThread,QRect,QTimer,Signal,QSignalMapper,QProcess,QEvent,QModelIndex,QRect
from appconfig.appConfig import appConfig 
from appconfig.appConfigStack import appConfigStack

import gettext
try:
	confText=gettext.translation("python3-appconfig")
	_ = confText.gettext
except:
	gettext.textdomain('python3-appconfig')
	_ = gettext.gettext

QString=type("")
QInt=type(0)

BTN_MENU_SIZE=24

class leftPanel(QListWidget):
	acceptChange=Signal()
	pendingChange=Signal("PyObject","PyObject")
	refreshConfig=Signal()

	def __init__(self,stacks):
		super().__init__()
		self.dbg=False
		self.stacks=stacks
		self.lastIndex=0
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setMinimumHeight(0)
	#def __init__

	def _debug(self,msg):
		if self.dbg:
			print("{}".format(msg))
	#def _debug

	def mousePressEvent(self, event):
		x=event.pos().x()
		y=event.pos().y()
		row=self.currentRow()
		item=self.currentItem()
		newItem=self.itemAt(x,y)
		self.setCurrentItem(newItem)
		newRow=self.currentRow()
		self._navigate(event,item,newItem,row,newRow)
		return True
	#def mousePressEvent

	def keyPressEvent(self, event):
		if event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Space):
			newRow=self.currentRow()
			newItem=self.currentItem()
			self.setCurrentItem(newItem)
			row=self.lastIndex
			item=self.item(row)
			self._navigate(event,item,newItem,row,newRow)
		elif event.key()==Qt.Key_Up:
			if self.currentRow()>0:
				row=self.currentRow()-1
				self.setCurrentRow(row)
		elif event.key()==Qt.Key_Down:
			if self.currentRow()<self.count()-1:
				row=self.currentRow()+1
				self.setCurrentRow(row)
		event.ignore()
		return False
	#def keyPressEvent

	def _navigate(self,event,item,newItem,row,newRow):
		if isinstance(item,QListWidgetItem):
			for idx,data in self.stacks.items():
				if item.text().lower()==data.get("name","").lower():
					self.lastIndex=idx
					self.updateIndex(idx)
		else:
			self.lastIndex+=1

		if isinstance(self.stacks.get(self.lastIndex,{}).get('module',None),appConfigStack)==True:
			if self.stacks[self.lastIndex]['module'].getChanges():
				event.ignore()
				self.setCurrentItem(item)
				self.pendingChange.emit(item,newItem)
				return False
			self.stacks[self.lastIndex]['module'].initScreen()
			if self.stacks[self.lastIndex]['module'].refresh:
				self._debug("Refresh config")
				self.refreshConfig.emit()
		event.accept()
		self._acceptNavigate(row)
	#def _navigate

	def _acceptNavigate(self,row):
		self.acceptChange.emit()
		return True
	#def _acceptChange

	def updateIndex(self,index):
		self._debug("Updating index: {}. Was {}".format(index,self.lastIndex))
		if isinstance(index,int)==False:
			index=0
		self.lastIndex=index
	#def updateIndex

	def updateIndexFromName(self,name):
		self._debug("Searching idx of {}".format(name))
		for idx,data in self.stacks.items():
			if data.get("name","").lower()==str(name).lower():
				self._debug("List Located {} at idx {}".format(name,idx))
				self.updateIndex(idx)
	#def updateIndexFromName

	def getIndex(self):
		return(self.currentRow())
	#def getIndex(self)

	def getLastIndex(self):
		return(self.lastIndex)
	#def getLastIndex

	def getIndexForStack(self):
		return(self.currentRow()+1)
	#def getIndexForStack

	def sizeHint(self):
		s = QSize()
		s.setHeight(super(QListWidget,self).sizeHint().height())
		s.setWidth(self.sizeHintForColumn(0))
		return s
#class leftPanel

class appConfigScreen(QWidget):
	def __init__(self,appName,parms={}):
		super().__init__()
		self.dbg=False
		self.level='user'
		exePath=sys.argv[0]
		if os.path.islink(sys.argv[0]):
			exePath=os.path.realpath(sys.argv[0])
		baseDir=os.path.abspath(os.path.dirname(exePath))
		os.chdir(baseDir)
		self.rsrc=os.path.join(baseDir,"rsrc")
		self.parms=parms
		self.modules=[]
		self.appName=appName
		self.textDomain=self.appName.lower().replace(" ","_")
		gettext.textdomain('{}'.format(self.textDomain))
		_ = gettext.gettext
		self.wikiPage=appName
		self.background=os.path.join(self.rsrc,"background.png")
		self.banner=os.path.join(self.rsrc,"banner.png")
		self.last_index=0
		self.stacks={0:{'name':_("Options"),'icon':'icon'}}
		self.appConfig=appConfig()
		self.hideLeftPanel=False
		self.setAttribute(Qt.WA_DeleteOnClose, True)
		self.config={}
	#def init
	
	def _debug(self,msg):
		if self.dbg:
			print("ConfigScreen: {}".format(msg))
	#def _debug

	def setWiki(self,url):
		self.wikiPage=url
	#def setWiki

	def hideNavMenu(self,hide=False):
		self.hideLeftPanel=False
		if isinstance(hide,bool):
			self.hideLeftPanel=hide
	#def hideNavMenu(self,hide=False):

	def setTextDomain(self,textDomain):
		self.textDomain=textDomain
	#def setTextDomain

	def setRsrcPath(self,rsrc):
		if os.path.isdir(rsrc):
			self.rsrc=rsrc
		else:
			self._debug("{} doesn't exists".format(rsrc))
		self._debug("Resources dir: {}".format(self.rsrc))
	#def setRsrcPath

	def setIcon(self,icon):
		self._debug("Icon: {}".format(icon))
		icn=icon
		if not os.path.isfile(icon):
			sw_ko=False
			self._debug("{} not found".format(icon))
			if QtGui.QIcon.fromTheme(icon):
				icn=QtGui.QIcon.fromTheme(icon)
				if icn.name()=="":
					self._debug("{} not present at theme".format(icon))
					sw_ko=True
				else:
					self._debug("{} found at theme".format(icon))
					self._debug("Name: {} found at theme".format(icn.name()))
			elif os.path.isfile(os.path.join(self.rsrc,icon)):
				icon=os.path.join(self.rsrc,icon)
				self._debug("{} found at rsrc folder".format(icon))
				icn=QtGui.QIcon(icon)
			else:
				icn=QtGui.QIcon.fromTheme("application-menu")
				self._debug("Icon not found at {}".format(self.rsrc))
			if sw_ko:
				icn=QtGui.QIcon.fromTheme("application-menu")
				self._debug("Icon {} not found at theme".format(icon))
		self.setWindowIcon(icn)
	#def setIcon

	def setBanner(self,banner):
		if not os.path.isfile(banner):
			if os.path.isfile(os.path.join(self.rsrc,banner)):
				banner=os.path.join(self.rsrc,banner)
			else:
				banner=""
				self._debug("Banner not found at {}".format(self.rsrc))
		self.banner=banner
	#def setBanner
	
	def setBackgroundImage(self,background):
		if not os.path.isfile(background):
			if os.path.isfile(os.path.join(self.rsrc,background)):
				banner=os.path.join(self.rsrc,background)
			else:
				background=""
				self._debug("Background not found at {}".format(self.rsrc))
		self.background=background
	#def setBanner

	def setConfig(self,confDirs,confFile):
		self.appConfig.set_baseDirs(confDirs)
		self.appConfig.set_configFile(confFile)
	#def setConfig(self,confDirs,confFile):
	
	def _searchWiki(self):
		url=""
		baseUrl="https://wiki.edu.gva.es/lliurex/tiki-index.php?page"
		if self.wikiPage.startswith("http"):
			url=self.wikiPage
		else:
			url="{0}={1}".format(baseUrl,self.wikiPage)
		#try:
		#	req=Request(url)
		#	content=urlopen(req).read()
		#except:
		#	self._debug("Wiki not found at %s"%url)
		#	url=""
		return(url)
	#def _searchWiki

	def _get_default_config(self):
		data={}
		self._debug("Forcing system for level {}".format(self.level))
		#data=self.appConfig.getConfig('system')
		data=self.appConfig.getConfig()
		self.level=data.get('system',{}).get('config','user')
		if self.level!='system':
			data=self.appConfig.getConfig(self.level)
			level=data[self.level].get('config','n4d')
			if level!=self.level:
				self.level=level
				data=self.appConfig.getConfig(level)
				data[self.level]['config']=self.level
				
		self._debug("Read level from config: {}".format(self.level))
		return (data)
	#def _get_default_config(self,level):
	
	def getConfig(self,level=None,exclude=[]):
		data=self._get_default_config()
		if not level:
			level=self.level
		if level!='system':
			data={}
			data=self.appConfig.getConfig(level,exclude)
		self.config=data.copy()
		self._debug("Read level from config: {}".format(level))
		return (data)
	#def getConfig(self,level):

	def Show(self):
		if self.config=={}:
			self.getConfig()
		self.setStyleSheet(self._define_css())
		if os.path.isdir("stacks"):
			for mod in os.listdir("stacks"):
				if mod.endswith(".py"):
					mod_name=mod.split(".")[0]
					mod_import="from stacks.{0} import {0}".format(mod_name)
					try:
						exec(mod_import)
						self.modules.append(mod_name)
						self._debug("Load stack {}".format(mod_name))
					except Exception as e:
						self._debug("Unable to load {0} (perhaps aux lib): {1}".format(mod_name,e))
#						print("Unable to load %s: %s"%(mod_name,e))
		idx=1
		for mod_name in self.modules:
			try:
				mod=eval("{}(self)".format(mod_name))
			except Exception as e:
#				self._debug("Import failed for %s: %s"%(mod_name,e))
				print("Import failed for {0}: {1}".format(mod_name,e))
				continue
			if type(mod.index)==type(0):
				if mod.index>0:
					idx=mod.index
			try:
				if mod.enabled==False:
					continue
			except:
				pass
			while idx in self.stacks.keys():
				idx+=1
				self._debug("New idx for {}: {}".format(mod_name,idx))
			if 'parm' in mod.__dict__.keys():
				try:
					if mod.parm:
						self._debug("Setting parms for {}".format(mod_name))
						self._debug("self.parms['{}']".format(mod.parm))
						mod.apply_parms(eval("self.parms['{}']".format(mod.parm)))
				except Exception as e:
					self._debug("Failed to pass parm {0} to {1}: {2}".format(mod.parm,mod_name,e))
			try:
				mod.setTextDomain(self.textDomain)
			except Exception as e:
				print("Can't set textdomain for {}: {}".format(mod_name,e))
			try:
				mod.setAppConfig(self.appConfig)
			except Exception as e:
				print("Can't set appConfig for {}: {}".format(mod_name,e))
			try:
				if mod.visible==False:
					visible=False
				else:
					visible=True
			except:
				visible=True
			self.stacks[idx]={'name':mod.description,'icon':mod.icon,'tooltip':mod.tooltip,'module':mod,'visible':visible}
			try:
				#mod.message.connect(self._show_message)
				mod.requestWindowTitle.connect(self._requestWindowTitle)
			except:
				pass
		self._render_gui()
		return(False)
	#def Show
	
	def _render_gui(self):
		self.getConfig()
		box=QGridLayout()
		img_banner=QLabel()
		if os.path.isfile(self.banner):
			img=QtGui.QPixmap(self.banner)
			img_banner.setPixmap(img)
			img_banner.setAlignment(Qt.AlignCenter)
			img_banner.setObjectName("banner")
			box.addWidget(img_banner,0,0,1,2)
		self.lst_options=leftPanel(self.stacks)#QListWidget()
		self.stk_widget=QStackedWidget()
		self.stk_widget.setMinimumHeight(1)
		r_panel=self._right_panel()
		box.addWidget(r_panel,1,1,1,1)
		idx=0
		if len(self.stacks)>2:
			l_panel=self._left_panel()
			if self.hideLeftPanel==False:
				box.addWidget(l_panel,1,0,1,1)
				box.setColumnStretch(1,1)
			else:
				idx=1
		#	self.stk_widget.setCurrentIndex(0)
		elif self.hideLeftPanel==False:
			idx=1

		#	self.stk_widget.setCurrentIndex(1)
		self.stk_widget.setCurrentIndex(idx)
		#self.gotoStack(idx,"")
		self.setLayout(box)
		margins=self.lst_options.geometry()
		self.show()
	#def _render_gui

	def _left_panel(self):
		panel=QWidget()
		box=QVBoxLayout()
		btn_menu=QPushButton()
		icn=QtGui.QIcon.fromTheme("application-menu")
		btn_menu.setIcon(icn)
		btn_menu.setIconSize(QSize(BTN_MENU_SIZE,BTN_MENU_SIZE))
		btn_menu.setMaximumWidth(BTN_MENU_SIZE)
		btn_menu.setMaximumHeight(BTN_MENU_SIZE)
		btn_menu.setToolTip(_("Options"))
		btn_menu.setObjectName("menuButton")
		indexes=[]
		for index,option in self.stacks.items():
			idx=index
			lst_widget=QListWidgetItem()
			lst_widget.setText(option['name'])
			mod=option.get('module',None)
			if mod:
				try:
					idx=mod.index
				except:
					pass
			if idx>0:
				icn=QtGui.QIcon.fromTheme(option['icon'])
				lst_widget.setIcon(icn)
				if 'tooltip' in option.keys():
					lst_widget.setToolTip(option['tooltip'])
				while idx in indexes:
					idx+=1
				indexes.append(index)
			self.stacks[idx]['widget' ]=lst_widget
		orderedStacks={}
		orderedStacks[0]=self.stacks[0]
		cont=0
		indexes.sort()
		for index in indexes:
			if index:
				orderedStacks[cont]=self.stacks[index].copy()
				if self.stacks[index].get('visible',True)==True:
					self.lst_options.addItem(orderedStacks[cont]['widget'])
				cont+=1

		self.stacks=orderedStacks.copy()
		box.addWidget(self.lst_options)
		self.lst_options.acceptChange.connect(self._show_stack)
		self.lst_options.pendingChange.connect(self._askForChanges)
		self.lst_options.refreshConfig.connect(self._refreshConfig)
		self.lst_options.setCurrentIndex(QModelIndex())
		self.last_index=0
		self.lst_options.updateIndex(self.last_index)
		panel.setLayout(box)

		return(panel)
	#def _left_panel

	def _right_panel(self):
		panel=QWidget()
		box=QVBoxLayout()
		idx=0
		#text=[
		#	_("Welcome to the configuration of ")+self.appName,
		#	_("From here you can:<br>")]
		text=[
			_("Welcome to the configuration of ")+"{}.<br>".format(self.appName)]
		orderIdx=list(self.stacks.keys())
		orderIdx.sort()
		linkIdx=1
		for idx in orderIdx:
			data=self.stacks[idx]
			stack=data.get('module',None)
			if stack:
				stack.setLevel(self.level)
				stack.setConfig(self.config)
				stack._load_screen()

				if self.stacks[idx].get('visible',True)==True:
					text.append("&nbsp;*&nbsp;<a href=\"appconf://{0}\"><span style=\"font-weight:bold;text-decoration:none\">{1}</span></a>".format(linkIdx,stack.menu_description))
				try:
					self.stk_widget.insertWidget(idx,stack)
				except:
					self.stk_widget.insertWidget(idx,stack.init_stack())
				linkIdx+=1
		stack=QWidget()
		stack.setObjectName("panel")
		s_box=QVBoxLayout()
		lbl_txt=QLabel()
		lbl_txt.setTextFormat(Qt.RichText)
		lbl_txt.setText("<br>".join(text))
		lbl_txt.linkActivated.connect(self._linkStack)
		lbl_txt.setObjectName("desc")
		lbl_txt.setAlignment(Qt.AlignTop)
		lbl_txt.setTextInteractionFlags(Qt.TextBrowserInteraction)
		s_box.addWidget(lbl_txt,1)
		#Get wiki page
		url=self._searchWiki()
		if url:
			desc=_("Wiki help")
			lbl_wiki=QLabel("<a href=\"{0}\"><span style=\"text-align: right;\">{1}</span></a>".format(url,desc))
			lbl_wiki.setOpenExternalLinks(True)
			s_box.addWidget(lbl_wiki,0,Qt.AlignRight)
		stack.setLayout(s_box)
		self.stk_widget.insertWidget(0,stack)
		#self.stacks[0]['module']=stack

		box.addWidget(self.stk_widget)
		panel.setLayout(box)
		return(panel)
	#def _right_panel

	def _refreshConfig(self):
		self.getConfig()

	def _linkStack(self,*args):
		stack=args[0].split('/')[-1]
		self.loadStack(int(stack),'')
	#def _linkStack

	def gotoStack(self,idx,parms):
		self._showStack(idx=idx-1,parms=parms,gotoIdx=idx)
	#def gotoStack

	def loadStack(self,idx,parms):
		self._showStack(idx=idx,parms=parms)
	#def loadStack

	def _show_stack(self,*args,item=None,idx=None,parms=None,gotoIdx=None):
		self._showStack(*args,item,idx,parms,gotoIdx)
	#def _show_stack

	def _showStack(self,*args,item=None,idx=None,parms=None,gotoIdx=None):
		if self.hideLeftPanel==False:
			if (self.last_index==abs(self.lst_options.currentRow()) and (idx==self.last_index or isinstance(item,int))):# or self.last_index==None)):
				return

		if isinstance(idx,int)==False:
			idx=self.lst_options.currentRow()+1
		#self.last_index=idx-1
		#self.lst_options.updateIndex(self.last_index)
		try:
			self.stacks[idx]['module'].setConfig(self.config)
		except:
			pass

#		self.statusBar.hide()
		if parms:
			self.stacks[idx]['module'].setParms(parms)
		if gotoIdx:
			idx=gotoIdx
		self.stk_widget.setCurrentIndex(idx)
	#def _show_stack

	def closeEvent(self,event):
		module=self.stacks.get(self.last_index,{}).get('module',None)
		if module!=None:
			if module.getChanges():
				if self._save_changes(self.stacks[self.last_index]['module'])==QMessageBox.Cancel:
					event.ignore()
	#def closeEvent(self,event):

	def _requestWindowTitle(self,title):
		self.setWindowTitle("{}".format(title))
	#def _requestWindowTitle

	def _show_message(self,msg,status=None):
		return
#		self.statusBar.setText(msg)
#		if status:
#			self.statusBar.show(status)
#		else:
#		self.statusBar.show(status)
	#def _show_message

	def _askForChanges(self,*args):
		item=self.lst_options.currentItem()
		#Update last index
		if isinstance(item,QListWidgetItem):
			for idx,data in self.stacks.items():
				if item.text().lower()==data.get("name","").lower():
					self.last_index=idx
					self.lst_options.updateIndexFromName(data.get("name"))
					break
		if isinstance(self.stacks.get(self.last_index,{}).get('module',None),appConfigStack)==True:
			if self.stacks[self.last_index]['module'].getChanges():
				if self._save_changes(self.stacks[self.last_index]['module'])==QMessageBox.Cancel:
					return False
				else:
					self.stacks[self.last_index]['module'].setChanged(False)
			self.stacks[self.last_index]['module'].initScreen()
			if self.stacks[self.last_index]['module'].refresh:
				self._debug("Refresh config")
				self.getConfig()
		else:
			self._debug(self.stacks.get(self.last_index,{}).get('module'))
			self.last_index=0
			#self.lst_options.updateIndex(self.last_index)
		self.lst_options.setCurrentItem(args[1])
		self.stk_widget.setCurrentIndex(self.lst_options.getIndexForStack())
	#def _askForChanges

	def _save_changes(self,module):
		dia=QMessageBox(QMessageBox.Question,_("Apply changes"),_("There're changes not saved at current screen.\nDiscard them and continue?"),QMessageBox.Discard|QMessageBox.Cancel,self)
		resp=dia.exec()
		return(resp)
	#def _save_changes

	def _define_css(self):
		css="""
		QPushButton{
			padding: 6px;
			margin:6px;
		}
		QPushButton#menu:active{
			background:none;
		}
		QStatusBar{
			background:red;
			color:white;
		}
		QLabel{
			padding:6px;
			margin:6px;
		}
	
		#dlgLabel{
			margin:0px;
			border:0px;
			padding:3px;
		}
		
		QLineEdit{
			border:0px;
			border-bottom:1px solid grey;
			padding:1px;
			margin-right:6px;
		}
		#panel{
			background-image:url("%s");
			background-size:stretch;
			background-repeat:no-repeat;
			background-position:center;
		}
		#desc{
			background-color:rgba(255,255,255,0.7);
			color:black;
		}
		#banner{
			padding:1px;
			margin:1px;
			border:0px;
		}
		"""%self.background
		return(css)
	#def _define_css

