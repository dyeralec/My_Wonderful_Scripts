'''
ESI Data Processing

Latest version: 5/13/2015
'''
import sys, os, arcpy, csv, ShpFile_Editor_V2, shutil, glob, shapefile
from arcpy import env
from arcpy import GetCount_management
import glob #WORK FROM HERE!


BaseTable_name = "biofile"
dissolve_field = "RARNUM"
RARNUM_biofileIndex = 28

# define spatial reference as NAD 1983
sr = arcpy.SpatialReference(4269)

#List of feature classes related to 'biofile'
PotentialFCs_biofile = ["birds","fish","habitats","invertebrates","marineMammals","reptiles","terrestrial_mammals"] #birds_polygon is way to big, as is reptiles, so is habitats; m_mammal doesnt match

ParentFolder = r'P:\02_DataWorking\Atlantic\Environmental Sensitivity Index\Florida_Peninsula\'
ESI_GDB = r'\\Prod50-gis1\GAIA\01_DataOriginals\USA\Impacts\ESI_ByState\FloridaESI\FloridaPeninsula_1996_GDB\FloridaPeninsularESI.gdb\'
env.workspace = ESI_GDB

## Pull out 'biofile' table for joining values   
tables = arcpy.ListTables()
for table in tables:
    if (table == BaseTable_name):
        rows = arcpy.SearchCursor(table) 
        csvFile = csv.writer(open(format(ParentFolder) + "biofile.csv", 'wb'))
        fieldnames = [f.name for f in arcpy.ListFields(table)]
        
        allRows = []
        for row in rows:
            rowList = []
            for field in fieldnames:
                rowList.append(row.getValue(field))
            allRows.append(rowList)
        
        csvFile.writerow(fieldnames)
        for row in allRows:
            csvFile.writerow(row)

print "'biofile.csv' created here: " + format(ParentFolder)

# Create list of rows and rarenums from csv
filebiofile_CSV = open(format(ParentFolder) + "biofile.csv", 'r')
csv_fileInfo = format(ParentFolder) + "biofile.csv"
Lines = filebiofile_CSV.readlines()

biofile_RARNUM_list = []
biofileRow_list = []
l = 0
while (l < len(Lines)):
    line = Lines[l]
    element_noReturn = line.strip("\n")
    element = element_noReturn.split(",")
    try:
        RARNUM = element[RARNUM_biofileIndex]
        biofile_RARNUM_list.append(RARNUM)
        biofileRow_list.append(element_noReturn)
    except:
        print "List index is out of range"
    l += 1
        
'''
Create Feature dataset to put dissolved feature classes into; insert/update/delete rows based on biofile; ...
'''
# Create folder for 'biofile' relavent shapefile outputs
if not arcpy.Exists('DissolvedFeatures_' + BaseTable_name)
    arcpy.CreateFeatureDataset_management(ESI_GDB, 'DissolvedFeatures_' + BaseTable_name, sr)

# Run through user-defined list of feature classes to run throughenv.workspace = ESI_GDB
for featureClass in PotentialFCs_biofile: #run through each of the relavent feature classes
    
    #'''      Create shapefile from feature class     '''
    #Convert featureClass to shapefile
    #outFolder = format(ParentFolder) + format(BaseTable_name) + "\"
    #arcpy.FeatureClassToShapefile_conversion(featureClass,outFolder) #undo this comment-out block for future runs!!!
    #shapeFile = format(outFolder) + format(featureClass) + ".shp"
    #sr = arcpy.SpatialReference(format(shapeFile[0:-4]) + ".prj")
    
    #print "Created shapefile from " + format(featureClass)
    
    # set output folder
    outFolder = ESI_GDB + 'DissolvedFeatures_' + BaseTable_name

    ''' Dissolve feature class by RARNUM (or HUMNUM)'''
    FeatureClass = ESI_GDB + format(featureClass)
    dissolvedFeatureClass = format(outFolder) + format(featureClass) + "_dis"
    arcpy.Dissolve_management(shapeFile,dissolvedFeatureClass,dissolve_field,"","MULTI_PART","DISSOLVE_LINES")
    #FeatureClass = dissolvedFeatureClass
    
    print "Dissolved shapefile based on 'RARNUM'"

    '''     Create a list of ID, RARNUM, Shp_length, and Shp_area from shapefile     '''
    uniqueValues_ID = []
    uniqueValues_RARNUM = []
    uniqueValues_Shp_length = []
    uniqueValues_Shp_area = []
    
    with arcpy.da.SearchCursor(dissolvedFeatureClass, dissolve_field) as cursor:
        for row in cursor:
            RARNUM_value = row[0]
            if RARNUM_value not in uniqueValues_RARNUM
                uniqueValues_RARNUM.append(RARNUM_value)

    '''    Run through list of RARNUM values in biofile_csv list and shp list; if they match...    '''
    matchList = []
    biofileRow_matchList = []

    for RARNUM_featVal in uniqueValues_RARNUM:
        RARNUM_featVal_str = str(RARNUM_featVal)
        biofile_index = 0
        ObjID_List = []
        for RARNUM_csv in biofile_RARNUM_list:
            RARNUM_csv = biofile_RARNUM_list[biofile_index]
            EntireRow_wReturn = biofileRow_list[biofile_index]
            EntireRow = EntireRow_wReturn.strip("\n")
            EntireRow_split = EntireRow.split(",")
            ObjID = EntireRow_split[0]
            if (RARNUM_featVal_str == RARNUM_csv):
                    #print RARNUM_csv
                    #print RARNUM_shpVal_str
                    print EntireRow
                    ObjID_List.append(ObjID)
                    matchList.append(RARNUM_featVal)
                    biofileRow_matchList.append(format(EntireRow))
            biofile_index += 1

    print len(biofileRow_matchList)
    print "RARNUMs matched from shapefile and csv (in 'matchList'); associated rows from csv added to 'biofileRow_matchList'"
    
    ##Text checkpoint!
    test_txt = open(format(ParentFolder) + format(featureClass) + "_matchList.txt","w")
    header = Lines[0]
    test_txt.write(format(header))
    for item in biofileRow_matchList:
        test_txt.write(format(item) + "\n")
    test_txt.close()

    print "Created textfile of matching data: " + format(ParentFolder) + format(featureClass) + "_matchList.txt"
    
    '''    Open check point - use to add biofile fields and data   '''
    check_txt = open(format(ParentFolder) + format(featureClass) + "_matchList.txt","r")
    check_lines = check_txt.readlines()

    '''
    Add folder for selected out shapefiles
    '''
    # Create folder for selected out feature classes within geodatabase
    if not arcpy.Exists(format(ESI_GDB + format(BaseTable_name) + "\Selected\"):
        os.makedirs(format(ParentFolder) + format(BaseTable_name) + "\Selected\")

        
    print "Selecting out shapefiles based on matching 'RARNUM' values"    
    ''' Run through rows from biofile match csv and Select out whenever there is a new match! '''
    check_lines_index = 1 #Skip header
    while check_lines_index < len(check_lines):
        ctl = check_lines[check_lines_index] #ctl = acronym for check _text_line
        ctl_removeReturn = ctl.strip("\n")
        ctl_Element = ctl_removeReturn.split(",")
        ctl_Element_RARNUM = ctl_Element[RARNUM_biofileIndex]
        ctl_Element_RARNUM_INT = int(ctl_Element_RARNUM)
      
        '''  Call function to select out shapefile  '''
        selectFolder = format(ParentFolder) + format(BaseTable_name) + "/Selected/"
        #at_Edited = ShpFile_Editor_V2.selectOut(selectFolder,shapefile,ctl_Element_RARNUM_INT,check_lines_index)   # UNCOMMENT FOR RUNS  
        check_lines_index += 1    
    
    
    print "Creating a list of selected out shapefiles"
    SelectedShp_List = glob.glob(format(selectFolder) + "*.shp")
    print len(SelectedShp_List)
    
    print "Merging selected shapefiles --- defying the laws of topology"
    
    NewShapefile = ShpFile_Editor_V2.mergeShps(SelectedShp_List,featureClass)
    NewShapefile = format(outFolder) + format(featureClass) + "_e.shp"
    print "Merged shapefiles!"
    
    print "Deleting temporary selection folder"
    '''   Delete folder of selected shapefile to conserve disk space   '''
    shutil.rmtree(selectFolder)
    
    print "Adding data fields to merged shapefile"    
    '''Add Header Fields from Biofile to Shapefile'''
    header = check_lines[0]
    header_noReturn = header.strip("\n")
    biofile_fields = header_noReturn.split(",")
    fieldIndex = 0
    while fieldIndex < len(biofile_fields):
        field = biofile_fields[fieldIndex]
        if len(field) > 8:
            biofile_field = format(field[0:7]) + "_b"
        else:
            biofile_field = format(field) + "_b"   
        # Add 'biofile' fields to shapefile
        arcpy.AddField_management(NewShapefile, biofile_field, "TEXT", field_length = 50) #check the field 
        fieldIndex += 1
    
    
    ''' Create list of fields to be passed into function'''
    headerList = []
    header = Lines[0]
    Fields = header.split(",")
    for Field in Fields:
        headerList.append(Field)
    
    FOI_fullList = []
    for field_name in headerList:
        if len(field_name) > 8:
            if '\n' in field_name:
                field_name.strip('\n')   
            biofile_field_fixed = format(field_name[0:7]) + "_b"
        else:
            if '\n' in field_name:
                new_field_name = field_name.strip('\n')
                field_name = new_field_name
            biofile_field_fixed = format(field_name) + "_b"  
        FOI_fullList.append(biofile_field_fixed)
    print FOI_fullList
    
    print "Sorting out shapefile - RARNUM, ASCENDING"
    '''Sort Merged Shapefile (RARNUM Adcending)'''
    Shapefile_ready = format(outFolder) + format(featureClass) + "_wData.shp"
    arcpy.Sort_management(NewShapefile,Shapefile_ready,[["RARNUM","ASCENDING"]])
    
    print "Adding data to shapefile"
    ''' Run through rows from biofile match csv and UPDATE shapefile ''' # Edited to match RARNUM and ID and only do one row at a time
    with arcpy.da.UpdateCursor(Shapefile_ready, FOI_fullList) as cursor:
        rowMatch_index = 1
        try:
            for row in cursor:
                check_lines_index = rowMatch_index
                while check_lines_index < len(check_lines):
                    ctl = check_lines[check_lines_index] #ctl = acronym for check _text_line
                    ctl_removeReturn = ctl.strip("\n")
                    ctl_Element = ctl_removeReturn.split(",")
                    print "updating using: " + format(ctl_Element)
                    row_count = 0
                    element_index = 0
                    try:
                        while (element_index < (len(ctl_Element) - 1)):
                            element = ctl_Element[element_index]
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
            "Lucy rocks!"
            
    print "Completed processing: " + format(featureClass)