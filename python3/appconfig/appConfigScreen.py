#!/usr/bin/env python3
import sys
import os
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,\
				QDialog,QGridLayout,QHBoxLayout,QFormLayout,QLineEdit,QComboBox,\
				QStatusBar,QFileDialog,QDialogButtonBox,QScrollBar,QScrollArea,QListWidget,\
				QListWidgetItem,QStackedWidget,QButtonGroup,QComboBox,QTableWidget,QTableWidgetItem,\
				QHeaderView
from PyQt5 import QtGui
from PyQt5.QtCore import QSize,pyqtSlot,Qt, QPropertyAnimation,QThread,QRect,QTimer,pyqtSignal,QSignalMapper,QProcess,QEvent
import gettext
from edupals.ui import QAnimatedStatusBar

_ = gettext.gettext

QString=type("")
QInt=type(0)

BTN_MENU_SIZE=24

class appConfigScreen(QWidget):
	keybind_signal=pyqtSignal("PyQt_PyObject")
	update_signal=pyqtSignal("PyQt_PyObject")
	def __init__(self,appName,parms={}):
		super().__init__()
		self.dbg=True
		self.rsrc=""
		self.parms=parms
		self.modules=[]
		self.setStyleSheet(self._define_css())
		self.appName=appName
		gettext.textdomain(self.appName.lower().replace(" ","_"))
		self.categories={}
		self.desktops={}
		self.app_icons={}
		self.icon='shell'
		self.options={0:{'name':"Options",'icon':'icon'}}
		self.widgets={}
	#def init
	
	def _debug(self,msg):
		if self.dbg:
			print("%s"%msg)
	#def _debug

	def load_stacks(self):
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
						self._debug("Unable to load %s: %s"%(mod_name,e))
		idx=1
		for mod_name in self.modules:
			mod=eval("%s()"%mod_name)
			if mod.index>0:
				idx=mod.index
			if mod.enabled==False:
				continue
			while idx in self.options.keys():
				idx+=1
			try:
				if 'parm' in mod.__dict__.keys():
					if mod.parm:
						self._debug("Setting parms for %s"%mod_name)
						mod.apply_parms(eval("self.parms['%s']"%mod.parm))
			except Exception as e:
				self._debug("Failed to pass parm %s to %s: %s"%(mod_parm,mod_name,e))
			self.options[idx]={'name':mod.description,'icon':mod.icon,'tooltip':mod.tooltip,'module':mod}
		self._render_gui()
	
	def _render_gui(self):
		box=QGridLayout()
		img_banner=QLabel()
		img=QtGui.QPixmap("%s/banner.png"%self.rsrc)
		img_banner.setPixmap(img)
		img_banner.setAlignment(Qt.AlignCenter)
		self.statusBar=QAnimatedStatusBar.QAnimatedStatusBar()
		self.statusBar.setStateCss("success","background-color:qlineargradient(x1:0 y1:0,x2:0 y2:1,stop:0 rgba(0,0,255,1), stop:1 rgba(0,0,255,0.6));color:white;")
		self.lst_options=QListWidget()
		self.stk_widget=QStackedWidget()
		box.addWidget(self.statusBar,0,0,1,1)
		box.addWidget(img_banner,0,0,1,2)
		l_panel=self._left_panel()
		box.addWidget(l_panel,1,0,1,1,Qt.Alignment(1))
		r_panel=self._right_panel()
		box.addWidget(r_panel,1,1,1,1)
		self.setLayout(box)
		self.stk_widget.setCurrentIndex(0)
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
		for i in range (100):
			indexes.append("")
		for index,option in self.options.items():
			lst_widget=QListWidgetItem()
			lst_widget.setText(option['name'])
			mod=option.get('module',None)
			if mod:
				index=mod.index
			if index>0:
				icn=QtGui.QIcon.fromTheme(option['icon'])
				lst_widget.setIcon(icn)
				if 'tooltip' in option.keys():
					lst_widget.setToolTip(option['tooltip'])
					indexes.insert(index,index)
			self.options[index]['widget' ]=lst_widget

		new_dict={}
		new_dict[0]=self.options[0]
		self.lst_options.addItem(new_dict[0]['widget'])
		cont=1
		for index in indexes:
			if index:
				new_dict[cont]=self.options[index]
				self.lst_options.addItem(new_dict[cont]['widget'])
				cont+=1

		self.options=new_dict.copy()
		box.addWidget(self.lst_options)
		self.lst_options.itemClicked.connect(self._show_stack)
		panel.setLayout(box)
		return(panel)
	#def _left_panel

	def _right_panel(self):
		panel=QWidget()
		box=QVBoxLayout()
		idx=0
		text=[
			_("Welcome to %s config."%self.appName),
			_("From here you can:")]
		for idx,data in self.options.items():
			stack=self.options[idx].get('module',None)
			if stack:
				text.append(" * %s"%stack.menu_description)
				self.stk_widget.insertWidget(idx,stack)
		stack=QWidget()
		stack.setObjectName("panel")
		s_box=QVBoxLayout()
		lbl_txt=QLabel("\n".join(text))
		lbl_txt.setObjectName("desc")
		lbl_txt.setAlignment(Qt.AlignTop)
		s_box.addWidget(lbl_txt,Qt.Alignment(1))
		stack.setLayout(s_box)
		self.stk_widget.insertWidget(0,stack)
		self.options[0]['module']=stack

		box.addWidget(self.stk_widget)
		panel.setLayout(box)
		return(panel)
	#def _right_panel
	
	def _show_stack(self):
		self.stk_widget.setCurrentIndex(self.lst_options.currentRow())
	#def _show_stack

	def _show_message(self,msg,status=None):
		self.statusBar.setText(msg)
		if status:
			self.statusBar.show(status)
		else:
			self.statusBar.show()
	#def _show_message

	def _define_css(self):
		css="""
		QPushButton{
			padding: 6px;
			margin:6px;
			font: 14px Roboto;
		}
		QPushButton#menu:active{
			background:none;
		}
		QStatusBar{
			background:red;
			color:white;
			font: 14px Roboto bold;
		}
		QLabel{
			padding:6px;
			margin:6px;
		}
	
		#dlgLabel{
			font:12px Roboto;
			margin:0px;
			border:0px;
			padding:3px;
		}
		
		QLineEdit{
			border:0px;
			border-bottom:1px solid grey;
			padding:1px;
			font:14px Roboto;
			margin-right:6px;
		}
		#panel{
			background-image:url("../rsrc/background.png");
			background-repeat:no-repeat;
			background-position:center;
		}
		#desc{
			background-color:rgba(255,255,255,0.7);
			color:black;
		}
		"""
		return(css)
		#def _define_css

