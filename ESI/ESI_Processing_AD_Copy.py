'''
ESI Data Processing

Latest version: 6/27/2019
'''
import sys, os, arcpy, csv, shutil, glob
from ShpFile_Editor_V2 import selectOut
from arcpy import env
from os import path
from arcpy import GetCount_management
import glob  # WORK FROM HERE!

BaseTable_name = "biofile"
dissolve_field = "RARNUM"
dissolveField_biofileIndex = 28
dissolveField_featureIndex = 2

# define spatial reference as NAD 1983
sr = arcpy.SpatialReference(4269)

# set overwrite to true
arcpy.env.overwriteOutput = True

# List of feature classes related to 'biofile'
PotentialFCs_biofile = ["reptiles","terrestrial_mammals"]
# "birds", "fish", "habitats", "invertebrates", "marineMammals", # TODO: Add back later

ParentFolder = r'P:\02_DataWorking\Atlantic\Environmental Sensitivity Index\FloridaPeninsula_1996_GDB\\'
ESI_GDB = r'P:\02_DataWorking\Atlantic\Environmental Sensitivity Index\FloridaPeninsula_1996_GDB\FloridaPeninsularESI.gdb'
env.workspace = ESI_GDB
new_features_gdb = format(ParentFolder) + format(BaseTable_name) + '_Updated.gdb'
extra_features_gdb = format(ParentFolder) + format(BaseTable_name) + '_ExtraFeatures.gdb'

## Pull out 'biofile' table for joining values
tables = arcpy.ListTables()
for table in tables:
    
    if path.exists(format(ParentFolder) + format(BaseTable_name) + '.csv'):
        
        break
        
    if (table == BaseTable_name):
        rows = arcpy.SearchCursor(table)
        csvFile = csv.writer(open(format(ParentFolder) + '\\' + format(BaseTable_name) + ".csv", 'wb'))
        fieldnames = [f.name for f in arcpy.ListFields(table)]

        allRows = []
        for row in rows:
            rowList = []
            for field in fieldnames:
                rowList.append(row.getValue(field))
            allRows.append(rowList)

        """sort the rows by dissolve filed, ascending"""
        allRows = sorted(allRows, key = lambda row: row[dissolveField_biofileIndex])

        # write table to CSV
        csvFile.writerow(fieldnames)
        for row in allRows:
            csvFile.writerow(row)

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

'''
Add folder for the extra features and the updated features
'''
# Create new geodatabase for selected out feature classes within the parent folder
if not arcpy.Exists(new_features_gdb):
    arcpy.CreateFileGDB_management(format(ParentFolder), format(BaseTable_name) + '_Updated.gdb')
    
# create folder for extra feature classes within the geodatabase
if not arcpy.Exists(extra_features_gdb):
    arcpy.CreateFileGDB_management(ParentFolder, format(BaseTable_name) + '_ExtraFeatures.gdb')

# Run through user-defined list of feature classes to run through env.workspace = ESI_GDB
for feature in PotentialFCs_biofile:  # run through each of the relevant feature classes
    
    # create NewFeatureClass copy that does not contain any features that have a RARNUM/HUNUM of zero
    arcpy.FeatureClassToFeatureClass_conversion(feature, extra_features_gdb, feature,'"' + format(dissolve_field) + '" <> 0')
    CopyFeatureClass = format(extra_features_gdb) + '\\' + format(feature)
    
    # Sort the CopyFeatureClass by RARNUM/HUNUM, creates a new output feature
    arcpy.Sort_management(CopyFeatureClass, new_features_gdb + '\\' + format(feature), [[dissolve_field, "ASCENDING"]])
    NewFeatureClass = new_features_gdb + '\\' + format(feature)
    
    # create list of RARNUM/HUNUM values in the new feature class
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
    with arcpy.da.SearchCursor(NewFeatureClass, "*") as cursorA:
        for row in cursorA:
            RARNUM_featVal_str = str(row[dissolveField_featureIndex])
            ObjID_featVal_str = str(row[0])
            #biofile_index = 0
            #ObjID_tableList = []
            # keep track of the number of RARNUM matches. If more than one, need to create more geometries to fit the number of matches.
            number_of_matches = 0
            # create new match lists
            matchList = []
            biofileRow_matchList = []
            
            biofile_index = 0
            
            # Loop through biofile as a cursor
            with arcpy.da.SearchCursor(format(BaseTable_name), "*") as cursorB:
                for record in cursorB:
                    RARNUM_table = str(row[dissolveField_biofileIndex])
                    EntireRow = row
                    #ObjID_table = EntireRow[0]
                    
                    # check if the RARNUM/HUNUM values match. If so, add to matched lists
                    if RARNUM_featVal_str == RARNUM_table:
                        # add 1 to number of matches tally
                        number_of_matches += 1
                        print EntireRow
                        #ObjID_tableList.append(ObjID_table)
                        matchList.append(RARNUM_featVal_str)
                        biofileRow_matchList.append(EntireRow)
                    biofile_index += 1
                    
            """With the number of known matches now, the script can create a new feature class from the current row
            of the cursorA loop, create extra features if needed, add new headers, and then append rows to a new or
            existing output file"""
            
            # select current feature in cursor A based on ObjectID and create a new feature in the extra features GDB
            arcpy.FeatureClassToFeatureClass_conversion(NewFeatureClass, extra_features_gdb, feature + format(RARNUM_featVal_str),\
                                                        '"OBJECTID*" = ' + format(ObjID_featVal_str))
            # create a variable for this new feature class.. call it Temporary Feature Class
            TempFeatureClass = extra_features_gdb + '\\' + feature + format(RARNUM_featVal_str)
            
            # with the number of known matches, the geometry in the temprorary feature needs to be copied a certain number
            # of times so that there are an equal number of matches and geometries.
            if number_of_matches > 1:
    
                where_clause = '"' + format(dissolve_field) + '" = ' + format(RARNUM_featVal_str)
                extra_file = format(extra_features_gdb) + '\\' + format(feature) + '_' + format(
                    RARNUM_featVal_str)
    
                # select features within the temporary feature class to make an extra file
                arcpy.Select_analysis(feature, extra_file, where_clause)
    
                # create a loop that will append the new geometry to the temporary feature class a certain amount of times
                for i in range(1, number_of_matches):
                    
                    # append the extra file to the copy feature class
                    arcpy.Append_management(extra_file, TempFeatureClass, 'TEST')
                
            # Add headers to the Temporary Feature Class
            for field in FOI_fullList:
                arcpy.AddField_management(TempFeatureClass, field, "TEXT", field_length=50)
                
            # update the Temporary Feature Class with the biofileRow_matchedList
            with arcpy.da.UpdateCursor(TempFeatureClass, FOI_fullList) as cursorC:
                rowMatch_index = 0
                try:
                    for row in cursorC:
                        
                        while rowMatch_index < len(biofileRow_matchList):
                            ctl = biofileRow_matchList[rowMatch_index]  # ctl = acronym for check _text_line
                            print "updating using: " + format(ctl)
                            row_count = 0
                            element_index = 0
                            try:
                                while (element_index < (len(ctl) - 1)):
                                    element = ctl[element_index]
                                    row[row_count] = str(element)
                                    row_count += 1
                                    element_index += 1
                                cursorC.updateRow(row)
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
            
        
        
    
    
    
    
    
    
    
    
    
    """
    # create NewFeatureClass copy that does not contain any features that have a RARNUM/HUNUM of zero
    arcpy.FeatureClassToFeatureClass_conversion(feature, extra_features_gdb, feature, '"' + format(dissolve_field) + '" <> 0')
    CopyFeatureClass = format(extra_features_gdb) + '\\' + format(feature)
    
    # create another NewFeatureClass copy to append to
    #arcpy.FeatureClassToFeatureClass_conversion(feature, extra_features_gdb, feature + '_toAppend')
    #FeatureClassToAppend = format(extra_features_gdb) + '\\' + format(feature) + '_ToAppend'

    '''     Create a list of ID, RARNUM, Shp_length, and Shp_area from featureClass     '''
    uniqueValues_ID = []
    uniqueValues_RARNUM = []
    uniqueValues_Shp_length = []
    uniqueValues_Shp_area = []

    with arcpy.da.SearchCursor(CopyFeatureClass, dissolve_field) as cursor:
        for row in cursor:
            RARNUM_value = row[0]
            uniqueValues_RARNUM.append(int(RARNUM_value))

    # sort uniqueValues_RARNUM list from low to high
    uniqueValues_RARNUM = sorted(uniqueValues_RARNUM)

    '''    Run through list of RARNUM values in biofile_csv list and shp list; if they match add to a matched RARNUM and biofile row list.   '''
    matchList = []
    biofileRow_matchList = []
    
    # Need to keep track of which RARNUMs have already been completed. So, make a list
    completed_RARNUMs = []
    for RARNUM_featVal in uniqueValues_RARNUM:
        
        RARNUM_featVal_str = str(RARNUM_featVal)
        
        if RARNUM_featVal_str == '43':
            
            print('Found 43')

        biofile_index = 0
        ObjID_List = []
        # keep track of the number of RARNUM matches. If more than one, need to create more geometries to fit the number of matches.
        number_of_matches = 0
        for RARNUM_csv in biofile_RARNUM_list:
            RARNUM_csv = biofile_RARNUM_list[biofile_index]
            EntireRow = biofileRow_list[biofile_index]
            ObjID = EntireRow[0]
            if (RARNUM_featVal_str == RARNUM_csv):
                # add 1 to number of matches tally
                number_of_matches += 1
                print EntireRow
                ObjID_List.append(ObjID)
                matchList.append(RARNUM_featVal_str)
                biofileRow_matchList.append(EntireRow)
            biofile_index += 1

        # check if this RARNUM has already  been completed
        if RARNUM_featVal_str in completed_RARNUMs:
            # move onto next loop
            continue
        
        # append RARNUM to completed list
        completed_RARNUMs.append(RARNUM_featVal_str)
            
        # if the number of matches is greater than 1, add more geometries to match the number of matches
        if number_of_matches > 1:
            
            match_index = 1
            
            # create a list that the extra_file variable will be put into. Once it is filled, loop through and append the extra files to the feature class
            extra_features_list = []
            
            # create a loop for the correct amount of new features needed
            for i in range(1,number_of_matches):
    
                where_clause = '"' + format(dissolve_field) + '" = ' + format(RARNUM_featVal)
                extra_file = format(extra_features_gdb) + '\\' + format(feature) + '_' + format(
                    RARNUM_featVal) + '_' + format(match_index)
    
                # select features within the feature class
                arcpy.Select_analysis(feature, extra_file, where_clause)
    
                # append the extra file to the extra file list
                extra_features_list.append(extra_file)
    
                match_index += 1

            # append selected feature to the feature class. Try to merge all at once, if it fails, append one by one in a loop
            try:
                arcpy.Append_management(extra_features_list, CopyFeatureClass, 'TEST')
                
            except:
                
                for extra in extra_features_list:
                    
                    arcpy.Append_management(extra, CopyFeatureClass, 'TEST')

    # create a copy of the feature class in the new features data set folder with the dissolve field sorted ascending
    print "Sorting out feature - RARNUM, ASCENDING"
    '''Sort Feature Class (RARNUM Adcending)'''
    arcpy.Sort_management(CopyFeatureClass, new_features_gdb + '\\' + format(feature), [[dissolve_field, "ASCENDING"]])

    # set NewFeatureClass variable
    NewFeatureClassUpdated = format(new_features_gdb) + '\\' + format(feature)

    print len(biofileRow_matchList)
    print "RARNUMs matched from feature and csv (in 'matchList'); associated rows from csv added to " + format(BaseTable_name) + "'Row_matchList'"

    ##Text checkpoint! Create a text file of the rows that were matched by RARNUM
    with open(format(ParentFolder) + format(feature) + "_matchList.csv", "wb") as match_input:
        writer = csv.writer(match_input)
        header = Lines[0]
        writer.writerow(header)
        for item in biofileRow_matchList:
            writer.writerow(item)

    print "Created csv file of matching data: " + format(ParentFolder) + format(feature) + "_matchList.csv"

    '''    Open check point - use to add biofile fields and data   '''
    with open(format(ParentFolder) + format(feature) + "_matchList.csv", "rb") as match_input:
        reader = csv.reader(match_input)
        check_lines = []
        for row in reader:
            check_lines.append(row)

    print "Adding data fields to Feature Class"
    '''Add Header Fields from Biofile to Feature Class'''
    header = check_lines[0]
    # create list of the full headers that are appended into the new updated feature class
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
        # Add 'biofile' fields to feature
        arcpy.AddField_management(NewFeatureClassUpdated, biofile_field, "TEXT", field_length=50)  # check the field
        fieldIndex += 1

    print FOI_fullList

    print "Adding data to feature class"
    ''' Run through rows from biofile match csv and UPDATE feature '''
    
    # update feature class with row information
    # This only works if the matched rows to be appended are in the correct order
    with arcpy.da.UpdateCursor(NewFeatureClassUpdated, FOI_fullList) as cursor:
        rowMatch_index = 1
        try:
            for row in cursor:
                check_lines_index = rowMatch_index
                while check_lines_index < len(check_lines):
                    ctl = check_lines[check_lines_index]  # ctl = acronym for check _text_line
                    print "updating using: " + format(ctl)
                    row_count = 0
                    element_index = 0
                    try:
                        while (element_index < (len(ctl) - 1)):
                            element = ctl[element_index]
                            row[row_count] = str(element)
                            row_count += 1
                            element_index += 1
                        cursor.updateRow(row)
                    except:
                        index = "out of range"
                    check_lines_index += 1
                    rowMatch_index += 1
                    break
        except:
            "Alec rocks!"

    print "Completed processing: " + format(NewFeatureClassUpdated)
    
    """