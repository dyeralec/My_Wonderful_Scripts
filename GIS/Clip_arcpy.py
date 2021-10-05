import arcpy
from arcpy import env
import os

# going to loop through all shapefiles in a folder to do the clip
shpDir = r"P:\01_DataOriginals\World\Geology\BlueHabitat Seafloor Geomorphology"
# setting environment to the shapefile folder
env.workspace = shpDir

# extent to clip to
mask = r"P:\03_DataFinal\GOM\Boundaries\MiscBoundaries\GOM_Extent\GOMAllExtent\Bathy_Mask.shp"

# output directory
outputDir = r"P:\02_DataWorking\GOM\Geology\Geomorphology"

# loop through directory
for filename in os.listdir(shpDir):
    if filename.endswith(".shp"):
        outputLayer = os.path.join(outputDir, filename)
        arcpy.Clip_analysis(filename, mask, outputLayer)
        print('{} clip successful.'.format(filename))