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

Version 2 is going to use the updated storm data that now includes data from 2018 and 2019, as well as
new variables including the saffir-simpson hurricane category and wave height.

Version 3 is going to add the capability of creating stats for the storm categories

IBTrACS Data Source:

Knapp, K. R., M. C. Kruk, D. H. Levinson, H. J. Diamond, and C. J. Neumann, 2010:
The International Best Track Archive for Climate Stewardship (IBTrACS): Unifying tropical cyclone best track data.
Bulletin of the American Meteorological Society, 91, 363-376. non-gonvernment domain doi:10.1175/2009BAMS2755.1

Knapp, K. R., H. J. Diamond, J. P. Kossin, M. C. Kruk, C. J. Schreck, 2018:
International Best Track Archive for Climate Stewardship (IBTrACS) Project, Version 4. [1942-2019]. NOAA National
Centers for Environmental Information. non-gonvernment domain https://doi.org/10.25921/82ty-9e16 [4/8/2020].

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
from osgeo import ogr, gdal, osr

D_FORMAT = '%m/%d/%Y'
DT_FORMAT = '%m/%d/%Y %H:%M:%S'
DT_ISO_FORMAT = '%Y-%m-%d %H:%M:%S'

FIRST_DATE = datetime(1842, 1, 1)
LAST_DATE = datetime(2021, 1, 27)

FLD_NAME = 'Storms'


# NC_YEAR_FORMAT = f'Year.{year}.ibtracs_wmo.v03r10.nc'

class GridRecord(object):

    def __init__(self, grid, mask):

        self.grid = grid
        self.mask = mask
        # self.lat = float(Lat)
        # self.lon = float(Lon)
        self.x = grid.shape[0]
        self.y = grid.shape[1]
        self.grid_init_zeros = np.zeros((self.x, self.y), dtype=np.float)
        self.grid_init_zeros = np.zeros((self.x, self.y), dtype=np.float)
        self.grid_init_pos = np.full((self.x, self.y), 999999, dtype=np.float)
        self.grid_init_neg = np.full((self.x, self.y), -999999, dtype=np.float)
        self.stormTotal = np.zeros((self.x, self.y), dtype=np.float)
        self.cat_noneCount = np.zeros((self.x, self.y), dtype=np.float)
        self.tropical_hitCheck = False
        self.tropical = np.zeros((self.x, self.y), dtype=np.float)
        self.tropical_min = np.full((self.x, self.y), 999999, dtype=np.float)
        self.tropical_max = np.full((self.x, self.y), -999999, dtype=np.float)
        self.tropical_mean = np.zeros((self.x, self.y), dtype=np.float)
        self.tropical_days = np.zeros((self.x, self.y), dtype=np.float)
        self.tropical_days_min = np.full((self.x, self.y), 999999, dtype=np.float)
        self.tropical_days_max = np.full((self.x, self.y), -999999, dtype=np.float)
        self.tropical_days_mean = np.zeros((self.x, self.y), dtype=np.float)
        self.C1_hitCheck = False
        self.C1 = np.zeros((self.x, self.y), dtype=np.float)
        self.C1_min = np.full((self.x, self.y), 999999, dtype=np.float)
        self.C1_max = np.full((self.x, self.y), -999999, dtype=np.float)
        self.C1_mean = np.zeros((self.x, self.y), dtype=np.float)
        self.C1_days = np.zeros((self.x, self.y), dtype=np.float)
        self.C1_days_min = np.full((self.x, self.y), 999999, dtype=np.float)
        self.C1_days_max = np.full((self.x, self.y), -999999, dtype=np.float)
        self.C1_days_mean = np.zeros((self.x, self.y), dtype=np.float)
        self.C2_hitCheck = False
        self.C2 = np.zeros((self.x, self.y), dtype=np.float)
        self.C2_min = np.full((self.x, self.y), 999999, dtype=np.float)
        self.C2_max = np.full((self.x, self.y), -999999, dtype=np.float)
        self.C2_mean = np.zeros((self.x, self.y), dtype=np.float)
        self.C2_days = np.zeros((self.x, self.y), dtype=np.float)
        self.C2_days_min = np.full((self.x, self.y), 999999, dtype=np.float)
        self.C2_days_max = np.full((self.x, self.y), -999999, dtype=np.float)
        self.C2_days_mean = np.zeros((self.x, self.y), dtype=np.float)
        self.C3_hitCheck = False
        self.C3 = np.zeros((self.x, self.y), dtype=np.float)
        self.C3_min = np.full((self.x, self.y), 999999, dtype=np.float)
        self.C3_max = np.full((self.x, self.y), -999999, dtype=np.float)
        self.C3_mean = np.zeros((self.x, self.y), dtype=np.float)
        self.C3_days = np.zeros((self.x, self.y), dtype=np.float)
        self.C3_days_min = np.full((self.x, self.y), 999999, dtype=np.float)
        self.C3_days_max = np.full((self.x, self.y), -999999, dtype=np.float)
        self.C3_days_mean = np.zeros((self.x, self.y), dtype=np.float)
        self.C4_hitCheck = False
        self.C4 = np.zeros((self.x, self.y), dtype=np.float)
        self.C4_min = np.full((self.x, self.y), 999999, dtype=np.float)
        self.C4_max = np.full((self.x, self.y), -999999, dtype=np.float)
        self.C4_mean = np.zeros((self.x, self.y), dtype=np.float)
        self.C4_days = np.zeros((self.x, self.y), dtype=np.float)
        self.C4_days_min = np.full((self.x, self.y), 999999, dtype=np.float)
        self.C4_days_max = np.full((self.x, self.y), -999999, dtype=np.float)
        self.C4_days_mean = np.zeros((self.x, self.y), dtype=np.float)
        self.C5_hitCheck = False
        self.C5 = np.zeros((self.x, self.y), dtype=np.float)
        self.C5_min = np.full((self.x, self.y), 999999, dtype=np.float)
        self.C5_max = np.full((self.x, self.y), -999999, dtype=np.float)
        self.C5_mean = np.zeros((self.x, self.y), dtype=np.float)
        self.C5_days = np.zeros((self.x, self.y), dtype=np.float)
        self.C5_days_min = np.full((self.x, self.y), 999999, dtype=np.float)
        self.C5_days_max = np.full((self.x, self.y), -999999, dtype=np.float)
        self.C5_days_mean = np.zeros((self.x, self.y), dtype=np.float)
        self.waveHeightCount = np.zeros((self.x, self.y), dtype=np.float)
        self.waveHeightNoneCount = np.zeros((self.x, self.y), dtype=np.float)
        self.waveHeightSum = np.zeros((self.x, self.y), dtype=np.float)
        self.waveHeightAverage = np.zeros((self.x, self.y), dtype=np.float)
        self.waveHeightMax = np.full((self.x, self.y), -999999, dtype=np.float)
        self.waveHeightMin = np.full((self.x, self.y), 999999, dtype=np.float)
        self.windCount = np.zeros((self.x, self.y), dtype=np.float)
        self.windNoneCount = np.zeros((self.x, self.y), dtype=np.float)
        self.windSum = np.zeros((self.x, self.y), dtype=np.float)
        self.windAverage = np.zeros((self.x, self.y), dtype=np.float)
        self.windMax = np.full((self.x, self.y), -999999, dtype=np.float)
        self.windMin = np.full((self.x, self.y), 999999, dtype=np.float)
        self.gustCount = np.zeros((self.x, self.y), dtype=np.float)
        self.gustNoneCount = np.zeros((self.x, self.y), dtype=np.float)
        self.gustSum = np.zeros((self.x, self.y), dtype=np.float)
        self.gustAverage = np.zeros((self.x, self.y), dtype=np.float)
        self.gustMax = np.full((self.x, self.y), -999999, dtype=np.float)
        self.gustMin = np.full((self.x, self.y), 999999, dtype=np.float)
        self.yearCount = np.zeros((self.x, self.y), dtype=np.float)
        self.MCPCount = np.zeros((self.x, self.y), dtype=np.float)
        self.MCPNoneCount = np.zeros((self.x, self.y), dtype=np.float)
        self.MCPSum = np.zeros((self.x, self.y), dtype=np.float)
        self.MCPAverage = np.zeros((self.x, self.y), dtype=np.float)
        self.MCPMax = np.full((self.x, self.y), -999999, dtype=np.float)
        self.MCPMin = np.full((self.x, self.y), 999999, dtype=np.float)

    def addValue(self, cat, indx, wave, wind, gust, mcp):

        self.stormTotal[indx] += 1

        if wave is not None:
            self.waveHeightCount[indx] += 1
            self.waveHeightSum[indx] += wave
            self.waveHeightAverage[indx] = (self.waveHeightSum[indx] / self.waveHeightCount[indx])
            if (wave > self.waveHeightMax[indx].any()) or (wave < self.waveHeightMin[indx].any()):
                for xi, yi in np.array(indx).T.tolist():
                    if self.waveHeightMax[xi, yi] < wave:
                        self.waveHeightMax[xi, yi] = wave
                    if self.waveHeightMin[xi, yi] > wave:
                        self.waveHeightMin[xi, yi] = wave
        if wave is None:
            self.waveHeightNoneCount[indx] += 1

        if wind is not None:
            self.windCount[indx] += 1
            self.windSum[indx] += wind
            self.windAverage[indx] = (self.windSum[indx] / self.windCount[indx])
            if (wind > self.windMax[indx].any()) or (wind < self.windMin[indx].any()):
                for xi, yi in np.array(indx).T.tolist():
                    if self.windMax[xi, yi] < wind:
                        self.windMax[xi, yi] = wind
                    if self.windMin[xi, yi] > wind:
                        self.windMin[xi, yi] = wind
        if wind is None:
            self.windNoneCount[indx] += 1

        if gust is not None:
            self.gustCount[indx] += 1
            self.gustSum[indx] += gust
            self.gustAverage[indx] = (self.gustSum[indx] / self.gustCount[indx])
            if (gust > self.gustMax[indx].any()) or (gust < self.gustMin[indx].any()):
                for xi, yi in np.array(indx).T.tolist():
                    if self.gustMax[xi, yi] < gust:
                        self.gustMax[xi, yi] = gust
                    if self.gustMin[xi, yi] > gust:
                        self.gustMax[xi, yi] = gust
        if gust is None:
            self.gustNoneCount[indx] += 1

        if mcp is not None:
            self.MCPCount[indx] += 1
            self.MCPSum[indx] += mcp
            self.MCPAverage[indx] = (self.MCPSum[indx] / self.MCPCount[indx])
            if (mcp > self.MCPMax[indx].any()) or (mcp < self.MCPMin[indx].any()):
                for xi, yi in np.array(indx).T.tolist():
                    if self.MCPMax[xi, yi] < mcp:
                        self.MCPMax[xi, yi] = mcp
                    if self.MCPMin[xi, yi] > mcp:
                        self.MCPMin[xi, yi] = mcp
        if mcp is None:
            self.gustNoneCount[indx] += 1

        if cat is None:
            self.cat_noneCount[indx] += 1
            return
        if cat == 'tropical':
            if self.tropical_hitCheck is False:
                self.tropical[indx] += 1
                self.tropical_hitCheck = True
            self.tropical_days[indx] += 0.24
        if cat == 'C1':
            if self.C1_hitCheck is False:
                self.C1[indx] += 1
                self.C1_hitCheck = True
            self.C1_days[indx] += 0.24
        if cat == 'C2':
            if self.C2_hitCheck is False:
                self.C2[indx] += 1
                self.C2_hitCheck = True
            self.C2_days[indx] += 0.24
        if cat == 'C3':
            if self.C3_hitCheck is False:
                self.C3[indx] += 1
                self.C3_hitCheck = True
            self.C3_days[indx] += 0.24
        if cat == 'C4':
            if self.C4_hitCheck is False:
                self.C4[indx] += 1
                self.C4_hitCheck = True
            self.C4_days[indx] += 0.24
        if cat == 'C5':
            if self.C5_hitCheck is False:
                self.C5[indx] += 1
                self.C5_hitCheck = True
            self.C5_days[indx] += 0.24

    def ResetHitCheck(self):

        self.tropical_hitCheck = False
        self.C1_hitCheck = False
        self.C2_hitCheck = False
        self.C3_hitCheck = False
        self.C4_hitCheck = False
        self.C5_hitCheck = False

    def UpdateYearlyStats(self, YearStats):

        self.yearCount += 1

        topical_min_indx = np.where((YearStats.tropical - self.tropical_min) < 0)
        self.tropical_min[topical_min_indx] = YearStats.tropical[topical_min_indx]
        topical_max_indx = np.where((YearStats.tropical - self.tropical_max) > 0)
        self.tropical_max[topical_max_indx] = YearStats.tropical[topical_max_indx]
        self.tropical_mean = (self.tropical / self.yearCount)

        tropical_days_min_indx = np.where((YearStats.tropical_days - self.tropical_days_min) < 0)
        self.tropical_days_min[tropical_days_min_indx] = YearStats.tropical_days[tropical_days_min_indx]
        tropical_days_max_indx = np.where((YearStats.tropical_days - self.tropical_days_max) > 0)
        self.tropical_days_max[tropical_days_max_indx] = YearStats.tropical_days[tropical_days_max_indx]
        self.tropical_days_mean = (self.tropical_days / self.yearCount)

        c1_min_indx = np.where((YearStats.C1 - self.C1_min) < 0)
        self.C1_min[c1_min_indx] = YearStats.C1[c1_min_indx]
        c1_max_indx = np.where((YearStats.C1 - self.C1_max) > 0)
        self.C1_max[c1_max_indx] = YearStats.C1[c1_max_indx]
        self.C1_mean = (self.C1 / self.yearCount)

        c1_days_min_indx = np.where((YearStats.C1_days - self.C1_days_min) < 0)
        self.C1_days_min[c1_days_min_indx] = YearStats.C1_days[c1_days_min_indx]
        c1_days_max_indx = np.where((YearStats.C1_days - self.C1_days_max) > 0)
        self.C1_days_max[c1_days_max_indx] = YearStats.C1_days[c1_days_max_indx]
        self.C1_days_mean = (self.C1_days / self.yearCount)

        c2_min_indx = np.where((YearStats.C2 - self.C2_min) < 0)
        self.C2_min[c2_min_indx] = YearStats.C2[c2_min_indx]
        c2_max_indx = np.where((YearStats.C2 - self.C2_max) > 0)
        self.C2_max[c2_max_indx] = YearStats.C2[c2_max_indx]
        self.C2_mean = (self.C2 / self.yearCount)

        c2_days_min_indx = np.where((YearStats.C2_days - self.C2_days_min) < 0)
        self.C2_days_min[c2_days_min_indx] = YearStats.C2_days[c2_days_min_indx]
        c2_days_max_indx = np.where((YearStats.C2_days - self.C2_days_max) > 0)
        self.C2_days_max[c2_days_max_indx] = YearStats.C2_days[c2_days_max_indx]
        self.C2_days_mean = (self.C2_days / self.yearCount)

        c3_min_indx = np.where((YearStats.C3 - self.C3_min) < 0)
        self.C3_min[c3_min_indx] = YearStats.C3[c3_min_indx]
        c3_max_indx = np.where((YearStats.C3 - self.C3_max) > 0)
        self.C3_max[c3_max_indx] = YearStats.C3[c3_max_indx]
        self.C3_mean = (self.C3 / self.yearCount)

        c3_days_min_indx = np.where((YearStats.C3_days - self.C3_days_min) < 0)
        self.C3_days_min[c3_days_min_indx] = YearStats.C3_days[c3_days_min_indx]
        c3_days_max_indx = np.where((YearStats.C3_days - self.C3_days_max) > 0)
        self.C3_days_max[c3_days_max_indx] = YearStats.C3_days[c3_days_max_indx]
        self.C3_days_mean = (self.C3_days / self.yearCount)

        c4_min_indx = np.where((YearStats.C4 - self.C4_min) < 0)
        self.C4_min[c4_min_indx] = YearStats.C4[c4_min_indx]
        c4_max_indx = np.where((YearStats.C4 - self.C4_max) > 0)
        self.C4_max[c4_max_indx] = YearStats.C4[c4_max_indx]
        self.C4_mean = (self.C4 / self.yearCount)

        c4_days_min_indx = np.where((YearStats.C4_days - self.C4_days_min) < 0)
        self.C4_days_min[c4_days_min_indx] = YearStats.C4_days[c4_days_min_indx]
        c4_days_max_indx = np.where((YearStats.C4_days - self.C4_days_max) > 0)
        self.C4_days_max[c4_days_max_indx] = YearStats.C4_days[c4_days_max_indx]
        self.C4_days_mean = (self.C4_days / self.yearCount)

        c5_min_indx = np.where((YearStats.C5 - self.C5_min) < 0)
        self.C5_min[c5_min_indx] = YearStats.C5[c5_min_indx]
        c5_max_indx = np.where((YearStats.C5 - self.C5_max) > 0)
        self.C5_max[c5_max_indx] = YearStats.C5[c5_max_indx]
        self.C5_mean = (self.C5 / self.yearCount)

        c5_days_min_indx = np.where((YearStats.C5_days - self.C5_days_min) < 0)
        self.C5_days_min[c5_days_min_indx] = YearStats.C5_days[c5_days_min_indx]
        c5_days_max_indx = np.where((YearStats.C5_days - self.C5_days_max) > 0)
        self.C5_days_max[c5_days_max_indx] = YearStats.C5_days[c5_days_max_indx]
        self.C5_days_mean = (self.C5_days / self.yearCount)


class YearlyRecord(object):

    # This class is used to keep the stats per platform on a yearly basis
    # and will be used to update the stats for the PlatformRecord class

    def __init__(self, grid):
        self.x = grid[0]
        self.y = grid[1]
        self.grid_init_zeros = np.zeros((self.x, self.y), dtype=np.float)
        self.tropical_hitCheck = False
        self.tropical = np.zeros((self.x, self.y), dtype=np.float)
        self.tropical_days = np.zeros((self.x, self.y), dtype=np.float)
        self.C1_hitCheck = False
        self.C1 = np.zeros((self.x, self.y), dtype=np.float)
        self.C1_days = np.zeros((self.x, self.y), dtype=np.float)
        self.C2_hitCheck = False
        self.C2 = np.zeros((self.x, self.y), dtype=np.float)
        self.C2_days = np.zeros((self.x, self.y), dtype=np.float)
        self.C3_hitCheck = False
        self.C3 = np.zeros((self.x, self.y), dtype=np.float)
        self.C3_days = np.zeros((self.x, self.y), dtype=np.float)
        self.C4_hitCheck = False
        self.C4 = np.zeros((self.x, self.y), dtype=np.float)
        self.C4_days = np.zeros((self.x, self.y), dtype=np.float)
        self.C5_hitCheck = False
        self.C5 = np.zeros((self.x, self.y), dtype=np.float)
        self.C5_days = np.zeros((self.x, self.y), dtype=np.float)

    def AddHit(self, cat, indx):

        if cat == 'tropical':
            if self.tropical_hitCheck == False:
                self.tropical[indx] += 1
                self.tropical_hitCheck = True
            self.tropical_days[indx] += 0.24
        if cat == 'C1':
            if self.C1_hitCheck == False:
                self.C1[indx] += 1
                self.C1_hitCheck = True
            self.C1_days[indx] += 0.24
        if cat == 'C2':
            if self.C2_hitCheck is False:
                self.C2[indx] += 1
                self.C2_hitCheck = True
            self.C2_days[indx] += 0.24
        if cat == 'C3':
            if self.C3_hitCheck is False:
                self.C3[indx] += 1
                self.C3_hitCheck = True
            self.C3_days[indx] += 0.24
        if cat == 'C4':
            if self.C4_hitCheck is False:
                self.C4[indx] += 1
                self.C4_hitCheck = True
            self.C4_days[indx] += 0.24
        if cat == 'C5':
            if self.C5_hitCheck is False:
                self.C5[indx] += 1
                self.C5_hitCheck = True
            self.C5_days[indx] += 0.24

    def ResetHitCheck(self):

        self.tropical_hitCheck = False
        self.C1_hitCheck = False
        self.C2_hitCheck = False
        self.C3_hitCheck = False
        self.C4_hitCheck = False
        self.C5_hitCheck = False


def sph2xy(lon, lon_origin, lat, lat_origin):
    R = 6371 * 1e3
    dg2rad = scipy.pi / 180.0
    x = (R) * (lon - lon_origin) * (dg2rad) * (scipy.cos((lat_origin * dg2rad)))
    y = (R) * (lat - lat_origin) * (dg2rad)

    return x, y


def OpenFileGDB(path, name):
    # open the inShapefile as the driver type
    inDriver = ogr.GetDriverByName('OpenFileGDB')
    inDataSource = inDriver.Open(path, 0)
    inLayer = inDataSource.GetLayer(name)

    return inDataSource, inLayer


def OpenShp(path):
    # open the inShapefile as the driver type
    inDriver = ogr.GetDriverByName('ESRI Shapefile')
    inDataSource = inDriver.Open(path, 0)
    inLayer = inDataSource.GetLayer()

    return inDataSource, inLayer


def readStormDateTime(instr):
    start_date = datetime.strptime('11/17/1858 00:00:00', DT_FORMAT)
    delta = timedelta(days=instr)
    new_date = start_date + delta

    return new_date


def readStormDateTime_ISO(instr):
    iso_date = datetime.strptime(instr, DT_ISO_FORMAT)

    return iso_date


def readPlatDateTime(instr):
    return datetime.strptime(instr, D_FORMAT)


def exportGdalRaster_wMask(outputPath, array, x, y, geotransform, projection, mask_array):
    """
    Exports an array and raster properties to file (.tif)

    Args:
        outputPath: path to export raster, ending in .tif extension
        array: numpy array
        x: dimension of raster in X direction
        y: dimension of raster in Y direction
        geotransform: geotransform property from a raster
        projection: gdal projection object from a raster or peojection file

    Returns: N/A

    """

    from osgeo import gdal
    import numpy as np

    if not outputPath.endswith('.tif'):
        outputPath = outputPath + '.tif'

    # apply mask to array
    indx = np.where(mask_array != 1)
    array[indx] = np.nan

    # save to output GeoTIFF
    driver = gdal.GetDriverByName('GTiff')
    out = driver.Create(outputPath, x, y, 1, gdal.GDT_Float32)
    out.SetGeoTransform(geotransform)
    out.SetProjection(projection)
    bandOut = out.GetRasterBand(1)
    outNoData = np.iinfo(gdal.GDT_Float32).max
    bandOut.SetNoDataValue(outNoData)
    bandOut.WriteArray(array)


def loadArrays(grid_path, mask_path, cls=GridRecord):
    ds = gdal.Open(grid_path)
    band = ds.GetRasterBand(1)

    data = band.ReadAsArray()

    mask_ds = gdal.Open(mask_path)
    mask_band = mask_ds.GetRasterBand(1)
    mask = mask_band.ReadAsArray()

    arrs = cls(data, mask)

    return ds, arrs


def findNCDTInd(target, nc):
    ds = netCDF4.Dataset(nc)

    time_var = ds.variables['time']
    try:
        ind = netCDF4.date2index(target, time_var)
    except ValueError:
        return None, None
    else:
        return ds, ind


def ExtractLatLongInGDB_ByAttribute(inDataSource, inLayer, filterQuery):
    """
    This function will extract features from a feature class based on a SQL filter query and save the layer to
    memory. It will carry over any attributes in the input feature class.

    This function will only work with feature classes!!! The feature has to be in a geodatabase, and the driver
    MUST be 'FileGDB'. This function can be changed to use shapefiles by adjusting how the input is opened.

    Requirement: 'FileGDB' driver for ogr

    Args:
        inGDB: input geodatabase (must end with .gdb)
        inFileName: the name of the input feature class
        filterQuery: list of SQL query that is in the format of 'column = string' ... string must be quoted and number should NOT be quoted
        outLayerName: the name of the output feature class

    Returns: output memory data source and memory layer
    """

    from osgeo import ogr

    inLayer_query = inLayer

    # query out the wanted fields
    for i in filterQuery:
        inLayer_query.SetAttributeFilter(i)

    print('filter set')

    print('feature count: {}'.format(inLayer_query.GetFeatureCount()))

    pt_list = []

    # feat = inLayer_query.GetNextFeature()
    #
    # geom = feat.GetGeometryRef()
    #
    # pt = geom.GetPoint()

    # get lat and long of filtered point(s)
    for inFeature in inLayer_query:
        # get geometry
        geom = inFeature.GetGeometryRef()
        # get point
        pt = geom.GetPoint()

        pt_list.append(pt)

    if len(pt_list) > 1:
        print('UH OH TOO  MANY POINTS FILTERED!!!!')

    inLayer.ResetReading()

    return inDataSource, inLayer, pt_list


def GetPlatformCoords(platform_points):
    # open platform
    p_ds, p_lyr = OpenShp(platform_points)

    plat_coords = {}

    # loop through features
    for feat in p_lyr:
        # get geometry
        geom = feat.GetGeometryRef()
        # get point
        pt = geom.GetPoint()
        # get id
        p_id = str(feat.GetField('PlatformID'))

        plat_coords[p_id] = pt

    return plat_coords


def GetStormCoords(storm_points):
    # open platform
    p_ds, p_lyr = OpenShp(storm_points)

    storm_coords = {}

    # loop through features
    for feat in p_lyr:
        # get geometry
        geom = feat.GetGeometryRef()
        # get point
        pt = geom.GetPoint()
        # get id
        s_sid = feat.GetField('SID')
        s_iso = feat.GetField('ISO_TIME')

        storm_coords[s_sid + '_' + s_iso] = pt

    return storm_coords


def GetDistance(position_1, position_2, coordTransform):
    """
        Returns distance in 'units' (default km) between two Lat Lon point sets
                position_1 and position_2 are dicts containing "lon" and "lat"

                Units (optional) can be "km", "sm", or "nm"
        """
    point1 = ogr.Geometry(ogr.wkbPoint)
    point1.AddPoint(position_1[0], position_1[1])
    # point1.Transform(coordTransform)

    point2 = ogr.Geometry(ogr.wkbPoint)
    point2.AddPoint(position_2[0], position_2[1])
    # point2.Transform(coordTransform)

    raw_dist = point2.Distance(point1)

    return raw_dist


def GetDistanceBetweenPoints(p1_lon, p1_lat, p2_lon, p2_lat):
    # get point from platform points based on attributes
    wkt1 = "POINT ({} {})".format(p1_lon, p1_lat)
    pt1 = ogr.CreateGeometryFromWkt(wkt1)
    wkt2 = "POINT ({} {})".format(p2_lon, p2_lat)
    pt2 = ogr.CreateGeometryFromWkt(wkt2)

    dist = pt1.Distance(pt2)

    return dist


def parse_coords(x, y, gt):
    # Convert projected coordinates to raster cell indices
    row, col = None, None
    if x:
        col = int((x - gt[0]) // gt[1])
        # If only x coordinate is provided, return column index
        if not y:
            return col
    if y:
        row = int((y - gt[3]) // gt[5])
        # If only x coordinate is provided, return column index
        if not x:
            return row
    return (row, col)


def build_cell(row, col, gt):
    # Construct polygon geometry from raster cell
    xres, yres = gt[1], gt[5]
    x_0, y_0 = gt[0], gt[3]
    top = (yres * row) + y_0
    bottom = (yres * (row + 1)) + y_0
    right = (xres * col) + x_0
    left = (xres * (col + 1)) + x_0
    # Create ring topology
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(left, bottom)
    ring.AddPoint(right, bottom)
    ring.AddPoint(right, top)
    ring.AddPoint(left, top)
    ring.AddPoint(left, bottom)
    # Create polygon
    box = ogr.Geometry(ogr.wkbPolygon)
    box.AddGeometry(ring)
    return box


def Pixel2World(x, y, gt):
    """
    Using equation from Bharath Comandur at Purdue University (not a published paper)
    https://engineering.purdue.edu/RVL/blog/doku.php?id=blog:2018:1003_pixel_to_geodesic_coordinate_transformations_using_geotiffs

    Args:
        x:
        y:
        px_w:
        rot1:
        xoffset:
        px_h:
        rot2:
        yoffset:
        srs:

    Returns:

    """

    Xgeo = gt[0] + (x + 0.5) * gt[1] + (y + 0.5) * gt[2]
    Ygeo = gt[3] + (x + 0.5) * gt[4] + (y + 0.5) * gt[5]

    return (Xgeo, Ygeo)


def GetIndicesOfIntersection(ds_grid, rad, lon, lat):
    # build circle geometry
    wkt = "POINT ({} {})".format(lon, lat)
    pt = ogr.CreateGeometryFromWkt(wkt)
    bufferDistance = rad
    poly = pt.Buffer(bufferDistance)

    gt = ds_grid.GetGeoTransform()

    matched_cells = []
    # for f, feature in enumerate(poly):
    #     geom = feature.GetGeometryRef()
    bbox = poly.GetEnvelope()
    xmin, xmax = [parse_coords(x, None, gt) for x in bbox[:2]]
    ymin, ymax = [parse_coords(None, y, gt) for y in bbox[2:]]

    print('begin loop')
    hits = 0
    for cell_row in range(ymax, ymin + 1):
        for cell_col in range(xmin, xmax + 1):
            lon_x, lat_y = Pixel2World(cell_row, cell_col, gt)
            dist = GetDistanceBetweenPoints(lon_x, lat_y, lon, lat)
            if dist <= rad:
                hits += 1
                matched_cells += [[(cell_row, cell_col)]]

    print('end loop. {} hits!'.format(hits))

    return ds_grid, matched_cells


def GetIndicesOfIntersection_Ver2(ds_grid, rad, lon, lat):
    # get projection
    gomalbers_srs = osr.SpatialReference()  # makes an empty spatial ref object
    gomalbers_srs.ImportFromWkt(ds_grid.GetProjection())
    wgs84_srs = osr.SpatialReference()
    wgs84_srs.ImportFromEPSG(4326)

    # build point geometry
    wkt = "POINT ({} {})".format(lon, lat)
    pt = ogr.CreateGeometryFromWkt(wkt)
    # project point geometry from wgs84 to gomAlbers
    transform = osr.CoordinateTransformation(wgs84_srs, gomalbers_srs)
    pt.Transform(transform)
    # create point layer
    ogr_mem_driver = ogr.GetDriverByName('MEMORY')
    point_ds = ogr_mem_driver.CreateDataSource('point')
    point_lyr = point_ds.CreateLayer('point', gomalbers_srs, ogr.wkbPoint)

    # add feature to ogr layer
    pointLayerDefn = point_lyr.GetLayerDefn()

    # Create output Feature
    outFeature = ogr.Feature(pointLayerDefn)

    # Set geometry
    outFeature.SetGeometry(pt)

    # Add new feature to output Layer
    point_lyr.CreateFeature(outFeature)

    del outFeature
    del pt

    # create polygon layer
    poly_ds = ogr_mem_driver.CreateDataSource('poly')
    poly_lyr = poly_ds.CreateLayer('poly', gomalbers_srs, ogr.wkbPolygon)

    # add feature to ogr layer
    polyLayerDefn = poly_lyr.GetLayerDefn()

    # Create output Feature
    outFeature = ogr.Feature(polyLayerDefn)

    # get point from point layer
    feat_pt = point_lyr.GetNextFeature()
    pt = feat_pt.GetGeometryRef()
    # buffer point
    buff = pt.Buffer(rad)

    # Set geometry
    outFeature.SetGeometry(buff)

    # Add new feature to output Layer
    poly_lyr.CreateFeature(outFeature)

    gt = ds_grid.GetGeoTransform()

    # set up new raster
    mem_driver = gdal.GetDriverByName("MEM")
    mask_ds = mem_driver.Create('buff_mask', ds_grid.RasterXSize, ds_grid.RasterYSize, 1, gdal.GDT_Float32)
    mask_ds.SetGeoTransform(gt)
    mask_ds.SetProjection(ds_grid.GetProjection())
    mask_ds.GetRasterBand(1).SetNoDataValue(-999)

    # rasterize polygon
    gdal.RasterizeLayer(mask_ds, [1], poly_lyr)

    # retrieve indices where mask =1
    indx = np.where(mask_ds.ReadAsArray()==255)

    del mask_ds

    return ds_grid, indx


def checkHurricaneEffect(arrays, ds_grid, storm_lon, storm_lat, cat, wind_speed, wave, gust, lon_min, lat_min, mcp, sid,
                         iso_t):
    # Saffir-Simpson Scale Hurricane Category
    # Category  mph		m/s		kts
    # 1		  74-95	   33-42   64-82
    # 2		  96-110   43-49   83-95
    # 3 	 111-130   50-58   96-113
    # 4		 131-155   59-69   114-135
    # 5		   156+     70+		136+

    # Hurricane radius based on category
    #	Category		Radius (km)
    # tropical storm 	 100,000
    # 	  1-2			 300,000
    # 	  3-5			 450,000

    # determine radius (m) of the storm by the wind speed

    category = None
    radius = None

    # try to use given category, but if cat is None use wind speed
    # to get the radius of the hurricane
    if cat is not None:
        if cat == 0:
            radius = 100000
            category = 'tropical'
        if cat == 1:
            radius = 300000
            category = 'C1'
        if cat == 2:
            radius = 300000
            category = 'C2'
        if cat == 3:
            radius = 450000
            category = 'C3'
        if cat == 4:
            radius = 450000
            category = 'C4'
        if cat == 5:
            radius = 450000
            category = 'C5'
    else:
        # if there is no category given, use the wind speed to approximate radius
        if wind_speed is not None:
            wind_speed = float(wind_speed)
            if (wind_speed >= 34) and (wind_speed < 64):
                radius = 100000
                category = 'tropical'
            if (wind_speed >= 64) and (wind_speed < 83):
                radius = 300000
                category = 'C1'
            if (wind_speed >= 83) and (wind_speed < 96):
                radius = 300000
                category = 'C2'
            if (wind_speed >= 96) and (wind_speed < 113):
                radius = 450000
                category = 'C3'
            if (wind_speed >= 113) and (wind_speed < 137):
                radius = 450000
                category = 'C4'
            if wind_speed >= 137:
                radius = 450000
                category = 'C5'

    if radius is not None:
        # convert lat and long coordinates (degrees) into x and y (meters)
        # storm_x, storm_y = sph2xy(storm_lon, lon_min, storm_lat, lat_min)
        # use squared distance function to determine if the platform lies within the hurricane buffer
        # distance = np.sqrt((((platform.x - storm_x) ** 2) + ((platform.y - storm_y) ** 2)))

        # get get the grid indices that are within the radius
        ds_grid, indx = GetIndicesOfIntersection_Ver2(ds_grid, radius, storm_lon, storm_lat)

        if indx:

            # update platform record with stat
            arrays.addValue(category, indx, wave, wind_speed, gust, mcp)

            return arrays, ds_grid, indx, category

        else:

            return arrays, ds_grid, None, None

    else:
        return arrays, ds_grid, None, None


def processStats(arrays, ds_grid, numStorms, lat, lon, time, categ, msw, wave, gust, lon_min, lat_min, mcp, region, sid,
                 iso_time):
    # loop through each storm
    error_count = 0
    # set year to none for later
    year = None
    YearStats = YearlyRecord(ds_grid.ReadAsArray().shape)

    for i in range(0, numStorms):

        print('Processing storm {} out of {}'.format(i, numStorms))

        # make sure storm hitCheck is False to begin each storm
        arrays.ResetHitCheck()
        YearStats.ResetHitCheck()

        try:
            # grab variables for that one storm
            lat_storm = lat[i:i + 1].tolist()[0]
            lon_storm = lon[i:i + 1].tolist()[0]
            time_storm = time[i:i + 1].tolist()[0]
            cat_storm = categ[i:i + 1].tolist()[0]
            msw_storm = msw[i:i + 1].tolist()[0]
            wave_storm = wave[i:i + 1].tolist()[0]
            gust_storm = gust[i:i + 1].tolist()[0]
            mcp_storm = mcp[i:i + 1].tolist()[0]
            region_storm = region[i:i + 1].tolist()[0]
            sid_storm = sid[i:i + 1].tolist()[0]
            iso_time_storm = iso_time[i:i + 1].tolist()[0]
        except:
            error_count += 1
            print("Read failed, storm # " + format(i))
            continue

        sid_list = sid_storm
        sid_num = b''.join(sid_list).decode('utf-8')

        # iso_t = b"".join(iso_time_storm[0]).decode("utf-8")
        # if iso_t != None:
        # 	# get distance between the two points
        # 	distance = GetDistanceBetweenPoints(platform.id, iso_t, sid_num)

        # if sid_num == '1997198N27267':
        # 	print('woah!')

        # for each storm loop through all observations
        # for lat_s, lon_s, time_s, msw_s in zip(lat_storm,lon_storm,time_storm,msw_storm):
        for t in range(0, len(time_storm)):

            if region_storm[t][0] is not None:

                r_list = region_storm[t]
                r_reg = b''.join(r_list)

                # if (r_reg == b'GM') or (r_reg == b'NA'):

                # turn time_v into datetime object
                try:
                    iso_t = b"".join(iso_time_storm[t]).decode("utf-8")
                    timeObs = readStormDateTime_ISO(iso_t)
                # timeObs_next = readStormDateTime(time_storm[t+1])
                except TypeError:
                    # print(TypeError)
                    # occurs when the time variable is missing
                    continue
                # keep track of the year for processing stats per year
                if year is None:
                    year = timeObs.year

                # if the year has changed, update the PlatformRecord with
                # the yearly stats and start new YearlyRecord
                if timeObs.year != year:
                    # update platform yearly stats with YearRecord
                    arrays.UpdateYearlyStats(YearStats)
                    # reset YearRecord
                    YearStats = YearlyRecord(ds_grid.ReadAsArray().shape)
                    # reset year
                    year = timeObs.year

                # check whether or not the platform is affected by the storm and by what category
                arrays, ds_grid, indx, category = checkHurricaneEffect(arrays, ds_grid, lon_storm[t], lat_storm[t], cat_storm[t],
                                                            msw_storm[t], wave_storm[t], gust_storm[t], lon_min,
                                                            lat_min, mcp_storm[t], sid_num, iso_t)
                # if the platform was "hit" by the hurricane, update the yearly stats
                if category:
                    YearStats.AddHit(category, indx)

    print(format(error_count) + ' number of storms failed to read')

    return arrays


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


def runStatsForStorms(arrays, ds_grid, ncDir):
    # get minimum values for all latitude and longitudes in the net CDFs
    lat_min = GetNC_Min(ncDir, 'usa_lat')
    lon_min = GetNC_Min(ncDir, 'usa_lon')

    ncFiles = iglob(ncDir)

    for nc in ncFiles:
        print('Processing: ' + format(nc))

        start = time.time()

        # open netCDF
        ds = netCDF4.Dataset(nc, 'r')

        # grab variables for current index
        c_lat = ds.variables['usa_lat']
        c_lon = ds.variables['usa_lon']
        c_time = ds.variables['time']
        c_time_iso = ds.variables['iso_time']
        c_cat = ds.variables['usa_sshs']
        c_msw = ds.variables['usa_wind']
        c_wave = ds.variables['usa_seahgt']
        c_gust = ds.variables['usa_gust']
        c_mcp = ds.variables['usa_pres']
        c_region = ds.variables['subbasin']
        c_sid = ds.variables['sid']

        # note number of storms in netCDF
        dsLen = len(ds.dimensions['storm'])

        processStats(arrays, ds_grid, dsLen, c_lat, c_lon, c_time, c_cat, c_msw, c_wave, c_gust, lon_min, lat_min,
                     c_mcp, c_region, c_sid, c_time_iso)

        end = time.time()
        print(end - start)

        return arrays


def writeResultsToGeoTIFF(arrs, outputFolder, mask_path):

    """
    Create separate geotiffs for each hurricnae statistic

    Args:
        arrs:
        outputFolder:
        dsgrid:

    Returns:

    """

    # open mask path
    ds_grid = gdal.Open(mask_path)

    y = arrs.x
    x = arrs.y
    geotransform = ds_grid.GetGeoTransform()
    projection = ds_grid.GetProjection()

    print('x: {}'.format(x))
    print('y: {}'.format(y))
    print(arrs.stormTotal.shape)

    exportGdalRaster_wMask(os.path.join(outputFolder, 'TotalStorms'), arrs.stormTotal, x, y, geotransform, projection, arrs.mask)

    exportGdalRaster_wMask(os.path.join(outputFolder, 'Tropical'), arrs.tropical, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'Tropical_Min'), arrs.tropical_min, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'Tropical_Max'), arrs.tropical_max, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'Tropical_Mean'), arrs.tropical_mean, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'TropicalDays'), arrs.tropical_days, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'TropicalDays_Min'), arrs.tropical_days_min, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'TropicalDays_Max'), arrs.tropical_days_max, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'TropicalDays_Mean'), arrs.tropical_days_mean, x, y, geotransform, projection, arrs.mask)

    exportGdalRaster_wMask(os.path.join(outputFolder, 'C1'), arrs.C1, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C1_Min'), arrs.C1_min, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C1_Max'), arrs.C1_max, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C1_Mean'), arrs.C1_mean, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C1Days'), arrs.C1_days, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C1Days_Min'), arrs.C1_days_min, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C1Days_Max'), arrs.C1_days_max, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C1Days_Mean'), arrs.C1_days_mean, x, y, geotransform, projection, arrs.mask)

    exportGdalRaster_wMask(os.path.join(outputFolder, 'C2'), arrs.C2, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C2_Min'), arrs.C2_min, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C2_Max'), arrs.C2_max, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C2_Mean'), arrs.C2_mean, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C2Days'), arrs.C2_days, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C2Days_Min'), arrs.C2_days_min, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C2Days_Max'), arrs.C2_days_max, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C2Days_Mean'), arrs.C2_days_mean, x, y, geotransform, projection, arrs.mask)

    exportGdalRaster_wMask(os.path.join(outputFolder, 'C3'), arrs.C3, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C3_Min'), arrs.C3_min, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C3_Max'), arrs.C3_max, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C3_Mean'), arrs.C3_mean, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C3Days'), arrs.C3_days, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C3Days_Min'), arrs.C3_days_min, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C3Days_Max'), arrs.C3_days_max, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C3Days_Mean'), arrs.C3_days_mean, x, y, geotransform, projection, arrs.mask)

    exportGdalRaster_wMask(os.path.join(outputFolder, 'C4'), arrs.C4, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C4_Min'), arrs.C4_min, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C4_Max'), arrs.C4_max, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C4_Mean'), arrs.C4_mean, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C4Days'), arrs.C4_days, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C4Days_Min'), arrs.C4_days_min, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C4Days_Max'), arrs.C4_days_max, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C4Days_Mean'), arrs.C4_days_mean, x, y, geotransform, projection, arrs.mask)

    exportGdalRaster_wMask(os.path.join(outputFolder, 'C5'), arrs.C5, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C5_Min'), arrs.C5_min, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C5_Max'), arrs.C5_max, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C5_Mean'), arrs.C5_mean, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C5Days'), arrs.C5_days, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C5Days_Min'), arrs.C5_days_min, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C5Days_Max'), arrs.C5_days_max, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'C5Days_Mean'), arrs.C5_days_mean, x, y, geotransform, projection, arrs.mask)

    exportGdalRaster_wMask(os.path.join(outputFolder, 'WaveHeight_Sum'), arrs.waveHeightSum, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'WaveHeight_Average'), arrs.waveHeightAverage, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'WaveHeight_Max'), arrs.waveHeightMax, x, y, geotransform, projection, arrs.mask)
    exportGdalRaster_wMask(os.path.join(outputFolder, 'WaveHeight_Min'), arrs.waveHeightMin, x, y, geotransform, projection, arrs.mask)

if __name__ == "__main__":
    nc_dir = r'P:\01_DataOriginals\GOM\Metocean\StormData\1842-2021'
    input_grid = r"C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\ML Testing\SMART Tool Ready\Input Data\BlankGrids\BlankGrid_GomAlbers.tif"
    input_mask = r'C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\ML Testing\SMART Tool Ready\Input Data\BlankGrids\land_mask_GomAlbers.tif'
    output_folder = r"C:\Users\dyera\Documents\Task 6\Metocean\Hurricane Stats"
    # platform_points = r'C:\Users\dyera\Documents\Offshore Task 3\GradientBoostingRegressor\1.DATA\Shapefiles\all_platforms_subset_GomAlbers.shp'
    # platform_points_name = 'All_Platforms_GomAlbers'
    storm_points = r'C:\Users\dyera\Documents\Offshore Task 3\GradientBoostingRegressor\1.DATA\Shapefiles\hurricane_points_GomAlbers.shp'
    # storm_points_name = 'IBTRACS_NA_Points_GomAlbers'

    prsr = ArgumentParser(description="Generate Stats for grid")
    prsr.add_argument('input_grid', type=str,
                      help='grid to compute hurricane statistics for')
    prsr.add_argument('input_mask', type=str, help='mask signifying land and ocean')
    prsr.add_argument('nc_dir', type=str, help='path to directory containing netcdf data')
    prsr.add_argument('outputs', type=str, help='path to output data')
    # prsr.add_argument('--start_date', type=readPlatDateTime, default=FIRST_DATE, help='Start of querying period')
    # prsr.add_argument('--stop_date', type=readPlatDateTime, default=LAST_DATE, help='End of querying period')
    prsr.add_argument('--stats', '-s', nargs='+', help='statistics to run')

    args = prsr.parse_args([input_grid, input_mask, nc_dir, output_folder])

    # if args.start_date >= args.stop_date:
    # 	raise Exception('start_date must proceed stop_date')

    # open platform and storm points and get IDs and coordinates as a list
    # platform_coords_list = GetPlatformCoords(platform_points)
    storm_coords_list = GetStormCoords(storm_points)

    # load the platforms csv
    ds_grid, arrays = loadArrays(args.input_grid, args.input_mask)

    arrays = runStatsForStorms(arrays, ds_grid, os.path.join(args.nc_dir, '*.nc'))

    writeResultsToGeoTIFF(arrays, output_folder, input_mask)