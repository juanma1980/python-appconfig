#!/usr/bin/env python3
import sys
import os
from appconfig import manager

name="Parameter1"
config=manager.manager(relativepath="/tmp/configDir",name="configFile.json") # relativepath="path" use confdir in $PWD as base
oldconf=config.getConfig()
newconf=oldconf.copy()
newconf.update({"field":name})
conf=config.writeConfig(newconf)
print(conf)
