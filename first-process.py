#!/usr/bin/python

import re
import pprint
import csv


def getItemNumberRE(n):
	# ^\d(\s*\d)*\s+
	p = r'\n'
	if (n > 99):
		p += str(n / 100) + r'\s*'
	if (n > 9):
		p += str((n % 100) / 10) + r'\s*'
	p += str(n % 10) + r'\s+'
	return p

def getItemNumberBodyRE(n):
	p = getItemNumberRE(n) + r'.*?(?=' + getItemNumberRE(n + 1) + ')'
	return p

def extractNumberFromClassHeading(classHeading):
	h = re.sub(class_label_RE, '', classHeading)
	h = re.sub('\s', '', h) # No spaces
	h = re.sub('\.$', '', h) # No trailing period
	h = re.sub('I', '1', h) # I's are really 1's
	h = re.sub('T', '7', h) # T's are really 7's
	return int(h)


def extractAll(countries):
	data = {}
	# for country in countries:
	for i in range(len(countries)):
		country = countries[i]
		# countryNumber = (i < 10 ? '0' : '') + str(i)
		countryCount = i + 1
		countryCountText = ('0' if countryCount < 10 else '') + str(countryCount)
		countryFilename = 'Catalog-' + countryCountText + '_' + country + '.txt'
		# print countryFilename
		data[country] = extractCountry(countryFilename)
	return data


def extractCountry(country):
	
	f = open(country, 'r')
	catalogText = ''
	for line in f:
		catalogText += line

	return extractClasses(catalogText)
	

def extractClasses(countryText):

	data = []

	for classListingMatch in re.finditer(class_body_RE, countryText):

		classListing = classListingMatch.group()
		classHeading = class_heading_RE.search(classListing).group()
		classNumber = extractNumberFromClassHeading(classHeading)
		classItems = extractItems(classListing)
		if len(classItems) > 0:
			data.append({ 'class_number': classNumber, 'class_items': classItems })

	return data


def extractItems(classText):

	data = []

	for i in range(1, 200):
		itemMatch = re.compile(getItemNumberBodyRE(i), re.MULTILINE | re.DOTALL).search(classText)
		if (itemMatch is None):
			a = 0
			# print  'Item ' + str(i) + ' - none'
		else:
			itemText = itemMatch.group()
			itemText = re.sub(getItemNumberRE(i), '', itemText) # Trim number off beginning of line
			itemText = re.sub(re.compile(r'\s+$'), '', itemText) # No whitespace at end of line
			itemText = re.sub(re.compile(r'\s+'), ' ', itemText) # All whitespace reduced to single space
			itemText = re.sub(re.compile('\\s*\xe2\x80\x94\\s*'), '---', itemText)
			data.append({ 'text':itemText, 'number': i })
			classListing = classText[itemMatch.end():]

	return data


def writeToCSV(data):
	with open('glass-palace-catalog.csv', 'w') as csvfile:
	    fieldnames = ['country','class','item_number','item']
	    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

	    writer.writeheader()

	    for country in data:
	    	for classListing in data[country]:
	    		for classItem in classListing['class_items']:
	    			writer.writerow({'country':country, 'class': classListing['class_number'], 'item_number': classItem['number'], 'item':classItem['text']})

	    


def main():

	pp = pprint.PrettyPrinter(indent=4)

	countries = ['USA','UK','Germany','Belgium','France','Switzerland','Holland','Austria','Italy','British-Guiana','Newfoundland','Sweden-Norway','Mexico','Turkey']

	# pp.pprint(extractAll(countries))
	writeToCSV(extractAll(countries))



# Define global regular expressions

class_label = r'[CGU].{1,3}(?:A.|.S)S' # fuzzy match for the word "CLASS"
class_label_RE = re.compile(class_label)
class_pattern = class_label + r'\s+[\dIT]{1,2}\.?'
class_heading_RE = re.compile(class_pattern)
class_body_RE = re.compile(class_pattern + '.*?(?=' + class_pattern + ')', re.MULTILINE | re.DOTALL)

main()

