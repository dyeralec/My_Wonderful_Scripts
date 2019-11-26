""""""
"""This code will take mulitple csv's and use the latitude and longitude fields to create a points shapefile with all of the attributes associated."""

import arcpy
import os

# set environment variables
arcpy.env.workspace = r'P:\02_DataWorking\GOM\Infrastructure\Rigs\RigMovements\Shapefiles_Rasters\RigPoints_YearMonth'
# NOTE: for this code there are sub-folders within this dataFolder that will be iterated through
dataFolder = r'P:\02_DataWorking\GOM\Infrastructure\Rigs\RigMovements\Month_Year_Tables'
outputFolder = r'P:\02_DataWorking\GOM\Infrastructure\Rigs/RigMovements\Shapefiles_Rasters\RigPoints_YearMonth'
# set spatial coordinate system
spRef = arcpy.SpatialReference(4326)
# set latitude variable name
lat = 'RigLa_55'
long = 'RigLo_56'

# loop through the subfolders within the dataFolder. Code found from https://stackoverflow.com/questions/19587118/iterating-through-directories-with-python
for subdir, dirs, files in os.walk(dataFolder):
    for file in files:
        # try to use the file, but if it is not a csv print the except block
        try:
            # create variable of full path location
            file_location = os.path.join(subdir,file)
            # set the input table to use
            in_Table = file_location
            # set x and y coordinates from lat and long above
            x_coords = long
            y_coords = lat
            # there are no z coordinates so setting it as blank
            z_coords = ""
            # create name for the layer
            out_Layer = format(file.replace('.csv', '')) + '_points' # may need reformatting
            # create the location and name of the shapefile that is going to be saved
            saved_Layer = format(outputFolder) + '/' + format(file.replace('.csv',''))
            # set the spatial reference
            spRef = spRef
            # make the XY event layer
            arcpy.MakeXYEventLayer_management(in_Table, x_coords, y_coords, out_Layer, spRef, z_coords)
            # save to layer file
            arcpy.SaveToLayerFile_management(out_Layer, saved_Layer)
        except:
            print(file_location + ' is not supported')