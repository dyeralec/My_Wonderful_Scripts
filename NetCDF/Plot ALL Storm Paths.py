"""
code to take a storm netCDF and plot all of the storms that are in the Gulf of Mexico
for one year, all on one plot.
"""
import os

os.environ['PROJ_LIB'] = r"C:\Anaconda3\pkgs\basemap-1.2.0-py37h4e5d7af_0\Lib\site-packages\mpl_toolkits\basemap"
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np


class Storm(object):
	
	def __init__(self):
		
		self.weak_x = []
		self.weak_y = []
		self.trop_x = []
		self.trop_y = []
		self.c_123_x = []
		self.c_123_y = []
		self.c_45_x = []
		self.c_45_y = []
	
	def addVal(self, x, y, cat):
		if cat == 'weak':
			self.weak_x.append(x)
			self.weak_y.append(y)
		if cat == 'trop':
			self.trop_x.append(x)
			self.trop_y.append(y)
		if cat == '123':
			self.c_123_x.append(x)
			self.c_123_y.append(y)
		if cat == '45':
			self.c_45_x.append(x)
			self.c_45_y.append(y)

nc_path = r"P:\01_DataOriginals\GOM\Metocean\StormData\Year.2005.ibtracs_wmo.v03r10.nc"

m = Basemap(llcrnrlon=-98., llcrnrlat=17., urcrnrlon=-80., urcrnrlat=31., \
			projection='lcc', lat_0=30., lon_0=-90., \
			resolution='l', area_thresh=1000.)
# draw coastlines and meridians
m.drawcoastlines()
m.drawlsmask(land_color='#827d7c', ocean_color='#8dcef9', lakes=True)
m.drawparallels(np.arange(10, 70, 5), labels=[1, 1, 0, 0])
m.drawmeridians(np.arange(-100, 0, 5), labels=[0, 0, 0, 1])

# first open and get all the names of the storms
with Dataset(nc_path, 'r') as ds:
	basin = ds.variables['basin']
	lon = ds.variables['lon_wmo']
	lat = ds.variables['lat_wmo']
	wind = ds.variables['wind_wmo']
	dsLen = len(ds.variables['basin'])
	
	# loop through each storm
	for i in range(0, dsLen):
		
		print('storm ' + format(i))
		
		basins = basin[i:i + 1].tolist()[0]
		
		try:
			
			if basins[0] == 0:
				
				lon_storm = lon[i:i + 1].tolist()[0]
				lat_storm = lat[i:i + 1].tolist()[0]
				wind_storm = wind[i:i + 1].tolist()[0]
				
				# get rid of None values
				lon_storm = [i for i in lon_storm if i]
				lat_storm = [i for i in lat_storm if i]
				wind_storm = [i for i in wind_storm if i]
				
				# convert to projection coordinates
				x, y = m(lon_storm, lat_storm)
				# plot hurricane line track
				m.plot(x, y, color='black')
				
				storm = Storm()
				
				for i in range(0, len(wind_storm)):
					if int(wind_storm[i]) < 34:
						storm.addVal(x[i], y[i], 'weak')
					if int(wind_storm[i]) in range(34, 64):
						storm.addVal(x[i], y[i], 'trop')
					if int(wind_storm[i]) in range(64, 113):
						storm.addVal(x[i], y[i], '123')
					if int(wind_storm[i]) >= 113:
						storm.addVal(x[i], y[i], '45')
				
				# plot storm observation points
				plt.scatter(storm.weak_x, storm.weak_y, c='springgreen', edgecolors='black', label='Weak')
				plt.scatter(storm.trop_x, storm.trop_y, c='C', edgecolors='black', label='Tropical')
				plt.scatter(storm.c_123_x, storm.c_123_y, c='darkorange', edgecolors='black', label='Cat 1-3')
				plt.scatter(storm.c_45_x, storm.c_45_y, c='maroon', edgecolors='black', label='Cat 4-5')
		
		except:
			print('X and Y arrays not the same. Failure to plot storm')

# plt.legend(loc='upper right', frameon = False)
plt.show()
