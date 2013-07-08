#!/usr/bin/python
# coding=utf-8

import urllib
import os
import logging
import re
import datetime
import random
import time

from time import localtime, strftime
from grab.spider import Spider, Task

imgDict = {}

class SitePars(Spider):
	initial_urls = ['http://realty.dmir.ru/msk/sale-tbl/prodazha-kvartir-v-moskve/?csort=best&page=1']

	def prepare(self):
		self.result_file = open(self.glb.envOutput + 'realty.dmir.txt', 'w')
		self.result_file.write('ID объекта;Тип недвижимости;Адрес;Станция метро;Этаж/Этажность;Количество комнат;Площадь общая;Площадь жилая;\
	Площадь кухни;Вид передаваемого права;Цена продажи;Дата предложения;Описание;Агентство;Телефон;Ссылка\n')

	#определяем номер последней страницы навигации. НАДО АВТОМАТИЗИРОВАТЬ
	def task_initial(self, grab, task):
		#num_of_pages = int(grab.xpath_number(u'//a[@title="Перейти на последнюю страницу"]'))
		num_of_pages = 1
		for n in range(1, num_of_pages + 1):
			yield Task('nav', url = 'http://realty.dmir.ru/msk/sale-tbl/prodazha-kvartir-v-moskve/?csort=best&page=%s' % n)

	#перебираем навигационные страницы и ищем ссылки на карточки
	def task_nav(self, grab, task):
		for elem in grab.tree.xpath('//a[@class="view-img"]/@href'):
			yield Task('dmirobject', url=grab.make_url_absolute(elem))

	def task_dmirobject(self, grab, task):
		global imgDict
		temp, temp2 = '', ''

		cleanFlag = False

		nonNum = re.compile(u'[^0-9]', re.U)
		dateYest = datetime.timedelta(days=1)

		objID = str(task.url.split('/')[4].split('-')[-1:]).replace("'", "").replace('[', '').replace(']', '')

		rType, rAddress, rMetro, rFloor, rRoomCount, rSquare, rLiveSquare, rDinnerSquare, rRights, rCost, rDate, rDescr, rAgency, rPhone, rawDescr = \
			';', ';', ';', ';', ';', ';', ';', ';', ';', ';', ';', ';', ';', ';', ''

		rType = 'Квартира;'

		#вид передаваемого права
		rRights = 'Вторичка;'

		#стоимость
		temp = grab.xpath('//span[@id="price_offer"]')
		rCost = str(re.sub(nonNum, '', temp.text_content().encode('utf-8'))) + ';'

		#количество комнат
		try:
			temp = grab.xpath('//li[@class="rooms"]')
		except IndexError:
			cleanFlag = True
		else:
			rRoomCount = temp.text_content().encode('utf-8') + ';'

		#площадь
		try:
			temp = grab.xpath('//li[@class="square"]')
		except IndexError:
			cleanFlag = True
		else:
			if len(temp.text_content().encode('utf-8').replace(' ', '').replace('\r\n', '').split('/')) > 1:
				rSquare = temp.text_content().encode('utf-8').replace(' ', '').replace('\r\n', '').split('/')[0] + ';'
				rLiveSquare = temp.text_content().encode('utf-8').replace(' ', '').replace('\r\n', '').split('/')[1] + ';'
				#rDinnerSquare = temp.text_content().encode('utf-8').replace(' ', '').replace('\r\n', '').split('/')[2] + ';'
			else:
				rSquare = temp.text_content().encode('utf-8') + ';'

		#метро
		try:
			temp = grab.xpath('//li[@class="metro"]')		
		except IndexError:
			cleanFlag = True
		else:
			rMetro = temp.text_content().encode('utf-8') + ';'
		
		#этаж
		try:
			temp = grab.xpath('//li[@class="floor"]')
		except IndexError:
			cleanFlag = True
		else:
			rFloor = temp.text_content().encode('utf-8').replace(' ', '').replace('\r\n', '').replace('этажиз', '/') + ';'

		#описание
		temp = grab.xpath('//div[@class="mb20"]')
		rDescr = temp.text_content().encode('utf-8').replace('"', '').replace('\r\n', '').replace('\t', '').replace('\n', '').replace('\r', '').replace(';', '|').strip() + ';'

		#дата размещения
		try:
			#если блок изменения цены существует
			flag = True
			temp = grab.xpath('//table[@id="history_data"]')
		except IndexError:
			flag = False
			temp = grab.xpath('//div[@id="contacts_data"]')
			
		if flag:
			rDate = ''
			for temp2 in temp.text_content().encode('utf-8').split(' ')[:3]:
				rDate += temp2 + ' '
			rDate = rDate.strip() + ';'
		else:
			rDate = temp.text_content().encode('utf-8').split('Размещено')[1][:10] + ';'

		#телефон и организация
		temp = grab.xpath('//div[@id="contacts_data"]')
		rPhone = temp.text_content().encode('utf-8').split('нашли объявление на Дмир.ру')[1][:18] + ';'
		try:
			rAgency = temp.text_content().encode('utf-8').split('Компания')[1].split('Размещено')[0] + ';'
		except IndexError:
			rAgency = temp.text_content().encode('utf-8').split('Разместил(а)')[1].split('Размещено')[0] + ';'

		#адрес
		try:
			temp = grab.xpath('//h1[@class="displayinline pr10"]')
		except IndexError:
			cleanFlag = True
		else:
			if len(temp.text_content().encode('utf-8').split(',')) > 2:
				rAddress = ''
				for temp2 in temp.text_content().encode('utf-8').split(',')[1:]:
					rAddress += temp2 + ','
				rAddress = rAddress + ';'

		#составляем строку для заливки 
		stringO = objID + ';' + rType + rAddress + rMetro + rFloor \
			+ rRoomCount + rSquare + rLiveSquare + rDinnerSquare \
			+ rRights + rCost + rDate + rDescr + rAgency + rPhone + task.url + ';'

		#пишем в файл
		if cleanFlag==False:
			stringO = stringO.strip('\r\n\t').replace('\r\n', ' ')
			self.result_file.write(stringO + "\n")

		if cleanFlag==False:
			#меняем каталог для работы с фс
			os.chdir(self.glb.envOutput)
			os.mkdir(objID)
			# save an url screenshot
			##scrFolder = self.glb.envOutput + 'screenshots/'
			
			scrFolder = self.glb.envOutput + objID

			if self.glb.usrFlag == 1:
				# write here your command! change sript_name to your
				currCmd = self.glb.envDir + 'script_name' + ' ' + task.url + ' -o ' + scrFolder + task.url.split('/')[-2] + '.png'
			elif self.glb.usrFlag == -1:
				currCmd = 'python ' + '/root/Desktop/pyParser/webkit2png' + ' ' + task.url + ' -o ' + scrFolder + '/' + objID + '.png'
				#currCmd = 'python ' + self.glb.envDir + 'Modules/webkit2png_lin.py' + ' ' + task.url + ' -o ' + scrFolder + task.url.split('=')[1] + '.png'
			
			os.system(currCmd)

			# saving all images. PLEASE, CREATE imgs folder in pyOutput 
			for nxtElem in grab.tree.xpath('//img[@alt=""]/@src'):
				if str(grab.make_url_absolute(nxtElem)).encode('utf-8').split('/')[2] == 'realty.dmir.ru':
					imgDict[grab.make_url_absolute(nxtElem)]=objID
					yield Task('imageSave', url=grab.make_url_absolute(nxtElem))

	#images saving...
	def task_imageSave(self, grab, task):
		global imgDict
		imgRes = imgDict[task.url] + '_' + str(random.randint(1,99))
		path = self.glb.envOutput + imgDict[task.url] + '/%s.jpg' % imgRes
		grab.response.save(path)

def GoGrab(glb, threads = 1, debug = False, getNew = True):
	print ''
	print 'Go grab realty.dmir.ru '
	print ' at ' + strftime("%Y-%m-%d %H:%M:%S", localtime())
	print '----------------------------'
	print '----------------------------'
	if debug:
		logging.basicConfig(level=logging.DEBUG)
	bot = SitePars(thread_number = threads)
	bot.glb = glb
	bot.run()
