#!/usr/bin/python
# coding=utf-8

import os
import shutil
import logging
import datetime
import re
from time import localtime, strftime
from Modules.webkit2png import LockNLoad


# ToDo: handle broken lines
# ToDo: fix encoding in output file

def post_parser (glb, *arSiteName):
	#regex patterns
	nonUtf = re.compile(u'\W', re.U)
	nonNum = re.compile(u'[^0-9.]', re.U)
	nonCls = re.compile(ur'[^ABC]', re.U)
	
	oFile = open(r'' + glb.envOutput + 'pyParser_output.txt', 'w')
	oFile.write(u"source;photo_folder;source_instance;obj_type;offer_type;dwn_date;submited_date;contact_info;price;price_per_sqm;currancy;region;town;district;metro_station;domain;range;address;building_type;function;class;area;state;land_class;land_planned_function;land_has_constructions;land_has_railway;land_has_infrastructure;land_with_const_permit;raw_description\n")
	
	#======================================
	for SiteName in arSiteName:
		
		rawFile = open(glb.envOutput + SiteName + '.txt', 'r')
		hFile = open(glb.envOutput + 'h' + SiteName +'.txt', 'r')

		#get raw file mask
		dInputFields = {}

		for Hdr in hFile.readlines():
			Hdr = Hdr.replace('\n','')
			aHdr = Hdr.split('|')
			i = int(aHdr[0])
			h = aHdr[1]
			dInputFields[h] = i
		hFile.close()

#		print dInputFields


		#go line by line
		for rawLine in rawFile.readlines():
			spLine = rawLine.split(';')
#			print rawLine
			oString = "\n"
			
			#source info
			oStr_source, oStr_photo_folder ,oStr_source_instance, oStr_obj_type, oStr_offer_type = ';', ';', ';', ';', ';'
			
			#dates
			oStr_dwn_date, oStr_submited_date = ';', ';'
			
			#pricing
			oStr_price, oStr_price_per_sqm, oStr_currancy = ';', ';', ';'
			
			#location
			oStr_region, oStr_town, oStr_district, oStr_metro_station, oStr_domain, oStr_range, oStr_address = ';', ';', ';', ';', ';', ';', ';'
			
			#bulding info
			oStr_building_type, oStr_function, oStr_class, oStr_area, oStr_state = ';', ';', ';', ';', ';'
			
			#land info
			oStr_land_class, oStr_land_planned_function = ';', ';'
			
			#land infrastructure
			oStr_land_has_constructions, oStr_land_has_railway = ';', ';'
			oStr_land_has_infrastructure, oStr_land_with_const_permit = ';', ';'
			
			#raw
			oStr_contact_info = ';'
			oStr_raw_description = ';'
			
			
			#samle clause a filed with several technics
			if 'source_xClean' in dInputFields:
				oStr_source = spLine[dInputFields['source_xClean']].strip('  \t') + ';'
		#	elif 'ZZZ_xSimple' in dInputFields:
		#		oStr_ZZZ = spLine[dInputFields['ZZZ_xSimple']].strip('  \t') + ';'
		#	elif 'ZZZ_xTrash' in dInputFields:
		#		oStr_ZZZ = spLine[dInputFields['ZZZ_xTrash']].strip('  \t') + ';'
			
			if 'photo_folder' in dInputFields:
				oStr_photo_folder = spLine[dInputFields['photo_folder']] + ';'
			else:
				oStr_photo_folder = 'imgs/zem/' + spLine[dInputFields['source_xClean']].split('/')[-2] + '/;'
					
			if 'source_instance_xClean' in dInputFields:
				oStr_source_instance = spLine[dInputFields['source_instance_xClean']].strip('  \t') + ';'
			else:
				oStr_source_instance = '0;'

			if 'obj_type_xClean' in dInputFields:
				oStr_obj_type = spLine[dInputFields['obj_type_xClean']].strip('  \t') + ';'
			
			if 'offer_type_xClean' in dInputFields:
				oStr_offer_type = spLine[dInputFields['offer_type_xClean']].strip('  \t') + ';'
			elif 'offer_type_xSimple' in dInputFields:
				oStr_offer_type = spLine[dInputFields['offer_type_xSimple']].strip('  \t').lower()
				if oStr_offer_type.find('прода') <> -1:
					oStr_offer_type = 'Продажа;'
				elif oStr_offer_type.find('аренд') <> -1:
					oStr_offer_type = 'Аренда;'
				else:
					oStr_offer_type = ';'

			#ToDo: oStr_dwn_date - if missing, get from file properties
			if 'dwn_date_xClean' in dInputFields:
				oStr_dwn_date = spLine[dInputFields['dwn_date_xClean']].strip('  \t') + ';'
			else:
				oStr_dwn_date = str(datetime.date.today()) + ';'
			
			
			if 'submited_date_xClean' in dInputFields:
				oStr_submited_date = spLine[dInputFields['submited_date_xClean']].strip('  \t') + ';'
			elif 'submited_date_xSimple' in dInputFields:
				oStr_submited_date = spLine[dInputFields['submited_date_xSimple']].strip('  \t').split(' ')[0] + ';'

			if 'contact_info_xClean' in dInputFields:
				oStr_contact_info = spLine[dInputFields['contact_info_xClean']].strip('  \t') + ';'
			elif 'contact_info_xMerge_0' in dInputFields:
				oStr_contact_info = spLine[dInputFields['contact_info_xMerge_0']].strip('  \t')
				try:
					oStr_contact_info += ' ' + spLine[dInputFields['contact_info_xMerge_1']].strip('  \t')
					oStr_contact_info += ' ' + spLine[dInputFields['contact_info_xMerge_2']].strip('  \t')
				except:
					pass
				
				oStr_contact_info += ';'

			if 'raw_description' in dInputFields:
				oStr_raw_description = spLine[dInputFields['raw_description']].replace(' ',' ') \
																				.replace(',,',',') \
																				.replace(',,',',') \
																				.replace('  ',' ') \
																				.replace('  ',' ') \
																				.strip('  \t\r\n,') \
																				

			if 'price_xClean' in dInputFields:
				oStr_price = spLine[dInputFields['price_xClean']].replace(' ','') \
																	.replace(',','.') \
																	+ ';'
			elif 'price_xSimple' in dInputFields:
				oStr_currancy = 'RUR;'
				oStr_price = spLine[dInputFields['price_xSimple']].lower() \
																	.replace(' ','') \
																	.replace(',','.') \
																	.replace('руб','') \
																	.replace('руб.','') \
																	.replace('rur','') \
																	+ ';'

			if 'price_per_sqm_xClean' in dInputFields:
				oStr_price_per_sqm = spLine[dInputFields['price_per_sqm_xClean']].replace(' ','') \
																					.replace(',','.') \
																					+ ';'
			elif 'price_per_sqm_xSimple' in dInputFields:
				oStr_price_per_sqm = spLine[dInputFields['price_per_sqm_xSimple']].lower()
				
				if len(oStr_price_per_sqm) <> 0:
					if oStr_price_per_sqm.find('usd') <> -1:
						oStr_currancy = 'USD;'
						oStr_price_per_sqm = re.sub(nonNum, '', oStr_price_per_sqm).strip('.') + ';'
					elif oStr_price_per_sqm.find('\$') <> -1:
						oStr_currancy = 'USD;'
						oStr_price_per_sqm = re.sub(nonNum, '', oStr_price_per_sqm).strip('.') + ';'
					elif oStr_price_per_sqm.find('eur') <> -1:
						oStr_currancy = 'EUR;'
						oStr_price_per_sqm = re.sub(nonNum, '', oStr_price_per_sqm).strip('.') + ';'
					elif oStr_price_per_sqm.find('€') <> -1:
						oStr_currancy = 'EUR;'
						oStr_price_per_sqm = re.sub(nonNum, '', oStr_price_per_sqm).strip('.') + ';'
					elif oStr_price_per_sqm.find('rur') <> -1:
						oStr_currancy = 'RUR;'
						oStr_price_per_sqm = re.sub(nonNum, '', oStr_price_per_sqm).strip('.') + ';'
					elif oStr_price_per_sqm.find('р') <> -1:
						oStr_currancy = 'RUR;'
						oStr_price_per_sqm = re.sub(nonNum, '', oStr_price_per_sqm).strip('.') + ';'
					elif oStr_price_per_sqm.find('у.') <> -1:
						oStr_currancy = 'CU;'
						oStr_price_per_sqm = re.sub(nonNum, '', oStr_price_per_sqm).strip('.') + ';'
				else:
					oStr_price_per_sqm = ';'


			if 'currancy_xClean' in dInputFields:
				oStr_currancy = spLine[dInputFields['currancy_xClean']] + ';'
			else:
				oStr_currancy = 'RUR;'


			if 'region_xClean' in dInputFields:
				oStr_region = spLine[dInputFields['region_xClean']].strip('  \t') + ';'
			elif 'region_xNoise' in dInputFields:
				oStr_region = spLine[dInputFields['region_xNoise']].strip('  \t,').split('  ')[0] + ';'
			
			if 'town_xClean' in dInputFields:
				oStr_town = spLine[dInputFields['town_xClean']].strip('  \t') + ';'
				if oStr_town in ['Москва;','Санкт-Петербург;']:
					oStr_region = oStr_town
			
			if 'address_xClean' in dInputFields:
				oStr_address = spLine[dInputFields['address_xClean']].strip('  \t') + ';'

			if 'district_xClean' in dInputFields:
				oStr_district = spLine[dInputFields['district_xClean']].strip('  \t') + ';'
							
			if 'metro_stationn_xClean' in dInputFields:
				oStr_metro_station = spLine[dInputFields['metro_station_xClean']].strip('  \t') + ';'
			elif 'metro_station_xNoise' in dInputFields:
				oStr_metro_station = spLine[dInputFields['metro_station_xNoise']].strip('  \t,').split('  ')[0] + ';'
				oStr_metro_station = spLine[dInputFields['metro_station_xNoise']].strip('  \t,').split(',')[0] + ';'
			
	
			if 'domain_xClean' in dInputFields:
				oStr_domain = spLine[dInputFields['domain_xClean']].strip('  \t') + ';'
			elif 'domain_xNoise' in dInputFields:
				oStr_domain = spLine[dInputFields['domain_xNoise']].strip('  \t,')
				if oStr_domain.find(' км') <> -1:
					oStr_domain = oStr_domain.split(" км")[0][0:-2]
				oStr_domain = oStr_domain.replace('?','') + ';'


			if 'range_xClean' in dInputFields:
				oStr_range = spLine[dInputFields['range_xClean']].strip('  \t') + ';'


			if 'building_type_xClean' in dInputFields:
				oStr_building_type = spLine[dInputFields['building_type_xClean']].strip('  \t') + ';'


			if 'function_xClean' in dInputFields:
				oStr_function = spLine[dInputFields['function_xClean']].strip('  \t') + ';'


			if 'class_xClean' in dInputFields:
				oStr_class = spLine[dInputFields['class_xClean']].strip('  \t') + ';'
			elif 'class_xTrash' in dInputFields:
				oStr_class = spLine[dInputFields['class_xTrash']].replace('-','').replace('+','')
				oStr_class = oStr_class.replace('(БЕЗ КОМИССИИ)','')
				
				#replace cyrillic with latin
				oStr_class = oStr_class.replace(' А',' A') \
										.replace(' В',' B') \
										.replace(' С',' C')
				
				oStr_class = re.sub(nonCls, '', oStr_class)
				
				#get the last char
				l = len(oStr_class) - 1
				if l > 0: oStr_class = oStr_class[l]
				
				oStr_class += ';'
	

			if 'area_xClean' in dInputFields:
				oStr_area = spLine[dInputFields['area_xClean']].strip('  \t') + ';'
			elif 'area_xSimple' in dInputFields:
				oStr_area = spLine[dInputFields['area_xSimple']]
				
				splChar = ';'
				m = 1
				
				if oStr_area.find('м2') <> -1:
					splChar = 'м2'
				elif oStr_area.find('кв. м') <> -1:
					splChar = 'кв. м'
				elif oStr_area.find('кв.м') <> -1:
					splChar = 'кв.м'
				elif oStr_area.find('кв м') <> -1:
					splChar = 'кв м'
				elif oStr_area.find('сот') <> -1:
					splChar = ' сот'
					m = 100
				elif oStr_area.find('ге') <> -1:
					splChar = ' ге'
					m = 10000
				elif oStr_area.find('га') <> -1:
					splChar = ' га'
					m = 10000
				else:
					oStr_area = re.sub(nonNum, '', oStr_area)
				
				oStr_area = oStr_area.split(splChar)[0].replace(',','.').replace(' ','')

				if len(oStr_area) <> 0:
					oStr_area = str(float(oStr_area) * m)
				oStr_area += ';'

			elif 'area_xTrash' in dInputFields:
				oStr_area = spLine[dInputFields['area_xTrash']]
				
				if oStr_area.find(' и ') <> -1:
					oStr_area.split(' и ')[0]
				
				splChar = ';'
				m = 1
				
				if oStr_area.find('м2') <> -1:
					splChar = 'м2'
				elif oStr_area.find('кв. м') <> -1:
					splChar = 'кв. м'
				elif oStr_area.find('кв.м') <> -1:
					splChar = 'кв.м'
				elif oStr_area.find('кв м') <> -1:
					splChar = 'кв м'
				elif oStr_area.find('сот') <> -1:
					splChar = ' сот'
					m = 100
				elif oStr_area.find('ге') <> -1:
					splChar = ' ге'
					m = 10000
				elif oStr_area.find('га') <> -1:
					splChar = ' га'
					m = 10000
					
				oStr_area = oStr_area.split(splChar)[0].replace(',','.')
				oStr_area = re.sub(nonNum, '', oStr_area).strip('.')
				if len(oStr_area) <> 0:
					oStr_area = str(float(oStr_area) * m)
				oStr_area += ';'

			if 'state_xClean' in dInputFields:
				oStr_state = spLine[dInputFields['state_xClean']].strip('  \t') + ';'
				

			if 'land_planned_function_xClean' in dInputFields:
				oStr_land_planned_function = spLine[dInputFields['land_planned_function_xClean']].strip('  \t') + ';'
			elif 'land_planned_function_xSimple' in dInputFields:
				oStr_land_planned_function = spLine[dInputFields['land_planned_functionZ_xSimple']].strip('  \t') + ';'
			elif 'land_planned_function_xNoise' in dInputFields:
				oStr_land_planned_function = spLine[dInputFields['land_planned_function_xNoise']]
				oStr_land_planned_function = oStr_land_planned_function.split('   ')[0].strip('  \t') + ';'
			
			if 'land_has_constructions_xClean' in dInputFields:
				oStr_land_has_constructions = spLine[dInputFields['land_has_constructions_xClean']].strip('  \t') + ';'
			
			
			#write parsed string to file
			oString = oStr_source \
					+ oStr_photo_folder \
					+ oStr_source_instance \
					+ oStr_obj_type \
					+ oStr_offer_type \
					+ oStr_dwn_date \
					+ oStr_submited_date \
					+ oStr_contact_info \
					+ oStr_price \
					+ oStr_price_per_sqm \
					+ oStr_currancy \
					+ oStr_region \
					+ oStr_town \
					+ oStr_district \
					+ oStr_metro_station \
					+ oStr_domain \
					+ oStr_range \
					+ oStr_address \
					+ oStr_building_type \
					+ oStr_function \
					+ oStr_class \
					+ oStr_area \
					+ oStr_state \
					+ oStr_land_class \
					+ oStr_land_planned_function \
					+ oStr_land_has_constructions \
					+ oStr_land_has_railway \
					+ oStr_land_has_infrastructure \
					+ oStr_land_with_const_permit \
					+ oStr_raw_description
					
			oFile.write(oString + '\n')


		rawFile.close()
		#==============================================================
	oFile.close()

#finds misplace screenshots and puts them to objec photo folder
def sort_screenshots_tmp(glb):
#	pass
	#ToDo: group folders by 50
	#ToDo: make it context aware
	
	files = os.listdir(glb.envImgOutput + 'zem/')
	for file in files:
		if file.split('.')[-1] in ['png', 'jpg', 'jpeg', 'gif']:
			idObj = file.split('lot')[-1]
			idObj = idObj.split('-full')[0]
			#print idObj
			source = glb.envImgOutput + 'zem/' + file
			destanation = glb.envImgOutput + 'zem/' + idObj + '/'
			print source + ' >> ' + destanation
			
			if not os.path.isdir(destanation):
				os.mkdir(destanation)
			
			destanation += file
			shutil.move(source, destanation)
			

#	files = os.listdir(glb.envImgOutput + 'mgan/')
#	for file in files:
#		if file.split('.')[-1] in ['png', 'jpg', 'jpeg', 'gif']:
#			idObj = file.split('id')[-1]
#			idObj = idObj.split('html')[0]
##			print idObj
#			source = glb.envImgOutput + 'mgan/' + file
#			destanation = glb.envImgOutput + 'mgan/' + idObj + '/'
#			print source + ' >> ' + destanation
#
#			if not os.path.isdir(destanation):
#				os.mkdir(destanation)
#			
#			destanation += file
#			shutil.move(source, destanation)


def sort_screenshots(glb):
	dir = glb.envImgOutput + 'zem/'
	tmpSubDirs = os.listdir(dir)
	subDirs = []
	dGrouped = {}
	
	for d in tmpSubDirs:
		if os.path.isdir(dir + d):
			subDirs.append(dir + d)
	
	grpCounter = 0
	dirCounter = 0
	arOutItem = []
	strGrp = str(grpCounter)
	strGrp = '00000'[len(strGrp):4] + strGrp
	strGrp = 'p' + strGrp + '/'
	
	for d in subDirs:
		if dirCounter == 200:
			grpCounter += 1
			dirCounter = 0
			strGrp = str(grpCounter)
			#ToDo: use .zfill(5)
			strGrp = '00000'[len(strGrp):4] + strGrp
			strGrp = 'p' + strGrp + '/'
		
		dirCounter += 1
		odjId = d.split('/')[-1]

		destanation = dir[0:-1] + '_grouped/' + strGrp + odjId + '/'
		dGrouped[odjId] = [d + '/', destanation]
	
	shutil.move(
				glb.envOutput + 'pyParser_output.txt',
				glb.envOutput + 'pyParser_output.bkp'
				)
	
	rFile = open(glb.envOutput + 'pyParser_output.bkp', 'r')
	wFile = open(glb.envOutput + 'pyParser_output.txt', 'w')
	
	hdrFlag = False
			
	for rawLine in rFile.readlines():
		if not hdrFlag:
			wFile.write(rawLine)
			hdrFlag = True
		else:
			spRawLine = rawLine.split(';')
			url = spRawLine[0]
			objId = url.split('/')[-2]
			outLine = u''
			
			if objId in dGrouped:
				srcPath = dGrouped[objId][0]
				dstPath = dGrouped[objId][1]
				tmp = dstPath.split('/')
				imgPath = tmp[-5] + '/' + tmp[-4] + '/' + tmp[-3] + '/' + tmp[-2] + '/' + tmp[-1]
				outLine = spRawLine[0] + ';' + imgPath
				for e in spRawLine[2:]:
					outLine += ';' + e
				outLine += '\n'
				wFile.write(outLine)
				
				
				thePath = dstPath.split('/')
				chDir = ''
				for tp in thePath[:-1]:
					chDir += tp + '/'
					if not os.path.isdir(chDir):
						os.mkdir(chDir)
				
				dirList = os.listdir(srcPath)
				for f in dirList:
					fName = f.split('/')[-1]
					try :
						shutil.copy(
									srcPath + f,
									dstPath + f
									)
					except:
						print srcPath + f, dstPath + f
						pass
			else:
				wFile.write(rawLine + '\n')
	rFile.close()
	wFile.close()

def make_zem_shots(glb):
	dir = glb.envImgOutput + 'zem/'
	tmpSubDirs = os.listdir(dir)
	subDirs = []
	arHasShots = []
	arShotQueue = []
	
	for d in tmpSubDirs:
		if os.path.isdir(dir + d):
			subDirs.append(dir + d)
	
	for d in subDirs:
		files = os.listdir(d)
		for file in files:
			if file.split('.')[-1] == 'png':
				idObj = file.split('lot')[-1]
				idObj = idObj.split('-full')[0]
				arHasShots.append(idObj)
	
	
	SiteName = 'zem'
	rawFile = open(glb.envOutput + SiteName + '.txt', 'r')
	cur = 0
	arQueueElement = []
	
	for rawLine in rawFile.readlines():
		url = rawLine.split(';')[3]
		objId = url.split('/')[-2]
		if objId not in arHasShots:
			arQueueElement.append(url)
			cur += 1
			if cur == 20:
				arShotQueue.append(arQueueElement)
				cur = 0
				arQueueElement = []
	
	print len(arShotQueue) * 20, 'missing screenshots identified'

	for qi in arShotQueue:
		LockNLoad(qi, glb.envDir, dir)


	#sort by folders
	files = os.listdir(dir)
	for file in files:
		if file.split('.')[-1] in ['png', 'jpg', 'jpeg', 'gif']:
			idObj = file.split('lot')[-1]
			idObj = idObj.split('-full')[0]
			#print idObj
			source = glb.envImgOutput + dir + file
			destanation = glb.envImgOutput + dir + idObj + '/'
			#print source + ' >> ' + destanation

			if not os.path.isdir(destanation):
				os.mkdir(destanation)

			destanation += file
			shutil.move(source, destanation)
		



