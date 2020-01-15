"""

"""

import os

# years = list(range(2005,2020))
years = [2005]

months = ['01','02','03','04','05','06','07','08','09','10','11','12']

for y in years:
	for m in months:
		
		if (y == 2005) and (m == '01'):
			continue
		
		url = "https://data.nodc.noaa.gov/thredds/dodsC/ncep/nww3/{}/{}/gribs/multi_1.at_10m.wind.{}.grb2".format(str(y),m,str(y) + m)
		
		path = "data.nodc.noaa.gov/thredds/dodsC/ncep/nww3/{}/{}/gribs/multi_1.at_10m.wind.{}.grb2".format(str(y),m,str(y) + m)
		
		file = "at_10m_{}.grb2".format(m+str(y))
		
		print(file)
		
		os.system("ncks -d lon,262.0,282.0 -d lat,18.0,30.8 {} -l {}".format(url,file))
		
		os.system("cdo -f nc copy {} {}".format(file, file.replace('.grb2', '.nc')))