"""
This script will take in a set of net CDFs and using a time variable calculate statistics on the temporal range.
"""

import netCDF4
from glob import iglob
from datetime import datetime
from datetime import timedelta
import os
import matplotlib.pyplot as plt
import numpy as np
from statistics import mean, median

D_FORMAT = '%m/%d/%Y'

class StatRecord(object):
	
	def __init__(self):
		
		self.minTimeDelta = None
		self.maxTimeDelta = None
		
def readStormDateTime(instr):
	start_date = datetime.strptime('11/17/1858', D_FORMAT)
	delta = timedelta(days=instr)
	new_date = start_date + delta

	return new_date

def PlotHist(x, n_bins):
	
	plt.hist(np.asarray(x), n_bins)
	
	plt.show()
		
if __name__ == '__main__':
	
	ncDir = r'P:\01_DataOriginals\GOM\Metocean\StormData\storm_test'
	time_var_name = 'time_wmo'
	# iterator of nc paths
	ncFiles = iglob(os.path.join(ncDir, '*.nc'))
	# create stat variables
	Stats = StatRecord()
	# keep track of all deltas for histogram later
	delta_days_list = []
	# loop through all nc in the directory
	for nc in ncFiles:
		# open nc
		ds = netCDF4.Dataset(nc, 'r')
		# grab time variable
		time_var = ds.variables[time_var_name]
		# grab length
		dsLen = ds.dimensions['storm'].size
		# loop through all the dimensions (in this case number of storms)
		for i in range(0,dsLen):
		
			time = time_var[i:i+1].tolist()[0]
			
			l = len(time)
			
			for t in range(0,len(time)):
				print(time[t])
				
				try:
					time_a = readStormDateTime(time[t])
					time_b = readStormDateTime(time[t+1])
					
					delta = time_a - time_b
					
					delta_days = delta.total_seconds() / timedelta(days=1).total_seconds()
					
					delta_days_list.append(delta_days)
					
					if (Stats.minTimeDelta == None) and (Stats.maxTimeDelta == None):
						Stats.minTimeDelta = abs(delta_days)
						Stats.maxTimeDelta = abs(delta_days)
						continue
					
					if abs(delta_days) < Stats.minTimeDelta:
						Stats.minTimeDelta = abs(delta_days)
					if abs(delta_days) > Stats.maxTimeDelta:
						Stats.maxTimeDelta = abs(delta_days)
					
				except IndexError:
					continue
				except TypeError:
					continue
					
	print('\nNetCDF Temporal Resolution Report:')
	print('Min range = ' + format(Stats.minTimeDelta))
	print('Max range = ' + format(Stats.maxTimeDelta))
	print('Average = ' + format(mean(delta_days_list)))
	print('Median = ' + format(median(delta_days_list)))
	
	PlotHist(delta_days_list, n_bins= 50)