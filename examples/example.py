#!/usr/bin/env python3
import sys
import os
from PySide2.QtWidgets import QApplication
from appconfig.appConfigScreen import appConfigScreen as appConfig

app=QApplication(["Config app"])
name="Parameter1"
config=appConfig("Config App",{'parameter1':name})
config.setRsrcPath("%s/rsrc"%("."))
config.setIcon('icon.png')
config.setBanner('banner.png')
config.setBackgroundImage('background.svg')
config.Show()
app.exec_()
