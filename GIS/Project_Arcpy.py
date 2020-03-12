import arcpy
import os

Shapefiles = []

main_dir = r'R:\GEOWorkspace\C_Projects\BOEM IAA\BOEM_IAA_Database'
out_dir = r'R:\GEOWorkspace\C_Projects\BOEM IAA\BOEM_IAA_Database'

outCS = arcpy.SpatialReference(4326)
transformation = 'NAD_1927_To_NAD_1983_NADCON + WGS_1984_(ITRF00)_To_NAD_1983'

for shp in os.listdir(main_dir):
	
	if shp.endswith('.shp'):
		ref = arcpy.Describe(os.path.join(main_dir, shp)).spatialReference
		
		print(ref)
		
		arcpy.Project_management(in_dataset=os.path.join(main_dir, shp),
								 out_dataset=os.path.join(out_dir, shp),
								 out_coor_system=outCS,
								 transform_method=transformation,
								 preserve_shape="PRESERVE_SHAPE")
