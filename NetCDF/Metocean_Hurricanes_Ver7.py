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

Version 7 updates the way the hurricane radius is calculated using a function developed by
Nederhoff, K., Giardino, A., van Ormondt, M., & Vatvani, D. (2019). Estimates of tropical cyclone geometry parameters  based on best-track data. Nat. Hazards Earth Syst. Sci., 19(11), 2359–2370. https://doi.org/10.5194/nhess-19-2359-2019

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
from argparse import ArgumentParser
from glob import iglob
import os
import scipy
import time
from osgeo import ogr
#from wind_radii_nederhoff import wind_radii_nederhoff

D_FORMAT = '%m/%d/%Y'
DT_FORMAT = '%m/%d/%Y %H:%M:%S'
DT_ISO_FORMAT = '%Y-%m-%d %H:%M:%S'

FIRST_DATE = datetime(1972,1,1)
LAST_DATE = datetime(2021,1,27)

FLD_NAME = 'Storms'

# NC_YEAR_FORMAT = f'Year.{year}.ibtracs_wmo.v03r10.nc'

class PlatformRecord(object):

    def __init__(self, PlatformID, Lat, Lon, InstallDate, RemovalDate=None, IncidentDates=''):

        self.id = PlatformID
        self.lat = float(Lat)
        self.lon = float(Lon)
        self.install_date = None
        if InstallDate is not None and len(InstallDate) > 0:
            self.install_date = datetime.strptime(InstallDate, D_FORMAT)
        self.remove_date = None
        if RemovalDate is not None and len(RemovalDate ) >0:
            self.remove_date = datetime.strptime(RemovalDate, D_FORMAT)
        self.x = None
        self.y = None
        self.incident_dates = (datetime.strptime(x, D_FORMAT) for x in IncidentDates.split(';') if len(x) > 0)
        self.stormTotal = 0
        self.cat_noneCount = 0
        self.tropical_hitCheck = False
        self.tropical = 0
        self.tropical_min = float('inf')
        self.tropical_max = float('-inf')
        self.tropical_mean = 0
        self.tropical_days = 0
        self.tropical_days_min = float('inf')
        self.tropical_days_max = float('-inf')
        self.tropical_days_mean = 0
        self.C1_hitCheck = False
        self.C1 = 0
        self.C1_min = float('inf')
        self.C1_max = float('-inf')
        self.C1_mean = 0
        self.C1_days = 0
        self.C1_days_min = float('inf')
        self.C1_days_max = float('-inf')
        self.C1_days_mean = 0
        self.C2_hitCheck = False
        self.C2 = 0
        self.C2_min = float('inf')
        self.C2_max = float('-inf')
        self.C2_mean = 0
        self.C2_days = 0
        self.C2_days_min = float('inf')
        self.C2_days_max = float('-inf')
        self.C2_days_mean = 0
        self.C3_hitCheck = False
        self.C3 = 0
        self.C3_min = float('inf')
        self.C3_max = float('-inf')
        self.C3_mean = 0
        self.C3_days = 0
        self.C3_days_min = float('inf')
        self.C3_days_max = float('-inf')
        self.C3_days_mean = 0
        self.C4_hitCheck = False
        self.C4 = 0
        self.C4_min = float('inf')
        self.C4_max = float('-inf')
        self.C4_mean = 0
        self.C4_days = 0
        self.C4_days_min = float('inf')
        self.C4_days_max = float('-inf')
        self.C4_days_mean = 0
        self.C5_hitCheck = False
        self.C5 = 0
        self.C5_min = float('inf')
        self.C5_max = float('-inf')
        self.C5_mean = 0
        self.C5_days = 0
        self.C5_days_min = float('inf')
        self.C5_days_max = float('-inf')
        self.C5_days_mean = 0
        self.waveHeightCount = 0
        self.waveHeightNoneCount = 0
        self.waveHeightSum = 0
        self.waveHeightAverage = 0
        self.waveHeightMax = float('-inf')
        self.waveHeightMin = float('inf')

        self.windCount = 0
        self.windNoneCount = 0
        self.windSum = 0
        self.windAverage = 0
        self.windMax = float('-inf')
        self.windMin = float('inf')
        ###############################################
        self.windYearlyMin_min = float('inf')
        self.windYearlyMax_min = float('-inf')
        self.windYearlySum_min = 0
        self.windYearlyAvg_min = 0

        self.windYearlyMin_max = float('inf')
        self.windYearlyMax_max = float('-inf')
        self.windYearlySum_max = 0
        self.windYearlyAvg_max = 0

        self.windYearlyMin_sum = float('inf')
        self.windYearlyMax_sum = float('-inf')
        self.windYearlySum_sum = 0
        self.windYearlyAvg_sum = 0

        self.windYearlyMin_avg = float('inf')
        self.windYearlyMax_avg = float('-inf')
        self.windYearlySum_avg = 0
        self.windYearlyAvg_avg = 0
        ##############################################

        self.gustCount = 0
        self.gustNoneCount = 0
        self.gustSum = 0
        self.gustAverage = 0
        self.gustMax = float('-inf')
        self.gustMin = float('inf')
        ###############################################
        self.gustYearlyMin_min = float('inf')
        self.gustYearlyMax_min = float('-inf')
        self.gustYearlySum_min = 0
        self.gustYearlyAvg_min = 0

        self.gustYearlyMin_max = float('inf')
        self.gustYearlyMax_max = float('-inf')
        self.gustYearlySum_max = 0
        self.gustYearlyAvg_max = 0

        self.gustYearlyMin_sum = float('inf')
        self.gustYearlyMax_sum = float('-inf')
        self.gustYearlySum_sum = 0
        self.gustYearlyAvg_sum = 0

        self.gustYearlyMin_avg = float('inf')
        self.gustYearlyMax_avg = float('-inf')
        self.gustYearlySum_avg = 0
        self.gustYearlyAvg_avg = 0
        ##############################################

        self.yearCount = 0
        self.MCPCount = 0
        self.MCPNoneCount = 0
        self.MCPSum = 0
        self.MCPAverage = 0
        self.MCPMax = float('-inf')
        self.MCPMin = float('inf')
        ###############################################
        self.mcpYearlyMin_min = float('inf')
        self.mcpYearlyMax_min = float('-inf')
        self.mcpYearlySum_min = 0
        self.mcpYearlyAvg_min = 0

        self.mcpYearlyMin_max = float('inf')
        self.mcpYearlyMax_max = float('-inf')
        self.mcpYearlySum_max = 0
        self.mcpYearlyAvg_max = 0

        self.mcpYearlyMin_sum = float('inf')
        self.mcpYearlyMax_sum = float('-inf')
        self.mcpYearlySum_sum = 0
        self.mcpYearlyAvg_sum = 0

        self.mcpYearlyMin_avg = float('inf')
        self.mcpYearlyMax_avg = float('-inf')
        self.mcpYearlySum_avg = 0
        self.mcpYearlyAvg_avg = 0

        ##############################################

    def addValue(self, cat, wave, wind, gust, mcp):

        self.stormTotal += 1

        if wave is not None:
            self.waveHeightCount += 1
            self.waveHeightSum += wave
            self.waveHeightAverage = (self.waveHeightSum/self.waveHeightCount)
            if wave > self.waveHeightMax:
                self.waveHeightMax = wave
            if wave < self.waveHeightMin:
                self.waveHeightMin = wave
        if wave is None:
            self.waveHeightNoneCount += 1

        if wind is not None:
            self.windCount += 1
            self.windSum += wind
            self.windAverage = (self.windSum / self.windCount)
            if wind > self.windMax:
                self.windMax = wind
            if wind < self.windMin:
                self.windMin = wind
        if wind is None:
            self.windNoneCount += 1

        if gust is not None:
            self.gustCount += 1
            self.gustSum += gust
            self.gustAverage = (self.gustSum / self.gustCount)
            if gust > self.gustMax:
                self.gustMax = gust
            if gust < self.gustMin:
                self.gustMin = gust
        if gust is None:
            self.gustNoneCount += 1

        if mcp is not None:
            self.MCPCount += 1
            self.MCPSum += mcp
            self.MCPAverage = (self.MCPSum / self.MCPCount)
            if mcp > self.MCPMax:
                self.MCPMax = mcp
            if mcp < self.MCPMin:
                self.MCPMin = mcp
        if mcp is None:
            self.gustNoneCount += 1

        if cat is None:
            self.cat_noneCount += 1
            return
        if cat == 'tropical':
            if self.tropical_hitCheck is False:
                self.tropical += 1
                self.tropical_hitCheck = True
            self.tropical_days += 0.24
        if cat == 'C1':
            if self.C1_hitCheck is False:
                self.C1 += 1
                self.C1_hitCheck = True
            self.C1_days += 0.24
        if cat == 'C2':
            if self.C2_hitCheck is False:
                self.C2 += 1
                self.C2_hitCheck = True
            self.C2_days += 0.24
        if cat == 'C3':
            if self.C3_hitCheck is False:
                self.C3 += 1
                self.C3_hitCheck = True
            self.C3_days += 0.24
        if cat == 'C4':
            if self.C4_hitCheck is False:
                self.C4 += 1
                self.C4_hitCheck = True
            self.C4_days += 0.24
        if cat == 'C5':
            if self.C5_hitCheck is False:
                self.C5 += 1
                self.C5_hitCheck = True
            self.C5_days += 0.24

    def ResetHitCheck(self):

        self.tropical_hitCheck = False
        self.C1_hitCheck = False
        self.C2_hitCheck = False
        self.C3_hitCheck = False
        self.C4_hitCheck = False
        self.C5_hitCheck = False

    def UpdateYearlyStats(self, YearStats):

        self.yearCount += 1

        if YearStats.tropical < self.tropical_min:
            self.tropical_min = YearStats.tropical
        if YearStats.tropical > self.tropical_max:
            self.tropical_max = YearStats.tropical
        self.tropical_mean = (self.tropical / self.yearCount)

        if YearStats.tropical_days < self.tropical_days_min:
            self.tropical_days_min = YearStats.tropical_days
        if YearStats.tropical_days > self.tropical_days_max:
            self.tropical_days_max = YearStats.tropical_days
        self.tropical_days_mean = (self.tropical_days / self.yearCount)

        if YearStats.C1 < self.C1_min:
            self.C1_min = YearStats.C1
        if YearStats.C1 > self.C1_max:
            self.C1_max = YearStats.C1
        self.C1_mean = (self.C1 / self.yearCount)

        if YearStats.C1_days < self.C1_days_min:
            self.C1_days_min = YearStats.C1_days
        if YearStats.C1_days > self.C1_days_max:
            self.C1_days_max = YearStats.C1_days
        self.C1_days_mean = (self.C1_days / self.yearCount)

        if YearStats.C2 < self.C2_min:
            self.C2_min = YearStats.C2
        if YearStats.C2 > self.C2_max:
            self.C2_max = YearStats.C2
        self.C2_mean = (self.C2 / self.yearCount)

        if YearStats.C2_days < self.C2_days_min:
            self.C2_days_min = YearStats.C2_days
        if YearStats.C2_days > self.C2_days_max:
            self.C2_days_max = YearStats.C2_days
        self.C2_days_mean = (self.C2_days / self.yearCount)

        if YearStats.C3 < self.C3_min:
            self.C3_min = YearStats.C3
        if YearStats.C3 > self.C3_max:
            self.C3_max = YearStats.C3
        self.C3_mean = (self.C3 / self.yearCount)

        if YearStats.C3_days < self.C3_days_min:
            self.C3_days_min = YearStats.C3_days
        if YearStats.C3_days > self.C3_days_max:
            self.C3_days_max = YearStats.C3_days
        self.C3_days_mean = (self.C3_days / self.yearCount)

        if YearStats.C4 < self.C4_min:
            self.C4_min = YearStats.C4
        if YearStats.C4 > self.C4_max:
            self.C4_max = YearStats.C4
        self.C4_mean = (self.C4 / self.yearCount)

        if YearStats.C4_days < self.C4_days_min:
            self.C4_days_min = YearStats.C4_days
        if YearStats.C4_days > self.C4_days_max:
            self.C4_days_max = YearStats.C4_days
        self.C4_days_mean = (self.C4_days / self.yearCount)

        if YearStats.C5 < self.C5_min:
            self.C5_min = YearStats.C5
        if YearStats.C5 > self.C5_max:
            self.C5_max = YearStats.C5
        self.C5_mean = (self.C5 / self.yearCount)

        if YearStats.C5_days < self.C5_days_min:
            self.C5_days_min = YearStats.C5_days
        if YearStats.C5_days > self.C5_days_max:
            self.C5_days_max = YearStats.C5_days
        self.C5_days_mean = (self.C5_days / self.yearCount)

        ######################################################

        if YearStats.MSWS_hit > 0:

            # if YearStats.MSWS_min < self.windYearlyMin_min:
            # 	self.windYearlyMin_min = YearStats.MSWS_min
            if YearStats.MSWS_min > self.windYearlyMax_min:
                self.windYearlyMax_min = YearStats.MSWS_min
            self.windYearlySum_min += YearStats.MSWS_min
            self.windYearlyAvg_min = (self.windYearlySum_min / self.yearCount)

            if YearStats.MSWS_max < self.windYearlyMin_max:
                self.windYearlyMin_max = YearStats.MSWS_max
            # if YearStats.MSWS_max > self.windYearlyMax_max:
            # 	self.windYearlyMax_max = YearStats.MSWS_max
            self.windYearlySum_max += YearStats.MSWS_max
            self.windYearlyAvg_max = (self.windYearlySum_max / self.yearCount)

            if YearStats.MSWS_sum < self.windYearlyMin_sum:
                self.windYearlyMin_sum = YearStats.MSWS_sum
            if YearStats.MSWS_sum > self.windYearlyMax_sum:
                self.windYearlyMax_sum = YearStats.MSWS_sum
            self.windYearlySum_sum += YearStats.MSWS_sum
            self.windYearlyAvg_sum = (self.windYearlySum_sum / self.yearCount)

            if YearStats.MSWS_avg < self.windYearlyMin_avg:
                self.windYearlyMin_avg = YearStats.MSWS_avg
            if YearStats.MSWS_avg > self.windYearlyMax_avg:
                self.windYearlyMax_avg = YearStats.MSWS_avg
            self.windYearlySum_avg += YearStats.MSWS_avg
            self.windYearlyAvg_avg = (self.windYearlySum_avg / self.yearCount)

        ######################################################

        if YearStats.MRWG_hit > 0:

            # if YearStats.MSWS_min < self.windYearlyMin_min:
            # 	self.windYearlyMin_min = YearStats.MSWS_min
            if YearStats.MRWG_min > self.gustYearlyMax_min:
                self.gustYearlyMax_min = YearStats.MRWG_min
            self.gustYearlySum_min += YearStats.MRWG_min
            self.gustYearlyAvg_min = (self.gustYearlySum_min / self.yearCount)

            if YearStats.MRWG_max < self.gustYearlyMin_max:
                self.gustYearlyMin_max = YearStats.MRWG_max
            # if YearStats.MSWS_max > self.windYearlyMax_max:
            # 	self.windYearlyMax_max = YearStats.MSWS_max
            self.gustYearlySum_max += YearStats.MRWG_max
            self.gustYearlyAvg_max = (self.gustYearlySum_max / self.yearCount)

            if YearStats.MRWG_sum < self.gustYearlyMin_sum:
                self.gustYearlyMin_sum = YearStats.MRWG_sum
            if YearStats.MRWG_sum > self.gustYearlyMax_sum:
                self.gustYearlyMax_sum = YearStats.MRWG_sum
            self.gustYearlySum_sum += YearStats.MSWS_sum
            self.gustYearlyAvg_sum = (self.gustYearlySum_sum / self.yearCount)

            if YearStats.MRWG_avg < self.gustYearlyMin_avg:
                self.gustYearlyMin_avg = YearStats.MRWG_avg
            if YearStats.MRWG_avg > self.gustYearlyMax_avg:
                self.gustYearlyMax_avg = YearStats.MRWG_avg
            self.gustYearlySum_avg += YearStats.MSWS_avg
            self.gustYearlyAvg_avg = (self.gustYearlySum_avg / self.yearCount)

        ######################################################

        if YearStats.MCP_hit > 0:

            # if YearStats.MSWS_min < self.windYearlyMin_min:
            # 	self.windYearlyMin_min = YearStats.MSWS_min
            if YearStats.MCP_min > self.mcpYearlyMax_min:
                self.mcpYearlyMax_min = YearStats.MCP_min
            self.mcpYearlySum_min += YearStats.MCP_min
            self.mcpYearlyAvg_min = (self.mcpYearlySum_min / self.yearCount)

            if YearStats.MCP_max < self.mcpYearlyMin_max:
                self.mcpYearlyMin_max = YearStats.MCP_max
            # if YearStats.MSWS_max > self.windYearlyMax_max:
            # 	self.windYearlyMax_max = YearStats.MSWS_max
            self.mcpYearlySum_max += YearStats.MCP_max
            self.mcpYearlyAvg_max = (self.mcpYearlySum_max / self.yearCount)

            if YearStats.MCP_sum < self.mcpYearlyMin_sum:
                self.mcpYearlyMin_sum = YearStats.MCP_sum
            if YearStats.MCP_sum > self.mcpYearlyMax_sum:
                self.mcpYearlyMax_sum = YearStats.MCP_sum
            self.mcpYearlySum_sum += YearStats.MSWS_sum
            self.mcpYearlyAvg_sum = (self.mcpYearlySum_sum / self.yearCount)

            if YearStats.MCP_avg < self.mcpYearlyMin_avg:
                self.mcpYearlyMin_avg = YearStats.MCP_avg
            if YearStats.MCP_avg > self.mcpYearlyMax_avg:
                self.mcpYearlyMax_avg = YearStats.MCP_avg
            self.mcpYearlySum_avg += YearStats.MSWS_avg
            self.mcpYearlyAvg_avg = (self.mcpYearlySum_avg / self.yearCount)

    def Clean(self):

        if self.waveHeightCount == 0:
            self.waveHeightSum = None
            self.waveHeightAverage = None
            self.waveHeightMax = None
            self.waveHeightMin = None

        if self.windCount == 0:
            self.windSum = None
            self.windAverage = None
            self.windMax = None
            self.windMin = None

            self.windYearlyMin_min = None
            self.windYearlyMax_min = None
            self.windYearlySum_min = None
            self.windYearlyAvg_min = None

            self.windYearlyMin_max = None
            self.windYearlyMax_max = None
            self.windYearlySum_max = None
            self.windYearlyAvg_max = None

            self.windYearlyMin_sum = None
            self.windYearlyMax_sum = None
            self.windYearlySum_sum = None
            self.windYearlyAvg_sum = None

            self.windYearlyMin_avg = None
            self.windYearlyMax_avg = None
            self.windYearlySum_avg = None
            self.windYearlyAvg_avg = None

        ##############################################

        if self.gustCount == 0:
            self.gustSum = None
            self.gustAverage = None
            self.gustMax = None
            self.gustMin = None

            self.gustYearlyMin_min = None
            self.gustYearlyMax_min = None
            self.gustYearlySum_min = None
            self.gustYearlyAvg_min = None

            self.gustYearlyMin_max = None
            self.gustYearlyMax_max = None
            self.gustYearlySum_max = None
            self.gustYearlyAvg_max = None

            self.gustYearlyMin_sum = None
            self.gustYearlyMax_sum = None
            self.gustYearlySum_sum = None
            self.gustYearlyAvg_sum = None

            self.gustYearlyMin_avg = None
            self.gustYearlyMax_avg = None
            self.gustYearlySum_avg = None
            self.gustYearlyAvg_avg = None

        #############################################

        if self.MCPCount == 0:
            self.MCPSum = None
            self.MCPAverage = None
            self.MCPMax = None
            self.MCPMin = None

            self.mcpYearlyMin_min = None
            self.mcpYearlyMax_min = None
            self.mcpYearlySum_min = None
            self.mcpYearlyAvg_min = None

            self.mcpYearlyMin_max = None
            self.mcpYearlyMax_max = None
            self.mcpYearlySum_max = None
            self.mcpYearlyAvg_max = None

            self.mcpYearlyMin_sum = None
            self.mcpYearlyMax_sum = None
            self.mcpYearlySum_sum = None
            self.mcpYearlyAvg_sum = None

            self.mcpYearlyMin_avg = None
            self.mcpYearlyMax_avg = None
            self.mcpYearlySum_avg = None
            self.mcpYearlyAvg_avg = None

class YearlyRecord(object):

    # This class is used to keep the stats per platform on a yearly basis
    # and will be used to update the stats for the PlatformRecord class

    def __init__(self):
        self.tropical_hitCheck = False
        self.tropical = 0
        self.tropical_days = 0
        self.C1_hitCheck = False
        self.C1 = 0
        self.C1_days = 0
        self.C2_hitCheck = False
        self.C2 = 0
        self.C2_days = 0
        self.C3_hitCheck = False
        self.C3 = 0
        self.C3_days = 0
        self.C4_hitCheck = False
        self.C4 = 0
        self.C4_days = 0
        self.C5_hitCheck = False
        self.C5 = 0
        self.C5_days = 0
        self.MSWS_hitCheck = False
        self.MSWS_hit = 0
        self.MSWS_min = float('inf')
        self.MSWS_max = float('-inf')
        self.MSWS_sum = 0
        self.MSWS_avg = 0
        self.MRWG_hitCheck = False
        self.MRWG_hit = 0
        self.MRWG_min = float('inf')
        self.MRWG_max = float('-inf')
        self.MRWG_sum = 0
        self.MRWG_avg = 0
        self.MCP_hitCheck = False
        self.MCP_hit = 0
        self.MCP_min = float('inf')
        self.MCP_max = float('-inf')
        self.MCP_sum = 0
        self.MCP_avg = 0

    def AddHit(self, cat, msws, mrwg, mcp):

        if cat == 'tropical':
            if self.tropical_hitCheck == False:
                self.tropical += 1
                self.tropical_hitCheck = True
            self.tropical_days += 0.24
        if cat == 'C1':
            if self.C1_hitCheck == False:
                self.C1 += 1
                self.C1_hitCheck = True
            self.C1_days += 0.24
        if cat == 'C2':
            if self.C2_hitCheck is False:
                self.C2 += 1
                self.C2_hitCheck = True
            self.C2_days += 0.24
        if cat == 'C3':
            if self.C3_hitCheck is False:
                self.C3 += 1
                self.C3_hitCheck = True
            self.C3_days += 0.24
        if cat == 'C4':
            if self.C4_hitCheck is False:
                self.C4 += 1
                self.C4_hitCheck = True
            self.C4_days += 0.24
        if cat == 'C5':
            if self.C5_hitCheck is False:
                self.C5 += 1
                self.C5_hitCheck = True
            self.C5_days += 0.24

        if msws:
            self.MSWS_hit += 1
            if msws < self.MSWS_min:
                self.MSWS_min = msws
            if msws > self.MSWS_max:
                self.MSWS_max = msws
            self.MSWS_sum += msws
            self.MSWS_avg = (self.MSWS_sum / self.MSWS_hit)

        if mrwg:
            self.MRWG_hit += 1
            if mrwg < self.MRWG_min:
                self.MRWG_min = mrwg
            if mrwg > self.MRWG_max:
                self.MRWG_max = mrwg
            self.MRWG_sum += mrwg
            self.MRWG_avg = (self.MRWG_sum / self.MRWG_hit)

        if mcp:
            self.MCP_hit += 1
            if mcp < self.MCP_min:
                self.MCP_min = mcp
            if mcp > self.MCP_max:
                self.MCP_max = mcp
            self.MCP_sum += mcp
            self.MCP_avg = (self.MCP_sum / self.MCP_hit)

    def ResetHitCheck(self):

        self.tropical_hitCheck = False
        self.C1_hitCheck = False
        self.C2_hitCheck = False
        self.C3_hitCheck = False
        self.C4_hitCheck = False
        self.C5_hitCheck = False


def sph2xy(lon, lon_origin, lat, lat_origin):
    import numpy as np

    R = 6371 * 1e3
    dg2rad = scipy.pi / 180.0
    x = (R) * (lon - lon_origin) * (dg2rad) * (np.cos((lat_origin * dg2rad)))
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

def loadPlatformCsv(path, cls=PlatformRecord):
    with open(path, 'r') as inFile:
        dRdr = csv.DictReader(inFile)

        ret = []
        for row in dRdr:
            ret.append(cls(**row))

        return ret

def findNCDTInd(target, nc):

    ds = netCDF4.Dataset(nc)

    time_var = ds.variables['time']
    try:
        ind = netCDF4.date2index(target,time_var)
    except ValueError:
        return None, None
    else:
        return ds,ind


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
        #point1.Transform(coordTransform)

        point2 = ogr.Geometry(ogr.wkbPoint)
        point2.AddPoint(position_2[0], position_2[1])
        #point2.Transform(coordTransform)

        raw_dist = point2.Distance(point1)

        return raw_dist

def GetDistanceBetweenPoints(platform_coords_list, storm_coords_list, id, iso_t, sid):

    # get point from platform points based on attributes
    p_pt = platform_coords_list[id]

    # get point from storm point based on attributes
    s_pt = storm_coords_list[sid + '_' + iso_t]

    dist = GetDistance(p_pt, s_pt, None)

    return dist

def wind_radii_nederhoff(vmax=None, lat=None, region=None, probability=None, *args, **kwargs):
    import numpy as np

    # varargin = wind_radii_nederhoff.varargin
    # nargin = wind_radii_nederhoff.nargin

    # Function calculates RMW and R35 including RMSE needed for probablistic
    # forecasting of tropical cyclones
    # v1.0  Nederhoff   Jan-17
    # v1.1  Nederhoff   Feb-17
    # v1.2  Nederhoff   Jun-17
    # v1.3  Nederhoff   Aug-18
    # v1.4  Nederhoff   Mar-19
    # v1.5  Nederhoff   Sep-20

    ## Input
    # vmax in m/s, 10 meter height and 1-minute averaged
    # lat in degrees
    # region, see below
    # probablity if 1 script will generate 1000 realisations

    ## Idea: lognormal distributions for RMW and delta R35 based on curve fitting of the coefficients determing their shape
    # A-value is used for the standard deviation.
    # B-value is used for the median

    ## Area definitions                     METHOD 1 (-360 TO 0)                    METHOD 2 (-180 TO +180)
    # region 0: North Indian Ocean          (x<-260) & (y >w 0);
    # region 1: South West Indian Ocean     (x<-270) & (y < 0)
    # region 2: South East Indian Ocean	    (x>-270) & (x<-225) & (y < 0);
    # region 3: South Pacific Ocean'        (x>-225) & (AL < 0) & (y < 0);
    # region 4: North West Pacific Ocean    (x>-260) & (x<-180) & (y > 0);
    # region 5: North East Pacific Ocean    (x>-180) & (AL < 0) & (y > 0);
    # region 6: Atlantic Ocean              (x>-140) & (AL> 0) & (y>0)
    # region 7: all data points

    ## Area definitions                     METHOD 2 (-180 TO +180)
    # region 0: North Indian Ocean          (x > 0) & (x<+100) & (y > 0);
    # region 1: South West Indian Ocean     (x > 0) & (x<+90)  & (y < 0)
    # region 2: South East Indian Ocean	    (x>+90) & (x+135) & (y < 0);
    # region 3: South Pacific Ocean'        ( (x>+135) | (x < 0) ) & (y < 0);
    # region 4: North West Pacific Ocean    (x<+100) & (x>0) & (y > 0);
    # region 5: North East Pacific Ocean    (AL < 0) & (x<0) &  & (y > 0);
    # region 6: Atlantic Ocean              (AL > 0)
    # region 7: all data points

    # convert wind speed from knots to m/s
    if not isinstance(vmax, list):
        vmax = [vmax]

    vmax = np.divide(vmax, 0.93)

    vmax = np.multiply(vmax, 0.514)

    ## Radius of maximum winds (RMW or Rmax) in km
    # 1. Coefficients for A
    coefficients_a = [0.30698254, 0.338409237, 0.34279145, 0.36354649, 0.358572938, 0.310729085, 0.395431764, 0.370190027]
    # wind_radii_nederhoff.m:43
    # 2. Coefficients for B
    coefficients_b = [[132.4119062, 14.56403797, - 0.002597033, 20.38080365], [229.2458441, 9.538650691, 0.003988105, 28.44573672],
         [85.25766551, 30.69208726, 0.00243248, 5.781165406], [127.8333007, 11.84747574, 0.015936312, 25.46820005],
         [153.7332947, 11.47888854, 0.007471193, 28.94897887], [261.5288742, 7.011517854, 0.026191256, 29.20227871],
         [19.08992428, 24.08855731, 0.10624034, 23.18020146], [44.82417433, 23.37171288, 0.030469057, 22.42820361]]

    # wind_radii_nederhoff.m:53
    # 3. Get the best guess for a and b given wind speed and latitude
    a_value = np.dot(np.ones((1, len(vmax))), coefficients_a[region]).reshape(-1)
    # wind_radii_nederhoff.m:63
    # b_1 = np.dot(coefficients_b[0][region], np.exp(- vmax / coefficients_b[1][region]))
    # b_2 = np.multiply(b_1, (1 + np.dot(coefficients_b[2][region], abs(lat))))
    # b_3 = coefficients_b[3][region]
    # b_value = b_2 + b_3
    b_value = np.add(np.multiply(np.dot(coefficients_b[region][0], np.exp(-1*np.divide(vmax, coefficients_b[region][1]))),
                          (np.add(1, np.dot(coefficients_b[region][2], np.absolute(lat))))), coefficients_b[region][3])
    # wind_radii_nederhoff.m:64

    rmax={}
    rmax['mode'] = [None] * len(vmax)
    rmax['mean'] = [None] * len(vmax)
    rmax['median'] = [None] * len(vmax)
    rmax['lowest'] = [None] * len(vmax)
    rmax['highest'] = [None] * len(vmax)
    rmax['numbers'] = [None] * len(vmax)

    # 4. Compute 1000 delta R35 values
    for ii in range(a_value.shape[0]): #.reshape(-1):
        rmax['mode'][ii] = np.exp(np.log(b_value[ii]) - a_value[ii] ** 2)
        # wind_radii_nederhoff.m:68
        if probability == 1:
            numbers = np.sort(np.exp(np.add(np.multiply(np.random.randn(100000, 1), a_value[ii]), np.log(b_value[ii]))), axis=None)
            # wind_radii_nederhoff.m:70
            rmax['mean'][ii] = np.mean(numbers)
            # wind_radii_nederhoff.m:71
            rmax['mean'][ii] = np.exp(np.log(b_value[ii]) + (a_value[ii] ** 2) / 2)
            # wind_radii_nederhoff.m:72
            rmax['median'][ii] = np.median(numbers)
            # wind_radii_nederhoff.m:73
            # wind_radii_nederhoff.m:74
            rmax['median'][ii] = b_value[ii]
            rmax['lowest'][ii] = numbers[int(np.multiply(0.05, len(numbers)))]
            # wind_radii_nederhoff.m:75
            rmax['highest'][ii] = numbers[int(np.multiply(0.95, len(numbers)))]
            # wind_radii_nederhoff.m:76
            rmax['numbers'][ii] = np.copy(np.sort(numbers))
            # wind_radii_nederhoff.m:77

    ## Delta radius of 35 knots (R35)
    # 1. Coefficients for A
    # coefficients_a = np.concatenate(
    #     [0.121563729, - 0.052184289, 0.032953813, 0.131188105, - 0.044389473, 0.002253258, 0.122286754, - 0.045355772,
    #      0.013286154, 0.120490659, - 0.035029431, - 0.005249445, 0.156059522, - 0.041685377, 0.004952978, - 0.251333213,
    #      - 0.009072243, - 0.00506365, 0.131903526, - 0.042096876, 0.012443195, 0.190044585, - 0.044602083, 0.006117124])
    # # wind_radii_nederhoff.m:83
    # # 2. Coefficients for B
    # coefficients_b = np.concatenate(
    #     [30.92867473, 0.530681714, - 0.012001645, 30.21210133, 0.414897465, 0.021689596, 26.58686237, 0.425916004,
    #      0.028547278, 23.88007085, 0.43109144, 0.038119083, 33.26829485, 0.42859578, 0.017209431, 18.11013691,
    #      0.486399912, 0.02955688, 16.9973011, 0.453713419, 0.054643743, 29.61141102, 0.4132484, 0.024418947])
    # # wind_radii_nederhoff.m:93
    # # 3. Get the best guess for a and b given wind speed and latitude
    # a_value = coefficients_a[region + 1, 1] + np.multiply(np.exp(np.dot(vmax, coefficients_a[region + 1, 2])),
    #                                                       (1 + np.dot(coefficients_a[region + 1, 3], abs(lat))))
    # # wind_radii_nederhoff.m:103
    # b_value = np.multiply(np.multiply(coefficients_b[region + 1, 1], (vmax - 18) ** coefficients_b[region + 1, 2]),
    #                       (1 + np.dot(coefficients_b[region + 1, 3], abs(lat))))
    # # wind_radii_nederhoff.m:104
    # dr35 = {}
    # dr35['mode'] = list(range(1, len(a_value)))
    # dr35['mean'] = list(range(1, len(a_value)))
    # dr35['median'] = list(range(1, len(a_value)))
    # dr35['lowest'] = list(range(1, len(a_value)))
    # dr35['highest'] = list(range(1, len(a_value)))
    # dr35['numbers'] = None
    # # 4. Compute 1000 delta R35 values
    # for ii in range(1, len(a_value)): #.reshape(-1):
    #     if vmax > 20:
    #         dr35['mode'][ii] = np.exp(np.log(b_value(ii)) - a_value(ii) ** 2)
    #         # wind_radii_nederhoff.m:109
    #         if probability == 1:
    #             numbers = np.sort(np.exp(np.multiply(np.randn(100000, 1), a_value(ii)) + np.log(b_value(ii))))
    #             # wind_radii_nederhoff.m:111
    #             dr35['mean'][ii] = np.exp(np.log(b_value(ii)) + (a_value(ii) ** 2) / 2)
    #             # wind_radii_nederhoff.m:112
    #             dr35['median'][ii] = b_value(ii)
    #             # wind_radii_nederhoff.m:113
    #             dr35['lowest'][ii] = numbers[np.dot(0.05, len(numbers))]
    #             # wind_radii_nederhoff.m:114
    #             dr35['highest'][ii] = numbers[np.dot(0.95, len(numbers))]
    #             # wind_radii_nederhoff.m:115
    #             dr35['numbers'] = np.copy(np.sort(numbers))
    #             # wind_radii_nederhoff.m:116
    #     else:
    #         dr35['mode'][ii] = np.NaN
    #         # wind_radii_nederhoff.m:119

    return rmax #, dr35

def checkHurricaneEffect(platform, storm_lon, storm_lat, cat, wind_speed, wave, gust, lon_min, lat_min, mcp, sid, iso_t, platform_coords_list, storm_coords_list, basin, rmw):

    # Saffir-Simpson Scale Hurricane Category
    #Category  mph		m/s		kts
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

    # region 0: North Indian Ocean
    # region 1: South West Indian Ocean
    # region 2: South East Indian Ocean
    # region 3: South Pacific Ocean
    # region 4: North West Pacific Ocean
    # region 5: North East Pacific Ocean
    # region 6: Atlantic Ocean
    # region 7: all data points

    # if category is -1 or below, return None
    if cat < 0:
        return None

    category = None
    radius = None
    region = None

    # if the radius of maximum winds is not given, calculate it
    if rmw is not None:
        radius = rmw
    else:
        if basin == 'NI':
            region = 0
        if basin == 'SA':
            region = 1
        if basin == 'SP':
            region = 3
        if basin == 'WP':
            region = 4
        if basin == 'EP':
            region = 5
        if (basin == 'NA') or (basin == 'SA'):
            region = 6

        rmw_results = wind_radii_nederhoff(vmax=wind_speed, lat=storm_lat, region=region, probability=1)
        radius = rmw_results['median'][0] * 1000 # convert km to m
        print('RMW results: {} m'.format(radius))

    if cat is not None:
        if cat == 0:
            #radius = 100000
            category = 'tropical'
        if cat == 1:
            #radius = 300000
            category = 'C1'
        if cat == 2:
            #radius = 300000
            category = 'C2'
        if cat == 3:
            #radius = 450000
            category = 'C3'
        if cat == 4:
            # radius = 450000
            category = 'C4'
        if cat == 5:
            # radius = 450000
            category = 'C5'
    else:
        # if there is no category given, use the wind speed to approximate radius
        if wind_speed is not None:
            wind_speed = float(wind_speed)
            if (wind_speed >= 34) and (wind_speed < 64):
                # radius = 100000
                category = 'tropical'
            if (wind_speed >= 64) and (wind_speed < 83):
                # radius = 300000
                category = 'C1'
            if (wind_speed >= 83) and (wind_speed < 96):
                # radius = 300000
                category = 'C2'
            if (wind_speed >= 96) and (wind_speed < 113):
                # radius = 450000
                category = 'C3'
            if (wind_speed >= 113) and (wind_speed < 137):
                # radius = 450000
                category = 'C4'
            if wind_speed >= 137:
                # radius = 450000
                 category = 'C5'

    if radius is not None:
        # convert lat and long coordinates (degrees) into x and y (meters)
        #storm_x, storm_y = sph2xy(storm_lon, lon_min, storm_lat, lat_min)
        # use squared distance function to determine if the platform lies within the hurricane buffer
        #distance = np.sqrt((((platform.x - storm_x) ** 2) + ((platform.y - storm_y) ** 2)))

        # get distance between the two points
        distance = GetDistanceBetweenPoints(platform_coords_list, storm_coords_list, platform.id, iso_t, sid)

        if distance <= radius:
            # update platform record with stat
            platform.addValue(category, wave, wind_speed, gust, mcp)

            return category
        else:
            return None
    else:
        print('No radius found...')
        return None


def processStats(platform, numStorms, lat, lon, time, categ, msw, wave, gust, lon_min, lat_min, mcp, basin, region, sid, iso_time, platform_coords_list, storm_coords_list, s_rmw):
    # loop through each storm
    error_count = 0
    # set year to none for later
    year = None
    YearStats = YearlyRecord()

    for i in range(0, numStorms):
        # make sure storm hitCheck is False to begin each storm
        platform.ResetHitCheck()
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
            basin_storm = basin[i:i + 1].tolist()[0]
            region_storm = region[i:i + 1].tolist()[0]
            sid_storm = sid[i:i + 1].tolist()[0]
            iso_time_storm = iso_time[i:i + 1].tolist()[0]
            rmw_storm = s_rmw[i:i + 1].tolist()[0]
        except:
            error_count += 1
            print("Read failed, storm # " + format(i))
            continue

        sid_list = sid_storm
        sid_num = b''.join(sid_list).decode('utf-8')

        # for each storm loop through all observations
        # for lat_s, lon_s, time_s, msw_s in zip(lat_storm,lon_storm,time_storm,msw_storm):
        for t in range(0, len(time_storm)):

            if region_storm[t][0] is not None:

                #r_list = region_storm[t]
                #r_reg = b''.join(r_list)

                basin_iso = b''.join(basin_storm[t]).decode('utf-8')

                # if (r_reg == b'GM') or (r_reg == b'NA'):

                # turn time_v into datetime object
                try:
                    iso_t = b"".join(iso_time_storm[t]).decode("utf-8")
                    timeObs = readStormDateTime_ISO(iso_t)
                # timeObs_next = readStormDateTime(time_storm[t+1])
                except TypeError:
                    # occurs when the time variable is missing
                    continue
                # keep track of the year for processing stats per year
                if year is None:
                    year = timeObs.year

                # if the year has changed, update the PlatformRecord with
                # the yearly stats and start new YearlyRecord
                if timeObs.year != year:
                    # update platform yearly stats with YearRecord
                    platform.UpdateYearlyStats(YearStats)
                    # reset YearRecord
                    YearStats = YearlyRecord()
                    # reset year
                    year = timeObs.year

                # if there is no platform install date, skip it because we cannot accurately know how long
                # the platform has been in service
                if platform.install_date is None:
                    continue

                if (platform.remove_date is None) and (timeObs >= platform.install_date):
                    # check whether or not the platform is affected by the storm and by what category
                    categ_hit = checkHurricaneEffect(platform, lon_storm[t], lat_storm[t], cat_storm[t], msw_storm[t], wave_storm[t], gust_storm[t], lon_min, lat_min, mcp_storm[t], sid_num, iso_t, platform_coords_list, storm_coords_list, basin_iso, rmw_storm[t])
                    # if the platform was "hit" by the hurricane, update the yearly stats
                    if categ_hit is not None:
                        YearStats.AddHit(categ_hit, msw_storm[t], gust_storm[t], mcp_storm[t])

                    continue

                # check if the time is between the platform install and removal date or no removal date
                if (timeObs >= platform.install_date) and (timeObs <= platform.remove_date):
                    # check whether or not the platform is affected by the storm and by what category
                    categ_hit = checkHurricaneEffect(platform, lon_storm[t], lat_storm[t], cat_storm[t], msw_storm[t], wave_storm[t], gust_storm[t], lon_min, lat_min, mcp_storm[t], sid_num, iso_t, platform_coords_list, storm_coords_list,  basin_iso, rmw_storm[t])
                    # if the platform was "hit" by the hurricane, update the yearly stats
                    if categ_hit is not None:
                        YearStats.AddHit(categ_hit, msw_storm[t], gust_storm[t], mcp_storm[t])

    # update platform yearly stats with YearRecord
    platform.UpdateYearlyStats(YearStats)

    print(format(error_count) + ' number of storms failed to read')

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

def runStatsForStorms(platforms, ncDir, start_date, stop_date, platform_coords_list, storm_coords_list):

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
        c_basin = ds.variables['basin']
        c_region = ds.variables['subbasin']
        c_sid = ds.variables['sid']
        c_rmw = ds.variables['usa_rmw']

        # note number of storms in netCDF
        dsLen = len(ds.dimensions['storm'])
        # keeping track of platform records
        n = 1
        plat_length = len(platforms)
        # loop over each platform record
        for p in platforms:

            asd = p.lat

            if p.lat == asd:

                print('Completing ' + format(n) + ' out of ' + format(plat_length) + ' platform records')
                # print('Platform Record: ' + format(n))
                # calculate the x and y coordinates for the platform
                p.x, p.y = sph2xy(p.lon, lon_min, p.lat, lat_min)
                processStats(p, dsLen, c_lat, c_lon, c_time, c_cat, c_msw, c_wave, c_gust, lon_min, lat_min, c_mcp, c_basin, c_region, c_sid, c_time_iso, platform_coords_list, storm_coords_list, c_rmw)
                n += 1

                # clean platform record
                p.Clean()

        end = time.time()
        print(end - start)


def writeResultsToCSV(platforms, outpath):

    with open(outpath, 'w', newline='') as outfile:

        wtr = csv.writer(outfile)
        # write header
        hdr = ['PlatformID', 'Total Storms', 'Cat None Count', 'Tropical Sum','Tropical Min Yearly','Tropical Max Yearly','Tropical Mean Yearly',\
               'Tropical Days Sum','Tropical Days Min Yearly','Tropical Days Max Yearly', 'Tropical Days Mean Yearly',\
               'C1 Sum','C1 Min Yearly','C1 Max Yearly','C1 Mean Yearly','C1 Days Sum','C1 Days Min Yearly','C1 Days Max Yearly','C1 Days Mean Yearly',\
               'C2 Sum','C2 Min Yearly','C2 Max Yearly','C2 Mean Yearly','C2 Days Sum','C2 Days Min Yearly','C2 Days Max Yearly','C2 Days Mean Yearly',\
               'C3 Sum','C3 Min Yearly','C3 Max Yearly','C3 Mean Yearly','C3 Days Sum','C3 Days Min Yearly','C3 Days Max Yearly','C3 Days Mean Yearly',\
               'C4 Sum','C4 Min Yearly','C4 Max Yearly','C4 Mean Yearly','C4 Days Sum','C4 Days Min Yearly','C4 Days Max Yearly','C4 Days Mean Yearly',\
               'C5 Sum','C5 Min Yearly','C5 Max Yearly','C5 Mean Yearly','C5 Days Sum','C5 Days Min Yearly','C5 Days Max Yearly','C5 Days Mean Yearly',\
               'Wave Height Count', 'Wave Height None Count', 'Wave Height Sum', 'Wave Height Min', 'Wave Height Max', 'Wave Height Average',\
               'MSWS Count', 'MSWS None Count', 'MSWS Sum', 'MSWS Min', 'MSWS Max', 'MSWS Average',\
               'MSWS Max Yearly of Min', 'MSWS Sum Yearly of Min', 'MSWS Mean Yearly of Min',\
               'MSWS Min Yearly of Max', 'MSWS Sum Yearly of Max', 'MSWS Mean Yearly of Max',\
               'MSWS Min Yearly of Sum', 'MSWS Max Yearly of Sum', 'MSWS Mean Yearly of Sum',\
               'MSWS Min Yearly of Mean', 'MSWS Max Yearly of Mean', 'MSWS Sum Yearly of Mean', 'MSWS Mean Yearly of Mean',\
               'MRWG Count', 'MRWG None Count', 'MRWG Sum', 'MRWG Min', 'MRWG Max', 'MRWG Average',\
               'MRWG Max Yearly of Min', 'MRWG Sum Yearly of Min', 'MRWG Mean Yearly of Min',\
               'MRWG Min Yearly of Max', 'MRWG Sum Yearly of Max', 'MRWG Mean Yearly of Max',\
               'MRWG Min Yearly of Sum', 'MRWG Max Yearly of Sum', 'MRWG Mean Yearly of Sum',\
               'MRWG Min Yearly of Mean', 'MRWG Max Yearly of Mean', 'MRWG Sum Yearly of Mean', 'MRWG Mean Yearly of Mean',\
               'MCP Count', 'MCP None Count', 'MCP Sum', 'MCP Min', 'MCP Max', 'MCP Average',\
               'MCP Max Yearly of Min', 'MCP Sum Yearly of Min', 'MCP Mean Yearly of Min',\
               'MCP Min Yearly of Max', 'MCP Sum Yearly of Max', 'MCP Mean Yearly of Max',\
               'MCP Min Yearly of Sum', 'MCP Max Yearly of Sum', 'MCP Mean Yearly of Sum',\
               'MCP Min Yearly of Mean', 'MCP Max Yearly of Mean', 'MCP Sum Yearly of Mean', 'MCP Mean Yearly of Mean',\
               ]
        wtr.writerow(hdr)

        sPlats = sorted(platforms, key=lambda x: x.id)
        for p in sPlats:

            row = [p.id] + [p.stormTotal] + [p.cat_noneCount] + \
                  [p.tropical] + [p.tropical_min] + [p.tropical_max] + [p.tropical_mean] + \
                  [p.tropical_days] + [p.tropical_days_min] + [p.tropical_days_max] + [p.tropical_days_mean] + \
                  [p.C1] + [p.C1_min] + [p.C1_max] + [p.C1_mean] + \
                  [p.C1_days] + [p.C1_days_min] + [p.C1_days_max] + [p.C1_days_mean] + \
                  [p.C2] + [p.C2_min] + [p.C2_max] + [p.C2_mean] + \
                  [p.C2_days] + [p.C2_days_min] + [p.C2_days_max] + [p.C2_days_mean] + \
                  [p.C3] + [p.C3_min] + [p.C3_max] + [p.C3_mean] + \
                  [p.C3_days] + [p.C3_days_min] + [p.C3_days_max] + [p.C3_days_mean] + \
                  [p.C4] + [p.C4_min] + [p.C4_max] + [p.C4_mean] + \
                  [p.C4_days] + [p.C4_days_min] + [p.C4_days_max] + [p.C4_days_mean] + \
                  [p.C5] + [p.C5_min] + [p.C5_max] + [p.C5_mean] + \
                  [p.C5_days] + [p.C5_days_min] + [p.C5_days_max] + [p.C5_days_mean] + \
                  [p.waveHeightCount] + [p.waveHeightNoneCount] + [p.waveHeightSum] + [p.waveHeightMin] + [p.waveHeightMax] + [p.waveHeightAverage] + \
                  [p.windCount] + [p.windNoneCount] + [p.windSum] + [p.windMin] + [p.windMax] + [p.windAverage] + \
                  [p.windYearlyMax_min] + [p.windYearlySum_min] + [p.windYearlyAvg_min] + \
                  [p.windYearlyMin_max] + [p.windYearlySum_max] + [p.windYearlyAvg_max] + \
                  [p.windYearlyMin_sum] + [p.windYearlyMax_sum] + [p.windYearlyAvg_sum] + \
                  [p.windYearlyMin_avg] + [p.windYearlyMax_avg] + [p.windYearlySum_avg] + [p.windYearlyAvg_avg] + \
                  [p.gustCount] + [p.gustNoneCount] + [p.gustSum] + [p.gustMin] + [p.gustMax] + [p.gustAverage] + \
                  [p.gustYearlyMax_min] + [p.gustYearlySum_min] + [p.gustYearlyAvg_min] + \
                  [p.gustYearlyMin_max] + [p.gustYearlySum_max] + [p.gustYearlyAvg_max] + \
                  [p.gustYearlyMin_sum] + [p.gustYearlyMax_sum] + [p.gustYearlyAvg_sum] + \
                  [p.gustYearlyMin_avg] + [p.gustYearlyMax_avg] + [p.gustYearlySum_avg] + [p.gustYearlyAvg_avg] + \
                  [p.MCPCount] + [p.MCPNoneCount] + [p.MCPSum] + [p.MCPMin] + [p.MCPMax] + [p.MCPAverage] + \
                  [p.mcpYearlyMax_min] + [p.mcpYearlySum_min] + [p.mcpYearlyAvg_min] + \
                  [p.mcpYearlyMin_max] + [p.mcpYearlySum_max] + [p.mcpYearlyAvg_max] + \
                  [p.mcpYearlyMin_sum] + [p.mcpYearlyMax_sum] + [p.mcpYearlyAvg_sum] + \
                  [p.mcpYearlyMin_avg] + [p.mcpYearlyMax_avg] + [p.mcpYearlySum_avg] + [p.mcpYearlyAvg_avg]

            wtr.writerow(row)

if __name__ == "__main__":

    nc_dir = r'P:\01_DataOriginals\GOM\Metocean\StormData\1842-2021'
    platform_csv = r"C:\Users\dyera\Documents\Offshore Task 3\MEtocean\all_platforms_ver5_A_only20.csv"
    output_path = r"C:\Users\dyera\Documents\Offshore Task 3\MEtocean\Hurricane Processing Ver 7 Test\hurricane_output_AllPlatforms_08042021_Only20_TEST.csv"
    platform_points = r"C:\Users\dyera\Documents\Offshore Task 3\Shapefiles\All_Platforms_08042021_GomAlbers.shp"
    #platform_points_name = 'All_Platforms_GomAlbers'
    storm_points = r'C:\Users\dyera\Documents\Offshore Task 3\GradientBoostingRegressor\1.DATA\Shapefiles\hurricane_points_GomAlbers.shp'
    #storm_points_name = 'IBTRACS_NA_Points_GomAlbers'

    radius = wind_radii_nederhoff(vmax=[35,40,45,50,55,60,65,70], lat=[22,23,24,25,26,27,28,29], region=1, probability=1)

    prsr = ArgumentParser(description="Generate Stats per platform")
    prsr.add_argument('platform_csv', type=str,
                      help='csv with platform data')
    prsr.add_argument('nc_dir', type=str, help='path to directory containing netcdf data')
    prsr.add_argument('outputs', type=str, help='path to output data')
    prsr.add_argument('--start_date', type=readPlatDateTime, default=FIRST_DATE, help='Start of querying period')
    prsr.add_argument('--stop_date', type=readPlatDateTime, default=LAST_DATE, help='End of querying period')
    prsr.add_argument('--stats', '-s', nargs='+', help='statistics to run')

    args = prsr.parse_args([platform_csv, nc_dir, output_path])

    if args.start_date >= args.stop_date:
        raise Exception('start_date must proceed stop_date')

    # open platform and storm points and get IDs and coordinates as a list
    platform_coords_list = GetPlatformCoords(platform_points)
    storm_coords_list = GetStormCoords(storm_points)

    # load the platforms csv
    platforms = loadPlatformCsv(args.platform_csv)

    runStatsForStorms(platforms, os.path.join(args.nc_dir, '*.nc'), args.start_date, args.stop_date, platform_coords_list, storm_coords_list)

    writeResultsToCSV(platforms, output_path)