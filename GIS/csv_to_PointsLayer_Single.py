""""""
"""This code will take mulitple csv's and use the latitude and longitude fields to create a points shapefile with all of the attributes associated."""

import arcpy
import os

# set environment variables
mainFolder = r"R:\GEOWorkspace\C_Projects\BOEM IAA\Data Processing\BSEE Incidents"
arcpy.env.workspace = mainFolder
# NOTE: for this code there are sub-folders within this dataFolder that will be iterated through
CsvName = r"Matched_Incidents_Reformatted_Redacted.csv"
outputFolder = mainFolder
# set spatial coordinate system
spRef = arcpy.SpatialReference(4267)
# set latitude variable name
lat = 'P_LATITUDE'
long = 'P_LONGITUDE'

# try to use the file, but if it is not a csv print the except block

# set the input table to use
inCSV = os.path.join(mainFolder, CsvName)
# set x and y coordinates from lat and long above
x_coords = long
y_coords = lat
# there are no z coordinates so setting it as blank
z_coords = ""
# create name for the layer
outLayer = format(CsvName.replace('.csv', '')) # may need reformatting
# create the location and name of the shapefile that is going to be saved
savedLayer = os.path.join(outputFolder, CsvName.replace('.csv',''))
# set the spatial reference
spRef = spRef
# create table
#arcpy.TableToTable_conversion(inCSV, outputFolder, CsvName.replace('.csv','.dbf'))
# path to new table
#table = os.path.join(outputFolder, CsvName.replace('.csv','.dbf'))
# make the XY event layer
#arcpy.MakeXYEventLayer_management(table, x_coords, y_coords, outLayer, spRef, z_coords)
# use table to feature tool
arcpy.management.XYTableToPoint(inCSV, savedLayer, long, lat, None, spRef)
# save to layer file
arcpy.SaveToLayerFile_management(savedLayer, outLayer + '.shp')