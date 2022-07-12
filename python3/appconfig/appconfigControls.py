import os
from PySide2.QtWidgets import QWidget, QPushButton,QScrollArea,QVBoxLayout,QLabel,QHBoxLayout,QDialog,QScroller,QScrollerProperties,QTableWidget,QLineEdit,QListWidget,QHeaderView,QAbstractItemView
from PySide2 import QtGui
from PySide2.QtCore import Qt,Signal,QEvent,QThread,QSize
import gettext
import requests
_ = gettext.gettext

i18n={
	"PRESSKEY":_("Press keys")
}

class QSearchBox(QWidget):
	clicked=Signal()
	editingFinished=Signal()
	returnPressed=Signal()
	textChanged=Signal()
	def __init__(self,parent=None):
		QWidget.__init__(self, parent)
		lay=QHBoxLayout()
		self.setStyleSheet('QPushButton{margin-left:1px;} QLineEdit{margin-right:0px;}')
		lay.setContentsMargins(0, 0, 0, 0)
		lay.setSpacing(0)
		self.txtSearch=QLineEdit()
		self.txtSearch.editingFinished.connect(self._emitEdit)
		self.txtSearch.returnPressed.connect(self._emitReturn)
		self.txtSearch.textChanged.connect(self._emitChange)
		lay.addWidget(self.txtSearch)
		self.btnSearch=QPushButton()
		icn=QtGui.QIcon.fromTheme("search")
		self.btnSearch.clicked.connect(self._emitClick)
		self.btnSearch.setIcon(icn)
		lay.addWidget(self.btnSearch)
		self.setLayout(lay)
	#def __init__

	def _emitClick(self):
		self.clicked.emit()
	#def _emitClick

	def _emitEdit(self):
		self.editingFinished.emit()
	#def _emitEdit

	def _emitReturn(self):
		self.returnPressed.emit()
	#def _emitEdit

	def _emitChange(self):
		self.textChanged.emit()
	#def _emitEdit

	def text(self):
		return(self.txtSearch.text())
	#def text

	def setText(self,text):
		self.txtSearch.setText(text)
	#def setText
#class QSearchBox

class QTableTouchWidget(QTableWidget):
	def __init__(self,parent=None):
		QTableWidget.__init__(self, parent)
		self.scroller=QScroller()
		self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
		self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
#		sp=self.scroller.scrollerProperties()
#		sp.setScrollMetric(QScrollerProperties.DragVelocitySmoothingFactor,0.6)
#		sp.setScrollMetric(QScrollerProperties.MinimumVelocity,0.0)
#		sp.setScrollMetric(QScrollerProperties.MaximumVelocity,0.5)
#		sp.setScrollMetric(QScrollerProperties.AcceleratingFlickMaximumTime,0.4)
#		sp.setScrollMetric(QScrollerProperties.AcceleratingFlickSpeedupFactor,1.2)
#		sp.setScrollMetric(QScrollerProperties.SnapPositionRatio,0.2)
#		sp.setScrollMetric(QScrollerProperties.MaximumClickThroughVelocity,0)
#		sp.setScrollMetric(QScrollerProperties.DragStartDistance,0.001)
#		sp.setScrollMetric(QScrollerProperties.MousePressEventDelay,0.5)
		self.scroller.grabGesture(self,self.scroller.LeftMouseButtonGesture)
	#def __init__
#class QTableTouchWidget

class loadScreenShot(QThread):
	imageLoaded=Signal("PyObject")
	def __init__(self,*args):
		super().__init__()
		self.img=args[0]
	#def __init__

	def run(self,*args):
		img=None
		pxm=None
		try:
			img=requests.get(self.img)
		except:
			icn=QtGui.QIcon.fromTheme("image-x-generic")
			pxm=icn.pixmap(512,512)
		if img:
			pxm=QtGui.QPixmap()
			pxm.loadFromData(img.content)
		self.imageLoaded.emit(pxm)
		return True
	#def run

class QHotkeyButton(QPushButton):
	keybind_signal=Signal("PyObject")
	hotkeyAssigned=Signal("PyObject")
	def __init__(self,text="",parent=None):
		QPushButton.__init__(self, parent)
		self.installEventFilter(self)
		self.keymap={}
		for key,value in vars(Qt).items():
			if isinstance(value, Qt.Key):
				self.keymap[value]=key.partition('_')[2]
		self.modmap={
					Qt.ControlModifier: self.keymap[Qt.Key_Control],
					Qt.AltModifier: self.keymap[Qt.Key_Alt],
					Qt.ShiftModifier: self.keymap[Qt.Key_Shift],
					Qt.MetaModifier: self.keymap[Qt.Key_Meta],
					Qt.GroupSwitchModifier: self.keymap[Qt.Key_AltGr],
					Qt.KeypadModifier: self.keymap[Qt.Key_NumLock]
					}
		self.processed=False
		self.setText(text)
		self.originalText=text
	#def __init__

	def setIconSize(self,*args):
		pass
	#def setIconSize(self,*args):

	def mousePressEvent(self, ev):
		self.originalText=self.text()
		self.setText(i18n.get("PRESSKEY"))
		self.processed=False
		self._grab_alt_keys()
	#def mousePressEvent

	def eventFilter(self,source,event):
		sw_mod=False
		keypressed=[]
		if (event.type()==QEvent.KeyPress):
			for modifier,text in self.modmap.items():
				if event.modifiers() & modifier:
					sw_mod=True
					keypressed.append(text)
			key=self.keymap.get(event.key(),event.text())
			if key not in keypressed:
				if sw_mod==True:
					sw_mod=False
				keypressed.append(key)
			if sw_mod==False:
				self.keybind_signal.emit("+".join(keypressed))
		if (event.type()==QEvent.KeyRelease):
			self.releaseKeyboard()
			if self.processed==False:
				action=self.getSettingForHotkey()
				retVal={"hotkey":self.text(),"action":action}
				self.hotkeyAssigned.emit(retVal)
			self.processed=True

		return False
	#def eventFilter

	def _grab_alt_keys(self,*args):
		self.keybind_signal.connect(self._set_config_key)
		self.grabKeyboard()
	#def _grab_alt_keys

	def _set_config_key(self,keypress):
		keypress=keypress.replace("Control","Ctrl")
		self.setText(keypress)
	#def _set_config_key

	def getSettingForHotkey(self):
		hotkey=self.text()
		kfile="kglobalshortcutsrc"
		action=""
		sourceFolder=os.path.join(os.environ.get('HOME',"/usr/share/acccessibility"),".config")
		kPath=os.path.join(sourceFolder,kfile)
		with open(kPath,"r") as f:
			lines=f.readlines()
		for line in lines:
			if len(line.split(","))>2:
				if hotkey.lower()==line.split(",")[-2].lower():
					action=line.split(",")[-1]
					break
				elif line.startswith("_launch"):
					if hotkey.lower()==line.replace("_launch=","").split(",")[0].lower():
						action=line.split(",")[-1]
						break
		return(action.replace("\n",""))
	#def getSettingForHotkey

	def revertHotkey(self):
		self.setText(self.originalText)
	#def revertHotkey
#class QHotkeyButton

class QScrollLabel(QScrollArea):
	def __init__(self,text="",parent=None):
		QScrollArea.__init__(self, parent)
		self.setWidgetResizable(True)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		content = QWidget(self)
		self.setWidget(content)
		lay = QVBoxLayout(content)
		self.label = QLabel(content)
		self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
		self.label.setWordWrap(True)
		lay.addWidget(self.label)
		self.label.setText(text)
		self.label.adjustSize()
		self.setFixedWidth(self.label.sizeHint().width())
		self.setFixedHeight(self.label.sizeHint().height()/2)
	#def __init__

	def setText(self,text):
		self.label.setText(text)
		self.setFixedWidth(self.label.sizeHint().width())
		self.setFixedHeight(self.label.sizeHint().height())
		self.label.adjustSize()
	#def setText

	def setWordWrap(self,boolWrap):
		self.label.setWordWrap(boolWrap)
	#def setWordWrap

	def adjustWidth(self,width):
		if self.width()<width-50:
			self.setFixedWidth(width-50)
	#def adjustWidth

	def adjustHeight(self,height):
		if self.height()<height-50:
			self.setFixedHeight(height-50)
	#def adjustHeight
#class QScrollLabel

class QScreenShotContainer(QWidget):
	def __init__(self,parent=None):
		QWidget.__init__(self, parent)
		self.widget=QWidget()
		self.lay=QHBoxLayout()
		self.outLay=QHBoxLayout()
		self.scroll=QScrollArea()
		self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.scroll.setWidgetResizable(True)
		self.scroll.setWidget(self.widget)
		self.outLay.addWidget(self.scroll)
		self.setLayout(self.outLay)
		self.widget.setLayout(self.lay)
		self.th=[]
		self.btnImg={}
	#def __init__

	def eventFilter(self,source,qevent):
		if isinstance(qevent,QEvent):
			if qevent.type()==QEvent.Type.MouseButtonPress:
				self.carrousel(source)
		return(False)
	#def eventFilter

	def carrousel(self,btn=""):
		dlg=QDialog()	
		dlg.setModal(True)
		dlg.setFixedSize(680,540)
		#widget=QWidget()
		widget=QTableTouchWidget()
		widget.setRowCount(1)
		widget.setShowGrid(True)
		widget.verticalHeader().hide()
		widget.horizontalHeader().hide()
		widget.setRowCount(1)
		mainLay=QHBoxLayout()
		selectedImg=""
		arrayImg=[]
		for btnImg,img in self.btnImg.items():
			lbl=QLabel()
			lbl.setPixmap(img.scaled(640,480))
			if btnImg==btn:	
				selectedImg=lbl
			else:
				arrayImg.append(lbl)
		if selectedImg:
			#lay.addWidget(selectedImg)
			widget.setColumnCount(widget.columnCount()+1)
			widget.setCellWidget(0,widget.columnCount()-1,selectedImg)
			widget.horizontalHeader().setSectionResizeMode(widget.columnCount()-1,QHeaderView.ResizeToContents)

		for lbl in arrayImg:
			widget.setColumnCount(widget.columnCount()+1)
			#lay.addWidget(lbl)
			widget.setCellWidget(0,widget.columnCount()-1,lbl)
			widget.horizontalHeader().setSectionResizeMode(widget.columnCount()-1,QHeaderView.ResizeToContents)
		widget.verticalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
		mainLay.addWidget(widget)
		dlg.setLayout(mainLay)
		dlg.exec()
	#def carrousel
	
	def addImage(self,img):
		scr=loadScreenShot(img)
		self.th.append(scr)
		scr.imageLoaded.connect(self.load)
		scr.start()
	#def addImage

	def load(self,*args):
		img=args[0]
		btnImg=QPushButton()
		self.lay.addWidget(btnImg)
		self.btnImg[btnImg]=img
		icn=QtGui.QIcon(img)
		btnImg.setIcon(icn)
		btnImg.setIconSize(QSize(128,128))
		self.scroll.setFixedHeight(btnImg.sizeHint().height()+32)
		btnImg.installEventFilter(self)
		btnImg.show()
	#def load

	def clear(self):
		for i in reversed(range(self.lay.count())): 
			self.lay.itemAt(i).widget().setParent(None)
		self.btnImg={}
	#def clear
#class QScreenShotContainer
