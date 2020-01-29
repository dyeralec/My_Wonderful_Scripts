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
		
if __name__ == '__main__':

	webpage = 'https://ais-faa.opendata.arcgis.com/datasets/e747ab91a11045e8b3f8a3efd093d3b5_0?geometry=-128.877%2C20.427%2C-53.028%2C34.053'
	#webpage = 'https://www.arcgis.com/sharing/rest/content/items/e747ab91a11045e8b3f8a3efd093d3b5/info/metadata/metadata.xml?format=default&output=html'
	
	last_update = '01/9/2020'
	
	page = requests.get(webpage)
	
	soup = bs(page.text, 'html.parser')
	
	find_date = soup.find_all('div', class_='metatags ember-view')
	
	print(find_date)