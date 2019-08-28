#!/usr/bin/env python3
import sys
from appconfig.appConfig import appConfig

#Generate desktop
config=appConfig()
level='system'
key='default'
data=sys.argv[1]
if len(sys.argv)>1:
	level=sys.argv[2]
	if len(sys.argv)>2:
		key=sys.argv[3]
	
exit(not(config.write_config(data,level,key,True)))
