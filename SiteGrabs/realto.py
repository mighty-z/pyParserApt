#!/usr/bin/python
# coding=utf-8

import urllib
import os
import shutil
import logging
import time

from time import localtime, strftime

from grab import Grab
from grab.spider import Spider, Task
#from grab.selector import Selector

#from Modules.webkit2png import LockNLoad

class SitePars(Spider):
	initial_urls = [
					'http://www.realto.ru/base/flat_sale/'
					,'http://www.realto.ru/base/new_build/'
					]
	#this allows to pass variables into the class
	glb = ''
#	arScreenShotQueue = []
#	dObjPhotoReference = {}
	
	#create output files
	def prepare(self):
		self.result_file = open(self.glb.envOutput + 'realto.txt', 'w')
		self.result_file.write('ID объекта;' + \
							   'Тип недвижимости;Адрес;Станция метро;' + \
							   'Этаж/Этажность;Количество комнат;Площадь общая;Площадь жилая;Площадь кухни;' + \
							   'Вид передаваемого права;' + \
							   'Цена продажи;Дата предложения;' + \
							   'Описание;Агентство;Телефон;Ссылка\n' \
							   )

	#get navigation pages
	def task_initial(self, grab, task):
		if task.url.split('/')[4] == 'flat_sale':
			iNavPagesCount = grab.doc.select('//a[@class="pages"]')[-2].number()
			#print iNavPagesCount
			for n in range(1, iNavPagesCount)[0:1]:############################################################################
				yield Task('NavPages', url = 'http://www.realto.ru/base/flat_sale/?SecLodg_step=%s' % n)
		
		if task.url.split('/')[4] == 'new_build':
			urlLastNavPage = grab.doc.select('//div[@class="page_bar"]').select('.//a')[-1].attr('href')
			iNavPagesCount = int(urlLastNavPage.split('=')[-1])
			#print iNavPagesCount
			for n in range(1, iNavPagesCount)[0:1]:############################################################################
				yield Task('NavPages', url = 'http://www.realto.ru/base/new_build/?page=%s' % n)

	#get card pages // table view
	def task_NavPages(self, grab, task):
		for r in grab.doc.select('//tr[@class="row_base"]'):
			td = r.select('.//td[@class="base_td"]')[7]
			url =  td.select('.//a')[0].attr('href')
			yield Task('CardPages', url = grab.make_url_absolute(url))

	#parse cards
	def task_CardPages(self, grab, task):
		#define elements of output string
		sOutType = sOutRights = \
			sOutAddress = sOutMetro = \
			sOutFloor = sOutRoomCount = sOutFloorSpace = sOutLivingSpace = sOutKitchenSpace = \
			sOutPrice = \
			sOutDate = sOutDescription = sOutAgency = sOutPhone = \
				';'
		
		#dictionary for tmp information cells
		dCells = {}
					
		sOutType = u'Квартира;'
		if task.url.split('/')[4] == 'flat_sale':
			sOutRights = u'Вторичка;'
			sObjId = 'flat_sale/id'
		else:
			sOutRights = u'Новостройка;'
			sObjId = 'new_build/id'
		

		
		#print task.url
		listCellTitles = grab.doc.select('//td[@class="base_one_title"]')
		listCellContent = grab.doc.select('//td[@class="base_one_text"]')
		for i in range(0, len(listCellTitles)):
			#print listCellTitles[i].text().encode('utf-8'), '|', listCellContent[i].text().encode('utf-8')
			dCells[listCellTitles[i].text()] = listCellContent[i].text()

		if u'Адрес:' in dCells:
			sOutAddress = dCells[u'Адрес:'] + ';'
			try:
				sOutMetro = dCells[u'Адрес:'].split(u'ближайшая станция метро ')[1].split(', ')[0] + ';'
			except:
				pass
		#print sOutAddress.encode('utf-8')
		#print sOutMetro.encode('utf-8')

		if u'Этаж / этажность' in dCells:
			sOutFloor = dCells[u'Этаж / этажность'] + ';'
		#print sOutFloor.encode('utf-8')

		if u'Продается' in dCells:
			sOutRoomCount = dCells[u'Продается'].split(' ')[0] + ';'
		#print sOutRoomCount.encode('utf-8')

		if u'Площади(общая/жилая/кухня)' in dCells:
			listSpace = dCells[u'Площади(общая/жилая/кухня)'].split(' / ')
			sOutFloorSpace = listSpace[0] + ';'
			sOutLivingSpace = listSpace[1] + ';'
			sOutKitchenSpace = listSpace[2] + ';'
		#print sOutFloorSpace.encode('utf-8')
		#print sOutLivingSpace.encode('utf-8')
		#print sOutKitchenSpace.encode('utf-8')

		if u'Стоимость' in dCells:
			sOutPrice = dCells[u'Стоимость'].split(u' руб.')[0] + ';'
		#print sOutPrice.encode('utf-8')

		if u'Дата обновления' in dCells:
			sOutDate = dCells[u'Дата обновления'] + ';'
		#print sOutDate.encode('utf-8')

		if u'Комментарии' in dCells:
			sOutDescription = dCells[u'Комментарии'] + ';'
		#print sOutDescription.encode('utf-8')

		if u'Об объекте' in dCells:
			sOutDescription = dCells[u'Об объекте'] + ' // ' + sOutDescription
		#print sOutDescription.encode('utf-8')

		if u'О рекламодателе' in dCells:
			sOutAgency = dCells[u'О рекламодателе'] + ';'
		#print sOutAgency.encode('utf-8')

		if u'Телефоны' in dCells:
			sOutPhone = dCells[u'Телефоны'] + ';'
		#print sOutPhone.encode('utf-8')

		sObjId += task.url.split('id=')[-1]

		sOutputLine = sObjId + ';' + sOutType + \
			sOutAddress + sOutMetro + \
			sOutFloor + sOutRoomCount + sOutFloorSpace + sOutLivingSpace + sOutKitchenSpace + \
			sOutRights + sOutPrice + \
			sOutDate + sOutDescription + sOutAgency + sOutPhone + \
			task.url + '\n'
		
		#print sOutputLine.encode('utf-8')
		sOutputLine = sOutputLine.replace('&quot;','')
		self.result_file.write(sOutputLine.encode('utf-8'))

#			sObjId = task.url.split('=')[-1].strip(' ')
#			sImgFolder = '/imgs/rezon_realty/' + sObjId + '/;'
#			
#			OutputLine = task.url + ';' \
#				+ sOfferType + sOfferDate \
#				+ sObjType + sBldType \
#				+ sRegion + sTown + sDistrict \
#				+ sAddress + ' ' + sBldNumber + ';' \
#				+ sDomain + sRange \
#				+ sArea + sBldStoreys + sStorey \
#				+ sPrice + sPricePerSqm \
#				+ sFunction \
#				+ sLandFunction + sLandConstructions \
#				+ sContactNumber + sContactEmail + sContactName \
#				+ sImgFolder + rawDescr
#			
#			OutputLine.replace('\n','') \
#				.replace('\r','') \
#				.replace('\t','') \
#				.replace('\r\n','')
#			
#			OutputLine += '\n'
#			self.result_file.write(OutputLine)
#		
#		
#		#create task for saving images
#		for urlPhoto in grab.tree.xpath('//div[@id="ctl00_ContentPlaceHolder1_Div2"]//table//td/img/@src'):
#			urlPhoto = grab.make_url_absolute(urlPhoto)
#			yield Task('SavePhoto', url = urlPhoto)
#			refPhoto = urlPhoto.replace('/','_')
#			self.dObjPhotoReference[refPhoto] = sObjId
#	
#	#save all photos of the object
#	def task_SavePhoto(self,grab,task):
#		
#		refPhoto = task.url.replace('/','_')
#		filename = '/' + task.url.split('/')[-1]
#		sObjId = self.dObjPhotoReference[refPhoto]
#		path = self.glb.envImgOutput + 'rezon_realty/' + sObjId + filename
#		grab.response.save(path)

	
	def shutdown(self):
#		self.objCollection.close()
#		
#		#make screenshoots
#		print '----------------------------'
#		print 'Start making screanshoots '
#		print ' at ' + strftime("%Y-%m-%d %H:%M:%S", localtime())
#		print '----------------------------'
#		
#		dir = 'rezon_realty/'
#		
#		ssBlock = []
#		
#		for url in self.arScreenShotQueue:
#			ssBlock.append(url)
#			if len(ssBlock) == 50:
#				LockNLoad(ssBlock, self.glb.envDir, self.glb.envImgOutput + dir)
#				ssBlock = []
#		
#		if len(ssBlock) <> 0:
#			LockNLoad(ssBlock, self.glb.envDir, self.glb.envImgOutput + dir)
#		
#		
#		
#		print '----------------------------'
#		print ' ... and now moving to object photo folders '
#		print '----------------------------'
#		
#		files = os.listdir(self.glb.envImgOutput + dir)
#		for file in files:
#			if file.split('.')[-1] in ['png', 'jpg', 'jpeg', 'gif']:
#				idObj = file.split('ItemID')[-1]
#				idObj = idObj.split('-full')[0]
#				source = self.glb.envImgOutput + dir + file
#				destanation = self.glb.envImgOutput + dir + idObj + '/'
#				
#				if not os.path.isdir(destanation):
#					os.mkdir(destanation)
#				
#				destanation += file
#				shutil.move(source, destanation)
		
		print '----------------------------'
		print 'Finished with realto.ru '
		print ' at ' + strftime("%Y-%m-%d %H:%M:%S", localtime())
		print '----------------------------'
		print '----------------------------'

#=============================================
def GoGrab(glb, threads = 1, debug = False, getNew = True):
	print ''
	print 'Go grab realto.ru '
	print ' at ' + strftime("%Y-%m-%d %H:%M:%S", localtime())
	print '----------------------------'
	print '----------------------------'
	if debug:
		logging.basicConfig(level=logging.DEBUG)
	bot = SitePars(thread_number = threads)
	bot.glb = glb
	bot.run()

