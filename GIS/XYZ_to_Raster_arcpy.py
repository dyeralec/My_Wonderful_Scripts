import arcpy
arcpy.CheckOutExtension("3D")

workspace = arcpy.GetParameterAsText(0)
arcpy.env.workspace = workspace

projection = arcpy.GetParameterAsText(1)

suffix = arcpy.GetParameterAsText(2)

xyz_list = arcpy.ListFiles()

for xyz in xyz_list:
    shape_name = str(xyz[:-4])+".shp"
    raster_name = str(xyz[:-4])+"."+str(suffix)
    arcpy.ASCII3DToFeatureClass_3d(xyz, "XYZ", shape_name, "POINT", "1", projection, "5", "","DECIMAL_POINT")
    arcpy.PointToRaster_conversion(shape_name, "Shape.Z", raster_name, "MEAN", "NONE", "5")