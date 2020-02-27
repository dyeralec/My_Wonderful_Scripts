import arcpy
import os

wetland_inventory = [r"P:\01_DataOriginals\GOM\Environment\Wetlands\AL\AL_shapefile_wetlands\AL_shapefile_wetlands\AL_Wetlands.shp",
			  r"P:\01_DataOriginals\GOM\Environment\Wetlands\FL\FL_shapefile_wetlands\FL_shapefile_wetlands\FL_Wetlands.shp",
			  r"P:\01_DataOriginals\GOM\Environment\Wetlands\LA\LA_shapefile_wetlands\LA_shapefile_wetlands\LA_Wetlands.shp",
			  r"P:\01_DataOriginals\GOM\Environment\Wetlands\MS\MS_shapefile_wetlands\MS_shapefile_wetlands\MS_Wetlands.shp",
			  r"P:\01_DataOriginals\GOM\Environment\Wetlands\TX\TX_shapefile_wetlands\TX_shapefile_wetlands\TX_Wetlands_Central.shp",
			  r"P:\01_DataOriginals\GOM\Environment\Wetlands\TX\TX_shapefile_wetlands\TX_shapefile_wetlands\TX_Wetlands_East.shp",
			  r"P:\01_DataOriginals\GOM\Environment\Wetlands\TX\TX_shapefile_wetlands\TX_shapefile_wetlands\TX_Wetlands_West.shp"]

mask = r"E:\GOM\GOM_Ex_Extent.shp"

output_folder = r'P:\02_DataWorking\GOM\Environment\Wetlands\\'

# arcpy.env.workspace(r'P:\02_DataWorking\GOM\Environment\Wetlands')

outCS = arcpy.SpatialReference(4326)
transformation = 'NAD_1983_To_WGS_1984_1'

out_file_list = []

for wetland in wetland_inventory:
	
	layer_name = wetland.rsplit('\\',1)[1]
	layer_name_wgs84 = layer_name.replace('.shp','_WGS84.shp')
	wgs84_path = os.path.join(output_folder,layer_name_wgs84)
	layer_name_3km = layer_name.replace('.shp', '_3km.shp')
	
	print('Beginning process for ' + layer_name)
	
	arcpy.Project_management(in_dataset=wetland,
							 out_dataset=wgs84_path,
							 out_coor_system=outCS,
							 transform_method=transformation,
							 preserve_shape="PRESERVE_SHAPE")
	
	print(layer_name + ' projection successful.')
	
	layer = arcpy.MakeFeatureLayer_management(wgs84_path)
	
	selection = arcpy.SelectLayerByLocation_management(layer, overlap_type='WITHIN_A_DISTANCE', select_features=mask, search_distance="3000 Meters")
	
	print('Features selected.')
	
	out_name = os.path.join(output_folder, layer_name_3km)
	out_file_list.append(out_name)
	
	arcpy.CopyFeatures_management(selection, out_name)
	
	print(layer_name + ' is finished.')
	
arcpy.Merge_management(out_file_list, os.path.join(output_folder,'Wetlands_GOMcoast.shp'),"","ADD_SOURCE_INFO")