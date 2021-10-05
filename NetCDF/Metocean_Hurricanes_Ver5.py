"""
Script to calculate the number of times and duration a platform is hit by a certain category of hurricane.
Uses storm NetCDFs and determines the category based on wind speed, which determines the size of the
buffer that the platform must be within to be 'hit' by the storm.

The mean time between each storm observation is 0.23 days (approx. 5.5 hours). This number was used to
calculate the duration of each storm impact on a platform. Each time a platorm was within the buffer
of a storm, 0.23 days was added to the duration for the category of the type of storm.

In order to determine if the platform is within the storm buffer, the platform and storm latitude and
longitudes needed to be converted from degrees to a standard x/y distance in meters. The latitude and
longitude origins for each conversion was determined by their minimums of all the NetCDFs.

Version 2 is going to use the updated storm data that now includes data from 2018 and 2019, as well as
new variables including the saffir-simpson hurricane category and wave height.

Version 3 is going to add the capability of creating stats for the storm categories

IBTrACS Data Source:

Knapp, K. R., M. C. Kruk, D. H. Levinson, H. J. Diamond, and C. J. Neumann, 2010:
The International Best Track Archive for Climate Stewardship (IBTrACS): Unifying tropical cyclone best track data.
Bulletin of the American Meteorological Society, 91, 363-376. non-gonvernment domain doi:10.1175/2009BAMS2755.1

Knapp, K. R., H. J. Diamond, J. P. Kossin, M. C. Kruk, C. J. Schreck, 2018:
International Best Track Archive for Climate Stewardship (IBTrACS) Project, Version 4. [1942-2019]. NOAA National
Centers for Environmental Information. non-gonvernment domain https://doi.org/10.25921/82ty-9e16 [4/8/2020].

Developed by: Alec Dyer
alec.dyer@netl.doe.gov
(541) 918-4475
"""

import netCDF4
import csv
from datetime import datetime
from datetime import timedelta
from argparse import ArgumentParser
from glob import iglob
import os
import scipy
import time
from osgeo import ogr
import numpy as np

D_FORMAT = '%m/%d/%Y'
DT_FORMAT = '%m/%d/%Y %H:%M:%S'
DT_ISO_FORMAT = '%Y-%m-%d %H:%M:%S'

FIRST_DATE = datetime(1972,1,1)
LAST_DATE = datetime(2021,1,27)

FLD_NAME = 'Storms'

# NC_YEAR_FORMAT = f'Year.{year}.ibtracs_wmo.v03r10.nc'

class PlatformRecord(object):

	def __init__(self, PlatformID, Lat, Lon, InstallDate, RemovalDate=None, IncidentDates=''):
		
		self.id = PlatformID
		self.lat = float(Lat)
		self.lon = float(Lon)
		self.install_date = None
		if InstallDate is not None and len(InstallDate) > 0:
			self.install_date = datetime.strptime(InstallDate, D_FORMAT)
		self.remove_date = None
		if RemovalDate is not None and len(RemovalDate ) >0:
			self.remove_date = datetime.strptime(RemovalDate, D_FORMAT)
		self.x = None
		self.y = None
		self.incident_dates = (datetime.strptime(x, D_FORMAT) for x in IncidentDates.split(';') if len(x) > 0)
		self.totalHitCount = 0
		self.stormTotal = 0
		self.cat_noneCount = 0
		self.tropical_hitCheck = False
		self.tropical = 0
		self.tropical_min = float('inf')
		self.tropical_max = float('-inf')
		self.tropical_mean = 0
		self.tropical_days = 0
		self.tropical_days_min = float('inf')
		self.tropical_days_max = float('-inf')
		self.tropical_days_mean = 0
		self.C1_hitCheck = False
		self.C1 = 0
		self.C1_min = float('inf')
		self.C1_max = float('-inf')
		self.C1_mean = 0
		self.C1_days = 0
		self.C1_days_min = float('inf')
		self.C1_days_max = float('-inf')
		self.C1_days_mean = 0
		self.C2_hitCheck = False
		self.C2 = 0
		self.C2_min = float('inf')
		self.C2_max = float('-inf')
		self.C2_mean = 0
		self.C2_days = 0
		self.C2_days_min = float('inf')
		self.C2_days_max = float('-inf')
		self.C2_days_mean = 0
		self.C3_hitCheck = False
		self.C3 = 0
		self.C3_min = float('inf')
		self.C3_max = float('-inf')
		self.C3_mean = 0
		self.C3_days = 0
		self.C3_days_min = float('inf')
		self.C3_days_max = float('-inf')
		self.C3_days_mean = 0
		self.C4_hitCheck = False
		self.C4 = 0
		self.C4_min = float('inf')
		self.C4_max = float('-inf')
		self.C4_mean = 0
		self.C4_days = 0
		self.C4_days_min = float('inf')
		self.C4_days_max = float('-inf')
		self.C4_days_mean = 0
		self.C5_hitCheck = False
		self.C5 = 0
		self.C5_min = float('inf')
		self.C5_max = float('-inf')
		self.C5_mean = 0
		self.C5_days = 0
		self.C5_days_min = float('inf')
		self.C5_days_max = float('-inf')
		self.C5_days_mean = 0
		self.waveHeightCount = 0
		self.waveHeightNoneCount = 0
		self.waveHeightSum = 0
		self.waveHeightAverage = 0
		self.waveHeightMax = float('-inf')
		self.waveHeightMin = float('inf')
		self.windCount = 0
		self.windNoneCount = 0
		self.windVals = []
		self.windSum = 0
		self.windAverage = 0
		self.windMax = float('-inf')
		self.windMin = float('inf')
		self.windStdDev = None
		self.windP25 = None
		self.windMedian = None
		self.windP75 = None
		self.windP90 = None
		self.gustCount = 0
		self.gustNoneCount = 0
		self.gustVals = []
		self.gustSum = 0
		self.gustAverage = 0
		self.gustMax = float('-inf')
		self.gustMin = float('inf')
		self.gustStdDev = None
		self.gustP25 = None
		self.gustMedian = None
		self.gustP75 = None
		self.gustP90 = None
		self.yearCount = 0
		self.MCPCount = 0
		self.MCPNoneCount = 0
		self.MCPVals = []
		self.MCPSum = 0
		self.MCPAverage = 0
		self.MCPMax = float('-inf')
		self.MCPMin = float('inf')
		self.MCPStdDev = None
		self.MCPP25 = None
		self.MCPMedian = None
		self.MCPP75 = None
		self.MCPP90 = None

	def addValue(self, cat, wave, wind, gust, mcp):

		self.totalHitCount += 1
		
		if wave is not None:
			self.waveHeightCount += 1
			self.waveHeightSum += wave
			self.waveHeightAverage = (self.waveHeightSum/self.waveHeightCount)
			if wave > self.waveHeightMax:
				self.waveHeightMax = wave
			if wave < self.waveHeightMin:
				self.waveHeightMin = wave
		if wave is None:
			self.waveHeightNoneCount += 1
				
		if wind is not None:
			self.windVals.append(wind)
			self.windCount += 1
			self.windSum += wind
			self.windAverage = (self.windSum / self.windCount)
			if wind > self.windMax:
				self.windMax = wind
			if wind < self.windMin:
				self.windMin = wind
		if wind is None:
			self.windNoneCount += 1
				
		if gust is not None:
			self.gustVals.append(gust)
			self.gustCount += 1
			self.gustSum += gust
			self.gustAverage = (self.gustSum / self.gustCount)
			if gust > self.gustMax:
				self.gustMax = gust
			if gust < self.gustMin:
				self.gustMin = gust
		if gust is None:
			self.gustNoneCount += 1

		if mcp is not None:
			self.MCPVals.append(mcp)
			self.MCPCount += 1
			self.MCPSum += mcp
			self.MCPAverage = (self.MCPSum / self.MCPCount)
			if mcp > self.MCPMax:
				self.MCPMax = mcp
			if mcp < self.MCPMin:
				self.MCPMin = mcp
		if mcp is None:
			self.gustNoneCount += 1
		
		if cat is None:
			self.cat_noneCount += 1
			return
		if cat == 'tropical':
			if self.tropical_hitCheck is False:
				self.stormTotal += 1
				self.tropical += 1
				self.tropical_hitCheck = True
			self.tropical_days += 0.24
		if cat == 'C1':
			if self.C1_hitCheck is False:
				self.stormTotal += 1
				self.C1 += 1
				self.C1_hitCheck = True
			self.C1_days += 0.24
		if cat == 'C2':
			if self.C2_hitCheck is False:
				self.stormTotal += 1
				self.C2 += 1
				self.C2_hitCheck = True
			self.C2_days += 0.24
		if cat == 'C3':
			if self.C3_hitCheck is False:
				self.stormTotal += 1
				self.C3 += 1
				self.C3_hitCheck = True
			self.C3_days += 0.24
		if cat == 'C4':
			if self.C4_hitCheck is False:
				self.stormTotal += 1
				self.C4 += 1
				self.C4_hitCheck = True
			self.C4_days += 0.24
		if cat == 'C5':
			if self.C5_hitCheck is False:
				self.stormTotal += 1
				self.C5 += 1
				self.C5_hitCheck = True
			self.C5_days += 0.24

	def FinishPlatform(self):

		if len(self.windVals) > 0:
			self.windStdDev = np.std(self.windVals)
			self.windP25 = np.percentile(self.windVals, 25)
			self.windMedian = np.percentile(self.windVals, 50)
			self.windP75 = np.percentile(self.windVals, 75)
			self.windP90 = np.percentile(self.windVals, 90)

		if len(self.gustVals) > 0:
			self.gustStdDev = np.std(self.gustVals)
			self.gustP25 = np.percentile(self.gustVals, 25)
			self.gustMedian = np.percentile(self.gustVals, 50)
			self.gustP75 = np.percentile(self.gustVals, 75)
			self.gustP90 = np.percentile(self.gustVals, 90)

		if len(self.MCPVals) > 0:
			self.MCPStdDev = np.std(self.MCPVals)
			self.MCPP25 = np.percentile(self.MCPVals, 25)
			self.MCPMedian = np.percentile(self.MCPVals, 50)
			self.MCPP75 = np.percentile(self.MCPVals, 75)
			self.MCPP90 = np.percentile(self.MCPVals, 90)
			
	def ResetHitCheck(self):
		
		self.tropical_hitCheck = False
		self.C1_hitCheck = False
		self.C2_hitCheck = False
		self.C3_hitCheck = False
		self.C4_hitCheck = False
		self.C5_hitCheck = False
		
	def UpdateYearlyStats(self, YearStats):
		
		self.yearCount += 1
		
		if YearStats.tropical < self.tropical_min:
			self.tropical_min = YearStats.tropical
		if YearStats.tropical > self.tropical_max:
			self.tropical_max = YearStats.tropical
		self.tropical_mean = (self.tropical / self.yearCount)
		
		if YearStats.tropical_days < self.tropical_days_min:
			self.tropical_days_min = YearStats.tropical_days
		if YearStats.tropical_days > self.tropical_days_max:
			self.tropical_days_max = YearStats.tropical_days
		self.tropical_days_mean = (self.tropical_days / self.yearCount)
		
		if YearStats.C1 < self.C1_min:
			self.C1_min = YearStats.C1
		if YearStats.C1 > self.C1_max:
			self.C1_max = YearStats.C1
		self.C1_mean = (self.C1 / self.yearCount)
		
		if YearStats.C1_days < self.C1_days_min:
			self.C1_days_min = YearStats.C1_days
		if YearStats.C1_days > self.C1_days_max:
			self.C1_days_max = YearStats.C1_days
		self.C1_days_mean = (self.C1_days / self.yearCount)
		
		if YearStats.C2 < self.C2_min:
			self.C2_min = YearStats.C2
		if YearStats.C2 > self.C2_max:
			self.C2_max = YearStats.C2
		self.C2_mean = (self.C2 / self.yearCount)
		
		if YearStats.C2_days < self.C2_days_min:
			self.C2_days_min = YearStats.C2_days
		if YearStats.C2_days > self.C2_days_max:
			self.C2_days_max = YearStats.C2_days
		self.C2_days_mean = (self.C2_days / self.yearCount)
		
		if YearStats.C3 < self.C3_min:
			self.C3_min = YearStats.C3
		if YearStats.C3 > self.C3_max:
			self.C3_max = YearStats.C3
		self.C3_mean = (self.C3 / self.yearCount)
		
		if YearStats.C3_days < self.C3_days_min:
			self.C3_days_min = YearStats.C3_days
		if YearStats.C3_days > self.C3_days_max:
			self.C3_days_max = YearStats.C3_days
		self.C3_days_mean = (self.C3_days / self.yearCount)
		
		if YearStats.C4 < self.C4_min:
			self.C4_min = YearStats.C4
		if YearStats.C4 > self.C4_max:
			self.C4_max = YearStats.C4
		self.C4_mean = (self.C4 / self.yearCount)
		
		if YearStats.C4_days < self.C4_days_min:
			self.C4_days_min = YearStats.C4_days
		if YearStats.C4_days > self.C4_days_max:
			self.C4_days_max = YearStats.C4_days
		self.C4_days_mean = (self.C4_days / self.yearCount)
		
		if YearStats.C5 < self.C5_min:
			self.C5_min = YearStats.C5
		if YearStats.C5 > self.C5_max:
			self.C5_max = YearStats.C5
		self.C5_mean = (self.C5 / self.yearCount)
		
		if YearStats.C5_days < self.C5_days_min:
			self.C5_days_min = YearStats.C5_days
		if YearStats.C5_days > self.C5_days_max:
			self.C5_days_max = YearStats.C5_days
		self.C5_days_mean = (self.C5_days / self.yearCount)
		
class YearlyRecord(object):
	
	# This class is used to keep the stats per platform on a yearly basis
	# and will be used to update the stats for the PlatformRecord class
	
	def __init__(self):
		self.tropical_hitCheck = False
		self.tropical = 0
		self.tropical_days = 0
		self.C1_hitCheck = False
		self.C1 = 0
		self.C1_days = 0
		self.C2_hitCheck = False
		self.C2 = 0
		self.C2_days = 0
		self.C3_hitCheck = False
		self.C3 = 0
		self.C3_days = 0
		self.C4_hitCheck = False
		self.C4 = 0
		self.C4_days = 0
		self.C5_hitCheck = False
		self.C5 = 0
		self.C5_days = 0
		
	def AddHit(self, cat):
		
		if cat == 'tropical':
			if self.tropical_hitCheck == False:
				self.tropical += 1
				self.tropical_hitCheck = True
			self.tropical_days += 0.24
		if cat == 'C1':
			if self.C1_hitCheck == False:
				self.C1 += 1
				self.C1_hitCheck = True
			self.C1_days += 0.24
		if cat == 'C2':
			if self.C2_hitCheck is False:
				self.C2 += 1
				self.C2_hitCheck = True
			self.C2_days += 0.24
		if cat == 'C3':
			if self.C3_hitCheck is False:
				self.C3 += 1
				self.C3_hitCheck = True
			self.C3_days += 0.24
		if cat == 'C4':
			if self.C4_hitCheck is False:
				self.C4 += 1
				self.C4_hitCheck = True
			self.C4_days += 0.24
		if cat == 'C5':
			if self.C5_hitCheck is False:
				self.C5 += 1
				self.C5_hitCheck = True
			self.C5_days += 0.24
			
	def ResetHitCheck(self):
		
		self.tropical_hitCheck = False
		self.C1_hitCheck = False
		self.C2_hitCheck = False
		self.C3_hitCheck = False
		self.C4_hitCheck = False
		self.C5_hitCheck = False


def sph2xy(lon, lon_origin, lat, lat_origin):
	R = 6371 * 1e3
	dg2rad = scipy.pi / 180.0
	x = (R) * (lon - lon_origin) * (dg2rad) * (scipy.cos((lat_origin * dg2rad)))
	y = (R) * (lat - lat_origin) * (dg2rad)

	return x, y


def OpenFileGDB(path, name):
	# open the inShapefile as the driver type
	inDriver = ogr.GetDriverByName('OpenFileGDB')
	inDataSource = inDriver.Open(path, 0)
	inLayer = inDataSource.GetLayer(name)

	return inDataSource, inLayer

def OpenShp(path):
	# open the inShapefile as the driver type
	inDriver = ogr.GetDriverByName('ESRI Shapefile')
	inDataSource = inDriver.Open(path, 0)
	inLayer = inDataSource.GetLayer()

	return inDataSource, inLayer

def readStormDateTime(instr):
	start_date = datetime.strptime('11/17/1858 00:00:00', DT_FORMAT)
	delta = timedelta(days=instr)
	new_date = start_date + delta

	return new_date

def readStormDateTime_ISO(instr):

	iso_date = datetime.strptime(instr, DT_ISO_FORMAT)

	return iso_date

def readPlatDateTime(instr):
	return datetime.strptime(instr, D_FORMAT)

def loadPlatformCsv(path, cls=PlatformRecord):
	with open(path, 'r') as inFile:
		dRdr = csv.DictReader(inFile)

		ret = []
		for row in dRdr:
			ret.append(cls(**row))

		return ret
	
def findNCDTInd(target, nc):

	ds = netCDF4.Dataset(nc)

	time_var = ds.variables['time']
	try:
		ind = netCDF4.date2index(target,time_var)
	except ValueError:
		return None, None
	else:
		return ds,ind


def ExtractLatLongInGDB_ByAttribute(inDataSource, inLayer, filterQuery):
	"""
	This function will extract features from a feature class based on a SQL filter query and save the layer to
	memory. It will carry over any attributes in the input feature class.

	This function will only work with feature classes!!! The feature has to be in a geodatabase, and the driver
	MUST be 'FileGDB'. This function can be changed to use shapefiles by adjusting how the input is opened.

	Requirement: 'FileGDB' driver for ogr

	Args:
		inGDB: input geodatabase (must end with .gdb)
		inFileName: the name of the input feature class
		filterQuery: list of SQL query that is in the format of 'column = string' ... string must be quoted and number should NOT be quoted
		outLayerName: the name of the output feature class

	Returns: output memory data source and memory layer
	"""

	from osgeo import ogr

	inLayer_query = inLayer

	# query out the wanted fields
	for i in filterQuery:
		inLayer_query.SetAttributeFilter(i)

	print('filter set')

	print('feature count: {}'.format(inLayer_query.GetFeatureCount()))

	pt_list = []

	# feat = inLayer_query.GetNextFeature()
	#
	# geom = feat.GetGeometryRef()
	#
	# pt = geom.GetPoint()

	# get lat and long of filtered point(s)
	for inFeature in inLayer_query:

		# get geometry
		geom = inFeature.GetGeometryRef()
		# get point
		pt = geom.GetPoint()

		pt_list.append(pt)

	if len(pt_list) > 1:
		print('UH OH TOO  MANY POINTS FILTERED!!!!')

	inLayer.ResetReading()

	return inDataSource, inLayer, pt_list

def GetPlatformCoords(platform_points):

	# open platform
	p_ds, p_lyr = OpenShp(platform_points)

	plat_coords = {}

	# loop through features
	for feat in p_lyr:
		# get geometry
		geom = feat.GetGeometryRef()
		# get point
		pt = geom.GetPoint()
		# get id
		p_id = str(feat.GetField('PlatformID'))

		plat_coords[p_id] = pt

	return plat_coords

def GetStormCoords(storm_points):

	# open platform
	p_ds, p_lyr = OpenShp(storm_points)

	storm_coords = {}

	# loop through features
	for feat in p_lyr:
		# get geometry
		geom = feat.GetGeometryRef()
		# get point
		pt = geom.GetPoint()
		# get id
		s_sid = feat.GetField('SID')
		s_iso = feat.GetField('ISO_TIME')

		storm_coords[s_sid + '_' + s_iso] = pt

	return storm_coords

def GetDistance(position_1, position_2, coordTransform):
		"""
        Returns distance in 'units' (default km) between two Lat Lon point sets
                position_1 and position_2 are dicts containing "lon" and "lat"

                Units (optional) can be "km", "sm", or "nm"
        """
		point1 = ogr.Geometry(ogr.wkbPoint)
		point1.AddPoint(position_1[0], position_1[1])
		#point1.Transform(coordTransform)

		point2 = ogr.Geometry(ogr.wkbPoint)
		point2.AddPoint(position_2[0], position_2[1])
		#point2.Transform(coordTransform)

		raw_dist = point2.Distance(point1)

		return raw_dist

def GetDistanceBetweenPoints(platform_coords_list, storm_coords_list, id, iso_t, sid):

	# get point from platform points based on attributes
	p_pt = platform_coords_list[id]

	# get point from storm point based on attributes
	s_pt = storm_coords_list[sid + '_' + iso_t]

	dist = GetDistance(p_pt, s_pt, None)

	return dist

def checkHurricaneEffect(platform, storm_lon, storm_lat, cat, wind_speed, wave, gust, lon_min, lat_min, mcp, sid, iso_t, platform_coords_list, storm_coords_list):
	
	# Saffir-Simpson Scale Hurricane Category
	#Category  mph		m/s		kts
	# 1		  74-95	   33-42   64-82
	# 2		  96-110   43-49   83-95
	# 3 	 111-130   50-58   96-113
	# 4		 131-155   59-69   114-135
	# 5		   156+     70+		136+
	
	# Hurricane radius based on category
	#	Category		Radius (km)
	# tropical storm 	 100,000
	# 	  1-2			 300,000
	# 	  3-5			 450,000
	
	# determine radius (m) of the storm by the wind speed
	
	category = None
	radius = None
	
	# try to use given category, but if cat is None use wind speed
	# to get the radius of the hurricane
	if cat is not None:
		if cat == 0:
			radius = 100000
			category = 'tropical'
		if cat == 1:
			radius = 300000
			category = 'C1'
		if cat == 2:
			radius = 300000
			category = 'C2'
		if cat == 3:
			radius = 450000
			category = 'C3'
		if cat == 4:
			radius = 450000
			category = 'C4'
		if cat == 5:
			radius = 450000
			category = 'C5'
	else:
		# if there is no category given, use the wind speed to approximate radius
		if wind_speed is not None:
			wind_speed = float(wind_speed)
			if (wind_speed >= 34) and (wind_speed < 64):
				radius = 100000
				category = 'tropical'
			if (wind_speed >= 64) and (wind_speed < 83):
				radius = 300000
				category = 'C1'
			if (wind_speed >= 83) and (wind_speed < 96):
				radius = 300000
				category = 'C2'
			if (wind_speed >= 96) and (wind_speed < 113):
				radius = 450000
				category = 'C3'
			if (wind_speed >= 113) and (wind_speed < 137):
				radius = 450000
				category = 'C4'
			if wind_speed >= 137:
				radius = 450000
				category = 'C5'
	
	if radius is not None:
		# convert lat and long coordinates (degrees) into x and y (meters)
		#storm_x, storm_y = sph2xy(storm_lon, lon_min, storm_lat, lat_min)
		# use squared distance function to determine if the platform lies within the hurricane buffer
		#distance = np.sqrt((((platform.x - storm_x) ** 2) + ((platform.y - storm_y) ** 2)))

		# get distance between the two points
		distance = GetDistanceBetweenPoints(platform_coords_list, storm_coords_list, platform.id, iso_t, sid)

		if distance <= radius:
			# update platform record with stat
			platform.addValue(category, wave, wind_speed, gust, mcp)
			
			return category
		else:
			return None

	return None


def processStats(platform, numStorms, lat, lon, time, categ, msw, wave, gust, lon_min, lat_min, mcp, region, sid, iso_time, platform_coords_list, storm_coords_list):
	# loop through each storm
	error_count = 0
	# set year to none for later
	year = None
	YearStats = YearlyRecord()
	for i in range(0, numStorms):
		# make sure storm hitCheck is False to begin each storm
		platform.ResetHitCheck()
		YearStats.ResetHitCheck()
	
		try:
			# grab variables for that one storm
			lat_storm = lat[i:i + 1].tolist()[0]
			lon_storm = lon[i:i + 1].tolist()[0]
			time_storm = time[i:i + 1].tolist()[0]
			cat_storm = categ[i:i + 1].tolist()[0]
			msw_storm = msw[i:i + 1].tolist()[0]
			wave_storm = wave[i:i + 1].tolist()[0]
			gust_storm = gust[i:i + 1].tolist()[0]
			mcp_storm = mcp[i:i + 1].tolist()[0]
			region_storm = region[i:i + 1].tolist()[0]
			sid_storm = sid[i:i + 1].tolist()[0]
			iso_time_storm = iso_time[i:i + 1].tolist()[0]
		except:
			error_count += 1
			print("Read failed, storm # " + format(i))
			continue

		sid_list = sid_storm
		sid_num = b''.join(sid_list).decode('utf-8')

		# iso_t = b"".join(iso_time_storm[0]).decode("utf-8")
		# if iso_t != None:
		# 	# get distance between the two points
		# 	distance = GetDistanceBetweenPoints(platform.id, iso_t, sid_num)

		# if sid_num == '1997198N27267':
		# 	print('woah!')
		
		# for each storm loop through all observations
		# for lat_s, lon_s, time_s, msw_s in zip(lat_storm,lon_storm,time_storm,msw_storm):
		for t in range(0, len(time_storm)):

			if region_storm[t][0] is not None:

				r_list = region_storm[t]
				r_reg = b''.join(r_list)

				# if (r_reg == b'GM') or (r_reg == b'NA'):

				# turn time_v into datetime object
				try:
					iso_t = b"".join(iso_time_storm[t]).decode("utf-8")
					timeObs = readStormDateTime_ISO(iso_t)
				# timeObs_next = readStormDateTime(time_storm[t+1])
				except TypeError:
					#print(TypeError)
					# occurs when the time variable is missing
					continue
				# keep track of the year for processing stats per year
				if year is None:
					year = timeObs.year

				# if the year has changed, update the PlatformRecord with
				# the yearly stats and start new YearlyRecord
				if timeObs.year != year:
					# update platform yearly stats with YearRecord
					platform.UpdateYearlyStats(YearStats)
					# reset YearRecord
					YearStats = YearlyRecord()
					# reset year
					year = timeObs.year

				# if there is no platform install date, skip it because we cannot accurately know how long
				# the platform has been in service
				if platform.install_date is None:
					continue

				if (platform.remove_date is None) and (timeObs >= platform.install_date):
					# check whether or not the platform is affected by the storm and by what category
					categ_hit = checkHurricaneEffect(platform, lon_storm[t], lat_storm[t], cat_storm[t], msw_storm[t], wave_storm[t], gust_storm[t], lon_min, lat_min, mcp_storm[t], sid_num, iso_t, platform_coords_list, storm_coords_list)
					# if the platform was "hit" by the hurricane, update the yearly stats
					if categ_hit is not None:
						YearStats.AddHit(categ_hit)

					continue

				# check if the time is between the platform install and removal date or no removal date
				if (timeObs >= platform.install_date) and (timeObs <= platform.remove_date):
					# check whether or not the platform is affected by the storm and by what category
					categ_hit = checkHurricaneEffect(platform, lon_storm[t], lat_storm[t], cat_storm[t], msw_storm[t], wave_storm[t], gust_storm[t], lon_min, lat_min, mcp_storm[t], sid_num, iso_t, platform_coords_list, storm_coords_list)
					# if the platform was "hit" by the hurricane, update the yearly stats
					if categ_hit is not None:
						YearStats.AddHit(categ_hit)

	# update platform yearly stats with YearRecord
	platform.UpdateYearlyStats(YearStats)

	# finish platform by running std and percentile stats
	platform.FinishPlatform()
				
	print(format(error_count) + ' number of storms failed to read')
	
def GetNC_Min(ncDir, var_name):
	ncFiles = iglob(ncDir)
	min = None
	for nc in ncFiles:
		ds = netCDF4.Dataset(nc)
		var_min = ds.variables[var_name][:].min()
		if min == None:
			min = var_min
		if var_min < min:
			min = var_min
			
	return min

def runStatsForStorms(platforms, ncDir, start_date, stop_date, platform_coords_list, storm_coords_list):
	
	# get minimum values for all latitude and longitudes in the net CDFs
	lat_min = GetNC_Min(ncDir, 'usa_lat')
	lon_min = GetNC_Min(ncDir, 'usa_lon')
	
	ncFiles = iglob(ncDir)
	
	for nc in ncFiles:

		print('Processing: ' + format(nc))
		
		start = time.time()
		
		# open netCDF
		ds = netCDF4.Dataset(nc, 'r')
		
		# grab variables for current index
		c_lat = ds.variables['usa_lat']
		c_lon = ds.variables['usa_lon']
		c_time = ds.variables['time']
		c_time_iso = ds.variables['iso_time']
		c_cat = ds.variables['usa_sshs']
		c_msw = ds.variables['usa_wind']
		c_wave = ds.variables['usa_seahgt']
		c_gust = ds.variables['usa_gust']
		c_mcp = ds.variables['usa_pres']
		c_region = ds.variables['subbasin']
		c_sid = ds.variables['sid']
		
		# note number of storms in netCDF
		dsLen = len(ds.dimensions['storm'])
		# keeping track of platform records
		n = 1
		plat_length = len(platforms)
		# loop over each platform record
		for p in platforms:

			asd = p.lat

			if p.lat == asd:
			
				print('Completing ' + format(n) + ' out of ' + format(plat_length) + ' platform records')
				# print('Platform Record: ' + format(n))
				# calculate the x and y coordinates for the platform
				p.x, p.y = sph2xy(p.lon, lon_min, p.lat, lat_min)
				processStats(p, dsLen, c_lat, c_lon, c_time, c_cat, c_msw, c_wave, c_gust, lon_min, lat_min, c_mcp, c_region, c_sid, c_time_iso, platform_coords_list, storm_coords_list)
				n += 1
			
		end = time.time()
		print(end - start)
			
def writeResultsToCSV(platforms, outpath):
	
	with open(outpath, 'w', newline='') as outfile:

		wtr = csv.writer(outfile)
		# write header
		hdr = ['PlatformID', 'Total Storm Hit Count', 'Total Storms', 'Tropical Sum','Tropical Min Yearly','Tropical Max Yearly','Tropical Mean Yearly',\
			   'Tropical Days Sum','Tropical Days Min Yearly','Tropical Days Max Yearly', 'Tropical Days Mean Yearly',\
			   'C1 Sum','C1 Min Yearly','C1 Max Yearly','C1 Mean Yearly','C1 Days Sum','C1 Days Min Yearly','C1 Days Max Yearly','C1 Days Mean Yearly',\
			   'C2 Sum','C2 Min Yearly','C2 Max Yearly','C2 Mean Yearly','C2 Days Sum','C2 Days Min Yearly','C2 Days Max Yearly','C2 Days Mean Yearly',\
			   'C3 Sum','C3 Min Yearly','C3 Max Yearly','C3 Mean Yearly','C3 Days Sum','C3 Days Min Yearly','C3 Days Max Yearly','C3 Days Mean Yearly',\
			   'C4 Sum','C4 Min Yearly','C4 Max Yearly','C4 Mean Yearly','C4 Days Sum','C4 Days Min Yearly','C4 Days Max Yearly','C4 Days Mean Yearly',\
			   'C5 Sum','C5 Min Yearly','C5 Max Yearly','C5 Mean Yearly','C5 Days Sum','C5 Days Min Yearly','C5 Days Max Yearly','C5 Days Mean Yearly',\
			   'Wave Height Count', 'Wave Height None Count', 'Wave Height Sum', 'Wave Height Min', 'Wave Height Max', 'Wave Height Average',\
			   'MSWS Count', 'MSWS None Count', 'MSWS Min', 'MSWS Max', 'MSWS Average',\
			   'MSWS StdDev', 'MSWS P25', 'MSWS Median', 'MSWS P75', 'MSWS P90',\
			   'MRWG Count', 'MRWG None Count', 'MRWG Min', 'MRWG Max', 'MRWG Average', \
			   'MRWG StdDev', 'MRWG P25', 'MRWG Median', 'MRWG P75', 'MRWG P90',\
			   'MCP Count', 'MCP None Count', 'MCP Min', 'MCP Max', 'MCP Average',\
			   'MCP StdDev', 'MCP P25', 'MCP Median', 'MCP P75', 'MCP P90'
			   ]
		wtr.writerow(hdr)

		sPlats = sorted(platforms, key=lambda x: x.id)
		for p in sPlats:
			row = [p.id] + [p.totalHitCount] + [p.stormTotal] + \
				  [p.tropical] + [p.tropical_min] + [p.tropical_max] + [p.tropical_mean] + \
				  [p.tropical_days] + [p.tropical_days_min] + [p.tropical_days_max] + [p.tropical_days_mean] + \
				  [p.C1] + [p.C1_min] + [p.C1_max] + [p.C1_mean] + \
				  [p.C1_days] + [p.C1_days_min] + [p.C1_days_max] + [p.C1_days_mean] + \
				  [p.C2] + [p.C2_min] + [p.C2_max] + [p.C2_mean] + \
				  [p.C2_days] + [p.C2_days_min] + [p.C2_days_max] + [p.C2_days_mean] + \
				  [p.C3] + [p.C3_min] + [p.C3_max] + [p.C3_mean] + \
				  [p.C3_days] + [p.C3_days_min] + [p.C3_days_max] + [p.C3_days_mean] + \
				  [p.C4] + [p.C4_min] + [p.C4_max] + [p.C4_mean] + \
				  [p.C4_days] + [p.C4_days_min] + [p.C4_days_max] + [p.C4_days_mean] + \
				  [p.C5] + [p.C5_min] + [p.C5_max] + [p.C5_mean] + \
				  [p.C5_days] + [p.C5_days_min] + [p.C5_days_max] + [p.C5_days_mean] + \
				  [p.waveHeightCount] + [p.waveHeightNoneCount] + [p.waveHeightSum] + [p.waveHeightMin] + [p.waveHeightMax] + [p.waveHeightAverage] + \
				  [p.windCount] + [p.windNoneCount] + [p.windMin] + [p.windMax] + [p.windAverage] + \
				  [p.windStdDev] + [p.windP25] + [p.windMedian] + [p.windP75] + [p.windP90] + \
				  [p.gustCount] + [p.gustNoneCount] + [p.gustMin] + [p.gustMax] + [p.gustAverage] + \
				  [p.gustStdDev] + [p.gustP25] + [p.gustMedian] + [p.gustP75] + [p.gustP90] + \
				  [p.MCPCount] + [p.MCPNoneCount] + [p.MCPMin] + [p.MCPMax] + [p.MCPAverage] + \
				  [p.MCPStdDev] + [p.MCPP25] + [p.MCPMedian] + [p.MCPP75] + [p.MCPP90]

			wtr.writerow(row)

if __name__ == "__main__":
	
	nc_dir = r'P:\01_DataOriginals\GOM\Metocean\StormData\1842-2021'
	platform_csv = r"C:\Users\dyera\Documents\Offshore Task 3\MEtocean\all_platforms_ver5_A.csv"
	output_path = r"C:\Users\dyera\Documents\Offshore Task 3\MEtocean\hurricane_output_AllPlatforms_Ver5_A_completed_REDO_3.csv"
	platform_points = r'C:\Users\dyera\Documents\Offshore Task 3\GradientBoostingRegressor\1.DATA\Shapefiles\all_platforms_subset_GomAlbers.shp'
	#platform_points_name = 'All_Platforms_GomAlbers'
	storm_points = r'C:\Users\dyera\Documents\Offshore Task 3\GradientBoostingRegressor\1.DATA\Shapefiles\hurricane_points_GomAlbers.shp'
	#storm_points_name = 'IBTRACS_NA_Points_GomAlbers'
	
	prsr = ArgumentParser(description="Generate Stats per platform")
	prsr.add_argument('platform_csv', type=str,
					  help='csv with platform data')
	prsr.add_argument('nc_dir', type=str, help='path to directory containing netcdf data')
	prsr.add_argument('outputs', type=str, help='path to output data')
	prsr.add_argument('--start_date', type=readPlatDateTime, default=FIRST_DATE, help='Start of querying period')
	prsr.add_argument('--stop_date', type=readPlatDateTime, default=LAST_DATE, help='End of querying period')
	prsr.add_argument('--stats', '-s', nargs='+', help='statistics to run')

	args = prsr.parse_args([platform_csv, nc_dir, output_path])

	if args.start_date >= args.stop_date:
		raise Exception('start_date must proceed stop_date')

	# open platform and storm points and get IDs and coordinates as a list
	platform_coords_list = GetPlatformCoords(platform_points)
	storm_coords_list = GetStormCoords(storm_points)

	# load the platforms csv
	platforms = loadPlatformCsv(args.platform_csv)

	runStatsForStorms(platforms, os.path.join(args.nc_dir, '*.nc'), args.start_date, args.stop_date, platform_coords_list, storm_coords_list)
	
	writeResultsToCSV(platforms, output_path)