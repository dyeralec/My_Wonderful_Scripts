'''
ShpFile_Editor

Functions
    - Insert row
    - Update row

Function Inputs
    - shapefile (folder path and file)
    - Row index
    - RARNUM to base insert row on
    
    - Should I add in the essential geometeric information here?
    
    - Row data based on 'biofile'  
         
'''
import sys, os, arcpy, glob
from arcpy import env

def selectOut(input,extra_gdb,name,dissolve_field,RARNUM,index):
    
    where_clause = '"""' + format(dissolve_field) + ' = ' + format(RARNUM)
    #selectedFeature = format(selectFolder) + '\\' + format(name) + '_' + format(RARNUM) + '_' + format(index)
    
    extra_file = extra_gdb + '\\' + format(name) + '_' + format(RARNUM) + '_' + format(index)
    
    # select features within the feature class
    arcpy.Select_analysis(input,extra_file,where_clause)
    
    # append selected feature to the feature class
    arcpy.Append_management(extra_file,input,'TEST')

def mergeShps(inList,featureClass):
    outFolder_Edited = "C:/Users/romeolf/Desktop/MergeTest/"
    
    # Put this in a loop
    NewShapefile = format(outFolder_Edited) + format(featureClass) + ".shp"
    w = shapefile.Writer()
    for f in inList:
        r = shapefile.Reader(f)
        w._shapes.extend(r.shapes())
        w.records.extend(r.records())
    w.fields = list(r.fields)
    w.save(NewShapefile)
    
    # Merge together shapefiles previously stored in a loop