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
from PySide2.QtCore import QSize,Slot,Qt, QPropertyAnimation,QThread,QRect,QTimer,Signal,QSignalMapper,QProcess,QEvent,QModelIndex
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

class appConfigScreen(QWidget):
	keybind_signal=Signal("QObject")
	update_signal=Signal("QObject")
	def __init__(self,appName,parms={}):
		super().__init__()
		self.dbg=False
		self.level='user'
		exePath=sys.argv[0]
		if os.path.islink(sys.argv[0]):
			exePath=os.path.realpath(sys.argv[0])
		baseDir=os.path.abspath(os.path.dirname(exePath))
		os.chdir(baseDir)
		self.rsrc="%s/rsrc"%baseDir
		self.parms=parms
		self.modules=[]
		self.appName=appName
		self.textDomain=self.appName.lower().replace(" ","_")
		gettext.textdomain('{}'.format(self.textDomain))
		_ = gettext.gettext
		self.wikiPage=appName
		self.background="%s/background.png"%self.rsrc
		self.banner="%s/%s"%(self.rsrc,"banner.png")
		self.last_index=0
		self.stacks={0:{'name':_("Options"),'icon':'icon'}}
		self.appConfig=appConfig()
		self.hideLeftPanel=False
		self.config={}
	#def init
	
	def _debug(self,msg):
		if self.dbg:
			print("%s"%msg)
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
			self._debug("%s doesn't exists")
		self._debug("Resources dir: %s"%self.rsrc)
	#def setRsrcPath

	def setIcon(self,icon):
		self._debug("Icon: %s"%icon)
		icn=icon
		if not os.path.isfile(icon):
			sw_ko=False
			self._debug("%s not found"%icon)
			if QtGui.QIcon.fromTheme(icon):
				icn=QtGui.QIcon.fromTheme(icon)
				if icn.name()=="":
					self._debug("%s not present at theme"%icon)
					sw_ko=True
				else:
					self._debug("%s found at theme"%icon)
					self._debug("Name: %s found at theme"%icn.name())
			elif os.path.isfile("%s/%s"%(self.rsrc,icon)):
				icon="%s/%s"%(self.rsrc,icon)
				self._debug("%s found at rsrc folder"%icon)
				icn=QtGui.QIcon(icon)
			else:
				icn=QtGui.QIcon.fromTheme("application-menu")
				self._debug("Icon not found at %s"%self.rsrc)
			if sw_ko:
				icn=QtGui.QIcon.fromTheme("application-menu")
				self._debug("Icon %s not found at theme"%icon)
		self.setWindowIcon(icn)
	#def setIcon

	def setBanner(self,banner):
		if not os.path.isfile(banner):
			if os.path.isfile("%s/%s"%(self.rsrc,banner)):
				banner="%s/%s"%(self.rsrc,banner)
			else:
				banner=""
				self._debug("Banner not found at %s"%self.rsrc)
		self.banner=banner
	#def setBanner
	
	def setBackgroundImage(self,background):
		if not os.path.isfile(background):
			if os.path.isfile("%s/%s"%(self.rsrc,background)):
				background="%s/%s"%(self.rsrc,background)
			else:
				background=""
				self._debug("Background not found at %s"%self.rsrc)
		self.background=background
	#def setBanner

	def setConfig(self,confDirs,confFile):
		self.appConfig.set_baseDirs(confDirs)
		self.appConfig.set_configFile(confFile)
	#def setConfig(self,confDirs,confFile):
	
	def _searchWiki(self):
		url=""
		baseUrl="https://wiki.edu.gva.es/lliurex/tiki-index.php?page="
		if self.wikiPage.startswith("http"):
			url=self.wikiPage
		else:
			url="%s%s"%(baseUrl,self.wikiPage)
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
		data=self.appConfig.getConfig('system')
		self.level=data['system'].get('config','user')
		if self.level!='system':
			data=self.appConfig.getConfig(self.level)
			level=data[self.level].get('config','n4d')
			if level!=self.level:
				self.level=level
				data=self.appConfig.getConfig(level)
				data[self.level]['config']=self.level
				
		self._debug("Read level from config: %s"%self.level)
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
		self._debug("Read level from config: %s"%level)
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
					mod_import="from stacks.%s import *"%mod_name
					try:
						exec(mod_import)
						self.modules.append(mod_name)
						self._debug("Load stack %s"%mod_name)
					except Exception as e:
#						self._debug("Unable to load %s: %s"%(mod_name,e))
						print("Unable to load %s: %s"%(mod_name,e))
		idx=1
		for mod_name in self.modules:
			try:
				mod=eval("%s(self)"%mod_name)
			except Exception as e:
#				self._debug("Import failed for %s: %s"%(mod_name,e))
				print("Import failed for %s: %s"%(mod_name,e))
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
				self._debug("New idx for %s: %s"%(mod_name,idx))
			if 'parm' in mod.__dict__.keys():
				try:
					if mod.parm:
						self._debug("Setting parms for %s"%mod_name)
						self._debug("self.parms['%s']"%mod.parm)
						mod.apply_parms(eval("self.parms['%s']"%mod.parm))
				except Exception as e:
					self._debug("Failed to pass parm %s to %s: %s"%(mod.parm,mod_name,e))
			try:
				mod.setTextDomain(self.textDomain)
			except Exception as e:
				print("Can't set textdomain for %s: %s"%(mod_name,e))
			try:
				mod.setAppConfig(self.appConfig)
			except Exception as e:
				print("Can't set appConfig for %s: %s"%(mod_name,e))
			try:
				if mod.visible==False:
					visible=False
				else:
					visible=True
			except:
				visible=True
			self.stacks[idx]={'name':mod.description,'icon':mod.icon,'tooltip':mod.tooltip,'module':mod,'visible':visible}
			try:
				mod.message.connect(self._show_message)
			except:
				pass
		self._render_gui()
		return(False)
	
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
		self.lst_options=QListWidget()
		self.stk_widget=QStackedWidget()
		idx=0
		if len(self.stacks)>2:
			l_panel=self._left_panel()
			if self.hideLeftPanel==False:
				box.addWidget(l_panel,1,0,1,1,Qt.Alignment(1)|Qt.AlignTop)
			else:
				idx=1
		#	self.stk_widget.setCurrentIndex(0)
		elif self.hideLeftPanel==False:
			idx=1

		#	self.stk_widget.setCurrentIndex(1)
		r_panel=self._right_panel()
		self.stk_widget.setCurrentIndex(idx)
		#self.gotoStack(idx,"")
		box.addWidget(r_panel,1,1,1,1)
		self.setLayout(box)
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
#		box.addWidget(btn_menu,Qt.Alignment(1))
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
		#self.lst_options.addItem(orderedStacks[0]['widget'])
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
		self.lst_options.currentRowChanged.connect(self._show_stack)
		self.lst_options.setCurrentIndex(QModelIndex())
		self.last_index=None
		panel.setLayout(box)
		self.resize(self.size().width()+box.sizeHint().width(),self.size().height()+box.sizeHint().height()/2)
		self.lst_options.setFixedSize(self.lst_options.sizeHintForColumn(0)  +2 * (self.lst_options.frameWidth() +15), self.height())#self.lst_options.sizeHintForRow(0) * self.lst_options.count() + 2 * (self.lst_options.frameWidth()+15))

		return(panel)
	#def _left_panel

	def _right_panel(self):
		panel=QWidget()
		box=QVBoxLayout()
		idx=0
		text=[
			_("Welcome to the configuration of ")+self.appName,
			_("From here you can:<br>")]
		orderIdx=list(self.stacks.keys())
		for idx in orderIdx:
			data=self.stacks[idx]
			stack=data.get('module',None)
			if stack:
				stack.setLevel(self.level)
				stack.setConfig(self.config)
				stack._load_screen()

				if self.stacks[idx].get('visible',True)==True:
					text.append("&nbsp;*&nbsp;<a href=\"appconf://%s\"><span style=\"font-weight:bold;text-decoration:none\">%s</span></a>"%(idx+1,stack.menu_description))
				try:
					self.stk_widget.insertWidget(idx,stack)
				except:
					self.stk_widget.insertWidget(idx,stack.init_stack())
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
			lbl_wiki=QLabel("<a href=\"%s\"><span style=\"text-align: right;\">%s</span></a>"%(url,desc))
			lbl_wiki.setOpenExternalLinks(True)
			s_box.addWidget(lbl_wiki,0,Qt.AlignRight)
		stack.setLayout(s_box)
		self.stk_widget.insertWidget(0,stack)
		#self.stacks[0]['module']=stack

		box.addWidget(self.stk_widget)
		panel.setLayout(box)
		return(panel)
	#def _right_panel

	def _linkStack(self,*args):
		stack=args[0].split('/')[-1]
		self.loadStack(int(stack),'')

	def gotoStack(self,idx,parms):
		self._showStack(idx=idx-1,parms=parms,gotoIdx=idx)

	def loadStack(self,idx,parms):
		self._showStack(idx=idx,parms=parms)

	def _show_stack(self,*args,item=None,idx=None,parms=None,gotoIdx=None):
		self._showStack(*args,item,idx,parms,gotoIdx)

	def _showStack(self,*args,item=None,idx=None,parms=None,gotoIdx=None):
		if self.hideLeftPanel==False:
			if (self.last_index==abs(self.lst_options.currentRow()) and (idx==self.last_index or isinstance(item,int))):# or self.last_index==None)):
				return

		if isinstance(self.stacks.get(self.last_index,{}).get('module',None),appConfigStack)==True:
			if self.stacks[self.last_index]['module'].getChanges():
				if self._save_changes(self.stacks[self.last_index]['module'])==QMessageBox.Cancel:
					self.lst_options.setCurrentRow(self.last_index)
					return
				else:
					self.stacks[self.last_index]['module'].setChanged(False)
			self.stacks[self.last_index]['module'].initScreen()
			if self.stacks[self.last_index]['module'].refresh:
				self._debug("Refresh config")
				self.getConfig()
		else:
			self._debug(self.stacks.get(self.last_index,{}).get('module'))
			self.last_index=0
		if isinstance(idx,int)==False:
			idx=self.lst_options.currentRow()+1
		self.last_index=idx-1
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
		try:
			if self.stacks[self.last_index]['module'].getChanges():
				if self._save_changes(self.stacks[self.last_index]['module'])==QMessageBox.Cancel:
					event.ignore()
		except:
			pass

	def _show_message(self,msg,status=None):
		return
#		self.statusBar.setText(msg)
#		if status:
#			self.statusBar.show(status)
#		else:
#		self.statusBar.show(status)
	#def _show_message

	def _save_changes(self,module):
		dia=QMessageBox(QMessageBox.Question,_("Apply changes"),_("There're changes not saved at current screen.\nDiscard them and continue?"),QMessageBox.Discard|QMessageBox.Cancel,self)
		return(dia.exec_())

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

