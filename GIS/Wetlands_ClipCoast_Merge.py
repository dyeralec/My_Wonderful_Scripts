import arcpy
import os

wetland_inventory = ["MS_Wetlands.shp",
			  "TX_Wetlands_Central.shp",
			  "TX_Wetlands_East.shp",
			  "TX_Wetlands_West.shp"]

mask = r"E:\GOM\GOM_waters_extent_NAD83_albers.shp"

#output_folder = r'E:\GOM\Wetlands'

arcpy.env.workspace = r'E:\GOM\Wetlands'

outCS = arcpy.SpatialReference(4326)
transformation = "WGS_1984_(ITRF00)_To_NAD_1983"

out_file_list = []

for wetland in wetland_inventory:
	
	#layer_name = wetland.rsplit('\\',1)[1]
	layer_name_3km = wetland.replace('.shp', '_3km.shp')
	layer_name_wgs84 = layer_name_3km.replace('.shp', '_WGS84.shp')
	
	print('Beginning process for ' + wetland)
	
	# layer = arcpy.MakeFeatureLayer_management(wgs84_path)
	layer = arcpy.MakeFeatureLayer_management(wetland)
	
	selection = arcpy.SelectLayerByLocation_management(layer, overlap_type='WITHIN_A_DISTANCE', select_features=mask, search_distance="3 Kilometers")
	
	print('Features selected.')
	
	arcpy.CopyFeatures_management(selection, layer_name_3km)
	
	del layer
	del selection
	
	arcpy.Project_management(in_dataset=layer_name_3km,
							 out_dataset=layer_name_wgs84,
							 out_coor_system=outCS,
							 transform_method=transformation,
							 preserve_shape="PRESERVE_SHAPE")
	
	print(layer_name_wgs84 + ' projection successful.')
	
	print(wetland + ' is finished.')
	
	out_file_list.append(layer_name_wgs84)
	
arcpy.Merge_management(out_file_list, "Wetlands_GOMcoast.shp","","ADD_SOURCE_INFO")