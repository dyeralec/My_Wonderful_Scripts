""""""
"""This code will take mulitple csv's and use the latitude and longitude fields to create a points shapefile with all of the attributes associated."""

import arcpy
import os

# set environment variables
arcpy.env.workspace = r"P:\01_DataOriginals\GOM\Infrastructure\Emissions\2017_Gulfwide_Platform_Inventory_20190705_CAP_GHG\Shapefiles.csv"
# NOTE: for this code there are sub-folders within this dataFolder that will be iterated through
dataFolder = r'"P:\01_DataOriginals\GOM\Infrastructure\Emissions\2017_Gulfwide_Platform_Inventory_20190705_CAP_GHG\2017_Gulfwide_Platform_20190705_CAP_GHG.csv"'
outputFolder = r"P:\01_DataOriginals\GOM\Infrastructure\Emissions\2017_Gulfwide_Platform_Inventory_20190705_CAP_GHG\Shapefiles"
# set spatial coordinate system
spRef = arcpy.SpatialReference(4267)
# set latitude variable name
lat = 'Y_COORDINATE'
long = 'X_COORDINATE'

# loop through the subfolders within the dataFolder. Code found from https://stackoverflow.com/questions/19587118/iterating-through-directories-with-python
for subdir, dirs, files in os.walk(dataFolder):
    for file in files:
        # create variable of full path location
        file_location = os.path.join(subdir, file)
        
        # try to use the file, but if it is not a csv print the except block
        try:
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