"""
This script will take a set of rasters (assumed all overlapping and equal sized) and convert
to a multi point shapefile with the raster values set as attributes in the shapefile

created by Alec Dyer
"""

import os
from osgeo import ogr, osr, gdal
import csv
import numpy as np
import sys
import pandas as pd
from math import isnan

from MyFunctions import getRasterValuesAtPoints, CreateShapefile_Memory, RasterToPoints, SpatialFilter_Remove, ExtractValueByLocation

def GetRasterCenterCoordinates(tif_path):
    import rasterio
    import numpy as np
    from affine import Affine
    from pyproj import Proj, transform
    from pyproj.transformer import Transformer

    # Read raster
    with rasterio.open(tif_path) as r:
        T0 = r.transform  # upper-left pixel corner affine transform
        p1 = Proj(r.crs)
        A = r.read()  # pixel values

    # All rows and columns
    cols, rows = np.meshgrid(np.arange(A.shape[2]), np.arange(A.shape[1]))

    # Get affine transform for pixel centres
    T1 = T0 * Affine.translation(0.5, 0.5)
    # Function to convert pixel row/column index (from 0) to easting/northing at centre
    rc2en = lambda r, c: (c, r) * T1

    # All eastings and northings (there is probably a faster way to do this)
    eastings, northings = np.vectorize(rc2en, otypes=[np.float, np.float])(rows, cols)

    # Project all longitudes, latitudes
    p2 = Proj(proj='latlong', datum='WGS84')
    lats, longs = transform(p1, p2, eastings, northings)

    return longs, lats

# input raster layers
# inputLayers = {
#     "Aspect": r'C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\ML Testing\SMART Tool Ready\Input Data\GEBCO_2020_Aspect_SNAP.tif',
#     # "Basins": r'C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\ML Testing\SMART Tool Ready\Input Data\basins_mask_SNAP.tif',
#     # "Canyons": r'C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\ML Testing\SMART Tool Ready\Input Data\canyons_mask_SNAP.tif',
#     # "Channels": r'C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\ML Testing\SMART Tool Ready\Input Data\channels_mask.tif',
#     # "Curvature": r'C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\ML Testing\SMART Tool Ready\Input Data\GEBCO_2020_Curvature_SNAP.tif',
#     # "Escarpments": r'C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\ML Testing\SMART Tool Ready\Input Data\escarpments_mask_SNAP.tif',
#     # "Faults": r'C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\ML Testing\SMART Tool Ready\Input Data\DistanceToFaults.tif',
#     # "Gas": r'C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\ML Testing\SMART Tool Ready\Input Data\DistanceToGas.tif',
#     # "Hydrates": r'C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\ML Testing\SMART Tool Ready\Input Data\DistanceToHydrates.tif',
#     # "Mud Volcanoes": r'C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\ML Testing\SMART Tool Ready\Input Data\DistanceToMudVolcanoes.tif',
#     # "Pockmarks": r'C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\ML Testing\SMART Tool Ready\Input Data\DistanceToPockmarks.tif',
#     # "Rugosity": r'C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\ML Testing\SMART Tool Ready\Input Data\GEBCO_2020_Rugosity.tif',
#     # "Salt Diapirs": r'C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\ML Testing\SMART Tool Ready\Input Data\DistanceToSaltDiapirs.tif',
#     # "Sediment Type": r'C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\ML Testing\SMART Tool Ready\Input Data\sediment_type_SNAP.tif',
#     # "Seeps": r'C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\ML Testing\SMART Tool Ready\Input Data\DistanceToSeepsPolyplumes.tif',
#     # "Slope": r'C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\ML Testing\SMART Tool Ready\Input Data\GEBCO_2020_Slope_SNAP.tif',
#     # "Sediment Accumulation": r'C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\ML Testing\SMART Tool Ready\Input Data\SedimentAccumulation_SNAP.tif',
#     # "Sediment Thickness": r"C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\ML Testing\SMART Tool Ready\Input Data\SedimentThickness_500m_GomAlbers.tif",
# }

master_name = 'obs_usgs_walsh_dod_m'
master_path = r"C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\NRL MRDF Analysis\Resampling\Observations\obs_usgs_walsh_dod_m_Resampled_0.5.tif"

inputLayers = {
    'obs_usgs_walsh_dod_m': r"C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\NRL MRDF Analysis\Resampling\Observations\obs_usgs_walsh_dod_m_Resampled_0.5.tif"
}

input_dir = r"C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\NRL MRDF Analysis\Resampling\Predictors"
output_path = r"C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\NRL MRDF Analysis\Points Shapefile\obe_usgs_walsh_dod_predictors_resampled_0.5.shp"

countries = r"C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\Data Prep\Shapefiles\Country_Boundaries_GomAlbers_GOM_Dissolve.shp"

for subdir, dirs, files in os.walk(input_dir):
    for file in files:
        if file.endswith('.tif'):
            inputLayers[file.replace('.tif', '')] = os.path.join(input_dir, file)

# get array of rasters
rasterData = {}
for r in inputLayers:
    path = inputLayers[r]
    print(path)
    r_ds = gdal.Open(path)
    arr = r_ds.ReadAsArray()
    rasterData[r] = arr
    if r == 'Aspect':
        proj = r_ds.GetProjectionRef()
        geotransform = r_ds.GetGeoTransform()

# create schema for output layer
schema = []
for r in rasterData:
    arr = rasterData[r]
    t = arr.dtype
    if (t == 'float32') or (t == 'float64'):
        schema.append([r, ogr.OFTReal])
    elif (t == 'int8') or (t == 'int16') or (t == 'uint8'):
        schema.append([r, ogr.OFTInteger])
    else:
        print('Unknown dtype for {}: {}'.format(os.path.basename(inputLayers[r]), t))

# open countires to get srs
srs = osr.SpatialReference()
srs.ImportFromEPSG(4326)

# create output layer from raster
# memDs, coords = RasterToPoints(inputLayers['obs_usgs_walsh_dod_m'], srs=GomAlbers, schema=schema)
# memLyr = memDs.GetLayer()

# ds = gdal.Open(master_path)
# band = ds.GetRasterBand(1)
#
# (upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size) = ds.GetGeoTransform()
#
# data = band.ReadAsArray()
#
# lats = []
# lons = []
# for i in range(0, data.shape[0]):
#     for j in range(0, data.shape[1]):
#         #         print(i, j)
#         x_dist_i = upper_left_x + (x_size * i)
#         #         print(x_dist_i)
#         y_dist_j = upper_left_y + (y_size * j)
#         #         print(y_dist_j)
#         lons.append(x_dist_i)
#         lats.append(y_dist_j)

lons, lats = GetRasterCenterCoordinates(master_path)
lons = lons.flatten()
lats = lats.flatten()

# start logging for data frame later
vals = [lons, lats]
field_names = ['Longitude', 'Latitude']

# create point shapefile
memLyr_ds = CreateShapefile_Memory('MemPoints', srs, ogr.wkbPoint, schema=schema)

memLyr = memLyr_ds.GetLayer()
memLyr_Defn = memLyr.GetLayerDefn()

# get rest of values from the input rasters
for r in inputLayers:
    print('Extracting values for {}'.format(r))
    r_arr = gdal.Open(inputLayers[r]).ReadAsArray()
    vals.append(r_arr.flatten())
    field_names.append(r)
    t = r_arr.dtype
    if (t == 'float32') or (t == 'float64'):
        const =  ogr.OFTReal
    elif (t == 'int8') or (t == 'int16') or (t == 'uint8'):
        const = ogr.OFTInteger
    else:
        print('Unknown dtype for {}: {}'.format(os.path.basename(inputLayers[r]), t))
    coord_fld = ogr.FieldDefn(r, const)
    #coord_fld.SetWidth(8)
    #coord_fld.SetPrecision(3)
    memLyr.CreateField(coord_fld)

vals = np.transpose(vals)

df = pd.DataFrame(vals, columns=field_names)

coord_fld = ogr.FieldDefn('Longitude', ogr.OFTReal)
#coord_fld.SetWidth(11)
#coord_fld.SetPrecision(3)
memLyr.CreateField(coord_fld)
coord_fld.SetName('Latitude')
memLyr.CreateField(coord_fld)

print(len(lats))

# loop through coordinates and create points based off of them
for i in range(len(lats)):
    check = False
    # print(i)
    #print(lons[i], lats[i])
    outFeat = ogr.Feature(memLyr_Defn)
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(lons[i], lats[i])
    outFeat.SetGeometry(point)
    #outFeat.SetField('Longitude', lons[i])
    #outFeat.SetField('Latitude', lats[i])
    for f in df:
        v = df[f][i]
        if isnan(v):
            check = True
        # print(v)
        outFeat.SetField(f, v)
    if check == False:
        memLyr.CreateFeature(outFeat)
    del outFeat

# spatial filter to remove points inside of spatial layer
#memDs = SpatialFilter_Remove(memDs, countries, keep_within=False)

# extract raster values to the points
# for r in inputLayers:
#     print('Extracting values for {}'.format(r))
#     r_ds = gdal.Open(inputLayers[r])
#     for c in coords:
#         print(c)
#         val = ExtractValueByLocation(r_ds, c[0], c[1])
#         # select point based on lat and lon
#         query = '(Longitude = {}) AND (Latitude = {})'.format(c[0], c[1])
#         # add value to points shapefile
#         memLyr.SetAttributeFilter(query)
#         print('filter complete')
#         # check feature count
#         if memLyr.GetFeatureCount() > 1:
#             print('Too many points selected with attribute filter: {}'.format(query))
#         # get feature
#         feat = memLyr.GetNextFeature()
#         # now set the field for that feature
#         feat.SetField(r, val[0])
#         print('field set!')

# save output
driver = ogr.GetDriverByName('ESRI Shapefile')
out_ds = driver.CreateDataSource(output_path)
out_ds.CopyLayer(memLyr, 'obe_usgs_walsh_dod_predictors')
del out_ds, memLyr_ds