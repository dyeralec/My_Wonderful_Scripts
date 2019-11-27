""""""
""" This script will be used to combine all of the like-named feature classes for all of the states/regions within the
Environmental Sustainability Index for the Atlantic. A previous script (ESI_Processing_AD.py) was used to reformat
the feature classes and append additional attributes from a table to them. See that script for more detail. Before
running this script, the updated feature classes need to be grouped into a single geodatabase for each like-named
feature class from each region/state, as well as all of the geodatabases being located within a single folder (Parent
Folder). The script will run through each geodatabase and merge the feature classes together and create a final output
feature class within the geodatabase. """

# import modules
import arcpy
from arcpy import env
import csv
from os import path

# Set local variables
ParentFolder = r'R:\GEO Workspace\D_Users\81_Dyer\Environmental Sensitivity Index\ESI_Merge_Test'
env.workspace = ParentFolder

# create a list of all the geodatabases within the ParentFolder
geodatabases = arcpy.ListWorkspaces("*","FileGDB")

for workspace in geodatabases:
	
	# set the environment workspace to this workspace for the loop
	env.workspace = workspace
	
	# set the filename for naming the output file
	filename = str(workspace.rsplit("\\",1)[-1].replace('.gdb',''))
	
	# create a list of all the feature classes within the geodatabase
	features = arcpy.ListFeatureClasses()
	
	# set output feature class name
	output = format(workspace) + '\\' + format(filename) + '_merged'
	
	# use merge arcpy tool to combine all of the feature classes into one
	arcpy.Merge_management(features, output,"")