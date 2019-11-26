from osgeo import ogr, osr, gdal
from os import path
from csv import reader as CSVReader, Sniffer as CSVSniffer
import re
import sys, os

from VGMExceptions import VGMFileException

OUTPUT_CS_WKT = 'PROJCS["WGS 84 / Pseudo-Mercator",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,' \
				'AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],' \
				'UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],' \
				'PROJECTION["Mercator_1SP"],PARAMETER["central_meridian",0],PARAMETER["scale_factor",1],' \
				'PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],' \
				'AXIS["X",EAST],AXIS["Y",NORTH],EXTENSION["PROJ4","+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 ' \
				'+lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs"],AUTHORITY["EPSG","3857"]]'


def DuplicateOGRLayer(inLayer, outDir, outLayerName, outCS=None):
	""" Copy an OGR layer into a directory and optionally re-project it.
	Args:
		inLayer (ogr.Layer):
		outDir (str):
		outLayerName (str):
		outCS (osr.SpatialReference.):
	Returns: (outputLayer, ds, outputPath): newly copied layer, Dataset, the output path.
	"""
	
	# https://pcjericks.github.io/py-gdalogr-cookbook/projection.html#reproject-a-layer
	driver = ogr.GetDriverByName("ESRI Shapefile")
	outPath = path.join(outDir, outLayerName + '.shp')
	
	ds = driver.CreateDataSource(outPath)
	outLayer = ds.CreateLayer(outLayerName, srs=inLayer.GetSpatialRef() if outCS is None else outCS,
							  geom_type=inLayer.GetLayerDefn().GetGeomType())
	
	transform = None
	origCoordSys = inLayer.GetSpatialRef()
	if outCS is not None and origCoordSys is not None:
		transform = osr.CoordinateTransformation(origCoordSys, outCS)
	
	lyrDefn = inLayer.GetLayerDefn()
	for i in range(lyrDefn.GetFieldCount()):
		outLayer.CreateField(lyrDefn.GetFieldDefn(i))
	
	outDefn = outLayer.GetLayerDefn()
	inLayer.ResetReading()
	feat = inLayer.GetNextFeature()
	while feat:
		geom = feat.GetGeometryRef().Clone()
		if transform is not None:
			geom.Transform(transform)
		outFeat = ogr.Feature(outDefn)
		outFeat.SetGeometry(geom)
		for i in range(outDefn.GetFieldCount()):
			outFeat.SetField(outDefn.GetFieldDefn(i).GetNameRef(), feat.GetField(i))
		outLayer.CreateFeature(outFeat)
		del outFeat
		del geom
		feat = inLayer.GetNextFeature()
	
	return outLayer, ds, outPath


def DriverForExt(ext):
	"""Return OGR driver for the extension
		Args:
			ext (str): extension (.csv / .shp / etc...) to pick driver from.
		Returns: ogr.Driver for extension.
	"""
	extLower = ext.lower()
	if extLower[0] != '.':
		extLower = '.' + ext
	
	if extLower == '.shp':
		driver = ogr.GetDriverByName("ESRI Shapefile")
	elif extLower == '.csv':
		driver = ogr.GetDriverByName("CSV")
	elif extLower == '.ply':  # and others
		driver = ogr.GetDriverByName("Memory")
	else:
		raise Exception("Unrecognized file extension: " + ext)
	
	return driver


def NewLayer(ds, outName, srs, wkbType):
	""" Create a new layer with the dataset and given parameters.
	Args:
		ds (ogr.Dataset): dataset to create a layer for.
		outName (str): name for new layer.
		srs (ogr.SpatialReference): spatial reference system to use in the new layer.
		wkbType (ogr.wkbType): what type of geometry will be in this layer.
	Returns: newly created layer for the dataset.
	"""
	
	layerOpts = []
	drvName = ds.GetDriver().name
	if drvName.lower() == 'csv':
		layerOpts += ['GEOMETRY=AS_WKT', 'CREATE_CSVT=YES']
	
	# add more as needed
	# turns out CreateLayer doesn't like unicode strings; encode appropriately.
	# see: https://gis.stackexchange.com/questions/53920/ogr-createlayer-returns-typeerror
	if sys.version_info[0] < 3:
		return ds.CreateLayer(outName.encode('utf-8'), srs, wkbType, layerOpts)
	else:
		return ds.CreateLayer(outName, srs, wkbType, layerOpts)


def DriverForPath(filepath):
	"""Return OGR driver for the filetype specified by the path
	Args:
		filepath (str): Path to grab type from
	Returns: ogr.Driver for filetype.
	"""
	return DriverForExt(path.splitext(filepath)[1].lower())


def GetLayerWildcard(isread=True):
	""" Get wildcards for save/load filetypes.
	Args:
		isread (bool): Is the operation a read operation. If true add read specific wildcards. Else add write wildcards.
	Returns: The created list of options.
	"""
	options = ["ESRI Shapefiles (*.shp)", "*.shp",
			   "CSV or geoCSV (*.csv)", "*.csv",
			   ]
	if isread:
		options += ["Earthvision Property Point Data (*.pdat)", "*.pdat",
					"Earthvision Point Data (*.dat)", "*.dat",
					"Raster File (*.tif)", "*.tif"
					]
		allOpts = [options[i] for i in range(len(options)) if i % 2 == 1]
		allStr = ';'.join(allOpts)
		options = ["All Supported ({})".format(allStr), allStr] + options
	else:
		options += ["Earth Vision Polygon file (*.ply)", "*.ply"]
	return "|".join(options)


def LoadRaster(rasDS):
	# Get projection and convert for ogr
	prj = rasDS.GetProjection()
	srs = osr.SpatialReference(wkt=prj)
	
	# Get no data value from first band
	band = rasDS.GetRasterBand(1)
	no_val = band.GetNoDataValue()
	
	return (RasterToPoint(rasDS, srs=srs, field="VALUE", no_val=no_val))


def RasterToPoint(rasterDS, driver=None, srs=None, field="VALUE", no_val=0):
	# https://pcjericks.github.io/py-gdalogr-cookbook/raster_layers.html
	
	# convert raster to numpy array
	bandData = rasterDS.GetRasterBand(1).ReadAsArray()
	
	# build new geometry from bandData
	if driver is not None:
		outDS = driver.CreateDataSource('IDWDS')
	else:
		driver = ogr.GetDriverByName("MEMORY")
		outDS = driver.CreateDataSource("MemDS")  # ogr.DataSource
	# driver = gdal.GetDriverByName('Memory')
	# outDS = driver.Create('', 0, 0, 0, gdal.GDT_Unknown) #gdal.Dataset
	
	# lifted from raster.cpp in BLOSOM
	geoTrans = rasterDS.GetGeoTransform()
	originX = geoTrans[0]
	originY = geoTrans[3]
	pSizeX = geoTrans[1]
	pSizeY = geoTrans[5]
	
	if srs is not None:
		lyr = NewLayer(outDS, 'IDWPoints', srs, ogr.wkbPoint)
	else:
		lyr = outDS.CreateLayer("MemDS", geom_type=ogr.wkbPoint)
	
	fd = ogr.FieldDefn(field, ogr.OFTReal)
	lyr.CreateField(fd)
	
	for x in range(rasterDS.RasterXSize):
		for y in range(rasterDS.RasterYSize):
			
			if bandData[y, x] != no_val:
				# build point
				pt = ogr.Geometry(ogr.wkbPoint)
				pt.AddPoint(originX + (x * (pSizeX)) + (pSizeX / 2), originY + (y * (pSizeY)) + (pSizeY / 2))
				
				# build feature
				feat = ogr.Feature(lyr.GetLayerDefn())
				feat.SetGeometry(pt)
				
				# set field value
				feat.SetField(field, float(bandData[y, x]))
				
				# create feature
				lyr.CreateFeature(feat)
				
				# cleanup feature
				feat.Destroy()
	
	return outDS, lyr


def getLayerFields(layer):
	"""Get field names from layer if the type is valid
	Valid types: ogr.OFTInteger, ogr.OFTReal, ogr.OFTInteger64
	Args:
		layer (ogr.Layer): Layer to grab all field information from
	Returns: list of field names of valid types.
	"""
	validFieldTypes = [ogr.OFTInteger, ogr.OFTReal, ogr.OFTInteger64]
	defn = layer.GetLayerDefn()
	return [defn.GetFieldDefn(i).GetName() for i in range(defn.GetFieldCount()) if
			defn.GetFieldDefn(i).GetType() in validFieldTypes]


######################
# CSV Creation Stuff #
######################

def openGenericCSV(path):
	"""Open the CSV at the specified path. Try to guess the type of CSV.
	Args:
		path (str): CSV filepath to be opened.
	Returns: dict containing 'headers' list of headers and 'rows' list of rows.
	"""
	with open(path, 'r') as inFile:
		# Use sniffer to guess type of csv
		dialect = CSVSniffer().sniff(inFile.read(2048))
		inFile.seek(0)
		
		rdr = CSVReader(inFile, dialect)
		
		itr = iter(rdr)
		headers = next(itr)
		
		rows = []
		for r in itr:
			
			# check for empty row ( happens with some dat files originating from csvs)
			if len(''.join(r)) == 0:
				continue
			rows.append(r)
		
		return {'headers': headers,
				'rows': rows}


def _scrubNumber(strVal):
	return float(re.sub('[, _]', '', strVal))


def GeneratePointsFromCSV(name, colMap, data):
	"""Generate a dataset of points from CSV given corresponding columns
	Args:
		name (str): Name for the generated Dataset
		colMap (dict): Map of column names to input type (x/y/attributes)
		data (dict): Rows and row headers from the CSV
	"""
	
	headers = data['headers']
	rows = data['rows']
	
	drvr = ogr.GetDriverByName("Memory")
	ds = drvr.CreateDataSource('csv_pts')
	
	inlyr = ds.CreateLayer(name, geom_type=ogr.wkbPoint)
	
	for aInd in colMap['aInds']:
		# assume all fields are doubles
		fdfn = ogr.FieldDefn(headers[aInd], ogr.OFTReal)
		inlyr.CreateField(fdfn)
	
	xCol = colMap['xInd']
	yCol = colMap['yInd']
	for r in rows:
		newPt = ogr.Geometry(ogr.wkbPoint)
		newPt.AddPoint_2D(_scrubNumber(r[xCol]), _scrubNumber(r[yCol]))
		feat = ogr.Feature(inlyr.GetLayerDefn())
		feat.SetGeometry(newPt)
		
		for aInd in colMap['aInds']:
			feat.SetField(headers[aInd], _scrubNumber(r[aInd]))
		
		inlyr.CreateFeature(feat)
	
	return ds


def packUserCols(colInds, headers):
	""" Pack user specified columns into dictionary specifying x/y positions and attributes.
	Args:
		colInds (dict): dict of indexes keyed to 'xInd', 'yInd' or 'aInds'
		headers (list): CSV column headers
	Returns: Dict with 'x_col', 'y_col', 'a_cols' mapped to appropriate CSV columns.
	"""
	return {'x_col': headers[colInds['xInd']],
			'y_col': headers[colInds['yInd']],
			'a_cols': [headers[i] for i in colInds['aInds']]}


def unpackUserCols(names, headers):
	""" Unpack user specified columns from dictionary for x/y positions and attributes.
	Args:
		names (dict): Column names linked to indexes
		headers (list): List of CSV column headers
	Returns: Dict with 'xInd', 'yInd', 'aInds' representing CSV indexes.
	"""
	missing = []
	xInd = None
	yInd = None
	
	try:
		xInd = headers.index(names['x_col'])
	except ValueError as e:
		missing.append(str(e))
	
	try:
		yInd = headers.index(names['y_col'])
	except ValueError as e:
		missing.append(str(e))
	
	aInds = []
	for ac in names['a_cols']:
		try:
			aInds.append(headers.index(ac))
		except ValueError as e:
			missing.append(str(e))
	
	if len(missing) > 0:
		raise VGMFileException("The following errors encountered when loading CSV:\n" + '\n'.join(missing))
	
	return {'xInd': xInd,
			'yInd': yInd,
			'aInds': aInds,
			}