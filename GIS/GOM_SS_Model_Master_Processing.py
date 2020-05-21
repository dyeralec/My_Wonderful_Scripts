"""
This script will be used to for processing the final master map shapefiles for the Task 6
GOM subsurface model for identifying subsurface features within the Terrebonne basin.
5 members of the team have gone on their own to label features with lines and polygons.
Now, this script will take the notes created by AD and SP that reference the final features
to create 2 master shapefiles, one for points and one for polyons.

The shapefile will include  attribute fields of feature ID, feature name, who created it,
map scale, notes, and notes that others wrote for the same area (if applicable).

created by Alec Dyer, alec.dyer@netl.doe.gov
03-11-2020

"""

import os
from osgeo import ogr
from gdal import osr
from MyFunctions import*
import csv

class ShapefileLayers(object):

	def __init__(self, AD, SP, MMM, PAM, AJB):
		
		self.AD = AD
		self.SP = SP
		self.MMM = MMM
		self.PAM = PAM
		self.AJB = AJB
		
class Record(object):
	
	def __init__(self, list):
		
		self.fid = list[0]
		self.creator = list[1]
		self.featureId = list[2]
		self.featureName = list[3]
		self.AD_fid = list[4]
		self.SP_fid = list[5]
		self.MMM_fid = list[6]
		self.PAM_fid = list[7]
		self.AJB_fid = list[8]
		
def CreateShapefile(filePath, geomType):
	"""
	This function is specific to GOM_SS_Model_Master_Processing.py
	
	Creates a new shapefile with wanted fields
	
	Args:
		filePath: path to where the shapefile should be created (string)

	"""
	
	srs = osr.SpatialReference()
	srs.ImportFromEPSG(4326)
	
	# open new shapefile
	driver = ogr.GetDriverByName('ESRI Shapefile')
	dataSource = driver.CreateDataSource(filePath)
	layer = dataSource.CreateLayer('Layer', srs = srs, geom_type = geomType)
	
	# create new fields
	FeatureID = ogr.FieldDefn("FeatureID", ogr.OFTInteger)
	FeatureID.SetWidth(3)
	layer.CreateField(FeatureID)
	
	FeatureName = ogr.FieldDefn("Name", ogr.OFTString)
	FeatureName.SetWidth(20)
	layer.CreateField(FeatureName)
	
	MapScale = ogr.FieldDefn("MapScale", ogr.OFTString)
	FeatureName.SetWidth(15)
	layer.CreateField(MapScale)
	
	Creator = ogr.FieldDefn("Creator", ogr.OFTString)
	FeatureName.SetWidth(3)
	layer.CreateField(Creator)
	
	CreatorNotes = ogr.FieldDefn("CrtrNotes", ogr.OFTString)
	layer.CreateField(CreatorNotes)
	
	ADnotesField = ogr.FieldDefn("ADnotes", ogr.OFTString)
	layer.CreateField(ADnotesField)
	
	SPnotesField = ogr.FieldDefn("SPnotes", ogr.OFTString)
	layer.CreateField(SPnotesField)
	
	MMMnotesField = ogr.FieldDefn("MMMnotes", ogr.OFTString)
	layer.CreateField(MMMnotesField)
	
	PAMnotesField = ogr.FieldDefn("PAMnotes", ogr.OFTString)
	layer.CreateField(PAMnotesField)
	
	AJBnotesField = ogr.FieldDefn("AJBnotes", ogr.OFTString)
	layer.CreateField(AJBnotesField)
		
def AddFeatureToMaster(dataSource, feature, masterShapefile, ADnotes, SPnotes, MMMnotes, PAMnotes, AJBnotes):
	
	# open master shapefile
	masterDriver = ogr.GetDriverByName('ESRI Shapefile')
	masterDataSource = masterDriver.Open(masterShapefile, 1)
	masterLayer = masterDataSource.GetLayer()
	
	masterLyrDefn = masterLayer.GetLayerDefn()
	
	# from input feature, grab needed fields
	featureID = feature.GetField("ID")
	featureName = feature.GetField("Name")
	MapScale = feature.GetField("MapScale")
	Creator = feature.GetField("Reviewer")
	Notes = feature.GetField("Notes")
	
	# create feature in the master layer
	# Create output Feature
	outFeature = ogr.Feature(masterLyrDefn)
	
	# Set geometry as centroid
	geom = feature.GetGeometryRef()
	outFeature.SetGeometry(geom)
	
	# Add field values from input Layer
	outFeature.SetField(0, featureID)
	outFeature.SetField(1, featureName)
	outFeature.SetField(2, MapScale)
	outFeature.SetField(3, Creator)
	outFeature.SetField(4, Notes)
	outFeature.SetField(5, ADnotes)
	outFeature.SetField(6, SPnotes)
	outFeature.SetField(7, MMMnotes)
	outFeature.SetField(8, PAMnotes)
	outFeature.SetField(9, AJBnotes)
	
	# Add new feature to output Layer
	masterLayer.CreateFeature(outFeature)
	
	del masterLayer
	del masterDataSource
	del feature
	del dataSource
		
if __name__ == "__main__":
	
	# inputs will be a csv and the shapefiles for both line and polygons. These will be handled separately.
	lineCsv = None
	polyCsv = r"P:\05_AnalysisProjects_Working\GOM Subsurface Data Model\Seafloor Mapping\GOM_Master\GOM_SS_Master_Spreadsheet_Poly_AD.csv"
	
	ADlineShp = None
	ADpolyShp = r"P:\05_AnalysisProjects_Working\GOM Subsurface Data Model\Seafloor Mapping\GOM_Master\AD_Features\GOMFeatures_Poly_AD.shp"
	SPlineShp = None
	SPpolyShp = r"P:\05_AnalysisProjects_Working\GOM Subsurface Data Model\Seafloor Mapping\GOM_Master\SP_Features\GOMFeatures_Poloygon_SP.shp"
	MMMlineShp = None
	MMMpolyShp = r"P:\05_AnalysisProjects_Working\GOM Subsurface Data Model\Seafloor Mapping\GOM_Master\MMM_Features\GOMFeatures_PolyMMM.shp"
	PAMlineShp = None
	PAMpolyShp = r"P:\05_AnalysisProjects_Working\GOM Subsurface Data Model\Seafloor Mapping\GOM_Master\PAM_Features\PolygonFeatures_GOM_PAM.shp"
	AJBlineShp = None
	AJBpolyShp = r"P:\05_AnalysisProjects_Working\GOM Subsurface Data Model\Seafloor Mapping\GOM_Master\AJB_Features\GOMFeatures_Poly.shp"
	
	# final outputs will be new line and polygon shapefiles
	lineShpMaster = None
	polyShpMaster = r'E:\masterPolyTest.shp'
	
	# create dictionary of names of each features id value
	featureDict = {1: "Fault", 2: "Landslide Extent", 3: "Scarp", 4: "Pockmark", 5: "Furrow", 6: "Dune", 7: "Dome", 8: "Misc", 9: "Mound",\
				   10: "Artifact (linear)", 11: "Artifact (low res area)", 12: "Fans", 13: "Ridges", 14: "Thalweg", 15: "Elevated area", 16: "Basin"}
	
	TypesToLoop = ['polys','lines']
	
	# loop through line and polygon
	for type in TypesToLoop:
		
		if type == 'polys':
			inputCsv = polyCsv
			inputShps = ShapefileLayers(ADpolyShp, SPpolyShp, MMMpolyShp, PAMpolyShp, AJBpolyShp)
			outputShp = polyShpMaster
			# create new shapefile
			CreateShapefile(outputShp, ogr.wkbMultiPolygon)
		if type == 'lines':
			inputCsv = lineCsv
			inputShps = ShapefileLayers(ADlineShp, SPlineShp, MMMlineShp, PAMlineShp, AJBlineShp)
			outputShp = lineShpMaster
			# create new shapefile
			CreateShapefile(outputShp, ogr.wkbMultiLineString)
			
		# create list of records from
		recordsList = CSV_to_list(inputCsv)
		
		# loop through each record
		for r in recordsList:
			
			if r == recordsList[0]:
				continue
			
			# create Record class
			record = Record(r)
			
			# assign shapefile to pick master feature from
			if record.creator == 'AD':
				masterShp = inputShps.AD
			if record.creator == 'SP':
				masterShp = inputShps.SP
			if record.creator == 'MMM':
				masterShp = inputShps.MMM
			if record.creator == 'PAM':
				masterShp = inputShps.PAM
			if record.creator == 'AJB':
				masterShp = inputShps.AJB
				
			print(record.creator)
	
			# for each record, grab feature from input layer
			dataSource, feat = GetFeatureFromShapefile(masterShp, record.fid)
			
			# grab the notes from each reviewers shapefiles based on their fid
			ADnotes = GetFieldFromShapefile(inputShps.AD, record.AD_fid, "Notes")
			SPnotes = GetFieldFromShapefile(inputShps.SP, record.SP_fid, "Notes")
			MMMnotes = GetFieldFromShapefile(inputShps.MMM, record.MMM_fid, "Notes")
			PAMnotes = GetFieldFromShapefile(inputShps.PAM, record.PAM_fid, "Notes")
			AJBnotes = GetFieldFromShapefile(inputShps.AJB, record.AJB_fid, "Notes")
	
			# for master layer, add new feature to it with add field values for notes
			new_feat = AddFeatureToMaster(dataSource, feat, outputShp, ADnotes, SPnotes, MMMnotes, PAMnotes, AJBnotes)