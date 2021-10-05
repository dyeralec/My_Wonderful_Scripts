"""
Script to run the Zonal Histogram tool in Arcpy using one shapefile
and a list of rasters
"""

import os
import arcpy
from arcpy.sa import *

arcpy.env.overwriteOutput = True

# path to the input zone data, as shapefile or feature class
zones = r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Submarine Landslide Analysis\SubmarineLandslides\SubmarineLandslides.gdb\LandslideSources_Merge"
zoneField = "OBJECTID"
attributeField = 'Source'
attributes = [
    #'NETL',
    "2007 Twichell, et al.",
    "2019 Sawyer et al.",
    "BOEM Seismic Anomalies"
]

# lists of the raster and zone field within a list
rasters_valueField= [
    # r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Arc Image Analyst\boem_composite-gdb\BOEM_Compoiste_Bands.gdb\BOEM_Bathymetry_Slope_Mosaic",
    # r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Arc Image Analyst\boem_composite-gdb\BOEM_Compoiste_Bands.gdb\BOEM_Bathymetry_Curvature_Mosaic",
    # r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Arc Image Analyst\boem_composite-gdb\BOEM_Compoiste_Bands.gdb\BOEM_Bathymetry_Aspect_Mosaic",
    # r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Arc Image Analyst\boem_composite-gdb\BOEM_Compoiste_Bands.gdb\BOEM_Bathymetry_PlanCurvature_Mosaic",
    # r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Arc Image Analyst\boem_composite-gdb\BOEM_Compoiste_Bands.gdb\BOEM_Bathymetry_ProfileCurvature_Mosaic",
    r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Submarine Landslide Analysis\SubmarineLandslides\SubmarineLandslides.gdb\usSEABED_domnc"
]

# directory where the output table will be
outputDirectory = r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Submarine Landslide Analysis\Zonal Statistics\ZonalHistograms.gdb"
outputDirectory_CSVs = r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Submarine Landslide Analysis\Zonal Statistics"

# loop through all attributes to choose from
for att in attributes:

    query = '"{}" = '.format(attributeField) + "'{}'".format(att)

    selectedLayer = arcpy.SelectLayerByAttribute_management(zones, "NEW_SELECTION", query)

    for raster in rasters_valueField:

        # get name of raster
        rasterName = raster.rsplit('\\', 1)[1]
        # path to output table
        outputTable = os.path.join(outputDirectory, 'ZonalHist_' + att.replace(' ','').replace(',','').replace('.','') + '_' + rasterName) # remove raster extension, if any
        # try to run zonal histogram, but may fail if the selected zones are not within the region
        try:
            # run zonal histogram tool
            outZonalHist = ZonalHistogram(selectedLayer, zoneField, raster, outputTable)
        except:
            print('No zones for {} were within the raster region'.format(att))
            continue
        # Convert Table To CSV File
        arcpy.TableToTable_conversion(outZonalHist, outputDirectory_CSVs, 'ZonalHist_' + att.replace(' ','').replace(',','').replace('.','') + '_' + rasterName + '.csv')

        print('zonal histogram for {} complete within {} zones.'.format(rasterName, att))