"""
https://desktop.arcgis.com/en/arcmap/latest/tools/conversion-toolbox/export-metadata.htm
"""

import arcpy
from arcpy import env
env.workspace = r"P:\04_Products (Maps, etc.)\Offshore_Geohaz\Published Data\Historic Submarine Landslides"
#set local variables
dir = arcpy.GetInstallInfo("desktop")["InstallDir"]
translator = r'C:\Program Files (x86)\ArcGIS\Desktop10.7\Metadata\Translator\ARCGIS2FGDC.xml'
arcpy.ExportMetadata_conversion (r"Historic_Submarine_Landslides_V3.shp", translator,
    r"Metadata_FGDC_FromArcpy.xml")