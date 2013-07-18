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

sitePath = 'mirkvartir/'

class SitePars(Spider):
	initial_urls = ['http://www.mirkvartir.ru/Москва/?onlyWithPhoto=true&p=1']

	def prepare(self):
		try:
			os.mkdir(self.glb.envOutput + sitePath)
		except OSError:
			print 'Folder ' + sitePath + ' exists. Was not created'
		self.result_file = open(self.glb.envOutput + 'mirkvartir.txt', 'w')
		self.result_file.write('ID объекта;Тип недвижимости;Адрес;Станция метро;Этаж/Этажность;Количество комнат;Площадь общая;Площадь жилая;\
	Площадь кухни;Вид передаваемого права;Цена продажи;Дата предложения;Описание;Агентство;Телефон;Ссылка\n')

	#определяем номер последней страницы навигации. НАДО АВТОМАТИЗИРОВАТЬ
	def task_initial(self, grab, task):
		num_of_pages = 1
		for n in range(1, num_of_pages + 8):
			yield Task('nav', url = 'http://www.mirkvartir.ru/Москва/?onlyWithPhoto=true&p=%s' % n)

	#перебираем навигационные страницы и ищем ссылки на карточки
	def task_nav(self, grab, task):
		for elem in grab.doc.select('//div[@class="list_item"]'):
			tmp = elem.select('.//a[@class="m cmpz-list-item"]').attr('href')
			yield Task('mirkvartir', url=grab.make_url_absolute(tmp))

	def task_mirkvartir(self, grab, task):
		
		temp, temp2 = '', ''
		listDescr = []

		cleanFlag = False

		nonNum = re.compile(u'[^0-9]', re.U)
		dateYest = datetime.timedelta(days=1)

		objID = str(task.url.split('/')[-2:-1]).replace("'", "").replace('[', '').replace(']', '')

		rType, rAddress, rMetro, rFloor, rRoomCount, rSquare, rLiveSquare, rDinnerSquare, rRights, rCost, rDate, rDescr, rAgency, rPhone, rawDescr = \
			';', ';', ';', ';', ';', ';', ';', ';', ';', ';', ';', ';', ';', ';', ''

		rType = 'Квартира;'

		#вид передаваемого права
		rRights = 'Вторичка;'

		#стоимость
		temp = grab.doc.select('//p[@class="price"]')
		rCost = str(re.sub(nonNum, '', temp.text().encode('utf-8'))) + ';'

		#адрес
		temp = grab.doc.select('//div[@class="twocolshead"]//h2[@class="s2"]')
		rAddress = str(temp.text().encode('utf-8').split('Москва')[1]) + ';'

		#телефон + имя контакта
		temp = grab.doc.select('//div[@class="name_block_rb name_block_rb-fix"]')
		rPhone = str(temp.text().encode('utf-8').split('Телефон: ')[1]) + ';'
		rAgency = str(temp.text().encode('utf-8').split('Телефон: ')[0]) + ';'

		#общее описание
		temp = grab.doc.select('//p[@class="estate-description"]')
		rDescr = temp.text().encode('utf-8').replace('"', '').replace('\r\n', '').replace('\t', '').replace('\n', '').replace('\r', '').replace(';', '|').strip() + ';'

		#метро
		temp = grab.doc.select('//dl[@class="info-item"]')
		rMetro = str(temp.text().encode('utf-8').replace('\t', '').replace('\r\n', '').split('Метро')[1].split('Ближайшее метро')[0]) + ';'

		#блок с описание (этажность, площадь, количество комнат)
		temp = grab.doc.select('//div[@class="objparams estate-info-container"]')
		listDescr = temp.text().encode('utf-8').replace('\t', '').strip().split('\r\n')
		for count in range(len(listDescr)):
			if listDescr[count].strip() == 'Этаж / этажность':
				rFloor = listDescr[count + 1].replace(' ', '') + ';'
			if listDescr[count].strip() == 'Площадь, м2':
				rSquare = listDescr[count + 1].split('/')[0].strip() + ';'
				rLiveSquare = listDescr[count + 1].split('/')[1].strip() + ';'
				rDinnerSquare = str(re.sub(noNum, '', listDescr[count + 1].split('/')[2].strip())) + ';'
			if listDescr[count].strip() == 'Кол-во комнат':
				rRoomCount = listDescr[count + 1].replace(' ', '') + ';'

		#дата обновления
		temp = grab.doc.select('//td[@class="tc-content"]')
		rDate = temp.text().encode('utf-8').strip() + ';'

		#составляем строку для заливки 
		stringO = objID + ';' + rType + rAddress + rMetro + rFloor \
			+ rRoomCount + rSquare + rLiveSquare + rDinnerSquare \
			+ rRights + rCost + rDate + rDescr + rAgency + rPhone + task.url + ';'

		#пишем в файл
		stringO = stringO.strip('\r\n\t').replace('\r\n', ' ')
		self.result_file.write(stringO + "\n")

def GoGrab(glb, threads = 1, debug = False, getNew = True):
	print ''
	print 'Go grab mirkvartir.ru '
	print ' at ' + strftime("%Y-%m-%d %H:%M:%S", localtime())
	print '----------------------------'
	print '----------------------------'
	if debug:
		logging.basicConfig(level=logging.DEBUG)
	bot = SitePars(thread_number = threads)
	bot.glb = glb
	bot.run()