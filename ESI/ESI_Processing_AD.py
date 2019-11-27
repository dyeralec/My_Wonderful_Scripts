'''
ESI Data Processing

Latest version: 6/27/2019
'''

"""This script can be used to process the BIOFILE from the Environmental Sensitivity Index. The script will take
records in the biofile and append attribute information to the correct feature if the dissolve value (RARNUM in
this case) is matched. The script will also create copies of features if needed since there will be instances where
there are separate records in the 'soc_dat' file and multiple features with the same RARNUM.

The user will need to set variables before running the code. This includes the dissolve field (RARNUM) index for the
biofile, the dissolve field (RARNUM) feature index,and the ParentFolder (the geodatabase containing
the ESI data is within), and the ESI Geodatabase (GDB) itself.

IMPORTANT!!! The user will also have to look at each feature class and determine which column index needs to be used for indexing
the RARNUM value. If it is a different index than identified in the dissolveField_featureIndex variable, then it will
need to be changed within the for loop. This occurs around line 106. """

import sys, os, arcpy, csv, shutil, glob
from ShpFile_Editor_V2 import selectOut
from arcpy import env
from os import path
from arcpy import GetCount_management
import glob  # WORK FROM HERE!

BaseTable_name = "biofile"
dissolve_field = "RARNUM"
dissolveField_biofileIndex = 1
dissolveField_featureIndex = 4

# define spatial reference as NAD 1983
sr = arcpy.SpatialReference(4269)

# set overwrite to true
arcpy.env.overwriteOutput = True

# List of feature classes related to 'biofile'
PotentialFCs_biofile = ['benthic_polygon',"BENTHIC","BIRDS","BIRDSPT",'birds_polygon',"FISH","FISHL",'fish_polygon','fishl_arc',"HABITATS",'habitats_polygon',"HERP",\
                        "INVERT",'invert_polygon',"INVERTPT","M_MAMMALS",'m_mammal_polygon','nests_point','reptiles_polygon','REPTILES',"T_MAMMALS",'t_mammal_polygon']

ParentFolder = r'P:\02_DataWorking\Atlantic\Environmental Sensitivity Index\FloridaPeninsula_1996_GDB\\'
ESI_GDB = r'P:\02_DataWorking\Atlantic\Environmental Sensitivity Index\FloridaPeninsula_1996_GDB\FloridaPeninsularESI.gdb'
env.workspace = ESI_GDB
new_features_gdb = format(ParentFolder) + format(BaseTable_name) + '_Updated.gdb'
extra_features_gdb = format(ParentFolder) + format(BaseTable_name) + '_ExtraFeatures.gdb'

'''
Add folder for the extra features and the updated features
'''
# Create new geodatabase for selected out feature classes within the parent folder
if not arcpy.Exists(new_features_gdb):
    arcpy.CreateFileGDB_management(format(ParentFolder), format(BaseTable_name) + '_Updated.gdb')

# create folder for extra feature classes within the geodatabase
if not arcpy.Exists(extra_features_gdb):
    arcpy.CreateFileGDB_management(ParentFolder, format(BaseTable_name) + '_ExtraFeatures.gdb')

## Pull out base table for joining values
tables = arcpy.ListTables()
for table in tables:
    
    if table == BaseTable_name:
    
        if path.exists(format(ParentFolder) + '\\' + format(BaseTable_name) + '.csv'):
            
            break
        
        else:
            
            # sort the table based on RARNUM, ascending
            arcpy.Sort_management(table, extra_features_gdb + '\\' + table + '_sorted', [[dissolve_field, "ASCENDING"]])
            arcpy.TableToTable_conversion(extra_features_gdb + '\\' + table + '_sorted', ParentFolder, BaseTable_name + '.csv')

print format(BaseTable_name) + "'.csv' created here: " + format(ParentFolder)

# Create list of rows and rarenums from csv
with open(format(ParentFolder) + '\\' + format(BaseTable_name) + ".csv", 'rb') as file:
    reader = csv.reader(file)
    Lines = []
    for row in reader:
        Lines.append(row)
  
csv_fileInfo = format(ParentFolder) + '\\' + format(BaseTable_name) + ".csv"

print(Lines[0])

# create a list of all the RARNUM values in the biofile as well as a list of all the rows in the biofile
biofile_RARNUM_list = []
biofileRow_list = []
l = 0
while (l < len(Lines)):
    line = Lines[l]
    
    try:
        RARNUM = line[dissolveField_biofileIndex]
        biofile_RARNUM_list.append(RARNUM)
        biofileRow_list.append(line)
    except:
        print "List index is out of range"
    l += 1

# Run through user-defined list of feature classes to run through env.workspace = ESI_GDB
for feature in PotentialFCs_biofile:  # run through each of the relevant feature classes
    
    # check if the feature exists. if not, continue to next feature
    if arcpy.Exists(feature):
        
        print(feature + ' exists. Commence updating process in \n5\n4\n3\n2\n1\nLAUNCH.')
    
    else:
        continue
    """
    
    IMPORTANT!!!!!!!!!
    
    The RARNUM field may be in a different column so the index number needs to change. Look at all of the features
    and change the index here if needed. Else, the index value set at the beginning of the script will be used.
    
    format:
    if feature == 'insert feature name here':
    
        dissolveField_featureIndex = index #
    """
    
    if feature == 'INVERT':
        
        dissolveField_featureIndex = 3

    # check if the BIOLOGY data set exists
    if arcpy.Exists('BIOLOGY'):

        env.workspace = format(ESI_GDB) + 'BIOLOGY'

    else:

        print('No workspace change needed.')
    
    # create NewFeatureClass copy that does not contain any features that have a RARNUM of zero
    arcpy.FeatureClassToFeatureClass_conversion(feature, extra_features_gdb, feature + '_copy',
                                                '"' + format(dissolve_field) + '" <> 0')
    CopyFeatureClass = format(extra_features_gdb) + '\\' + format(feature) + '_copy'

    # dissolve the CopyFeatureClass based on the RARNUM value
    arcpy.Dissolve_management(CopyFeatureClass, format(extra_features_gdb) + '\\' + format(feature) + "_dissolved",
                              "RARNUM", [["Shape_Length", "SUM"], ["Shape_Area", "SUM"]], "MULTI_PART", "UNSPLIT_LINES")
    DissolvedFeatureClass = format(extra_features_gdb) + '\\' + format(feature) + '_dissolved'
    
    # Sort the CopyFeatureClass by RARNUM, creates a new output feature
    arcpy.Sort_management(DissolvedFeatureClass, extra_features_gdb + '\\' + format(feature) + '_sorted', [[dissolve_field, "ASCENDING"]])
    NewFeatureClass = extra_features_gdb + '\\' + format(feature) + '_sorted'
    
    # create list of RARNUM values in the new feature class
    uniqueValues_RARNUM = []
    with arcpy.da.SearchCursor(NewFeatureClass, dissolve_field) as cursor:
        for row in cursor:
            RARNUM_value = row[0]
            uniqueValues_RARNUM.append(int(RARNUM_value))
    
    # sort uniqueValues_RARNUM list from low to high
    uniqueValues_RARNUM = sorted(uniqueValues_RARNUM)
    
    # create list of the full headers that are appended into the new updated feature class
    header = Lines[0]
    FOI_fullList = []
    fieldIndex = 0
    while fieldIndex < len(header):
        field = header[fieldIndex]
        if len(field) > 8:
            biofile_field = format(field[0:7]) + "_b"
        else:
            biofile_field = format(field) + "_b"
        # append biofile_field to FOI full list
        FOI_fullList.append(biofile_field)
        
        fieldIndex += 1
    
    '''    Run through list of RARNUM values in biofile_csv list and shp list; if they match add to a matched RARNUM and biofile row list.   '''
    
    # loop through each row in the new feature class as a cursor
    with arcpy.da.SearchCursor(NewFeatureClass,"*") as cursorA:
        for row in cursorA:
            RARNUM_featVal_str = str(int(row[dissolveField_featureIndex]))
            ObjID_featVal_str = str(int(row[0]))
            # biofile_index = 0
            # ObjID_tableList = []
            # keep track of the number of RARNUM matches. If more than one, need to create more geometries to fit the number of matches.
            number_of_matches = 0
            # create new match lists
            matchList = []
            biofileRow_matchList = []
            
            biofile_index = 0
            
            # Loop through biofile list
            for record in Lines:
                RARNUM_table = str(record[dissolveField_biofileIndex])
                
                # check if the RARNUM values match. If so, add to matched lists
                if RARNUM_featVal_str == RARNUM_table:
                    # add 1 to number of matches tally
                    number_of_matches += 1
                    print record
                    # ObjID_tableList.append(ObjID_table)
                    matchList.append(RARNUM_featVal_str)
                    biofileRow_matchList.append(record)
                biofile_index += 1
            
            """With the number of known matches now, the script can create a new feature class from the current row
            of the cursorA loop, create extra features if needed, add new headers, and then append rows to a new or
            existing output file"""
            
            # select current feature in cursor A based on ObjectID and create a new feature in the extra features GDB
            arcpy.FeatureClassToFeatureClass_conversion(NewFeatureClass, extra_features_gdb,
                                                        feature + '_' + format(RARNUM_featVal_str), \
                                                        '"OBJECTID*" = ' + format(ObjID_featVal_str))
            # create a variable for this new feature class.. call it Temporary Feature Class
            TempFeatureClass = extra_features_gdb + '\\' + feature + '_' + format(RARNUM_featVal_str)
            
            # with the number of known matches, the geometry in the temprorary feature needs to be copied a certain number
            # of times so that there are an equal number of matches and geometries.
            if number_of_matches > 1:
                
                where_clause = '"' + format(dissolve_field) + '" = ' + format(RARNUM_featVal_str)
                extra_file = format(extra_features_gdb) + '\\' + format(feature) + '_' + format(
                    RARNUM_featVal_str + '_extra')
                
                # select features within the temporary feature class to make an extra file
                arcpy.Select_analysis(TempFeatureClass, extra_file, where_clause)
                
                # create a loop that will append the new geometry to the temporary feature class a certain amount of times
                for i in range(1, number_of_matches):
                    # append the extra file to the copy feature class
                    arcpy.Append_management(extra_file, TempFeatureClass, 'TEST')
            
            # Add headers to the Temporary Feature Class
            for field in FOI_fullList:
                arcpy.AddField_management(TempFeatureClass, field, "TEXT", field_length=50)
            
            # update the Temporary Feature Class with the biofileRow_matchedList
            with arcpy.da.UpdateCursor(TempFeatureClass, FOI_fullList) as cursorB:
                rowMatch_index = 0
                try:
                    for object in cursorB:
                        
                        while rowMatch_index < len(biofileRow_matchList):
                            ctl = biofileRow_matchList[rowMatch_index]  # ctl = acronym for check _text_line
                            print "updating using: " + format(ctl)
                            row_count = 0
                            element_index = 0
                            try:
                                while (element_index < (len(ctl))):
                                    element = ctl[element_index]
                                    object[row_count] = str(element)
                                    row_count += 1
                                    element_index += 1
                                cursorB.updateRow(object)
                            except:
                                index = "out of range"
                            rowMatch_index += 1
                            break
                except:
                    print('Done updating feature with table info.')
            
            """Now, the temporary feature can be either appended to the file output feature, or used
            to create a new feature if it does not already exist."""
            
            # create a variable for the final output
            FinalFeatureClass = new_features_gdb + '\\' + feature
            
            # check if final feature already exists
            if arcpy.Exists(FinalFeatureClass):
                
                # if so, append temporary feature to it
                arcpy.Append_management(TempFeatureClass, FinalFeatureClass, 'TEST')
            
            else:
                
                # if not, create a new final feature using the temporary feature
                arcpy.FeatureClassToFeatureClass_conversion(TempFeatureClass, new_features_gdb, feature)
            
    print(format(feature) + 'Completed!')