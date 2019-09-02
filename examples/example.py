#!/usr/bin/env python3
import sys
import os
from PyQt5.QtWidgets import QApplication
from appconfig.appConfigScreen import appConfigScreen as appConfig

app=QApplication(["Config app"])
name="Parameter1"
config=appConfig("Config App",{'parameter1':name})
config.setRsrcPath("%s/rsrc"%("/home/lliurex/git/python3-appconfig/examples"))
config.setIcon('icon.png')
config.setBanner('banner.png')
config.setBackgroundImage('background.svg')
config.load_stacks()

app.exec_()
