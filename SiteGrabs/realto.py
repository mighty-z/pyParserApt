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

from Modules.webkit2png import ShootOne

class SitePars(Spider):
	initial_urls = [
					'http://www.realto.ru/base/flat_sale/'
					,'http://www.realto.ru/base/new_build/'
					]
	
	#this allows to pass variables into the class
	glb = ''
	
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
			for n in range(1, iNavPagesCount):
				yield Task('NavPages', url = 'http://www.realto.ru/base/flat_sale/?SecLodg_step=%s' % n)
		
		if task.url.split('/')[4] == 'new_build':
			urlLastNavPage = grab.doc.select('//div[@class="page_bar"]').select('.//a')[-1].attr('href')
			iNavPagesCount = int(urlLastNavPage.split('=')[-1])
			#print iNavPagesCount
			for n in range(1, iNavPagesCount):
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

		sObjId += task.url.split('id=')[-1].split('&SecLodg')[0]

		sOutputLine = sObjId + ';' + sOutType + \
			sOutAddress + sOutMetro + \
			sOutFloor + sOutRoomCount + sOutFloorSpace + sOutLivingSpace + sOutKitchenSpace + \
			sOutRights + sOutPrice + \
			sOutDate + sOutDescription + sOutAgency + sOutPhone + \
			task.url + '\n'
		
		#print sOutputLine.encode('utf-8')
		sOutputLine = sOutputLine.replace('&quot;','')
		self.result_file.write(sOutputLine.encode('utf-8'))

		sImgFolder = self.glb.envImgOutput + '/realto/' + sObjId + '/'

		#saving images
		for urlPhoto in grab.doc.select('//td[@class="base_one_text"]//img'):
			urlPhoto = grab.make_url_absolute(urlPhoto.attr('src'))
			g = Grab()
			g.go(urlPhoto)
			g.response.save(sImgFolder + 'phone.gif')

		if self.glb.usrFlag == 1:
			ShootOne(task.url, self.glb.envDir, sImgFolder, 'screenshot')
		elif self.glb.usrFlag == -1:
			currCmd = 'python ' + '/root/Desktop/pyParser/webkit2png' + ' ' + task.url + ' -o ' + sImgFolder + 'screenshot' + '.png'
				

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
	
	print '----------------------------'
	print 'Finished with realto.ru '
	print ' at ' + strftime("%Y-%m-%d %H:%M:%S", localtime())
	print '----------------------------'
	print '----------------------------'

