import os, subprocess
import rasterio
from rasterio.fill import fillnodata

main_dir = r'C:\Users\dyera\AppData\Local\ESRI\conda\envs\deeplearning\Scripts'
in_raster = r"P:\01_DataOriginals\GOM\Elevation\NOAA NCEI NOS Hydrographic Survey Bathymetry\Single Band Elevation Rasters\H11683_VB_2m_MLLW_2of2.tif"
out_raster = r"P:\01_DataOriginals\GOM\Elevation\NOAA NCEI NOS Hydrographic Survey Bathymetry\Single Band Elevation Rasters\H11683_VB_2m_MLLW_2of2_Filled_50search.tif"

# os.chdir(main_dir)
#
# command = r'python gdal_fillnodata.py {} {}'.format(in_raster, out_raster)
# subprocess.call(command, shell=True)

with rasterio.open(in_raster) as src:
    profile = src.profile
    arr = src.read(1)
    arr_filled = fillnodata(arr, mask=src.read_masks(1), max_search_distance=50, smoothing_iterations=0)

with rasterio.open(out_raster, 'w', **profile) as dest:
    dest.write_band(1, arr_filled)