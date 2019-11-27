"""
This script will contain a function that can dissolve layer and save it to a shapefile
"""

def Dissolve_ShapefileToShapefile(shapefileFolder,inFileName,outFileName):
	
	from osgeo import ogr
	import os
	
	# get layer from data source
	d_in = ogr.GetDriverByName('ESRI Shapefile')
	ds_in = d_in.Open(shapefileFolder + '\\' + inFileName + '.shp', 0)
	l_in = ds_in.GetLayer()
	
	# check the geometry of the layer
	check_geom = l_in.GetGeomType()
	
	if check_geom == 1:
		# crate multi point geometry
		multi_geom = ogr.Geometry(ogr.wkbMultiPoint)
		set_geom = ogr.wkbMultiPoint
	if check_geom == 2:
		# create multi line string geometry
		multi_geom = ogr.Geometry(ogr.wkbMultiLineString)
		set_geom = ogr.wkbMultiLineString
	if check_geom == 3:
		# create a multi polygon geometry
		multi_geom = ogr.Geometry(ogr.wkbMultiPolygon)
		set_geom = ogr.wkbMultiPolygon
	
	# Keep track of length variable
	length = 0
	
	# loop through each feature until there are no more
	for input_feat in l_in:
		if (check_geom == 2) or (check_geom == 3):
			length += input_feat.GetField('Shape_Leng')
		# get geometry from feature
		g = input_feat.GetGeometryRef()
		
		# add geometry to multi geometry
		multi_geom.AddGeometry(g)
	
	l_in.ResetReading()
	
	# dissolve the multi geometry using union cascaded if not a point a layer
	if (check_geom == 2) or (check_geom == 3):
		new_geom = multi_geom.UnionCascaded()
	else:
		new_geom = multi_geom
	
	d_out = ogr.GetDriverByName('ESRI Shapefile')
	
	# remove output shape file if it already exists
	if os.path.exists(shapefileFolder + '\\' + outFileName + '.shp'):
		d_out.DeleteDataSource(shapefileFolder + '\\' + outFileName + '.shp')
	
	# open new shapefile
	ds_out = d_out.CreateDataSource(shapefileFolder + '\\' + outFileName + '.shp')
	l_out = ds_out.CreateLayer(outFileName, l_in.GetSpatialRef(), set_geom)
	
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
		# if the field name is 'ID', set that value to blank
		if field_name == 'ID':
			field_value = ""
		if (field_name == 'SHAPE_Leng') or (field_name == 'Shape_Leng'):
			# set the calculated length from above to the  field value
			field_value = length
			if check_geom == 2:
				geom_length = newFeat.GetGeometryRef().Length()
				field_value = geom_length
		if (field_name == 'SHAPE_Area') or (field_name == 'Shape_Area'):
			# get geometry
			g = newFeat.GetGeometryRef()
			# calculate area
			field_value = g.Area()
		newFeat.SetField(i, field_value)
	# add new feature to the out layer
	l_out.CreateFeature(newFeat)
	
	# close data sources
	del ds_in
	del ds_out
	
if __name__ == '__main__':
	
	shapefileFolder = r'P:\02_DataWorking\Atlantic\Environmental Sensitivity Index\Birds_Only_Processing'
	name = 'HERP_separated_285000317'
	
	Dissolve_ShapefileToShapefile(shapefileFolder,name,'HERP_dissolved_285000317')