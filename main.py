#!/usr/bin/python
# coding=utf-8

import os
import datetime
import time
from time import localtime, strftime

#import urllib
#import logging
#import re
#from multiprocessing import Process
#from grab.spider import Spider, Task

#do we really ned this HERE?
try: 
	from Modules.webkit2png import LockNLoad
except:
	pass

from SiteGrabs import *
from Modules.postparser import post_parser, sort_screenshots



class ObjDummy:
	pass

def runInParallel(*fns):
	proc = []
	
	for fn in fns:
		p = Process(target=fn)
		p.start()
		proc.append(p)
	
	for p in proc:
		p.join()

#determine environment we are running in
def DetEnv(fTest = True):
	curr_uname = os.uname()[1].split('.')[0]
	glb = ObjDummy()
	
	if curr_uname == 'mighty-mbp':
		glb.usrFlag = 1
		glb.envDir = '/Users/mighty_z/Documents/pyParserApt'
		glb.envOutput = '/Users/mighty_z/Documents/pyOutput/'
		if fTest :
			glb.envImgOutput = '/Users/mighty_z/Documents/pyOutput/imgs/'
		else :
			glb.envImgOutput = '/Volumes/FAT32-1TB/pyOutput/imgs/'
	elif curr_uname == 'bt':
		glb.usrFlag = -1
		glb.envDir = '/root/pyParserAptGit/'
		glb.envOutput = '/root/Desktop/pyParser/pyOutput/'
		glb.envImgOutput = '/root/Desktop/pyParser/pyOutput/imgs/'
	
	return glb

print '== pyParser::main =========='
print 'Started on'
print strftime("%Y-%m-%d %H:%M:%S", localtime())
print '----------------------------'


# initialise object for global constats and return environment data
# DetEnv(bBool); bBool: <True> to run test mode, <False> to run production 
#glb = DetEnv(False)
glb = DetEnv()

# add site parsers here
# siteName.GoGrab(glb, [iNumberOfThreads], [bDebug], [bGetNew])

#cian.GoGrab(glb, 6, True)
realty_dmir.GoGrab(glb, 6, False)
#cian.GoGrab(glb, 6, True)
#realto.GoGrab(glb, 6, True)

#post_parser(
#			glb
#			,'sSiteName'
#			,'sSiteName'
#			,...
#			)


print '----------------------------'
print 'Completed on'
print strftime("%Y-%m-%d %H:%M:%S", localtime())
print '== pyParser::main =========='

