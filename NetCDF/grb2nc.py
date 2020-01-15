"""

"""

import os

folder = 'at_10m_wind/'

for file in os.listdir(folder):
	if file.endswith('.grb2'):
		os.system("cdo -f nc -copy {} {}".format(os.path.join(folder,file), os.path.join(folder,file.replace('.grb2','.nc'))))