#!/usr/bin/env python3
import sys,os
import json
from appconfig.appConfig import appConfig

#Parms:
#1->data
#2->level
#3->key
#4->confFile

#Generate desktop
config=appConfig()
level='system'
key='default'
confFile='app.conf'
defaultDir="/usr/share/appconfig"
data=json.loads(sys.argv[1])
if len(sys.argv)>2:
	level=sys.argv[2]
	if len(sys.argv)>3:
		key=sys.argv[3]
		if len(sys.argv)>4:
			confFile=sys.argv[4]
			if os.path.isfile(confFile):
				if os.path.dirname(confFile):
					defaultDir=os.path.dirname(confFile)
					
confDir="%s/%s"%(defaultDir,confFile.split('.')[0])
config.set_baseDirs({level:confDir})
config.set_configFile(confFile)
exit(not(config.write_config(data,level,key,True)))
