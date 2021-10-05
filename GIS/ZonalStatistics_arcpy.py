# Name: ZonalStatistics_arcpy.py
# Description: Summarizes values of a raster within the zones of
#              another dataset and reports the results to a table.
# Requirements: Spatial Analyst Extension

# Import system modules
import arcpy
from arcpy import env
from arcpy.sa import *

# Set environment settings
env.workspace = r'C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\GISApproach\Zonal Statistics\Zonal Statistics Ver 1\Area 1'
env.overwriteOutput = True

# Set local variables
inZoneData = "zones.shp"
inZoneRaster = r'C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\Data Prep\Landslides\Area 1\Landslides_Area1.tif'
# zoneField = "Classes"
inValueRaster = r"C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\GISApproach\Outputs\LS_RiskBased_Output.tif"
# outputFolder =


# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

# Execute ZonalStatisticsAsTable
outZSaT = ZonalStatisticsAsTable(inZoneRaster, 'value', inValueRaster,
                                 'ZonalStatistics_table.dbf', "DATA", "ALL")
# save dbf as csv
arcpy.conversion.TableToTable(outZSaT, env.workspace, 'ZonalStatistics_table.csv')

# Execute Zonal Histogram
# result = ZonalHistogram(inZoneRaster, 'value', inValueRaster, 'ZonalHistogram_table.dbf', 'ZonalHistogram_graph')

# Save dbf as csv
# arcpy.conversion.TableToTable(result, env.workspace, 'ZonalHistogram_table.csv')

#Execute SaveGraph
# arcpy.SaveGraph_management(result, 'ZonalHistogram_graph.png')