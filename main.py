#!/usr/bin/python
# coding=utf-8


import urllib
import os
import logging
import re
import datetime
import time

from multiprocessing import Process
from grab.spider import Spider, Task

from time import localtime, strftime

from Modules.webkit2png import LockNLoad
from Modules.postparser import post_parser, sort_screenshots

from SiteGrabs import *



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
		glb.envDir = '/Users/mighty_z/Documents/pyParser/pyParser/'
		glb.envOutput = '/Users/mighty_z/Documents/pyParser/pyOutput/'
		if fTest :
			glb.envImgOutput = '/Users/mighty_z/Documents/pyParser/pyOutput/imgs/'
		else :
			glb.envImgOutput = '/Volumes/FAT32-1TB/pyOutput/imgs/'
	elif curr_uname == 'bt':
		glb.envDir = '/root/Desktop/pyParser/'
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
# siteName.GoGtab(glb, [iNumberOfThreads], [bDebug], [bGetNew])


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

