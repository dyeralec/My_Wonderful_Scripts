"""
Use this script to update the oil refineries shapefile. Once new data is downloaded, run this code to:
1) clip to Gulf of Mexico region
2) re-project into WGS84 (or change projection if you want)

To run, fill in strings for the new shapefile location, location of file to clip with, and
the new output location.

Alec Dyer
alec.dyer@netl.doe.gov
"""

import arcpy

in_feature = r"P:\01_DataOriginals\USA\Infrastructure\ShippingFairwaysLanesandZones\shippinglanes"
out_feature = r"P:\03_DataFinal\GOM\Infrastructure\ShippingLanes\GOM_shippinglanes"
clip_feature = r"P:\03_DataFinal\GOM\Boundaries\Extent\GOM_Extent_All"

arcpy.Clip_analysis(in_feature + '.shp',clip_feature + '.shp',out_feature + '.shp')

sr = arcpy.SpatialReference(4326)

spatial_ref = arcpy.Describe(out_feature + '.shp').spatialReference

if spatial_ref.Name != sr.GCSName:

	arcpy.Project_management(out_feature + '.shp', out_feature + '.shp', sr)