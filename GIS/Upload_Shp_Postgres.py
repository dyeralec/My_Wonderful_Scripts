#import psycopg2
#from osgeo import ogr
#import pandas as pd
#import ogr2ogr
import os
from osgeo import ogr

# using ogr2ogr in python this function will upload a shp file to the postgres database
def upload_file(filename, directory):
    
    path = os.path.join(directory,filename)
    
    geom = GetGeomType_OGR(directory, filename, 'ESRI Shapefile')
    
    if geom == 1:
        geom_name = 'POINT'
    if geom == 2:
        geom_name = 'LINESTRING'
    if geom == 3:
        geom_name = 'POLYGON'
    
    # upload shapefile
    # use try blocks to catch errors
    # try:
    #     os.system('ogr2ogr -f "PostgreSQL" PG:"host=10.50.45.73 user=postgres dbname=BOEM_IAA password=postgres" "{}"'.format(path))
    #     print('Upload for {} complete.'.format(filename))
    #
    # except:
    try:
        os.system('ogr2ogr -f "PostgreSQL" PG:"host=10.50.45.73 user=postgres dbname=BOEM_IAA password=postgres" "{}" -nlt {} -lco overwrite=YES'.format(path, geom_name))
        print('Upload for {} complete.'.format(filename))
        
    except:
        print('Could not upload {} to server'.format(filename))


def GetGeomType_OGR(folder, inFileName, driverType):
    """
	This function will take a feature within a geodatabase or a shapefile and return an integer indicating
	the geometry type of the layer.

	1: Point
	2: Polyline
	3: Polygon

	Args:
		folder: path to the folder or geodatabase
		inFileName: name of the layer
		driverType: OGR driver type, MUST BE 'ESRI Shapefile' or 'FileGDB'

	Requirement: 'FileGDB' driver for OGR, if using a feature within a geodatabase as the input

	Returns: integer indicating the geometry type of the input layer

	"""
    # open layer
    if driverType == 'FileGDB':
        driver = ogr.GetDriverByName(driverType)
        dataSource = driver.Open(folder, 0)
        layer = dataSource.GetLayer(inFileName)
    if driverType == 'ESRI Shapefile':
        driver = ogr.GetDriverByName(driverType)
        dataSource = driver.Open(os.path.join(folder, inFileName), 0)
        layer = dataSource.GetLayer()
    
    # get the geometry type from the layer
    geometry_type = layer.GetGeomType()
    
    # return the geometry type integer
    return geometry_type
    
    # delete layers
    del layer
    del dataSource
    del driver
        
        
main_dir = r"R:\GEOWorkspace\C_Projects\BOEM IAA\BOEM_IAA_Database"

# loop through all files in the directory
for file in os.listdir(main_dir):
    
    # check if the file is a shapefile
    if file.endswith('.shp'):
        
        # this is the path to the shp file and then executing the function to load the data to postgres
        # this can be converted to loop through shape files through a folder.
        upload_file(file, main_dir)