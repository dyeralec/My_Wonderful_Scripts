"""
Simple script to plot mean values of a netCDF using matplotlib.

https://www.afahadabdullah.com/blog/plotting-climate-data-in-python-matplotlib
"""

from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

nc_file = r"P:\01_DataOriginals\GOM\Metocean\NewMetoceanData_11_26_19\Surface Current Velocity\hycom_uv_2018_3hr.nc"
nc = Dataset(nc_file, mode='r')

lat = nc.variables['Latitude'][:]
lon = nc.variables['Longitude'][:]
time = nc.variables['MT'][:]
u = nc.variables['u'][:]
nc.close()

big_array=[]
for i in u:
	big_array.append(i)
	big_array=np.array(big_array)
	Mean=np.mean(big_array, axis=0)

#plot output summary stats
map = Basemap(projection='merc',llcrnrlat=-40,urcrnrlat=-33,llcrnrlon=139.0,urcrnrlon=151.0,lat_ts=0,resolution='i')
map.drawcoastlines()
map.drawstates()
x,y=map(*np.meshgrid(lon,lat))
plt.title('Total Mean at 3pm')
ticks=[-5,0,5,10,15,20,25,30,35,40,45,50]
CS = map.contourf(x,y,Mean,ticks, cmap=plt.cm.jet)
l,b,w,h =0.1,0.1,0.8,0.8
cax = plt.axes([l+w+0.025, b, 0.025, h])
plt.colorbar(CS,cax=cax, drawedges=True)
plt.show()