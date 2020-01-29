"""This script will contain many of the functions that I have created, which can be accessed
and reused for various purposes."""

from osgeo import ogr
import os

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
	
	from osgeo import ogr
	
	# open the inShapefile as the driver type
	inDriver = ogr.GetDriverByName('FileGDB')
	inDataSource = inDriver.Open(inGDB, 0)
	inLayer = inDataSource.GetLayer(inFileName)
	
	# query out the wanted fields
	inLayer.SetAttributeFilter(filterQuery)
	
	# create the output driver
	outDriver = ogr.GetDriverByName('MEMORY')
	
	print('Out driver set as ' + format(outDriver.GetName()))
	
	# create output shape file
	outDataSource = outDriver.CreateDataSource('memData_' + format(outLayerName))
	outMemory = outDataSource.CreateLayer(outLayerName, inLayer.GetSpatialRef(), inLayer.GetGeomType())
	
	# Add input Layer Fields to the output Layer
	outMemory.CreateFields(inLayer.schema)
	
	# Get the output Layer's Feature Definition
	outLayerDefn = outMemory.GetLayerDefn()
	
	# Add features to the output Layer
	for inFeature in inLayer:
		
		# Create output Feature
		outFeature = ogr.Feature(outLayerDefn)
		
		# Set geometry as centroid
		geom = inFeature.GetGeometryRef()
		outFeature.SetGeometry(geom)
		
		# Add field values from input Layer
		for i in range(0, outLayerDefn.GetFieldCount()):
			outFeature.SetField(i, inFeature.GetField(i))
		
		# Add new feature to output Layer
		outMemory.CreateFeature(outFeature)
	
	# Save and close DataSources
	del inFeature
	del inLayer
	del inDataSource
	del inDriver
	return outDataSource, outMemory

def ExtractFeaturesInMemory_ByAttribute_ToMemory(inDataSource, inMemory, filterQuery, outLayerName):
	"""
	This function will extract features from an ogr memory data source based on a SQL filter query and save the layer to
	memory. It will carry over any attributes in the input feature. Both the data source and the memory and needed as
	inputs because the memory layer will not be able to be accessed without the data source.

	This function will only work with memory, and the driver MUST be 'Memory'.

	This function does NOT delete the input data source and layer.

	Requirement: 'FileGDB' driver for ogr

	Args:
		inDataSource: input data source
		inMemory: input memory
		filterQuery: SQL query that is in the format of 'column = string' ... string must be quoted and number should NOT be quoted
		outLayerName: the name of the output

	Returns: input and output memory data source and memory layer
	"""
	
	from osgeo import ogr
	
	# query out the wanted fields
	inMemory.SetAttributeFilter(filterQuery)
	
	# create the output driver
	outDriver = ogr.GetDriverByName('MEMORY')
	
	print('Out driver set as ' + format(outDriver.GetName()))
	
	# create output shape file
	outDataSource = outDriver.CreateDataSource('memData_' + format(outLayerName))
	outMemory = outDataSource.CreateLayer(outLayerName, inMemory.GetSpatialRef(), inMemory.GetGeomType())
	
	# Add input Layer Fields to the output Layer
	outMemory.CreateFields(inMemory.schema)
	
	# Get the output Layer's Feature Definition
	outLayerDefn = outMemory.GetLayerDefn()
	
	# Add features to the output Layer
	for inFeature in inMemory:
		
		# Create output Feature
		outFeature = ogr.Feature(outLayerDefn)
		
		# Set geometry as centroid
		geom = inFeature.GetGeometryRef()
		outFeature.SetGeometry(geom)
		
		# Add field values from input Layer
		for i in range(0, outLayerDefn.GetFieldCount()):
			outFeature.SetField(i, inFeature.GetField(i))
		
		# Add new feature to output Layer
		outMemory.CreateFeature(outFeature)
	
	inMemory.ResetReading()
	del inFeature
	
	# return DataSources and layers
	return inDataSource, inMemory, outDataSource, outMemory

def ExtractFeaturesinMemory_ByAttribute_ToShapefile(inDataSource, inLayer, filterQuery, outShapefileName,
													shapefileFolder):
	"""
	This function will extract features from an ogr memory data source based on a SQL filter query and save the layer to
	memory. It will carry over any attributes in the input feature. Both the data source and the memory and needed as
	inputs because the memory layer will not be able to be accessed without the data source.

	This function does NOT delete the input data source and layer.

	Args:
		inDataSource: input data source
		inMemory: input layer
		filterQuery: SQL query that is in the format of 'column = string' ... string must be quoted and number should NOT be quoted
		outShapefileName: the name of the output
		shapefileFolder: path the the folder that will contain the output shapefile

	Returns: input memory data source and memory layer
	"""
	
	from osgeo import ogr
	import os
	
	# query out the wanted fields
	inLayer.SetAttributeFilter(filterQuery)
	
	# create the output driver
	outDriver = ogr.GetDriverByName('ESRI Shapefile')
	
	# remove output shape file if it already exists
	if os.path.exists(shapefileFolder + '\\' + outShapefileName + '.shp'):
		outDriver.DeleteDataSource(shapefileFolder + '\\' + outShapefileName + '.shp')
	
	# create output shape file
	outDataSource = outDriver.CreateDataSource(shapefileFolder + '\\' + outShapefileName + '.shp')
	outLayer = outDataSource.CreateLayer(outShapefileName + '.shp', inLayer.GetSpatialRef(), inLayer.GetGeomType())
	
	# Add input Layer Fields to the output Layer
	outLayer.CreateFields(inLayer.schema)
	
	# Get the output Layer's Feature Definition
	outLayerDefn = outLayer.GetLayerDefn()
	
	# Add features to the output Layer
	for input_feat in inLayer:
		
		# Create output Feature
		outFeature = ogr.Feature(outLayerDefn)
		
		# Set geometry as centroid
		geom = input_feat.GetGeometryRef()
		outFeature.SetGeometry(geom)
		
		# Add field values from input Layer
		for i in range(0, outLayerDefn.GetFieldCount()):
			outFeature.SetField(i, input_feat.GetField(i))
		
		# Add new feature to output Layer
		outLayer.CreateFeature(outFeature)
	
	inLayer.ResetReading()
	
	del input_feat
	del outLayer
	del outDataSource
	del outDriver
	
	# return DataSources and layers
	return inDataSource, inLayer

def FeatureToFeature(inGDB, outGDB, inFileName, outFileName):
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
	
	from osgeo import ogr
	import os
	
	# open the inShapefile as the driver type
	inDriver = ogr.GetDriverByName('FileGDB')
	inDataSource = inDriver.Open(inGDB, 0)
	inLayer = inDataSource.GetLayer(inFileName)
	
	# grab the spatial reference system
	srs = inLayer.GetSpatialRef()
	
	# create the output driver
	outDriver = ogr.GetDriverByName('FileGDB')
	
	print('Out driver set as ' + format(outDriver.GetName()))
	
	# remove output shape file if it already exists
	if os.path.exists(outGDB + '\\' + outFileName):
		outDriver.DeleteDataSource(outGDB + '\\' + outFileName)
	
	# create output shape file
	outDataSource = outDriver.Open(outGDB, 1)
	outFile = outDataSource.CreateLayer(outFileName, srs, geom_type=inLayer.GetGeomType())
	
	# Add input Layer Fields to the output Layer
	outFile.CreateFields(inLayer.schema)
	
	# Get the output Layer's Feature Definition
	outLayerDefn = outFile.GetLayerDefn()
	
	# Add features to the output Layer
	for inFeature in inLayer:
		# Create output Feature
		outFeature = ogr.Feature(outLayerDefn)
		
		# Set geometry as centroid
		geom = inFeature.GetGeometryRef()
		outFeature.SetGeometry(geom)
		
		# Add field values from input Layer
		for i in range(0, outLayerDefn.GetFieldCount()):
			outFeature.SetField(i, inFeature.GetField(i))
		
		# Add new feature to output Layer
		outFile.CreateFeature(outFeature)
	
	inLayer.ResetReading()
	
	# Save and close DataSources
	del inDataSource
	del outDataSource

def MemoryToFeature(inDataSource, inMemory, outGDB, outFileName):
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
	
	from osgeo import ogr
	
	# create the output driver
	outDriver = ogr.GetDriverByName('FileGDB')
	
	print('Out driver set as ' + format(outDriver.GetName()))
	
	# create output shape file
	outDataSource = outDriver.Open(outGDB, 1)
	outFile = outDataSource.CreateLayer(outFileName, inMemory.GetSpatialRef(), inMemory.GetGeomType())
	
	# Add input Layer Fields to the output Layer
	inLayerDefn = inMemory.GetLayerDefn()
	for i in range(0, inLayerDefn.GetFieldCount()):
		fieldDefn = inLayerDefn.GetFieldDefn(i)
		outFile.CreateField(fieldDefn)
	
	# Get the output Layer's Feature Definition
	outLayerDefn = outFile.GetLayerDefn()
	
	# Add features to the output Layer
	for inFeature in inMemory:
		# Create output Feature
		outFeature = ogr.Feature(outLayerDefn)
		
		# Add field values from input Layer
		for i in range(0, outLayerDefn.GetFieldCount()):
			outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(),
								inFeature.GetField(i))
		
		# Set geometry as centroid
		geom = inFeature.GetGeometryRef()
		outFeature.SetGeometry(geom.Clone())
		# Add new feature to output Layer
		outFile.CreateFeature(outFeature)
		outFeature = None
	
	# Save and close DataSources
	outDriver = None
	outDataSource = None
	outFile = None
	inDataSource = None
	inMemory = None

def MemoryToShapefile(inDataSource, inMemory, shapefileFolder, outFileName):
	"""
	This tool will convert an ogr memory layer to a shapefile. The memory data source and memory layer are both
	needed for inputs because the memory layer will not be able to be accessed without the data source.
	
	Args:
		inDataSource: input memory data source
		inMemory: input memory layer
		shapefileFolder: path to the folder where the shapefile will be placed
		outFileName: name of the output shapefile (must end with .shp)

	Returns: N/A

	"""
	
	from osgeo import ogr
	import os
	
	# create the output driver
	outDriver = ogr.GetDriverByName('ESRI Shapefile')
	
	# remove output shape file if it already exists
	if os.path.exists(shapefileFolder + '\\' + outFileName + '.shp'):
		outDriver.DeleteDataSource(shapefileFolder + '\\' + outFileName + '.shp')
	
	# create output shape file
	outDataSource = outDriver.CreateDataSource(shapefileFolder + '\\' + outFileName + '.shp')
	outFile = outDataSource.CreateLayer(outFileName + '.shp', inMemory.GetSpatialRef(), inMemory.GetGeomType())
	
	# Add input Layer Fields to the output Layer
	outFile.CreateFields(inMemory.schema)
	
	# Get the output Layer's Feature Definition
	outLayerDefn = outFile.GetLayerDefn()
	
	inMemory.ResetReading()
	
	# Add features to the output Layer
	for input_feat in inMemory:
		
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
		outFile.CreateFeature(outFeature)
	
	# set the input data source and layer to none
	del inMemory
	del inDataSource
	del outFile
	del outDataSource
	del outDriver

def ShapefileToMemory(shapefileFolder, inFileName, outFileName):
	"""
	This tool will convert a shapefile into an ogr memory layer and return the memory data source
	and memory layer. Both are returned because the memory layer cannot be opened without having the data
	source. So keep these together as long as the memory layer needs to be accessed.

	Args:
		shapefileFolder: path to the folder where the input shapefile is located
		inFileName: name of the input shapefile (must end with .shp)
		outFileName: name for the output memory layer

	Returns: memory data source and memory layer

	"""
	
	from osgeo import ogr
	
	# open the inShapefile as the driver type
	inDriver = ogr.GetDriverByName('ESRI Shapefile')
	inDataSource = inDriver.Open(shapefileFolder + '\\' + inFileName, 0)
	inLayer = inDataSource.GetLayer()
	
	# create the output driver
	outDriver = ogr.GetDriverByName('MEMORY')
	
	print('Out driver set as ' + format(outDriver.GetName()))
	
	# create output shape file
	outDataSource = outDriver.CreateDataSource('memData_' + format(outFileName))
	outFile = outDataSource.CreateLayer(outFileName, inLayer.GetSpatialRef(), inLayer.GetGeomType())
	
	# Add input Layer Fields to the output Layer
	outFile.CreateFields(inLayer.schema)
	
	# Get the output Layer's Feature Definition
	outLayerDefn = outFile.GetLayerDefn()
	
	inLayer.ResetReading()
	
	# Add features to the output Layer
	for input_feat in inLayer:
		
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
		outFile.CreateFeature(outFeature)
	
	# Save and close DataSources
	del input_feat
	del inLayer
	del inDataSource
	del inDriver
	
	return outDataSource, outFile

def ShapefileToMemory_ForceMultiPoint(shapefileFolder, inFileName, outFileName):
	
	from osgeo import ogr
	
	# open the inShapefile as the driver type
	inDriver = ogr.GetDriverByName('ESRI Shapefile')
	inDataSource = inDriver.Open(shapefileFolder + '\\' + inFileName, 0)
	inLayer = inDataSource.GetLayer()
	
	# create the output driver
	outDriver = ogr.GetDriverByName('MEMORY')
	
	print('Out driver set as ' + format(outDriver.GetName()))
	
	# create output shape file
	outDataSource = outDriver.CreateDataSource('memData_' + format(outFileName))
	outFile = outDataSource.CreateLayer(outFileName, inLayer.GetSpatialRef(), ogr.wkbMultiPoint)
	
	# Add input Layer Fields to the output Layer
	outFile.CreateFields(inLayer.schema)
	
	# Get the output Layer's Feature Definition
	outLayerDefn = outFile.GetLayerDefn()
	
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
		outFile.CreateFeature(outFeature)
	
	# Save and close DataSources
	del inLayer
	del inDataSource
	del inDriver
	
	return outDataSource, outFile

def DissolveWithFiona_FromMemory(inDataSource, inMemory, inFileName, outFileName, shapefileFolder, dissolve_field):
	"""
	This function uses a script found online that uses fiona to dissolve a shapefile.
	url: https://gis.stackexchange.com/questions/149959/dissolving-polygons-based-on-attributes-with-python-shapely-fiona

	This function takes an ogr memory layer as an input, converts its to a shapefile, dissolves, and
	converts the dissolved shapefile back into a memory layer.

	IMPORTANT NOTE!!!!!!: If the dissolve function fails the inFileName will be added to a list called 'incompleted_list'.
	This section will need to be taken out, unless used.

	Args:
		inDataSource:
		inMemory:
		inFileName:
		outFileName:
		shapefileFolder:
		dissolve_field:

	Returns: dissolved memory data source and layer

	"""
	
	import fiona
	import itertools
	from shapely.geometry import shape, mapping
	from shapely.ops import unary_union
	
	MemoryToShapefile(inDataSource, inMemory, shapefileFolder, inFileName)
	
	"""use fiona to dissolve"""
	try:
		with fiona.open(shapefileFolder + '\\' + inFileName + '.shp') as input_layer:
			# preserve the schema of the original shapefile, including the crs
			meta = input_layer.meta
			with fiona.open(shapefileFolder + '\\' + outFileName + '.shp', 'w', **meta) as output:
				# groupby clusters consecutive elements of an iterable which have the same key so you must first sort the features by the 'STATEFP' field
				e = sorted(input_layer, key=lambda k: k['properties'][dissolve_field])
				# group by the dissolve field
				for key, group in itertools.groupby(e, key=lambda x: x['properties'][dissolve_field]):
					properties, geom = zip(*[(feature['properties'], shape(feature['geometry'])) for feature in group])
					# write the feature, computing the unary_union of the elements in the group with the properties of the first element in the group
					output.write({'geometry': mapping(unary_union(geom)), 'properties': properties[0]})
	
	except:
		print(inFileName + ' was not able to be dissolved.')
	
	outDataSource, outFile = ShapefileToMemory(shapefileFolder, outFileName + '.shp', outFileName)
	
	return outDataSource, outFile

def DissolveWithFiona(shapefileFolder, inFileName, outFileName, dissolveField):
	import fiona
	import itertools
	from shapely.geometry import shape, mapping
	from shapely.ops import unary_union
	import os
	from osgeo import ogr
	
	# remove output shape file if it already exists
	d_out = ogr.GetDriverByName('ESRI Shapefile')
	if os.path.exists(shapefileFolder + '\\' + outFileName + '.shp'):
		d_out.DeleteDataSource(shapefileFolder + '\\' + outFileName + '.shp')
	del d_out
	
	with fiona.open(shapefileFolder + '\\' + inFileName + '.shp') as input_layer:
		# preserve the schema of the original shapefile, including the crs
		meta = input_layer.meta
		with fiona.open(shapefileFolder + '\\' + outFileName + '.shp', 'w', **meta) as output:
			# groupby clusters consecutive elements of an iterable which have the same key so you must first sort the features by the 'STATEFP' field
			e = sorted(input_layer, key=lambda k: k['properties'][dissolveField])
			# group by the dissolve field
			for key, group in itertools.groupby(e, key=lambda x: x['properties'][dissolveField]):
				properties, geom = zip(
					*[(fiona_feature['properties'], shape(fiona_feature['geometry'])) for fiona_feature in group])
				# write the feature, computing the unary_union of the elements in the group with the properties of the first element in the group
				output.write({'geometry': mapping(unary_union(geom)), 'properties': properties[0]})

def SortLayer_GDB(inGDB, layerName, field):
	"""
	This function will sort a feature class by a certain field in ascending order. It works with numbered fields,
	but should work with string fields as well. This function will NOT create a new feature class.

	Requirement: 'FileGDB' driver for ogr

	Args:
		inGDB: geodatabase where the input feature class is located (must end with .gdb)
		layer: name of the feature class
		field: Name of the field to sort by

	Returns: N/A

	"""
	
	from osgeo import ogr
	
	# open input layer with driver
	inDriver = ogr.GetDriverByName('FileGDB')
	inDataSource = inDriver.Open(inGDB, 1)
	inLayer = inDataSource.GetLayer(layerName)
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
	ix = {fids[i]: vals[i][1] for i in xrange(len(fids))}
	
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
	del inLayer
	del inDataSource
	del inDriver

def Sort(inDataSource, inMemory, field):
	"""
		This function will sort a memory layer by a certain field in ascending order. It works with numbered fields,
		but should work with string fields as well.

		Requirement: ogr

		Args:
			inDataSource: data source of the memory layer
			inMemory: layer source of the memory
			field: Name of the field to sort by

		Returns: inDataSource, inMemory

		"""
	
	from osgeo import ogr
	
	# fids are unique, fids may be sorted or unsorted, fids may be consecutive or have gaps
	# don't care about semantics, don't touch fids and their order, reuse fids
	fids = []
	vals = []
	inMemory.ResetReading()
	for f in inMemory:
		fid = f.GetFID()
		fids.append(fid)
		vals.append((f.GetField(field), fid))
	vals.sort()
	# index as dict: {newfid: oldfid, ...}
	ix = {fids[i]: vals[i][1] for i in xrange(len(fids))}
	
	# swap features around in groups/rings
	for fidstart in ix.keys():
		if fidstart not in ix: continue
		ftmp = inMemory.GetFeature(fidstart)
		fiddst = fidstart
		while True:
			fidsrc = ix.pop(fiddst)
			if fidsrc == fidstart: break
			f = inMemory.GetFeature(fidsrc)
			f.SetFID(fiddst)
			inMemory.SetFeature(f)
			fiddst = fidsrc
		ftmp.SetFID(fiddst)
		inMemory.SetFeature(ftmp)
	
	inMemory.ResetReading()
	
	del f
	
	return inDataSource, inMemory

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
	inDriver = ogr.GetDriverByName('FileGDB')
	inDataSource = inDriver.Open(inGDB, 0)
	inLayer = inDataSource.GetLayer(inFileName)
	
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
	del inDriver
	
	return (unique_values)

def GrabUniqueValuesFromLayer(inDataSource, inMemory, field):
	"""
		This function will create and return a list of the unique values or strings from a single
		column of the input memory layer.

		Requirement: ogr

		Args:
			inDatasource: data source that holds the input memory layer
			inFileName: input memory layer
			field: name of the field to grab the values or strings from

		Returns: unique values list, inDataSource, inMemory

		"""
	
	from osgeo import ogr
	
	# reset reading
	inMemory.ResetReading()
	
	unique_values = []
	
	for feature in inMemory:
		value = feature.GetField(field)
		if value not in unique_values:
			unique_values.append(value)
	
	inMemory.ResetReading()
	
	return unique_values, inDataSource, inMemory

def AppendFeatureToFeature_GDB(inGDB, inFileName, appendingFileName, appendingFileGDB):
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
	
	from osgeo import ogr
	
	# open in file which will be appended to
	inDriver = ogr.GetDriverByName('FileGDB')
	inDataSource = inDriver.Open(inGDB, 1)
	inLayer = inDataSource.GetLayer(inFileName)
	
	# open the file which will be appended to the other
	extraDriver = ogr.GetDriverByName('FileGDB')
	extraDataSource = extraDriver.Open(appendingFileGDB, 0)
	extraLayer = extraDataSource.GetLayer(appendingFileName)
	
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
	del extraFeature
	del inLayer
	del inDataSource
	del inDriver
	del extraLayer
	del extraDataSource
	del extraDriver

def AppendLayerToShapefile(inFolder, inFileName, appendingDataSource, appendingMemory):
	"""
	This function will append an ogr memory layer to an existing feature class. As of now, it is uncertain
	if this will work with layers that have different attributes. Both the appending memory data source and layer
	are both needed because the memory layer cannot be opened without the data source.

	Requirement: 'FileGDB' driver for ogr

	Args:
		inGDB: path to the geodatabase where the feature class is located
		inFileName: name of the feature class
		appendingDataSource: memory data source that will be appended to the feature class
		appendingMemory: memory layer that will be appended to the feature class

	Returns: N/A

	"""
	
	from osgeo import ogr
	
	# open in file which will be appended to
	inDriver = ogr.GetDriverByName('ESRI Shapefile')
	inDataSource = inDriver.Open(inFolder + '\\' + inFileName + '.shp', 1)
	inLayer = inDataSource.GetLayer()
	
	appendingMemory.ResetReading()
	
	inLayerDefn = inLayer.GetLayerDefn()
	
	for input_feat in appendingMemory:
		
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
	del input_feat
	del inLayer
	del inDataSource
	del inDriver
	del appendingMemory
	del appendingDataSource

def AppendLayerToLayer(inDataSource, inMemory, appendingDataSource, appendingMemory):
	"""
	This function will append a memory layer to another memory layer, return the memory data source
	and layer that was appended, and delete the appended memory data source and layer. The two layers must
	have the same field names!!!

	Args:
		inDataSource: input memory data source
		inMemory: input memory layer
		appendingDataSource: memory data source that will be appended to the input
		appendingMemory: memory layer that will be appended to the input

	Returns: input memory data source and layer that was appended to as well as the appended data source and memory

	"""
	
	from osgeo import ogr
	
	inLayerDefn = inMemory.GetLayerDefn()
	
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
		inMemory.CreateFeature(extraFeature)
	
	del extraFeature
	
	inMemory.ResetReading()
	appendingMemory.ResetReading()
	
	return inDataSource, inMemory, appendingDataSource, appendingMemory

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
	
	from osgeo import ogr
	
	# open in feature using the driver
	inDriver = ogr.GetDriverByName('FileGDB')
	inDataSource = inDriver.Open(inGDB, 1)
	inLayer = inDataSource.GetLayer(inFileName)
	
	# open feature that has the fields wanted
	fieldsDriver = ogr.GetDriverByName('FileGDB')
	fieldsDataSource = fieldsDriver.Open(fieldsGDB, 0)
	fieldsLayer = fieldsDataSource.GetLayer(fieldsFeatureName)
	
	# add field layer fields to the inLayer
	inLayer.CreateFields(fieldsLayer.schema)
	
	# Save and close DataSources
	del inLayer
	del inDataSource
	del inDriver
	del fieldsLayer
	del fieldsDataSource
	del fieldsDriver

# def SeparateDissolveMerge(inDataSource, inMemory, inFeatureName, outFeaturePath, dissolveField, shapefileFolder):
# 	"""
#
# 	THIS FUNCTION DOESN'T WORK!!!!!!!!!!!!!!
#
# 	This function will take an input ogr memory layer, create a list of the unique values for a certain dissolve
# 	field, separate the memory layer based on unique dissolve field values, dissolve each unique dissolve field
# 	feature geometries into one, and merge all layers back together into one, fully dissolved, feature class.
#
# 	NOTE: This function requires the DissolveWithFiona_FromMemory function as well!!!!!!!! See the help for that
# 	for additional information.
#
# 	Requirement: 'FileGDB' driver for ogr
#
# 	Args:
# 		inDataSource: input memory data source
# 		inMemory: input memory layer
# 		inFeatureName: name of the input layer
# 		outFeaturePath: full path to the output feature class (must be in geodatabase)
# 		dissolveField: attribute field to be dissolved by
# 		shapefileFolder: folder that will be used to contain the shapefiles created with the
# 			DissolveWithFiona_FromMemory function.
#
# 	Returns: N/A
#
# 	"""
#
# 	print('Beginning dissolve function for ' + format(inFeatureName))
#
# 	# set inDataSource variable
# 	# inDataSource = inDataSource
#
# 	# from the input feature class, create a set of unique dissolve field values
# 	uniqueRARNUMs = set()
# 	for feature in inMemory:
# 		rarnum = feature.GetField(dissolveField)
# 		uniqueRARNUMs.add(rarnum)
#
# 	# create a list that the dissolved memory layers will be added to
# 	memory_list = []
#
# 	# for each unique RARNUM, separate into separate feature classes in the GDB
# 	for value in uniqueRARNUMs:
# 		print('Dissolving ' + format(value))
#
# 		query = '{} = {}'.format(dissolveField, value)
# 		dataSource, memory = ExtractFeaturesInMemory_ByAttribute_ToMemory(inDataSource, inMemory, query, format(inFeatureName) + '_separated_' + format(value))
#
# 		print('features for dissolve value of ' + format(value) + ' extracted from the input')
#
# 		inFileName = format(inFeatureName) + '_separated_' + format(value)
# 		outFileName = format(inFeatureName) + '_dissolved_' + format(value)
#
# 		dissolvedDataSource, dissolvedMemory = DissolveWithFiona_FromMemory(dataSource, memory, inFileName, outFileName,
# 																			shapefileFolder, dissolveField)
#
# 		print('dissolve completed for ' + format(value))
#
# 		# create a temporary list that will contain the previous data source and memory for the dissolved feature
# 		temp_list = [dissolvedDataSource, dissolvedMemory]
#
# 		# add dissolved memory layer to the memory list
# 		memory_list.append(temp_list)
#
# 		# delete memory to save space
# 		dissolvedDataSource = None
# 		dissolvedMemory = None
#
# 	# now the input data source and layer can be deleted
# 	inDataSource = None
# 	inMemory = None
#
# 	# now merge, if the new file doesn't exist, create a new one
# 	for pair in memory_list:
#
# 		if arcpy.Exists(outFeaturePath):
#
# 			# append to existing feature class
# 			AppendMemoryToFeature(outFeaturePath.rsplit('\\', 1)[0], outFeaturePath.rsplit('\\')[-1], pair[0],
# 								  pair[1])  # TODO: add data source input to function
#
# 		else:
#
# 			# create a new feature class
# 			MemoryToFeature(pair[0], pair[1], outFeaturePath.rsplit('\\', 1)[0], outFeaturePath.rsplit('\\')[-1])

def ListOGR_drivers():
	import ogr
	cnt = ogr.GetDriverCount()
	formatsList = []  # Empty List
	
	for i in range(cnt):
		driver = ogr.GetDriver(i)
		driverName = driver.GetName()
		if not driverName in formatsList:
			formatsList.append(driverName)
	
	formatsList.sort()  # Sorting the messy list of ogr drivers
	
	for i in formatsList:
		print i

def TableToCSV(inGDB, inTableName, outTablePath):
	from osgeo import ogr
	import csv
	
	# open table in geodatabase
	inDriver = ogr.GetDriverByName('FileGDB')
	inDataSource = inDriver.Open(inGDB, 0)
	inTable = inDataSource.GetLayer(inTableName)
	
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
	del inDriver

def CheckFeatureCount_Shapefile(shapefileFolder, fileName):
	
	from osgeo import ogr
	
	d = ogr.GetDriverByName('ESRI Shapefile')
	ds = d.Open(shapefileFolder + '\\' + fileName + '.shp', 0)
	l = ds.GetLayer()
	feat_num = l.GetFeatureCount()
	del l
	del ds
	del d
	
	return feat_num

def Dissolve_ShapefileToShapefile(shapefileFolder, inFileName, outFileName, lengthFieldName, areaFieldName):
	"""
	DOES NOT WORK YET!!!!
	
	Function to dissolve a shapefile. Will work for points, lines, or polygons. The function
	will calculate the new length and area for each feature, if applicable.

	Args:
		shapefileFolder: path to the folder where the shapefile is located
		inFileName: name of input shapefile
		outFileName: name of output shapefile
		lengthFieldName: name of the field in the shapefile that displays the
			length of a feature. If not applicable, enter empty string.
		areaFieldName: name of the field in the shapefile that displays the
			area of a feature. If not applicable, enter empty string.

	Returns: N/A

	"""
	
	# get layer from data source
	d_in = ogr.GetDriverByName('ESRI Shapefile')
	ds_in = d_in.Open(os.path.join(shapefileFolder, inFileName + '.shp'), 0)
	l_in = ds_in.GetLayer()
	
	# check the geometry of the layer
	check_geom = l_in.GetGeomType()
	multi_geom = None
	if check_geom == 1:
		# crate multi point geometry
		multi_geom = ogr.Geometry(ogr.wkbMultiPoint)
	if check_geom == 2:
		# create multi line string geometry
		multi_geom = ogr.Geometry(ogr.wkbMultiLineString)
	if check_geom == 3:
		# create a multi polygon geometry
		multi_geom = ogr.Geometry(ogr.wkbMultiPolygon)
	
	# Keep track of length variable
	length = 0
	
	# loop through each feature until there are no more
	for input_feat in l_in:
		try:
			length += input_feat.GetField(lengthFieldName)
		except:
			pass
		# get geometry from feature
		g = input_feat.GetGeometryRef()
		
		# add geometry to multi geometry
		multi_geom.AddGeometry(g)
	
	l_in.ResetReading()
	
	# dissolve the multi geometry using union cascaded
	new_geom = multi_geom.UnionCascaded()
	
	d_out = ogr.GetDriverByName('ESRI Shapefile')
	outPath = os.path.join(shapefileFolder, outFileName + '.shp')
	
	# remove output shape file if it already exists
	if os.path.exists(outPath):
		d_out.DeleteDataSource(outPath)
	
	# open new shapefile
	ds_out = d_out.CreateDataSource(outPath)
	l_out = ds_out.CreateLayer(outFileName, l_in.GetSpatialRef(), multi_geom.GetGeometryType())
	
	# add field schema to out layer
	l_out.CreateFields(l_in.schema)
	
	defn = l_in.GetLayerDefn()
	
	# create a new feature
	newFeat = ogr.Feature(l_out.GetLayerDefn())
	# add geometry to the new feature
	newFeat.SetGeometry(new_geom)
	# add field values to the new feature
	for i in range(0, defn.GetFieldCount()):
		field_value = l_in.GetFeature(0).GetField(i)
		field_name = defn.GetFieldDefn(i).GetNameRef()
		# get geometry
		g = newFeat.GetGeometryRef()
		if field_name == lengthFieldName:
			# set the calculated length from above to the  field value
			field_value = length
		if field_name == areaFieldName:
			# calculate area
			field_value = g.Area()
		newFeat.SetField(i, field_value)
	# add new feature to the out layer
	l_out.CreateFeature(newFeat)
	
	# close data sources
	del l_in
	del ds_in
	del d_in
	del l_out
	del ds_out
	del d_out

def CheckFeatureCount_FeatureGDB(GDB, inFileName):
	"""
	Use this function to calculate the number of features from a layer within a GDB.
	Args:
		GDB: path to the geodatabase
		inFileName: name of the layer

	Returns: object containing a number representing the number of features in the shapefile

	"""
	
	# open in feature using the driver
	inDriver = ogr.GetDriverByName('FileGDB')
	inDataSource = inDriver.Open(GDB, 1)
	inLayer = inDataSource.GetLayer(inFileName)
	
	# get feature count from layer
	feat_num = inLayer.GetFeatureCount()
	del inLayer
	del inDataSource
	del inDriver
	
	return feat_num

def SplitIntoTwoLayers_Shapefile(shapefileFolder, shapefileName):
	"""
	This function will take a shapefile and split it into 2 separate shapefiles. The first output will have the first half
	of the number of features, the second output will have the other half. The two outputs will have a '_A' and '_B'
	added to the names.

	Args:
		shapefileFolder:
		shapefileName:

	Returns: N/A

	"""
	
	# Open input shapefile
	inDriver = ogr.GetDriverByName('ESRI Shapefile')
	inDataSource = inDriver.Open(shapefileFolder + '\\' + shapefileName + '.shp')
	inLayer = inDataSource.GetLayer()
	
	# Get feature count
	feat_count = inLayer.GetFeatureCount()
	
	# open first new shapefile
	outDriver_A = ogr.GetDriverByName('ESRI Shapefile')
	
	# remove output shape file if it already exists
	if os.path.exists(shapefileFolder + '\\' + shapefileName + '_A.shp'):
		outDriver_A.DeleteDataSource(shapefileFolder + '\\' + shapefileName + '_A.shp')
	
	# create output shape file
	outDataSource_A = outDriver_A.CreateDataSource(shapefileFolder + '\\' + shapefileName + '_A.shp')
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
	
	# remove output shape file if it already exists
	if os.path.exists(shapefileFolder + '\\' + shapefileName + '_B.shp'):
		outDriver_B.DeleteDataSource(shapefileFolder + '\\' + shapefileName + '_B.shp')
	
	# create output shape file
	outDataSource_B = outDriver_B.CreateDataSource(shapefileFolder + '\\' + shapefileName + '_B.shp')
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
	del inDriver

def PullIndexFromFeature(GDB, inFileName, fieldName):
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
	driver = ogr.GetDriverByName('FileGDB')
	dataSource = driver.Open(GDB, 0)
	layer = dataSource.GetLayer(inFileName)
	
	# get feature definition from the layer
	defn = layer.GetLayerDefn()
	
	# get field index based on field name
	index = defn.GetFieldIndex(fieldName)
	
	# delete objects
	del layer
	del dataSource
	del driver
	
	return index

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
		dataSource = driver.Open(folder + '\\' + inFileName + '.shp', 0)
		layer = dataSource.GetLayer()
	
	# get the geometry type from the layer
	geometry_type = layer.GetGeomType()
	
	# return the geometry type integer
	return geometry_type
	
	# delete layers
	del layer
	del dataSource
	del driver

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


def CSV_to_list(csv_path):
	list = []
	with open(csv_path, 'r') as Record:
		reader = csv.reader(Record)
		for line in reader:
			list.append(line)
	
	return (list)


def CalculateAgeInYears(install_str, removal_str, format):
	"""
	Function to calculate the number of years between two dates.
	Will return a year float to 2 decimal places.

	Args:
		install_str: string indicating install date
		removal_str: string indicating removal date
		format: date string format according to datetime module

	Returns: float indicating years

	"""
	
	install = datetime.strptime(install_str, format)
	removal = datetime.strptime(removal_str, format)
	
	diff = removal - install
	
	years = round((diff.days + diff.seconds / 86400) / 365.2425, 1)
	
	return years


def ReturnAgeCategory(age):
	"""
		This function is specific, as in it will return a string of the
	year range that an age falls between. These current year ranges
	were picked for the offshore infrastructure project to help
	predict the possible range of age at removal for platforms
	using machine learning. This should be adjusted as necessary.

	Args:
		age: float or integer indicating age

	Returns: string indicating age range category

	"""
	
	if (age >= 0) and (age < 11):
		return '0-11'
	if (age >= 11) and (age <= 20):
		return '11-20'
	if (age >= 20) and (age < 30):
		return '20-30'
	if (age >= 0) and (age < 11):
		return '30-42'
	if (age >= 42):
		return '42-72'