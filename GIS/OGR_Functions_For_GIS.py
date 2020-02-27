"""
This is a compile of ogr functions created by Alec Dyer for the editing of GIS vector data.

All functions that edit features in an Esri geodatabase require the 'FileGDB' driver API
	from Esri for ogr.
	
Functions written using Python 2.7

Last updated: 11/25/2019
"""

from __future__ import print_function
from osgeo import ogr
import os
import csv

def Open_Shapefile_or_FeatureClass(dir, layerName, driver):
	"""
	Simple function to open either a shapefile of feature class.
	returns data source and layer
	
	Args:
		dir (string): path to directory where the layer is found. If a
			geodatabase, include '.gdb' at the end of the string
		layerName (string): name of the layer
		layerType (string): must be either 'shapefile' or 'featureClass'

	Returns: data source, layer

	"""
	if driver.lower() == 'esri shapefile':
		d = ogr.GetDriverByName('ESRI Shapefile')
		ds = d.Open(os.path.join(dir, layerName + '.shp'), 1)
		l = ds.GetLayer()
		
	if driver.lower() == 'filegdb':
		d = ogr.GetDriverByName('FileGDB')
		ds = d.Open(dir, 1)
		l = ds.GetLayer(layerName)
		
	return ds, l
	
def ExtractFeaturesInGDB_ByAttribute_ToMemory(inGDB, inFileName, filterQuery, outLayerName):
	"""
	This function will extract features from a feature class based on a SQL filter query and save the layer to
	memory. It will carry over any attributes in the input feature class.

	This function will only work with feature classes!!! The feature has to be in a geodatabase, and the driver
	MUST be 'FileGDB'. This function can be changed to use shapefiles by adjusting how the input is opened.

	Requirement: 'FileGDB' driver for ogr

	Args:
		inGDB: input geodatabase (must end with .gdb)
		inFileName: the name of the input feature class
		filterQuery: SQL query that is in the format of 'column = string' ... string must be quoted and number should NOT be quoted
		outLayerName: the name of the output feature class

	Returns: output memory data source and memory layer
	"""
	
	# open the inShapefile as the driver type
	inDataSource, inLayer = Open_Shapefile_or_FeatureClass(inGDB, inFileName, 'FileGDB')
	
	# query out the wanted fields
	inLayer.SetAttributeFilter(filterQuery)
	
	# create the output driver
	outDriver = ogr.GetDriverByName('MEMORY')
	
	print('Out driver set as ' + format(outDriver.GetName()))
	
	# create output shape file
	outDataSource = outDriver.CreateDataSource('memData_' + format(outLayerName))
	outMemory = outDataSource.CopyLayer(inLayer, outLayerName)
	
	# Save and close DataSources
	del inLayer
	del inDataSource
    
	return outDataSource, outMemory

def ExtractFeaturesinLayer_ByAttribute_ToShapefile(inDataSource, inLayer, filterQuery, outShapefileName, shapefileFolder):
	"""
	This function will extract features from an ogr memory data source based on a SQL filter query and save the layer to
	memory. It will carry over any attributes in the input feature. Both the data source and the memory and needed as
	inputs because the memory layer will not be able to be accessed without the data source.

	This function does NOT delete the input data source and layer.

	Args:
		inDataSource: input data source
		inMemory: input layer
		filterQuery: SQL query that is in the format of 'column = string' ... strings must be quoted and numbers should NOT be quoted
		outShapefileName: the name of the output (must NOT end with .shp)
		shapefileFolder: path the the folder that will contain the output shapefile

	Returns: input memory data source and memory layer
	"""
	
	# query out the wanted fields
	inLayer.SetAttributeFilter(filterQuery)
	
	# create the output driver
	outDriver = ogr.GetDriverByName('ESRI Shapefile')
	outPath = os.path.join(shapefileFolder,outShapefileName + '.shp')
	
	# remove output shape file if it already exists
	if os.path.exists(outPath):
		outDriver.DeleteDataSource(outPath)
	
	# create output shape file
	outDataSource = outDriver.CreateDataSource(outPath)
	outDataSource.CopyLayer(inLayer, outShapefileName + '.shp')
	
	del outDataSource
	del outDriver
	
	# return DataSources and layers
	return inDataSource, inLayer

def FeatureToFeature_GDB(inGDB, outGDB, inFileName, outFileName):
	"""
	This tool will take a feature that is within a database and create an exact copy of it to another
	geodatabase. The geodatabases could be the same one.

	Requirement: 'FileGDB' driver for ogr

	Args:
		inGDB: path to the geodatabase where the input feature class is located (must end with .gdb)
		outGDB: path to the geodatabase where the output feature class is to be placed (must end with .gdb)
		inFileName: nanme of the input feature class
		outFileName: name of the output feature class

	Returns: N/A

	"""
	
	# open the inShapefile as the driver type
	inDataSource, inLayer = Open_Shapefile_or_FeatureClass(inGDB, inFileName, 'FileGDB')
	
	# create the output driver
	outDriver = ogr.GetDriverByName('FileGDB')
	outPath = os.path.join(outGDB, outFileName)
	
	print('Out driver set as ' + format(outDriver.GetName()))
	
	# remove output shape file if it already exists
	if os.path.exists(outPath):
		outDriver.DeleteDataSource(outPath)
	
	# create output shape file
	outDataSource = outDriver.Open(outGDB, 1)
	outDataSource.CopyLayer(inLayer, outFileName)
	
	inLayer.ResetReading()
	
	# Save and close DataSources
	del inLayer
	del inDataSource
	del outDataSource

def LayerToFeature_GDB(inDataSource, inLayer, outGDB, outFileName):
	"""
	This tool will take an input ogr memory layer and convert it to a feature class within a geodatabase.
	The memory data source and memory layer are both needed for inputs because the memory layer will not
	be able to be accessed without the data source.

	Requirement: 'FileGDB' driver for ogr

	Args:
		inDataSource: in memory data source
		inMemory: in memory layer
		outGDB: path to the output geodatabase (must end with .gdb)
		outFileName: name of the output feature class

	Returns: N/A

	"""
	
	# create the output driver
	outDriver = ogr.GetDriverByName('FileGDB')
	
	print('Out driver set as ' + format(outDriver.GetName()))
	
	# create output shape file
	outDataSource = outDriver.Open(outGDB, 1)
	outDataSource.CopyLayer(inLayer, outFileName)
	
	# Save and close DataSources
	del outDriver
	del outDataSource
	del inDataSource
	del inLayer

def LayerToShapefile(inDataSource, inLayer, shapefileFolder, outFileName):
	"""
	This tool will convert an ogr memory layer to a shapefile. The memory data source and memory layer are both
	needed for inputs because the memory layer will not be able to be accessed without the data source.

	Args:
		inDataSource: input memory data source
		inMemory: input memory layer
		shapefileFolder: path to the folder where the shapefile will be placed
		outFileName: name of the output shapefile (does NOT end with .shp)

	Returns: N/A

	"""
	
	# create the output driver
	outDriver = ogr.GetDriverByName('ESRI Shapefile')
	outPath = os.path.join(shapefileFolder, outFileName + '.shp')
	
	# remove output shape file if it already exists
	if os.path.exists(outPath):
		outDriver.DeleteDataSource(outPath)
	
	# create output shape file
	outDataSource = outDriver.CreateDataSource(outPath)
	outDataSource.CopyLayer(inLayer, outFileName + '.shp')
	
	# set the input data source and layer to none
	del inLayer
	del inDataSource
	del outDataSource
	del outDriver

def ShapefileToMemory_ForceMultiPoint(shapefileFolder, inFileName, outFileName):
	"""
	Function to take a shapefile of points and create a new memory layer using the original
	but forcing each feature to multipoint.
	
	Args:
		shapefileFolder: path to folder where shapefile is located
		inFileName: name of the input shapefile
		outFileName: name for the memory layer

	Returns: memory data source, memory layer

	"""
	
	# open the inShapefile as the driver type
	inDataSource, inLayer = Open_Shapefile_or_FeatureClass(shapefileFolder, inFileName, 'ESRI Shapefile')
	
	# create the output driver
	outDriver = ogr.GetDriverByName('MEMORY')
	
	print('Out driver set as ' + format(outDriver.GetName()))
	
	# create output shape file
	outDataSource = outDriver.CreateDataSource('memData_' + format(outFileName))
	outLayer = outDataSource.CreateLayer(outFileName, inLayer.GetSpatialRef(), ogr.wkbMultiPoint)
	
	# Add input Layer Fields to the output Layer
	outLayer.CreateFields(inLayer.schema)
	
	# Get the output Layer's Feature Definition
	outLayerDefn = outLayer.GetLayerDefn()
	
	inLayer.ResetReading()
	
	# Add features to the output Layer
	for input_feat in inLayer:
		# Create output Feature
		outFeature = ogr.Feature(outLayerDefn)
		
		# Set geometry as centroid
		geom = input_feat.GetGeometryRef()
		geom_name = geom.GetGeometryName()
		if geom_name == 'POINT':
			geom = ogr.ForceToMultiPoint(geom)
		outFeature.SetGeometry(geom)
		
		# Add field values from input Layer
		for i in range(0, outLayerDefn.GetFieldCount()):
			field_value = input_feat.GetField(i)
			outFeature.SetField(i, field_value)
		
		# Add new feature to output Layer
		outLayer.CreateFeature(outFeature)
	
	# Save and close DataSources
	del inLayer
	del inDataSource
	
	return outDataSource, outLayer

def SortLayer_GDB(inGDB, layerName, field):
	"""
	This function will sort a feature class by a certain field in ascending order. It works with numbered fields,
	but should work with string fields as well. This function will NOT create a new feature class. The layer will
	be closed once completed.

	Requirement: 'FileGDB' driver for ogr

	Args:
		inGDB: geodatabase where the input feature class is located (must end with .gdb)
		layer: name of the feature class
		field: Name of the field to sort by

	Returns: N/A

	"""
	
	# open input layer with driver
	inDataSource, inLayer = Open_Shapefile_or_FeatureClass(inGDB, layerName, 'FileGDB')
	# fids are unique, fids may be sorted or unsorted, fids may be consecutive or have gaps
	# don't care about semantics, don't touch fids and their order, reuse fids
	fids = []
	vals = []
	inLayer.ResetReading()
	for f in inLayer:
		fid = f.GetFID()
		fids.append(fid)
		vals.append((f.GetField(field), fid))
	vals.sort()
	# index as dict: {newfid: oldfid, ...}
	ix = {fids[i]: vals[i][1] for i in range(len(fids))}
	
	# swap features around in groups/rings
	for fidstart in ix.keys():
		if fidstart not in ix: continue
		ftmp = inLayer.GetFeature(fidstart)
		fiddst = fidstart
		while True:
			fidsrc = ix.pop(fiddst)
			if fidsrc == fidstart: break
			f = inLayer.GetFeature(fidsrc)
			f.SetFID(fiddst)
			inLayer.SetFeature(f)
			fiddst = fidsrc
		ftmp.SetFID(fiddst)
		inLayer.SetFeature(ftmp)
	
	inLayer.ResetReading()
	
	# Save and close DataSources
	del f
	del inLayer
	del inDataSource

def Sort(inDataSource, inLayer, field):
	"""
		This function will sort a memory layer by a certain field in ascending order. It works with numbered fields,
		but should work with string fields as well.

		Requirement: ogr

		Args:
			inDataSource: data source of the memory layer
			inMemory: layer source of the memory
			field: Name of the field to sort by

		Returns: inDataSource, inLayer

		"""
	
	# fids are unique, fids may be sorted or unsorted, fids may be consecutive or have gaps
	# don't care about semantics, don't touch fids and their order, reuse fids
	fids = []
	vals = []
	inLayer.ResetReading()
	for f in inLayer:
		fid = f.GetFID()
		fids.append(fid)
		vals.append((f.GetField(field), fid))
	vals.sort()
	# index as dict: {newfid: oldfid, ...}
	ix = {fids[i]: vals[i][1] for i in range(len(fids))}
	
	# swap features around in groups/rings
	for fidstart in ix.keys():
		if fidstart not in ix: continue
		ftmp = inLayer.GetFeature(fidstart)
		fiddst = fidstart
		while True:
			fidsrc = ix.pop(fiddst)
			if fidsrc == fidstart: break
			f = inLayer.GetFeature(fidsrc)
			f.SetFID(fiddst)
			inLayer.SetFeature(f)
			fiddst = fidsrc
		ftmp.SetFID(fiddst)
		inLayer.SetFeature(ftmp)
	
	inLayer.ResetReading()
	
	del f
	
	return inDataSource, inLayer

def GrabUniqueValuesFromField_GDB(inGDB, inFileName, field):
	"""
	This function will create and return a list of the unique values or strings from a single
	column of the input feature class. This will only work with feature classes in a geodatabase!

	Requirement: 'FileGDB' driver for ogr

	Args:
		inGDB: path to the geodatabase where the input feature class is located (must end with .gdb)
		inFileName: name of the input feature class
		field: name of the field to grab the values or strings from

	Returns: unique values list

	"""
	# open the feature
	inDataSource, inLayer = Open_Shapefile_or_FeatureClass(inGDB, inFileName, 'FileGDB')
	
	# reset reading
	inLayer.ResetReading()
	
	unique_values = []
	
	for feature in inLayer:
		value = feature.GetField(field)
		if value not in unique_values:
			unique_values.append(value)
	
	inLayer.ResetReading()
	
	del inLayer
	del inDataSource
	
	return(unique_values)

def GrabUniqueValuesFromLayer(inDataSource, inLayer, field):
	"""
		This function will create and return a list of the unique values or strings from a single
		column of the input memory layer.

		Requirement: ogr

		Args:
			inDatasource: data source that holds the input memory layer
			inFileName: input memory layer
			field: name of the field to grab the values or strings from

		Returns: unique values list, data source object, layer object

		"""
	
	# reset reading
	inLayer.ResetReading()
	
	unique_values = []
	
	for feature in inLayer:
		value = feature.GetField(field)
		if value not in unique_values:
			unique_values.append(value)
	
	inLayer.ResetReading()
	
	return(unique_values, inDataSource, inLayer)

def AppendFeatureToFeature_GDB(inFileName, inGDB, appendingFileName, appendingFileGDB):
	"""
	The function will append a feature class to another feature class. This will only work for feature classes
	in a geodatabase. At this point, it is unknown if this function will work with features that have different
	attributes. The appending file/GDB will be the feature that gets appended to the in file/GDB.

	Requirement: 'FileGDB' driver for ogr

	Args:
		inGDB: path to the geodatabase that contains the main feature class
		inFileName: name of the main feature class
		appendingFileName: name of the feature class that will be appended to the main feature class
		appendingFileGDB: path to the geodatabase that contains the feature that is going to be appended.

	Returns: N/A

	"""
	
	# open in file which will be appended to
	inDataSource, inLayer = Open_Shapefile_or_FeatureClass(inGDB, inFileName, 'FileGDB')
	
	# open the file which will be appended to the other
	extraDataSource, extraLayer = Open_Shapefile_or_FeatureClass(appendingFileGDB, appendingFileName, 'FileGDB')
	
	extraLayerDefn = extraLayer.GetLayerDefn()
	
	for input_feat in inLayer:
		
		# create new feature
		extraFeature = ogr.Feature(extraLayerDefn)
		
		# set geometry
		geom = input_feat.GetGeometryRef()
		extraFeature.SetGeometry(geom)
		
		# Add field values from input Layer
		for i in range(0, extraLayerDefn.GetFieldCount()):
			extraFeature.SetField(i, input_feat.GetField(i))
		
		# append extra layer to in layer
		inLayer.CreateFeature(extraFeature)
	
	# Save and close DataSources
	del inLayer
	del inDataSource
	del extraLayer
	del extraDataSource

def AppendLayerToShapefile(inFolder, inFileName, appendingDataSource, appendingLayer):
	"""
	This function will append an ogr memory layer to an existing feature class. As of now, it is uncertain
	if this will work with layers that have different attributes. Both the appending memory data source and layer
	are both needed because the memory layer cannot be opened without the data source.

	Args:
		inFolder: path to the folder where the shapefile is located
		inFileName: name of the shapefile (must NOT have .shp)
		appendingDataSource: memory data source that will be appended to the feature class
		appendingLayer: layer that will be appended to the feature class

	Returns: N/A

	"""
	
	# open in file which will be appended to
	inDataSource, inLayer = Open_Shapefile_or_FeatureClass(inFolder, inFileName, 'ESRI Shapefile')
	
	appendingLayer.ResetReading()
	
	inLayerDefn = inLayer.GetLayerDefn()
	
	for input_feat in appendingLayer:
		
		# create new feature
		extraFeature = ogr.Feature(inLayerDefn)
		
		# Set geometry
		geom = input_feat.GetGeometryRef()
		extraFeature.SetGeometry(geom)
		
		# Add field values from input Layer
		for i in range(0, inLayerDefn.GetFieldCount()):
			field_value = input_feat.GetField(i)
			extraFeature.SetField(i, field_value)
		
		# append extra layer to in layer
		inLayer.CreateFeature(extraFeature)
	
	# Save and close DataSources
	del inLayer
	del inDataSource
	del appendingLayer
	del appendingDataSource

def AppendLayerToLayer(inDataSource, inLayer, appendingDataSource, appendingMemory):
	"""
	This function will append a memory layer to another memory layer, return the memory data source
	and layer that was appended, and delete the appended memory data source and layer. The two layers must
	have the same field names!!!

	Args:
		inDataSource: input memory data source
		inLayer: input memory layer
		appendingDataSource: memory data source that will be appended to the input
		appendingMemory: memory layer that will be appended to the input

	Returns: input memory data source and layer that was appended to as well as the appended data source and memory

	"""
	
	inLayerDefn = inLayer.GetLayerDefn()
	
	appendingMemory.ResetReading()
	
	for input_feat in appendingMemory:
		
		extraFeature = ogr.Feature(inLayerDefn)
		
		# Set geometry
		geom = input_feat.GetGeometryRef()
		extraFeature.SetGeometry(geom.Clone())
		
		# Add field values from input Layer
		for i in range(0, inLayerDefn.GetFieldCount()):
			field_value = input_feat.GetField(i)
			extraFeature.SetField(i, field_value)
		
		# append extra layer to in layer
		inLayer.CreateFeature(extraFeature)
	
	inLayer.ResetReading()
	appendingMemory.ResetReading()
	
	return(inDataSource, inLayer, appendingDataSource, appendingMemory)

def AddFieldsFromFeatureToFeature_GDB(inGDB, inFileName, fieldsGDB, fieldsFeatureName):
	"""
	This function will take the fields of a feature class and add them to another feature class. It will copy
	over all of the field names of the fields Feature.
	This function will only work with feature classes in a geodatabase.

	Requirement: 'FileGDB' driver for ogr

	Args:
		inGDB: path to geodatabase that contains the inFileName layer
		inFileName: name of the input feature class that will get the fields added to itself
		fieldsGDB: path to the geodatabase that contains the feature class with the wanted field names
		fieldsFeatureName: name of the feature class with the field names that are wanted for the in feature class

	Returns: N/A

	"""
	
	# open in feature using the driver
	inDataSource, inLayer = Open_Shapefile_or_FeatureClass(inGDB, inFileName, 'FileGDB')
	
	# open feature that has the fields wanted
	fieldsDataSource, fieldsLayer = Open_Shapefile_or_FeatureClass(fieldsGDB, fieldsFeatureName, 'FileGDB')
	
	# add field layer fields to the inLayer
	inLayer.CreateFields(fieldsLayer.schema)
	
	# Save and close DataSources
	del inLayer
	del inDataSource
	del fieldsLayer
	del fieldsDataSource

def ListOGR_drivers():
	"""
	Function to print out a list of all available drivers for OGR
	
	Returns: N/A

	"""
	
	cnt = ogr.GetDriverCount()
	formatsList = []  # Empty List
	
	for i in range(cnt):
		driver = ogr.GetDriver(i)
		driverName = driver.GetName()
		if not driverName in formatsList:
			formatsList.append(driverName)
	
	formatsList.sort()  # Sorting the messy list of ogr drivers
	
	for i in formatsList:
		print(i)

def TableToCSV_GDB(inGDB, inTableName, outTablePath):
	"""
	Function to convert the attribute table of a feature class
	in a geodatabase to a csv
	
	Args:
		inGDB: path to the geodatabase where the feature class is located
		inTableName: name of the feature class
		outTablePath: full path to the output CSV (must end with '.csv')

	Returns: N/A

	"""
	
	# open table in geodatabase
	inDataSource, inTable = Open_Shapefile_or_FeatureClass(inGDB, inTableName, 'FileGDB')
	
	# pull header information
	header = []
	inTableDefn = inTable.GetLayerDefn()
	for i in range(0, inTableDefn.GetFieldCount()):
		header.append((inTableDefn.GetFieldDefn(i)).GetName())
	
	with open(outTablePath, 'wb') as csvFile:
		writer = csv.DictWriter(csvFile, fieldnames=header)
		
		writer.writeheader()
		
		for line in inTable:
			rowdict = {}
			for i in range(0, inTableDefn.GetFieldCount()):
				rowdict.update(
					{inTableDefn.GetFieldDefn(i).GetNameRef(): line.GetField(inTableDefn.GetFieldDefn(i).GetNameRef())})
			
			line.Destroy()
			writer.writerow(rowdict)
		
		csvFile.close()
	
	del inTable
	del inDataSource

def CheckFeatureCount_Shapefile(shapefileFolder, fileName):
	"""
	Function that returns the number of features in a shapefile
	
	Args:
		shapefileFolder: path to the folder where the shapefile is located
		fileName: name of the shapefile

	Returns: feat_num

	"""
	# open the shapefile
	ds, l = Open_Shapefile_or_FeatureClass(shapefileFolder, fileName, 'ESRI Shapefile')
	# count features
	feat_num = l.GetFeatureCount()
	
	del l
	del ds
	
	return feat_num

def CheckFeatureCount_GDB(GDB, inFileName):
	"""
	Use this function to calculate the number of features from a layer within a GDB.
	
	Requires FileGDB driver for ogr.
	
	Args:
		GDB: path to the geodatabase
		inFileName: name of the layer

	Returns: object containing a number representing the number of features in the shapefile

	"""
	
	# open in feature using the driver
	inDataSource, inLayer = Open_Shapefile_or_FeatureClass(GDB, inFileName, 'FileGDB')
	
	# get feature count from layer
	feat_num = inLayer.GetFeatureCount()
	
	del inLayer
	del inDataSource
	
	return feat_num

def SplitIntoTwoLayers_Shapefile(shapefileFolder, shapefileName):
	"""
	This function will take a shapefile and split it into 2 separate shapefiles. The first output will have the first half
	of the number of features, the second output will have the other half. The two outputs will have a '_A' and '_B'
	added to the names.

	Args:
		shapefileFolder: path to folder where input shapefile is located
		shapefileName: name of input shapefile

	Returns: N/A

	"""
	
	# Open input shapefile
	inDataSource, inLayer = Open_Shapefile_or_FeatureClass(shapefileFolder, shapefileName, 'ESRI Shapefile')
	
	# Get feature count
	feat_count = inLayer.GetFeatureCount()
	
	# open first new shapefile
	outDriver_A = ogr.GetDriverByName('ESRI Shapefile')
	outPath_A = os.path.join(shapefileFolder, shapefileName + '_A.shp')
	
	# remove output shape file if it already exists
	if os.path.exists(outPath_A):
		outDriver_A.DeleteDataSource(outPath_A)
	
	# create output shape file
	outDataSource_A = outDriver_A.CreateDataSource(outPath_A)
	outFile_A = outDataSource_A.CreateLayer(shapefileName + '_A.shp', inLayer.GetSpatialRef(), inLayer.GetGeomType())
	
	# Add input Layer Fields to the output Layer
	outFile_A.CreateFields(inLayer.schema)
	
	# Get the output Layer's Feature Definition
	outLayerDefn = outFile_A.GetLayerDefn()
	
	inLayer.ResetReading()
	
	# now add first half of features from inLayer to shapefile A
	for i in range(0, int(feat_count / 2)):
		
		input_feat = inLayer.GetFeature(i)
		
		# Create output Feature
		outFeature = ogr.Feature(outLayerDefn)
		
		# Set geometry as centroid
		geom = input_feat.GetGeometryRef()
		outFeature.SetGeometry(geom)
		
		# Add field values from input Layer
		for i in range(0, outLayerDefn.GetFieldCount()):
			field_value = input_feat.GetField(i)
			outFeature.SetField(i, field_value)
		
		# Add new feature to output Layer
		outFile_A.CreateFeature(outFeature)
	
	# close new shapefile
	del outFile_A
	del outDataSource_A
	del outDriver_A
	
	# reset reading
	inLayer.ResetReading()
	
	# open first new shapefile
	outDriver_B = ogr.GetDriverByName('ESRI Shapefile')
	outPath_B = os.path.join(shapefileFolder, shapefileName + '_B.shp')
	
	# remove output shape file if it already exists
	if os.path.exists(outPath_B):
		outDriver_B.DeleteDataSource(outPath_B)
	
	# create output shape file
	outDataSource_B = outDriver_B.CreateDataSource(outPath_B)
	outFile_B = outDataSource_B.CreateLayer(shapefileName + '_B.shp', inLayer.GetSpatialRef(), inLayer.GetGeomType())
	
	# Add input Layer Fields to the output Layer
	outFile_B.CreateFields(inLayer.schema)
	
	# Get the output Layer's Feature Definition
	outLayerDefn = outFile_B.GetLayerDefn()
	
	inLayer.ResetReading()
	
	# now add first half of features from inLayer to shapefile A
	for i in range(int(feat_count / 2), feat_count):
		
		input_feat = inLayer.GetFeature(i)
		
		# Create output Feature
		outFeature = ogr.Feature(outLayerDefn)
		
		# Set geometry as centroid
		geom = input_feat.GetGeometryRef()
		outFeature.SetGeometry(geom)
		
		# Add field values from input Layer
		for i in range(0, outLayerDefn.GetFieldCount()):
			field_value = input_feat.GetField(i)
			outFeature.SetField(i, field_value)
		
		# Add new feature to output Layer
		outFile_B.CreateFeature(outFeature)
	
	# close new shapefile
	del outFile_B
	del outDataSource_B
	del outDriver_B
	del inLayer
	del inDataSource

def PullIndexFromFeature_GDB(GDB, inFileName, fieldName):
	"""
	Simple function to grab the field index based off of a field name from a feature within a geodatabase.
	The field index of the first field matching the passed field name (case insensitively) is returned.

	Args:
		GDB: path to the geodatabase containing the feature (string)
		inFileName: name of the feature (string)
		fieldName: name of field for the index (string)

	Returns: field index (integer)

	"""
	# open feature
	dataSource, layer = Open_Shapefile_or_FeatureClass(GDB, inFileName, 'FileGDB')
	
	# get feature definition from the layer
	defn = layer.GetLayerDefn()
	
	# get field index based on field name
	index = defn.GetFieldIndex(fieldName)
	
	# delete objects
	del layer
	del dataSource
	
	return(index)

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
		dataSource, layer = Open_Shapefile_or_FeatureClass(folder, inFileName, driverType)
	if driverType == 'ESRI Shapefile':
		dataSource, layer = Open_Shapefile_or_FeatureClass(folder, inFileName, driverType)
	
	# get the geometry type from the layer
	geometry_type = layer.GetGeomType()
	
	# delete layers
	del layer
	del dataSource
	
	# return the geometry type integer
	return geometry_type

def CheckFeatureExistsInGDB(GDB, featureName):
	"""
	This little function will check if a feature layer exists in a geodatabase using OGR.

	Args:
		GDB: path to the geodatabase
		featureName: name of the feature layer as a string

	Returns: True or False object

	"""
	driver = ogr.GetDriverByName('FileGDB')
	dataSource = driver.Open(GDB, 0)
	if dataSource.GetLayer(featureName):
		feat = True
	else:
		feat = False
	
	return feat