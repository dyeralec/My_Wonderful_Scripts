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

Developed by: Alec Dyer
alec.dyer@netl.doe.gov
(541) 918-4475
"""

import netCDF4
import csv
from datetime import datetime
from datetime import timedelta
import numpy as np
from argparse import ArgumentParser
from glob import iglob
import os
import scipy
import time

D_FORMAT = '%m/%d/%Y'
DT_FORMAT = D_FORMAT + '_H:%H'

FIRST_DATE = datetime(1972,1,1)
LAST_DATE = datetime(2017,12,31)

FLD_NAME = 'Storms'

# year = None

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
		self.stormTotal = 0
		self.none_count = 0
		self.tropical = 0
		self.tropical_days = 0
		self.C1 = 0
		self.C1_days = 0
		self.C2 = 0
		self.C2_days = 0
		self.C3 = 0
		self.C3_days = 0
		self.C4 = 0
		self.C4_days = 0
		self.C5 = 0
		self.C5_days = 0
		self.hitCheck = False
		
	def addValue(self, cat):
		if cat is None:
			self.none_count+=1
			return
		if cat == 'tropical':
			if self.hitCheck is False:
				self.tropical += 1
				self.hitCheck = True
			self.tropical_days += 0.24
		if cat == 'C1':
			if self.hitCheck is False:
				self.C1 += 1
				self.hitCheck = True
			self.C1_days += 0.24
		if cat == 'C2':
			if self.hitCheck is False:
				self.C2 += 1
				self.hitCheck = True
			self.C2_days += 0.24
		if cat == 'C3':
			if self.hitCheck is False:
				self.C3 += 1
				self.hitCheck = True
			self.C3_days += 0.24
		if cat == 'C4':
			if self.hitCheck is False:
				self.C4 += 1
				self.hitCheck = True
			self.C4_days += 0.24
		if cat == 'C5':
			if self.hitCheck is False:
				self.C5 += 1
				self.hitCheck = True
			self.C5_days += 0.24
			
		self.stormTotal += 1
			
class StatRecord(object):
	
	def __init__(self, varName, start, end):
		self.varName = varName
		self.sample_date_start = start
		self.sample_date_end = end
		self.sample_count = 0
		self.numStorms = 0
		self.tropical = 0
		self.C1 = 0
		self.C2 = 0
		self.C3 = 0
		self.C4 = 0
		self.C5 = 0
		self.nan_count = 0

	def addValue(self, v, cat):
		if np.isnan(v):
			self.nan_count+=1
			return

		cat += 1

		self.numStorms += v

# class PlatformStats(PlatformRecord):
#
# 	def __init__(self, *args, **kwargs):
# 		super().__init__(*args, **kwargs)
#
# 		self.stats = {}


def readStormDateTime(instr):
	start_date = datetime.strptime('11/17/1858', D_FORMAT)
	delta = timedelta(days=instr)
	new_date = start_date + delta

	return new_date

def readPlatDateTime(instr):
	return datetime.strptime(instr, D_FORMAT)

# def loadNCFile(datadir, year, varName):
# 	inpath = datadir + NC_YEAR_FORMAT.format(year=year)
# 	ds = netCDF4.Dataset(inpath)
#
# 	print(f'Loading {inpath} for year {year}.')
#
# 	return ds, ds.variables[varName], ds.variables['Times']

def loadPlatformCsv(path, cls=PlatformRecord):
	with open(path, 'r') as inFile:
		dRdr = csv.DictReader(inFile)

		ret = []
		for row in dRdr:
			ret.append(cls(**row))

		return ret
	
def findNCDTInd(target, nc):

	ds = netCDF4.Dataset(nc)

	time_var = ds.variables['time_wmo']
	try:
		ind = netCDF4.date2index(target,time_var)
	except ValueError:
		return None, None
	else:
		return ds,ind
	
def checkHurricaneEffect(platform, storm_lon, storm_lat, wind_speed, lon_min, lat_min):
	# determine radius (m) of the storm by the wind speed
	category = None
	radius = None
	if int(wind_speed) in range(34,64):
		radius = 100000
		category = 'tropical'
	if int(wind_speed) in range(64,83):
		radius = 300000
		category = 'C1'
	if int(wind_speed) in range(83,96):
		radius = 300000
		category = 'C2'
	if int(wind_speed) in range(96,113):
		radius = 450000
		category = 'C3'
	if int(wind_speed) in range(113,137):
		radius = 450000
		category = 'C4'
	if int(wind_speed) >= 137:
		radius = 450000
		category = 'C5'
	
	if radius is not None:
		# convert lat and long coordinates (degrees) into x and y (meters)
		storm_x, storm_y = sph2xy(storm_lon, lon_min, storm_lat, lat_min)
		# use squared distance function to determine if the platform lies within the hurricane buffer
		distance_squared = (((platform.x - storm_x)**2) + ((platform.y - storm_y)**2))
		if distance_squared <= ((radius)**2):
			# print('HIT!')
			# update platform record with stat
			platform.addValue(category)
		
def sph2xy(lon, lon_origin, lat, lat_origin):
	R = 6371 * 1e3
	dg2rad = scipy.pi / 180
	x = (R)*(lon-lon_origin)*(dg2rad)*(scipy.cos((lat_origin*dg2rad)))
	y = (R)*(lat - lat_origin)*(dg2rad)
	
	return x,y
	
def processStats(platform, numStorms, lat, lon, time, msw, lon_min, lat_min):
	# loop through each storm
	for i in range(0,numStorms):
		# make sure storm hitCheck is False to begin each storm
		platform.hitCheck = False
		# grab variables for that one storm
		lat_storm = lat[i:i+1].tolist()[0]
		lon_storm = lon[i:i+1].tolist()[0]
		time_storm = time[i:i+1].tolist()[0]
		msw_storm = msw[i:i+1].tolist()[0]
		# for each storm loop through all observations
		# for lat_s, lon_s, time_s, msw_s in zip(lat_storm,lon_storm,time_storm,msw_storm):
		for t in range(0,len(time_storm)):
			
			# turn time_v into datetime object
			try:
				timeObs = readStormDateTime(time_storm[t])
				#timeObs_next = readStormDateTime(time_storm[t+1])
			except TypeError:
				# occurs when the time variable is missing
				continue
			# if there is no platform install date, skip it because we cannot accurately know how long
			# the platform has been in service
			if platform.install_date is None:
				continue
				
			if (platform.remove_date is None) and (timeObs >= platform.install_date):
				# check whether or not the platform is affected by the storm and by what category
				checkHurricaneEffect(platform, lon_storm[t], lat_storm[t], msw_storm[t], lon_min, lat_min)
				continue
				
			# check if the time is between the platform install and removal date or no removal date
			if (timeObs >= platform.install_date) and (timeObs <= platform.remove_date):
			
				# check whether or not the platform is affected by the storm and by what category
				checkHurricaneEffect(platform, lon_storm[t], lat_storm[t], msw_storm[t], lon_min, lat_min)
			
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

def runStatsForStorms(platforms, ncDir, start_date, stop_date):
	
	# get minimum values for all latitude and longitudes in the net CDFs
	lat_min = GetNC_Min(ncDir, 'lat_wmo')
	lon_min = GetNC_Min(ncDir, 'lon_wmo')
	
	ncFiles = iglob(ncDir)
	
	for nc in ncFiles:

		print('Processing: ' + format(nc))
		
		start = time.time()
		
		# open netCDF
		ds = netCDF4.Dataset(nc, 'r')
		
		# grab variables for current index
		c_lat = ds.variables['lat_wmo']
		c_lon = ds.variables['lon_wmo']
		c_time = ds.variables['time_wmo']
		c_msw = ds.variables['wind_wmo']
		
		# note number of storms in netCDF
		dsLen = len(ds.dimensions['storm'])
		# keeping track of platform records
		n = 1
		# loop over each platform record
		for p in platforms:
			# print('Platform Record: ' + format(n))
			# calculate the x and y coordinates for the platform
			p.x, p.y = sph2xy(p.lon, lon_min, p.lat, lat_min)
			processStats(p, dsLen, c_lat, c_lon, c_time, c_msw, lon_min, lat_min)
			n += 1
			
		end = time.time()
		print(end - start)
			
def writeResultsToCSV(platforms, outpath):
	
	with open(outpath, 'w', newline='') as outfile:

		wtr = csv.writer(outfile)
		# write header
		hdr = ['PlatformID', 'Total Storms', 'None Count', 'Tropical', 'Tropical Days', 'C1', 'C1 Days', 'C2', 'C2 Days',\
			   'C3', 'C3 Days', 'C4', 'C4 Days', 'C5', 'C5 Days']
		wtr.writerow(hdr)

		sPlats = sorted(platforms, key=lambda x: x.id)
		for p in sPlats:
			row = [p.id] + [p.stormTotal] + [p.none_count] + [p.tropical] + [p.tropical_days] + [p.C1] + [p.C1_days]\
				  + [p.C2] + [p.C2_days] + [p.C3] + [p.C3_days] + [p.C4] + [p.C4_days] + [p.C5] + [p.C5_days]
			wtr.writerow(row)

if __name__ == "__main__":
	
	nc_dir = r'P:\01_DataOriginals\GOM\Metocean\StormData\1972_2017'
	platform_csv = r"P:\05_AnalysisProjects_Working\Offshore Infrastructure and Incidents REORG\02_DataWorking\Platforms\PlatformIDs_forPatrick_ML.csv"
	output_path = r'P:/01_DataOriginals/GOM/Metocean/StormData/hurricane_output_AllPlatforms.csv'
	
	prsr = ArgumentParser(description="Generate Stats per platform")
	prsr.add_argument('platform_csv', type=str,
					  help='csv with platform data, and mapped to spatial with "classify_nodes_HYCOM.py"')
	prsr.add_argument('nc_dir', type=str, help='path to directory containing netcdf data')
	prsr.add_argument('outputs', type=str, help='path to output data')
	prsr.add_argument('--start_date', type=readPlatDateTime, default=FIRST_DATE, help='Start of querying period')
	prsr.add_argument('--stop_date', type=readPlatDateTime, default=LAST_DATE, help='End of querying period')
	prsr.add_argument('--stats', '-s', nargs='+', help='statistics to run')

	args = prsr.parse_args([platform_csv, nc_dir, output_path])

	if args.start_date >= args.stop_date:
		raise Exception('start_date must preceed stop_date')

	# load the platforms csv
	platforms = loadPlatformCsv(args.platform_csv)

	runStatsForStorms(platforms, os.path.join(args.nc_dir, '*.nc'), args.start_date, args.stop_date)
	
	writeResultsToCSV(platforms, output_path)