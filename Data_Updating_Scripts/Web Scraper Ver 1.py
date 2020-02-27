"""
This script is the first version of a web scraping tool that, for a data source, search online to
see if there is an update available. If so, download into specified folder.
"""

import os
from datetime import datetime
import urllib3
import zipfile, shutil
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import requests
import re

def download_file(download_url, download_folder, filename):
	# try:
	http = urllib3.PoolManager()
	print("Downloading: ", filename)
	with http.request('GET', download_url, preload_content = False) as resp:
		with open(os.path.join(download_folder,filename),'wb') as out:
			shutil.copyfileobj(resp, out)
		resp.release_conn()
	# except:
	# 	print("Error with web page")

def unzip(file_path):
	with zipfile.ZipFile(file_path) as zf:
		zf.extractall()
		
def LastUpdateArcMeta(metadata_url):
	"""
	Function to grab the text of the last time a data set has been updated
	through the ESRI arcgis metadata format. This function is specific for
	data hosted online through ESRI. url has to go to the metadata page.
	
	This function assumes that the string 'Last update:' will be exact
	for searching the html. If it is different, the function will not work.
	
	Args:
		metadata_url: string of metadata webpage

	Returns: string of date in format YYYY-MM-DD

	"""
	
	content = requests.get(metadata_url).text
	
	soup = bs(content, 'html.parser')
	
	text = soup.find_all(text=True)
	
	index = text.index('Last update:')
	
	date_string = text[index + 1].replace('\n', '')
	
	date = datetime.strptime(date_string.strip(' '), '%Y-%m-%d')
	
	return date

def LastUpdateBoemDataCenterBasic(url, file_name):
	"""
	Function to grab the text of the last time a data set has been updated
	through the BOEM Data Center information page format. The url has to go
	to a page that contains a table with the 'File Name' and 'Last Updated'
	fields. Here is an example of the type of page:
	
	https://www.data.boem.gov/Main/Platform.aspx

	This function assumes that the file name string will be exact
	for searching the html. If it is different, the function will not work.

	Args:
		metadata_url: string of BOEM webpage
		file_name: string of the file name

	Returns: date class from datetime module

	"""
	
	content = requests.get(url).text
	
	soup = bs(content, 'html.parser')
	
	text = soup.find_all(text=True)
	
	index = text.index(file_name)
	
	full_string = text[index + 2].replace('\n', '')
	
	date = datetime.strptime(full_string, '%m/%d/%Y %H:%M:%S %p')
	
	return(date)

def LastUpdateBoemDataCenterMapping(dataset_name):
	"""
	Function to grab the text of the last time a data set has been updated
	through the BOEM Data Center Mapping page format. This function is
	specific to this webpage:

	https://www.data.boem.gov/Main/Mapping.aspx

	This function assumes that the dataset_name string will be exactly the
	same as listed on the webpage. If it is different, the function will not work.

	Args:
		dataset_name: string of the name of the data set

	Returns: date class from datetime module

	"""
	
	content = requests.get('https://www.data.boem.gov/Main/Mapping.aspx').content
	
	soup = bs(content, 'html.parser')
	
	stuff = soup.find_all("tr", {'class': 'dxgvDataRow'})
	
	for s in stuff:
		
		text = s.text
		
		if format(dataset_name + '\n') in text:
			
			string = s.contents[4].contents[0]
			
			date = datetime.strptime(string, '%m/%d/%Y %H:%M:%S %p')
			
			return(date)
		
def LastUpdateBoemTablePage(url):
	"""
	Function to grab the late update date from a BOEM
	Data Center page that shows the available data grid
	for one data set. Here is an example of the type of
	page format
	
	https://www.data.boem.gov/Other/DataTables/DeepQualFields.aspx
	
	Args:
		url: webpage url sring

	Returns: date class from datetime module

	"""
	
	content = requests.get(url).content
	
	soup = bs(content, 'html.parser')
	
	stuff = soup.find_all("span", {'id': 'ASPxLabelUpdate'})
	
	for s in stuff:
		
		text = s.text
		
		if 'data last updated' in text:
			date_string = re.findall("[0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9]", text)
			
			date = datetime.strptime(date_string[0], '%m-%d-%Y')
			
			return(date)

def LastUpdateBoemDataCenterSands(sands_plays_Chronozones_orRef, year):
	"""
	Function to grab the date of the last time a data set has been updated
	through the BOEM Data Center sands data page format.

	the first argument must be one of the following:
	- 'sands'
	- 'plays'
	- 'chronozones'
	- 'xref_oper-comp'
	
	the second argument is the year that you want to know the last update
	date for. The webpage currently has all years between 2004 to 2018, and contains
	some data for 1999, 2001, and 2003. See the webpage for more info
	
	https://www.data.boem.gov/Main/GandG.aspx

	Args:
		metadata_url: string of BOEM Sands data webpage
		sands_plays_Chronozones_orRef: string of 'sands', 'plays', 'chronozones', or 'xref_oper-comp'
		year = string of the year you want to know the update date for

	Returns: date class from datetime module

	"""
	
	content = requests.get('https://www.data.boem.gov/Main/GandG.aspx').text
	
	soup = bs(content, 'html.parser')
	
	text = soup.find_all(text=True)
	
	index = text.index(format(year) + sands_plays_Chronozones_orRef.lower())
	
	full_string = text[index + 2].replace('\n', '')
	
	date = datetime.strptime(full_string, '%m/%d/%Y %H:%M:%S %p')
	
	return(date)

def LastUpdateNoaaFisheries(url):
	"""
	Funciton to grab the date of last update for data stored online
	at fisheries.noaa.gov. This is an example of the page format:
	
	https://www.fisheries.noaa.gov/resource/map/gulf-sturgeon-critical-habitat-map-and-gis-data
	
	Args:
		url: string to webpage

	Returns: date object from datetime module

	"""
	
	content = requests.get(url).content
	
	soup = bs(content, 'html.parser')
	
	stuff = soup.find_all("div", {'class': 'last-updated'})
	
	for s in stuff:
		text = s.text
		
		date_string = re.findall("[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]", text)
		
		date = datetime.strptime(date_string[0], '%m/%d/%Y')
		
		return(date)
		
if __name__ == '__main__':
	
	content = requests.get('https://www.eia.gov/maps/layer_info-m.php').content
	
	soup = bs(content, 'html.parser')
	
	stuff = soup.find_all("table", {'class': 'basic_table all_left'})
	
	# using specific route to all data content
	good_stuff = stuff[0].contents[5].contents
	
	for s in good_stuff:
		
		try:
		
			text = s.text
		
			if 'Liquefied Natural Gas Import/Export Terminals' in text:
			
				date_string = re.findall("[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]", text)
				
				date = datetime.strptime(date_string[0], '%m/%d/%Y')
				
				print(date)
			
		except:
			continue