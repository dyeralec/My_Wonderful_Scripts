"""
Creates a continuous surface showing the distance from a feature.
A mask can be used to limit the continuous surface areal coverage.

created by Alec Dyer
alec.dyer@netl.doe.gov
"""

import arcpy
from arcpy import env
from arcpy.sa import *
import os

env.overwriteOutput

# mask feature
maskLayer = r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Submarine Landslide Analysis\SubmarineLandslides\LandslideGeodatabase.gdb\DistanceFrom_anomaly_channels_GomAlbers"
# raster layer with cell resolution wanted for output
cellSizeLayer = ''
# layer to limit extent
extentLayer = r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Bathy\Bathy.gdb\GEBCO_2020_GomAlbers"
# set output folder or geodatabase
outputDir = r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Submarine Landslide Analysis\SubmarineLandslides\LandslideGeodatabase.gdb"
# output coordinate system
outputCS = r"P:\03_DataFinal\GOM\!SpatialReference\GomAlbers84.prj"

# set up arcpy environments
env.cellSize = 451.994232873225
env.mask = maskLayer
env.extent = extentLayer
env.outputCoordinateSystem = outputCS

# check out Spatial Analyst extenstion
arcpy.CheckOutExtension("Spatial")

# create list of features to loop through
list = [
    # r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Submarine Landslide Analysis\SubmarineLandslides\SubmarineLandslides.gdb\anomaly_channels_GomAlbers",
    # r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Submarine Landslide Analysis\SubmarineLandslides\SubmarineLandslides.gdb\anomaly_salt_GomAlbers",
    # r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Submarine Landslide Analysis\SubmarineLandslides\SubmarineLandslides.gdb\gcfaultsg_GomAlbers",
    # r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Submarine Landslide Analysis\SubmarineLandslides\SubmarineLandslides.gdb\gcfltzoneg_GomAlbers",
    # r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Submarine Landslide Analysis\SubmarineLandslides\SubmarineLandslides.gdb\plumes_Ek60_points_GomAlbers",
    # r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Submarine Landslide Analysis\SubmarineLandslides\SubmarineLandslides.gdb\plumes_EM302_400ft_diam_GomAlbers",
    # r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Submarine Landslide Analysis\SubmarineLandslides\SubmarineLandslides.gdb\seep_anomaly_confirmed_mud_volcanoes_GomAlbers",
    # r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Submarine Landslide Analysis\SubmarineLandslides\SubmarineLandslides.gdb\seep_anomaly_mud_volcanoes_GomAlbers",
    # r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Submarine Landslide Analysis\SubmarineLandslides\SubmarineLandslides.gdb\seep_anomaly_pockmarks_GomAlbers",
    # r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Submarine Landslide Analysis\SubmarineLandslides\SubmarineLandslides.gdb\seep_anomaly_positives_confirmed_gas_GomAlbers",
    # r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Submarine Landslide Analysis\SubmarineLandslides\SubmarineLandslides.gdb\seep_GomAlbers",
    # r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Submarine Landslide Analysis\SubmarineLandslides\SubmarineLandslides.gdb\gcdiapirg_GomAlbers",
    # r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Submarine Landslide Analysis\SubmarineLandslides\SubmarineLandslides.gdb\Country_Boundaries_GomAlbers.shp",
    # r"P:\01_DataOriginals\GOM\Geology\USGS GLORIA\seep\seep.shp"
    # r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Submarine Landslide Analysis\SubmarineLandslides\SubmarineLandslides.gdb\hydrates_BOEM_USGS_merge",
    r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Submarine Landslide Analysis\SubmarineLandslides\SubmarineLandslides.gdb\SeepRelatedAnomalies_GomAlbers"
]


for feature in list:
    # output raster layer
    outputName = feature.rsplit('\\',1)[1]
    outputRaster = os.path.join(outputDir, "DistanceFrom_{}".format(outputName.replace('.shp','')))

    # run Path Distance function in arcpy
    distanceRaster = EucDistance(feature, distance_method='GEODESIC')

    # save output
    distanceRaster.save(outputRaster)

    print("{} distance raster complete".format(outputName))