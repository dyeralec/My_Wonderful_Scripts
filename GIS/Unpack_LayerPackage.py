"""
Use this script to unpack an ArcGIS layer package are turn all layers into
a sepearate shapefile.
"""

import arcpy
import os

layerPkgPath = r"E:\GOM\BOEM_SeismicAnomolies\BOEM_Seafloor_Anomalies_June_2019.lpk"
mapPath = r"E:\GOM\BOEM_SeismicAnomolies\GOM_SeismicAnomolies.mxd"

outFolder = r"E:\GOM\BOEM_SeismicAnomolies"

lyrFile = arcpy.MakeFeatureLayer_management(layerPkgPath)

#mxd = arcpy.mapping.MapDocument(mapPath)
#df = arcpy.mapping.ListDataFrames(mxd, '')[0]

for lyr in lyrFile.ListLayers():
	
	name = lyr.name
	print(name)
	
	#newLayer = arcpy.MakeFeatureLayer_management(lyr)
	
	#lyr.saveACopy(os.path.join(outFolder,name + '.shp'))