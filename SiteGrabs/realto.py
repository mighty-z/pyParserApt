#!/usr/bin/python
# coding=utf-8

import urllib
import os
import shutil
import logging
import time

from grab.spider import Spider, Task
from grab import Grab
from Modules.webkit2png import LockNLoad
from time import localtime, strftime

class SitePars(Spider):
	initial_urls = [
					'http://www.rezon-realty.ru/EntityFind.aspx?SectionID=8'
					]
	#this allows to pass variables into the class
	glb = ''
	arScreenShotQueue = []
	dObjPhotoReference = {}
	
	#create output files
	def prepare(self):
		self.result_file = open(self.glb.envOutput + r'rezon_realty.txt', 'w')
		self.objCollection = open(self.glb.envOutput + r'rezon_realty.obj', 'r+')
		self.arObjCollection = self.objCollection.readlines()
    
	#get cards by brute force
	def task_initial(self, grab, task):
		if self.glb.getNew:
			for id in range(self.glb.minObjId, self.glb.maxObjId):
				url = 'http://www.rezon-realty.ru/EntityDescription.aspx?ItemID=' + str(id)
				yield Task('cards', url = url)
		else:
			for ul in self.arObjCollection: #<limit>
				url = ul.strip(' \t\n\r')
				yield Task('cards', url = url)
    
	#parse cards
	def task_cards(self, grab, task):
		tRow = [u'',u'']
		tRowInd = 0
		CardType = ''
		
		#elements of the output string
		sOfferType = sObjType = sOfferDate = \
			sRegion = sTown = sDistrict = \
			sDomain = sRange = \
			sArea = sBldType = sBldStoreys = sStorey = \
			sPrice = sPricePerSqm = \
			sFunction = \
			sLandFunction = sLandConstructions = \
			sContactNumber = sContactEmail = sContactName = \
			sImgFolder = \
				';'
		
		sAddress = sBldNumber = ''
		rawDescr = ''
		OutputLine = ''
		
		CardType = grab.xpath('//title').text_content().strip(' \t\r\n').split(' ')[0]
		arExcludeCards = [
						  u'База',
						  u'Новостройки',
						  u'Вторичное',
						  u'Коттеджи,'
						  ]
		
		#output object url to the collection
		if self.glb.getNew and CardType not in arExcludeCards:
			ul = task.url + "\n"
			if ul not in self.arObjCollection:
				self.objCollection.write(ul)
		
		#make an array from all table cells and then parse all elements
		if CardType not in arExcludeCards:
			self.arScreenShotQueue.append(task.url)
			for elem in grab.tree.xpath('//div[@id="ctl00_ContentPlaceHolder1_Div2"]//table//td'):
				if elem.text_content() <> '':
					cellContent = elem.text_content().strip(' \t\r\n')
					if cellContent <> u"Изображение объекта":
						tRow[tRowInd] = cellContent
						if tRowInd == 0:
							tRowInd = 1
						else:
							tRowInd = 0
							
							if tRow[0] == u'Тип операции':
								sOfferType = tRow[1].encode('utf-8').replace(';',',') + ';'
							#-------------------------------------------------------------
							elif tRow[0] == u'Регион':
								sRegion = tRow[1].encode('utf-8').replace(';',',') + ';'
							#-------------------------------------------------------------
							elif tRow[0] in [u'Муниципальное образование', u'Населённый пункт']:
								sTown = tRow[1].encode('utf-8').replace(';',',') + ';'
							#-------------------------------------------------------------
							elif tRow[0] == u'Район':
								sDistrict = tRow[1].encode('utf-8').replace(';',',') + ';'
							#-------------------------------------------------------------
							elif tRow[0] == u'Объект':
								sObjType = tRow[1].encode('utf-8').replace(';',',') + ';'
							#-------------------------------------------------------------
							elif tRow[0] in [u'Площадь', u'площадь']:
								sArea = tRow[1].encode('utf-8').replace(';',',') + ';'
							#-------------------------------------------------------------
							elif tRow[0] == u'Площадь участка, соток':
								sArea = tRow[1].encode('utf-8').replace(';',',') + ' сот;'
							#-------------------------------------------------------------
							elif tRow[0] == u'Цена':
								sPrice = tRow[1].encode('utf-8').replace(';',',') + ';'
							#-------------------------------------------------------------
							elif tRow[0] == u'Тип цены':
								if tRow[1][0:3] == u'тыс':
									sPrice = str(float(sPrice[0:-1]) * 1000) + ';'
								
								tmpArray = tRow[1].split('/')
								if len(tmpArray) == 2:
									sArea = sArea[0:-1] + ' ' + tmpArray[1].encode('utf-8') + ';'
									sPricePerSqm = sPrice
									sPrice = ';'
							#-------------------------------------------------------------
							elif tRow[0] == u'Контактный телефон':
								sContactNumber = tRow[1].encode('utf-8').replace(';',',') + ';'
							#-------------------------------------------------------------
							elif tRow[0] == u'Контактное лицо':
								sContactName = tRow[1].encode('utf-8').replace(';',',') + ';'
							#-------------------------------------------------------------
							elif tRow[0] == u'Контактный E-Mail':
								sContactEmail = tRow[1].encode('utf-8').replace(';',',') + ';'
							#-------------------------------------------------------------
							elif tRow[0] == u'Дата продления (создания)':
								sOfferDate = tRow[1].encode('utf-8').replace(';',',') + ';'
							#-------------------------------------------------------------
							elif tRow[0] in (u'Улица н.п.', u'Улица'):
								sAddress = tRow[1].encode('utf-8').replace(';',',')
							#-------------------------------------------------------------
							elif tRow[0] == u'Номер дома':
								sBldNumber = 'д.' + tRow[1].encode('utf-8').replace(';',',')
							#-------------------------------------------------------------
							elif tRow[0] == u'Размещение':
								sBldType = tRow[1].encode('utf-8').replace(';',',') + ';'
							#-------------------------------------------------------------
							elif tRow[0] == u'Этажность':
								sBldStoreys = tRow[1].encode('utf-8').replace(';',',') + ';'
							#-------------------------------------------------------------
							elif tRow[0] == u'Этаж':
								sStorey = tRow[1].encode('utf-8').replace(';',',') + ';'
							#-------------------------------------------------------------
							elif tRow[0] == u'Примерное назначение объекта':
								sFunction = tRow[1].encode('utf-8').replace(';',',') + ';'
							#-------------------------------------------------------------
							elif tRow[0] == u'Удаленность от г. Перми':
								sRange = tRow[1].encode('utf-8').replace(';',',') + ';'
							#-------------------------------------------------------------
							elif tRow[0] == u'Категория земель':
								sLandFunction = tRow[1].encode('utf-8').replace(';',',') + ';'
							#-------------------------------------------------------------
							elif tRow[0] == u'Постройки на участке':
								sLandConstructions = tRow[1].encode('utf-8').replace(';',',') + ';'
							#-------------------------------------------------------------
							#							elif tRow[0] == u'':
							#								tmp = tRow[1].encode('utf-8').replace(';',',') + ';'
							#							#-------------------------------------------------------------
							#							elif tRow[0] == u'':
							#								tmp = tRow[1].encode('utf-8').replace(';',',') + ';'
							#							#-------------------------------------------------------------
							#							elif tRow[0] == u'':
							#								tmp = tRow[1].encode('utf-8').replace(';',',') + ';'
							#							#-------------------------------------------------------------
							#							elif tRow[0] == u'':
							#								tmp = tRow[1].encode('utf-8').replace(';',',') + ';'
							#							#-------------------------------------------------------------
							else:
								#all other values are appended to the separate string
								rawDescr += tRow[0].encode('utf-8').replace(',','|').replace(';','|') \
									+ ': ' \
									+ tRow[1].encode('utf-8').replace(',','.').replace(';','.').replace(':','') \
									+ ', '
			
			
			if CardType == u'Земельные':
				sObjType = 'Земля;'
			
			sObjId = task.url.split('=')[-1].strip(' ')
			sImgFolder = '/imgs/rezon_realty/' + sObjId + '/;'
			
			OutputLine = task.url + ';' \
				+ sOfferType + sOfferDate \
				+ sObjType + sBldType \
				+ sRegion + sTown + sDistrict \
				+ sAddress + ' ' + sBldNumber + ';' \
				+ sDomain + sRange \
				+ sArea + sBldStoreys + sStorey \
				+ sPrice + sPricePerSqm \
				+ sFunction \
				+ sLandFunction + sLandConstructions \
				+ sContactNumber + sContactEmail + sContactName \
				+ sImgFolder + rawDescr
			
			OutputLine.replace('\n','') \
				.replace('\r','') \
				.replace('\t','') \
				.replace('\r\n','')
			
			OutputLine += '\n'
			self.result_file.write(OutputLine)
		
		
		#create task for saving images
		for urlPhoto in grab.tree.xpath('//div[@id="ctl00_ContentPlaceHolder1_Div2"]//table//td/img/@src'):
			urlPhoto = grab.make_url_absolute(urlPhoto)
			yield Task('SavePhoto', url = urlPhoto)
			refPhoto = urlPhoto.replace('/','_')
			self.dObjPhotoReference[refPhoto] = sObjId
	
	#save all photos of the object
	def task_SavePhoto(self,grab,task):
		
		refPhoto = task.url.replace('/','_')
		filename = '/' + task.url.split('/')[-1]
		sObjId = self.dObjPhotoReference[refPhoto]
		path = self.glb.envImgOutput + 'rezon_realty/' + sObjId + filename
		grab.response.save(path)
	
	
	def shutdown(self):
		self.objCollection.close()
		
		#make screenshoots
		print '----------------------------'
		print 'Start making screanshoots '
		print ' at ' + strftime("%Y-%m-%d %H:%M:%S", localtime())
		print '----------------------------'
		
		dir = 'rezon_realty/'
		
		ssBlock = []
		
		for url in self.arScreenShotQueue:
			ssBlock.append(url)
			if len(ssBlock) == 50:
				LockNLoad(ssBlock, self.glb.envDir, self.glb.envImgOutput + dir)
				ssBlock = []
		
		if len(ssBlock) <> 0:
			LockNLoad(ssBlock, self.glb.envDir, self.glb.envImgOutput + dir)
		
		
		
		print '----------------------------'
		print ' ... and now moving to object photo folders '
		print '----------------------------'
		
		files = os.listdir(self.glb.envImgOutput + dir)
		for file in files:
			if file.split('.')[-1] in ['png', 'jpg', 'jpeg', 'gif']:
				idObj = file.split('ItemID')[-1]
				idObj = idObj.split('-full')[0]
				source = self.glb.envImgOutput + dir + file
				destanation = self.glb.envImgOutput + dir + idObj + '/'
				
				if not os.path.isdir(destanation):
					os.mkdir(destanation)
				
				destanation += file
				shutil.move(source, destanation)
		
		print '----------------------------'
		print 'Finished with rezon-realty.ru '
		print ' at ' + strftime("%Y-%m-%d %H:%M:%S", localtime())
		print '----------------------------'
		print '----------------------------'

#=============================================
def GoGrab(glb, threads = 1, debug = False, getNew = True, minObjId = 20000, maxObjId = 300000):
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
	bot.glb.minObjId = minObjId
	bot.glb.maxObjId = maxObjId
	bot.run()

