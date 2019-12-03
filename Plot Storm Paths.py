"""

"""
import os
os.environ['PROJ_LIB'] = r"C:\Anaconda3\pkgs\basemap-1.2.0-py37h4e5d7af_0\Lib\site-packages\mpl_toolkits\basemap"
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np

nc_path = r"P:\01_DataOriginals\GOM\Metocean\StormData\Year.2005.ibtracs_wmo.v03r10.nc"

# first open and get all the names of the storms
with Dataset(nc_path,'r') as ds:
	basin = ds.variables['basin']
	lon = ds.variables['lon_wmo']
	lat = ds.variables['lat_wmo']
	wind = ds.variables['wind_wmo']
	dsLen = len(ds.variables['basin'])
		
	# loop through each storm
	for i in range(0,dsLen):
		
		basins = basin[i:i+1].tolist()[0]
		
		if basins[0] == 0:
		
			lon_storm = lon[i:i + 1].tolist()[0]
			lat_storm = lat[i:i + 1].tolist()[0]
			wind_storm = wind[i:i + 1].tolist()[0]
			
			fig, ax = plt.subplots()
			
			# plt.plot(lon_storm, lat_storm, marker = 'o', color = 'r')
			m = Basemap(llcrnrlon=-100.,llcrnrlat=0.,urcrnrlon=-20.,urcrnrlat=57.,\
            	projection='lcc',lat_1=20.,lat_2=40.,lon_0=-60.,\
            	resolution ='l',area_thresh=1000.)
			# draw coastlines and meridians
			m.drawcoastlines()
			m.drawlsmask(land_color='#cc9966', ocean_color='#99ffff', lakes=True)
			m.drawparallels(np.arange(10, 70, 20), labels=[1, 1, 0, 0])
			m.drawmeridians(np.arange(-100, 0, 20), labels=[0, 0, 0, 1])
			
			lon_storm = [i for i in lon_storm if i]
			lat_storm = [i for i in lat_storm if i]
			wind_storm = [i for i in wind_storm if i]
			
			x, y = m(lon_storm, lat_storm)
			
			m.plot(x, y, color='black')
			
			storm_colors = []
			for s in wind_storm:
				if int(s) < 34:
					storm_colors.append('springgreen')
				if int(s) in range(34, 64):
					storm_colors.append('C')
				if int(s) in range(64, 113):
					storm_colors.append('darkorange')
				if int(s) >= 113:
					storm_colors.append('maroon')
			
			plt.scatter(x, y, c=storm_colors, edgecolors='black', label = storm_colors)
			plt.show()