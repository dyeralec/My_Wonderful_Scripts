"""
Script to format an excel spreadsheet into a table in arc, summarize the table
by lease block, and then join to a OCS lease block shapefile.
"""

import arcpy
import os

input_table = r"P:\01_DataOriginals\GOM\Infrastructure\Emissions\2017_Gulfwide_Platform_Inventory_20190705_CAP_GHG\2017_Gulfwide_Platform_20190705_CAP_GHG.xlsx"
input_blocks = r"P:\01_DataOriginals\GOM\Boundaries\Blocks\blk_clip.shp"
output_folder = r"P:\01_DataOriginals\GOM\Infrastructure\Emissions\2017_Gulfwide_Platform_Inventory_20190705_CAP_GHG\Shapefiles"

# set arcpy environment
arcpy.env.workspace = output_folder

# get table name
tableName = input_table.rsplit('\\',1)[1].replace('.xlsx','')
SumTablePath = os.path.join(output_folder,tableName + "_SummaryStats.dbf")
tablePath = os.path.join(output_folder,tableName + '.dbf')
blocksPath = os.path.join(output_folder,'OCS_Blocks_' + tableName + '.shp')

# create table
arcpy.ExcelToTable_conversion(input_table, tablePath,"")

print('Table Created')

# Summarize table stats
#arcpy.Statistics_analysis(tablePath, SumTablePath, [["CO","SUM"],["CO2","SUM"],["N2O","SUM"],["NH3","SUM"],["NOX","SUM"],["Pb","SUM"],["PM10","SUM"],["PM25","SUM"],["SO2","SUM"],["VOC","SUM"],["CO2e","SUM"]], "AC_LAB")
arcpy.Statistics_analysis(tablePath, SumTablePath, ["EMISSIONS_VALUE","SUM"], ["AREA_BLOCK","POLLUTANT_CODE"])

print('Summary Stats calculated')

# Create copy of blocks shapefile
blocks = arcpy.MakeFeatureLayer_management(input_blocks, 'Blocks', "", "", "")

# Give AC_LAB field in blocks an index
arcpy.AddIndex_management(blocks,"AC_LAB", "", "", "")

print('New blocks shapefile created and indexed AC LAB')

# join table to blocks shapefile
arcpy.AddJoin_management(blocks, "AC_LAB", SumTablePath, "AC_LAB", "KEEP_ALL")

print('Table joined')

# save blocks
arcpy.CopyFeatures_management(blocks, blocksPath, "", "", "", "")

print('Complete!')