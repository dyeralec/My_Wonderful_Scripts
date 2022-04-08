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

env.overwriteOutput = True

# mask feature
# maskLayer = r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Submarine Landslide Analysis\SubmarineLandslides\LandslideGeodatabase.gdb\DistanceFrom_anomaly_channels_GomAlbers"
# raster layer with cell resolution wanted for output
# cellSizeLayer = ''
# layer to limit extent
extentLayer = r"C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\ML Testing\Multi Scale Testing\Data\1000 m Res\Aspect.tif"
# set output folder or geodatabase
# outputDir = r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Submarine Landslide Analysis\SubmarineLandslides\LandslideGeodatabase.gdb"
# output coordinate system
outputCS = r"P:\03_DataFinal\GOM\!SpatialReference\GomAlbers84.prj"

# set up arcpy environments
# env.mask = maskLayer
env.extent = extentLayer
env.outputCoordinateSystem = outputCS

# check out Spatial Analyst extenstion
arcpy.CheckOutExtension("Spatial")

# create list of features to loop through
layers = {
    # 'anomalies': r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Submarine Landslide Analysis\SubmarineLandslides\SubmarineLandslides.gdb\SeepRelatedAnomalies_GomAlbers",
    'basins': r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Submarine Landslide Analysis\SubmarineLandslides\SubmarineLandslides.gdb\Basins",
    # 'canyons': r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Data\Data_GomAlbers.gdb\Canyons",
    # 'channels': r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Submarine Landslide Analysis\SubmarineLandslides\SubmarineLandslides.gdb\anomaly_channels_GomAlbers",
    # 'escarpment': r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Submarine Landslide Analysis\SubmarineLandslides\SubmarineLandslides.gdb\Escarpments",
    # 'salt': r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Data\Data_GomAlbers.gdb\gcdiapirg",
    # 'fault': r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Data\Data_GomAlbers.gdb\faults_Task2_USGS_merged",
    # 'mud_volcanoes': r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Submarine Landslide Analysis\SubmarineLandslides\SubmarineLandslides.gdb\seep_anomaly_confirmed_mud_volcanoes_GomAlbers",
    # 'pockmarks': r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Submarine Landslide Analysis\SubmarineLandslides\SubmarineLandslides.gdb\seep_anomaly_pockmarks_GomAlbers",
    # 'gas': r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Submarine Landslide Analysis\SubmarineLandslides\SubmarineLandslides.gdb\seep_anomaly_confirmed_gas_merged",
    # 'hydrate': r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Submarine Landslide Analysis\SubmarineLandslides\SubmarineLandslides.gdb\hydrates_BOEM_USGS_merge",
}

cell_sizes = [100, 250, 500, 1000, 2000]

for s in cell_sizes:

    print(s)

    env.cellSize = s

    outputDir = r"C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\ML Testing\Multi Scale Testing\Data\{} m Res".format(str(s))

    for feature in layers:
        # output raster layer
        outputRaster = os.path.join(outputDir, "{}.tif".format(feature))

        # run Path Distance function in arcpy
        distanceRaster = EucDistance(layers[feature], distance_method='PLANAR')

        # save output
        distanceRaster.save(outputRaster)

        print("{} distance raster complete".format(feature))