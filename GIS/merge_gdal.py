"""
https://gdal.org/programs/gdal_merge.html
"""

from osgeo import gdal

files_to_mosaic = [
    r"P:\01_DataOriginals\GOM\Elevation\HR_Bathy_BOEM\BOEM_Bathymetry_East_meters_tiff\BOEMbathyE_m.tif",
    r"P:\01_DataOriginals\GOM\Elevation\HR_Bathy_BOEM\BOEM_Bathymetry_West_meters_tiff\BOEMbathyW_m.tif"
] # However many you want.

output_path = r'C:\Users\dyera\Documents\Task 6\Landslide Detection\Data\GOM\Individual Bands\Elevation_3.tif'

g = gdal.Warp(output_path, files_to_mosaic, format="GTiff",
              options=["COMPRESS=LZW", "TILED=YES"])
g = None # Close file and flush to disk