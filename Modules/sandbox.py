#!/usr/bin/python
# coding=utf-8

import urllib
import os
import shutil
import logging
import time
import re

from grab.spider import Spider, Task
from grab import Grab
from Modules.webkit2png import LockNLoad
from time import localtime, strftime

class SitePars(Spider):
	initial_urls = [
					'http://www.rezon-realty.ru/EntityFind.aspx?SectionID=7'
					]
	#this allows to pass variables into the class
	glb = ''
	
	#create output files
	def prepare(self):
		self.result_file = open(self.glb.envOutput + r'rezon_realty.txt', 'w')
#		self.objCollection = open(self.glb.envOutput + r'rezon_realty.obj', 'r+')
    
	#parse all navigation pages
	def task_initial(self, grab, task):
#		grab.choose_form(id = "aspnetForm")
#		grab.submit(submit_name = "ctl00$ContentPlaceHolder1$bAllViews")
		grab.submit(make_request = False)
		yield Task('cards', grab = grab)
	
	#		for elem in grab.tree.xpath('//div[@id="ctl00_ContentPlaceHolder2_pCompare"]//table//td'):
	#			print elem
	#			yield Task('navigation_pages', url=grab.make_url_absolute(elem))
    
	#get all links to cards from search page
	#	def task_navigation_pages(self,grab,task):
	#
	#		for elem in grab.tree.xpath('//td[@class="title"]/a'):
	#			url = grab.make_url_absolute(elem.get("href"))
	#			yield Task('cards', url = url)
    
	#parse cards
	def task_cards(self, grab, task):
		print 'card', task.url
	
	
	def shutdown(self):
#		self.objCollection.close()
		
		#make screenshoots
		print '----------------------------'
		print 'Start making screanshoots '
		print ' at ' + strftime("%Y-%m-%d %H:%M:%S", localtime())
		print '----------------------------'
		
		#		dir = 'rezon_realty/'
		#
		#		global dCl
		#		ik = 0
		#		urlIkArray = []
		#
		#		for id in dCl.iterkeys():
		#			url = dCl[id][1]
		#			urlIkArray.append(url)
		#			ik += 1
		#			if ik == 50:
		#				LockNLoad(urlIkArray, self.glb.envDir, self.glb.envImgOutput + dir)
		#				urlIkArray = []
		#				ik = 0
		#
		#		if len(urlIkArray) <> 0:
		#			LockNLoad(urlIkArray, self.glb.envDir, self.glb.envImgOutput)
		
		print '----------------------------'
		print ' ... and now moving to object photo folders '
		print '----------------------------'
		
		#		files = os.listdir(self.glb.envImgOutput + dir)
		#		for file in files:
		#			if file.split('.')[-1] in ['png', 'jpg', 'jpeg', 'gif']:
		#				idObj = file.split('id')[-1]
		#				idObj = idObj.split('html')[0]
		#				#print idObj
		#				source = self.glb.envImgOutput + dir + file
		#				destanation = self.glb.envImgOutput + dir + idObj + '/'
		#				#print source + ' >> ' + destanation
		#
		#				if not os.path.isdir(destanation):
		#					os.mkdir(destanation)
		#
		#				destanation += file
		#				shutil.move(source, destanation)
		
		print '----------------------------'
		print 'Finished with rezon-realty.ru '
		print ' at ' + strftime("%Y-%m-%d %H:%M:%S", localtime())
		print '----------------------------'
		print '----------------------------'

#=============================================
def GoGrab(glb, threads = 1, debug = False, getNew = True):
	print ''
	print 'Go grab rezon-realty.ru '
	print ' at ' + strftime("%Y-%m-%d %H:%M:%S", localtime())
	print '----------------------------'
	print '----------------------------'
	if debug:
		logging.basicConfig(level=logging.DEBUG)
	bot = SitePars(thread_number = threads)
	bot.glb = glb
	bot.glb.getNew = getNew
	bot.run()


def read_rezon_obj(glb, filename = r'rezon_realty.obj'):
	file = open(glb.envOutput + filename, 'r')
	counter = 0
	summarizer = 0.0
	arObjId = []
	for line in file.readlines():
		counter += 1
		lineLen = len(line)
		summarizer += lineLen
		avrLen = summarizer / counter
		lenInd = abs(1.0 - (lineLen / avrLen))
		if lenInd > 0.10:
			print counter, round(lenInd,2), line
		
		sObjId = line.split('\n')[0].split('=')[-1]
		if sObjId != '':
			arObjId.append(int(sObjId))
	
	print '-----------'
	print 'min id:', min(arObjId)
	print 'max id:', max(arObjId)
	file.close()


def make_shots_from_file(glb, filename, dir):
	file = open(glb.envOutput + filename, 'r')
	dir += '/'
	
	ssBlock = []
	
	for line in file.readlines():
		url = line.split('\n')[0]
		ssBlock.append(url)
		if len(ssBlock) == 50:
			LockNLoad(ssBlock, glb.envDir, glb.envImgOutput + dir)
			ssBlock = []
	
	if len(ssBlock) <> 0:
		LockNLoad(ssBlock, glb.envDir, glb.envImgOutput + dir)
	
	print '//////////////////////////////'
	print 'sorting by dirs'
	
	#ToDo: makes split parametres variable
	files = os.listdir(glb.envImgOutput + dir)
	for file in files:
		if file.split('.')[-1] in ['png', 'jpg', 'jpeg', 'gif']:
			idObj = file.split('ItemID')[-1]
			idObj = idObj.split('-full')[0]
			source = glb.envImgOutput + dir + file
			destanation = glb.envImgOutput + dir + idObj + '/'
			
			if not os.path.isdir(destanation):
				os.mkdir(destanation)
			
			destanation += file
			shutil.move(source, destanation)

def broken_line_fix(glb, filename):
	inFile = open(glb.envOutput + filename, 'r')
	outFile = open(glb.envOutput + 'fixed_' + filename, 'w')
	for line in inFile.readlines():
		if line[0:5] == 'http:':
			outFile.write(line)
	inFile.close()
	outFile.close()

def tmp():
	print len(['ok','ok'])
	print ' con;'[0:-1]




def folder_sorter(dir):
	tmpSubDirs = os.listdir(dir)
	pattern1 = '[0-9a-z]'
	dIdentified = {}
	
	
	for d in tmpSubDirs:
		if os.path.isdir(dir + d):
			id = ''
			tmpStr = d.replace('-',' ').replace('_',' ').replace('VIP','').split(' ')
			for w in tmpStr[0:2]:
				if len(re.sub(pattern1, '', w)) != 0:
					if len(id) != 0:
						id += ' '
					id += w
			id.lstrip(' ')
			dIdentified[dir + d] = dir + id + '/' + d 

	for k, v in dIdentified.iteritems():
		print 'moving', k, 'to', v
		shutil.move(
					k,
					v
					)








