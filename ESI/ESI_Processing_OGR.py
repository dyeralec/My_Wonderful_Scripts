"""
ESI Data Processing

Written by: Alec Dyer

Latest version: 8/2/2019

IMPORTANT!!! PLEASE READ!!!

This script can be used to process Environmental Sensitivity Index data sets in a way that dissolves feautures so that
there are a smaller number of features, and also appends species attributes to those features to give more context.
The script will take records in the biofile and append attribute information to the correct feature
if the dissolve value is matched (RARNUM for species in this case). The script will also create
copies of features if needed since there will be instances where there are separate records in the base table file and
multiple features with the same RARNUM value in the feature classes.

This code is set up to only complete one region at a time. However, it could be changed to run through many regions
in one go if needed by adding a loop through certain directories.

The user will need to set these variables before running the code:
    - BaseTable_name: The name of the base table (usually 'biofile' or 'BIOFILE'. Capitalization matters!!!)
    - dissolve_field: name of the field that the feature will be dissolved by. Should be 'RARNUM' or 'HUNUM'. Capitalization matters!
    - PotentialFCs_biofile: The script uses a list called 'PotentialFCs_biofile' to loop through all of the possible features for processing the biology data.
        The user should confirm that all of the names of the biology features in the database are in this list. Capitalization
        does NOT matter here.
    - ParentFolder: path to the folder where the regional geodatabase is located
    - ESI_GDB: path to the regional database, should be in the ParentFolder

Additionally, if the user is going to process the social/economics data, then this list will need
to be completely changed along with the base table name, dissolve field name, dissolve field index, and feature lists.

It is possible that this script will run into memory issues, but Alec did his best to work around this with what he knows.

Important implications of this script:

    - The script takes advantage of the fact that all the ESI data has the field names 'Shape_Length' and 'Shape_Area' for
    the features, depending on if its a point, line or polygon feature class. If these field names are changed, the script
    will not work. It is also set up to deal with 'SHAPE_Length' and 'SHAPE_Area' spellings, since capitalization matters.
    Look at the data before running to confirm that either of theses names are correct.
    
    - The script tries to dissolve with the OGR function first, then if it fails will split the shapefile into two separate
    shapefiles because it failed due to a too large of a file size. The names of these two shapefiles will be added to a list
    and dealt with like the other shapefiles at the end of the script. There may still be unknown issues with this process,
    making the script fail.
    
"""

import os, csv
from osgeo import ogr
import gc


"""Functions!"""

def ExtractFeaturesInGDB_ByAttribute_ToMemory(inGDB,inFileName,filterQuery,outLayerName):
    """
    This function will extract features from a feature class based on a SQL filter query and save the layer to
    memory. It will carry over any attributes in the input feature class.
    
    This function will only work with feature classes!!! The feature has to be in a geodatabase, and the driver
    MUST be 'FileGDB'. This function can be changed to use shapefiles by adjusting how the input is opened.
    
    Requirement: 'FileGDB' driver for ogr
    
    Args:
        inGDB: input geodatabase (must end with .gdb)
        inFileName: the name of the input feature class
        filterQuery: SQL query that is in the format of 'column = string' ... string must be quoted and number should NOT be quoted
        outLayerName: the name of the output feature class

    Returns: output memory data source and memory layer
    """
    # open the inShapefile as the driver type
    inDriver = ogr.GetDriverByName('FileGDB')
    inDataSource = inDriver.Open(inGDB, 0)
    inLayer = inDataSource.GetLayer(inFileName)
    
    # query out the wanted fields
    inLayer.SetAttributeFilter(filterQuery)
    
    # create the output driver
    outDriver = ogr.GetDriverByName('MEMORY')
    
    print('Out driver set as ' + format(outDriver.GetName()))
        
    # create output shape file
    outDataSource = outDriver.CreateDataSource('memData_' + format(outLayerName))
    outMemory = outDataSource.CreateLayer(outLayerName, inLayer.GetSpatialRef(), inLayer.GetGeomType())

    # Add input Layer Fields to the output Layer
    outMemory.CreateFields(inLayer.schema)

    # Get the output Layer's Feature Definition
    outLayerDefn = outMemory.GetLayerDefn()
    
    # Delete ID field from layer defn

    # Add features to the output Layer
    for inFeature in inLayer:
        
        # Create output Feature
        outFeature = ogr.Feature(outLayerDefn)

        # Set geometry as centroid
        geom = inFeature.GetGeometryRef()
        outFeature.SetGeometry(geom)
    
        # Add field values from input Layer
        for i in range(0, outLayerDefn.GetFieldCount()):
            outFeature.SetField(i,inFeature.GetField(i))

        # Add new feature to output Layer
        outMemory.CreateFeature(outFeature)
    
    # Save and close DataSources
    del inFeature
    del inLayer
    del inDataSource
    del inDriver
    return outDataSource,outMemory

def ExtractFeaturesInMemory_ByAttribute_ToMemory(inDataSource,inMemory, filterQuery, outLayerName):
    """
    This function will extract features from an ogr memory data source based on a SQL filter query and save the layer to
    memory. It will carry over any attributes in the input feature. Both the data source and the memory and needed as
    inputs because the memory layer will not be able to be accessed without the data source.

    This function will only work with memory, and the driver MUST be 'Memory'.
    
    This function does NOT delete the input data source and layer.
    
    Requirement: 'FileGDB' driver for ogr

    Args:
        inDataSource: input data source
        inMemory: input memory
        filterQuery: SQL query that is in the format of 'column = string' ... string must be quoted and number should NOT be quoted
        outLayerName: the name of the output

    Returns: input and output memory data source and memory layer
    """
    
    # query out the wanted fields
    inMemory.SetAttributeFilter(filterQuery)
    
    # create the output driver
    outDriver = ogr.GetDriverByName('MEMORY')
    
    print('Out driver set as ' + format(outDriver.GetName()))
    
    # create output shape file
    outDataSource = outDriver.CreateDataSource('memData_' + format(outLayerName))
    outMemory = outDataSource.CreateLayer(outLayerName, inMemory.GetSpatialRef(), inMemory.GetGeomType())
    
    # Add input Layer Fields to the output Layer
    outMemory.CreateFields(inMemory.schema)
    
    # Get the output Layer's Feature Definition
    outLayerDefn = outMemory.GetLayerDefn()
    
    # Add features to the output Layer
    for inFeature in inMemory:
        
        # Create output Feature
        outFeature = ogr.Feature(outLayerDefn)

        # Set geometry as centroid
        geom = inFeature.GetGeometryRef()
        outFeature.SetGeometry(geom)
        
        # Add field values from input Layer
        for i in range(0, outLayerDefn.GetFieldCount()):
            outFeature.SetField(i,inFeature.GetField(i))
        
        # Add new feature to output Layer
        outMemory.CreateFeature(outFeature)
    
    inMemory.ResetReading()
    del inFeature
    
    # return DataSources and layers
    return inDataSource,inMemory,outDataSource,outMemory

def ExtractFeaturesinMemory_ByAttribute_ToShapefile(inDataSource,inLayer, filterQuery, outShapefileName, shapefileFolder):
    """
        This function will extract features from an ogr memory data source based on a SQL filter query and save the layer to
        memory. It will carry over any attributes in the input feature. Both the data source and the memory and needed as
        inputs because the memory layer will not be able to be accessed without the data source.

        This function does NOT delete the input data source and layer.

        Args:
            inDataSource: input data source
            inLayer: input layer
            filterQuery: SQL query that is in the format of 'column = string' ... string must be quoted and number should NOT be quoted
            outShapefileName: the name of the output
            shapefileFolder: path the the folder that will contain the output shapefile

        Returns: input memory data source and memory layer
        """
    
    # query out the wanted fields
    inLayer.SetAttributeFilter(filterQuery)
    
    # create the output driver
    outDriver = ogr.GetDriverByName('ESRI Shapefile')

    # remove output shape file if it already exists
    if os.path.exists(shapefileFolder + '\\' + outShapefileName + '.shp'):
        outDriver.DeleteDataSource(shapefileFolder + '\\' + outShapefileName + '.shp')
    
    # create output shape file
    outDataSource = outDriver.CreateDataSource(shapefileFolder + '\\' + outShapefileName + '.shp')
    outLayer = outDataSource.CreateLayer(outShapefileName + '.shp', inLayer.GetSpatialRef(), inLayer.GetGeomType())
    
    # Add input Layer Fields to the output Layer
    outLayer.CreateFields(inLayer.schema)
    
    # Get the output Layer's Feature Definition
    outLayerDefn = outLayer.GetLayerDefn()
    
    # Add features to the output Layer
    for input_feat in inLayer:
        
        # Create output Feature
        outFeature = ogr.Feature(outLayerDefn)
        
        # Set geometry as centroid
        geom = input_feat.GetGeometryRef()
        outFeature.SetGeometry(geom)
        
        # Add field values from input Layer
        for i in range(0, outLayerDefn.GetFieldCount()):
            outFeature.SetField(i, input_feat.GetField(i))
        
        # Add new feature to output Layer
        outLayer.CreateFeature(outFeature)
    
    inLayer.ResetReading()
    
    del input_feat
    del outLayer
    del outDataSource
    del outDriver
    
    # return DataSources and layers
    return inDataSource, inLayer

def ExtractFeaturesInShapefile_ByAttribute_ToShapefile(shapefileFolder,inFileName,outFileName,filterQuery):
    """
    This function can be used to query out features from a shapefile based on a field name and value, and then
    create a new shapefile in the same folder of these queried features.
    
    Args:
        shapefileFolder: path to the folder where the input shapefile is located
        inFileName: name of the input shapefile
        outFileName: name of the output shapefile
        filterQuery: query statement with string format --> "'field name' = 'field value'"

    """
    
    # open in shapefile
    inDriver = ogr.GetDriverByName('ESRI Shapefile')
    inDataSource = inDriver.Open(shapefileFolder + '\\' + inFileName + '.shp',0)
    inLayer = inDataSource.GetLayer()
    
    # query out the wanted fields
    inLayer.SetAttributeFilter(filterQuery)
    
    # create the output driver
    outDriver = ogr.GetDriverByName('ESRI Shapefile')
    
    # remove output shape file if it already exists
    if os.path.exists(shapefileFolder + '\\' + outFileName + '.shp'):
        outDriver.DeleteDataSource(shapefileFolder + '\\' + outFileName + '.shp')
    
    # create output shape file
    outDataSource = outDriver.CreateDataSource(shapefileFolder + '\\' + outFileName + '.shp')
    outLayer = outDataSource.CreateLayer(outFileName + '.shp', inLayer.GetSpatialRef(), inLayer.GetGeomType())
    
    # Add input Layer Fields to the output Layer
    outLayer.CreateFields(inLayer.schema)
    
    # Get the output Layer's Feature Definition
    outLayerDefn = outLayer.GetLayerDefn()
    
    # Add features to the output Layer
    for input_feat in inLayer:
        
        # Create output Feature
        outFeature = ogr.Feature(outLayerDefn)
        
        # Set geometry as centroid
        geom = input_feat.GetGeometryRef()
        outFeature.SetGeometry(geom)
        
        # Add field values from input Layer
        for i in range(0, outLayerDefn.GetFieldCount()):
            outFeature.SetField(i, input_feat.GetField(i))
        
        # Add new feature to output Layer
        outLayer.CreateFeature(outFeature)
    
    del input_feat
    del outFeature
    del inLayer
    del inDataSource
    del inDriver
    del outLayer
    del outDataSource
    del outDriver

def FeatureToFeature(inGDB, outGDB, inFileName, outFileName):
    """
    This tool will take a feature that is within a database and create an exact copy of it to another
    geodatabase. The geodatabases could be the same one.
    
    Requirement: 'FileGDB' driver for ogr
    
    Args:
        inGDB: path to the geodatabase where the input feature class is located (must end with .gdb)
        outGDB: path to the geodatabase where the output feature class is to be placed (must end with .gdb)
        inFileName: name of the input feature class
        outFileName: name of the output feature class

    Returns: N/A

    """
    # open the inShapefile as the driver type
    inDriver = ogr.GetDriverByName('FileGDB')
    inDataSource = inDriver.Open(inGDB, 0)
    inLayer = inDataSource.GetLayer(inFileName)
    
    # grab the spatial reference system
    srs = inLayer.GetSpatialRef()
    
    # create the output driver
    outDriver = ogr.GetDriverByName('FileGDB')
    
    print('Out driver set as ' + format(outDriver.GetName()))
    
    # remove output shape file if it already exists
    if os.path.exists(outGDB + '\\' + outFileName):
        outDriver.DeleteDataSource(outGDB + '\\' + outFileName)
    
    # create output shape file
    outDataSource = outDriver.Open(outGDB, 1)
    outFile = outDataSource.CreateLayer(outFileName, srs, geom_type=inLayer.GetGeomType())
    
    # Add input Layer Fields to the output Layer
    outFile.CreateFields(inLayer.schema)
    
    # Get the output Layer's Feature Definition
    outLayerDefn = outFile.GetLayerDefn()
    
    # Add features to the output Layer
    for inFeature in inLayer:
        # Create output Feature
        outFeature = ogr.Feature(outLayerDefn)

        # Set geometry as centroid
        geom = inFeature.GetGeometryRef()
        outFeature.SetGeometry(geom)
        
        # Add field values from input Layer
        for i in range(0, outLayerDefn.GetFieldCount()):
            outFeature.SetField(i,inFeature.GetField(i))
        
        # Add new feature to output Layer
        outFile.CreateFeature(outFeature)
    
    inLayer.ResetReading()
    
    # Save and close DataSources
    del inDataSource
    del outDataSource
    
def FeatureToShapefile_withQuery(inGDB,shapefileFolder,outFileName,query):
    """
    Use this function to query out features from a feature class based on a field name and value, and then
    create a new shapefile containing these queried features.
    
    Requirement: 'FileGDB' driver for ogr
    
    Args:
        inGDB: path to the input feature class, including feature name
        shapefileFolder: folder where the output shapfile will be saved to
        fileName: name of the output shapefile
        query: query statement with string format --> "'field name' = 'field value'"

    Returns: N/A

    """
    # open the inShapefile as the driver type
    inDriver = ogr.GetDriverByName('FileGDB')
    inDataSource = inDriver.Open(inGDB, 0)
    inLayer = inDataSource.GetLayer(outFileName)
    
    # query results
    inLayer.SetAttributeFilter(query)

    # create the output driver
    outDriver = ogr.GetDriverByName('ESRI Shapefile')

    # remove output shape file if it already exists
    if os.path.exists(shapefileFolder + '\\' + outFileName + '.shp'):
        outDriver.DeleteDataSource(shapefileFolder + '\\' + outFileName + '.shp')

    # create output shape file
    outDataSource = outDriver.CreateDataSource(shapefileFolder + '\\' + outFileName + '.shp')
    outLayer = outDataSource.CreateLayer(outFileName + '.shp', inLayer.GetSpatialRef(), inLayer.GetGeomType())
    
    # Add input Layer Fields to the output Layer
    outLayer.CreateFields(inLayer.schema)
    
    # Get the output Layer's Feature Definition
    outLayerDefn = outLayer.GetLayerDefn()
    
    # Add features to the output Layer
    for inFeature in inLayer:
        
        # Create output Feature
        outFeature = ogr.Feature(outLayerDefn)
        
        # Set geometry as centroid
        geom = inFeature.GetGeometryRef()
        outFeature.SetGeometry(geom)
        
        # Add field values from input Layer
        for i in range(0, outLayerDefn.GetFieldCount()):
            outFeature.SetField(i, inFeature.GetField(i))
        
        # Add new feature to output Layer
        outLayer.CreateFeature(outFeature)
    
    # Save and close DataSources
    del inFeature
    del inLayer
    del inDataSource
    del inDriver
    del outFeature
    del outLayer
    del outDataSource
    del outDriver
    
def MemoryToFeature(inDataSource,inMemory,outGDB,outFileName):
    """
    This tool will take an input ogr memory layer and convert it to a feature class within a geodatabase.
    The memory data source and memory layer are both needed for inputs because the memory layer will not
    be able to be accessed without the data source.
    
    Requirement: 'FileGDB' driver for ogr
    
    Args:
        inDataSource: in memory data source
        inMemory: in memory layer
        outGDB: path to the output geodatabase (must end with .gdb)
        outFileName: name of the output feature class

    Returns: N/A

    """
    
    # create the output driver
    outDriver = ogr.GetDriverByName('FileGDB')
    
    print('Out driver set as ' + format(outDriver.GetName()))
    
    # create output shape file
    outDataSource = outDriver.Open(outGDB, 1)
    outFile = outDataSource.CreateLayer(outFileName, inMemory.GetSpatialRef(), inMemory.GetGeomType())
    
    # Add input Layer Fields to the output Layer
    inLayerDefn = inMemory.GetLayerDefn()
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        outFile.CreateField(fieldDefn)
    
    # Get the output Layer's Feature Definition
    outLayerDefn = outFile.GetLayerDefn()
    
    # Add features to the output Layer
    for inFeature in inMemory:
        # Create output Feature
        outFeature = ogr.Feature(outLayerDefn)
        
        # Add field values from input Layer
        for i in range(0, outLayerDefn.GetFieldCount()):
            outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(),
                                inFeature.GetField(i))
        
        # Set geometry as centroid
        geom = inFeature.GetGeometryRef()
        outFeature.SetGeometry(geom.Clone())
        # Add new feature to output Layer
        outFile.CreateFeature(outFeature)
        outFeature = None
        
    # Save and close DataSources
    outDriver = None
    outDataSource = None
    outFile = None
    inDataSource = None
    inMemory = None

def MemoryToShapefile(inDataSource,inMemory,shapefileFolder,outFileName):
    """
    This tool will convert an ogr memory layer to a shapefile. The memory data source and memory layer are both
    needed for inputs because the memory layer will not be able to be accessed without the data source.
    
    Requirement: 'FileGDB' driver for ogr
    
    Args:
        inDataSource: input memory data source
        inMemory: input memory layer
        shapefileFolder: path to the folder where the shapefile will be placed
        outFileName: name of the output shapefile (must end with .shp)

    Returns: N/A

    """
    
    # create the output driver
    outDriver = ogr.GetDriverByName('ESRI Shapefile')
    
    # remove output shape file if it already exists
    if os.path.exists(shapefileFolder + '\\' + outFileName + '.shp'):
        outDriver.DeleteDataSource(shapefileFolder + '\\' + outFileName + '.shp')
    
    # create output shape file
    outDataSource = outDriver.CreateDataSource(shapefileFolder + '\\' + outFileName + '.shp')
    outFile = outDataSource.CreateLayer(outFileName + '.shp', inMemory.GetSpatialRef(), inMemory.GetGeomType())
    
    # Add input Layer Fields to the output Layer
    outFile.CreateFields(inMemory.schema)
    
    # Get the output Layer's Feature Definition
    outLayerDefn = outFile.GetLayerDefn()
    
    inMemory.ResetReading()
    
    # Add features to the output Layer
    for input_feat in inMemory:
        
        # Create output Feature
        outFeature = ogr.Feature(outLayerDefn)

        # Set geometry as centroid
        geom = input_feat.GetGeometryRef()
        outFeature.SetGeometry(geom)
        
        # Add field values from input Layer
        for i in range(0, outLayerDefn.GetFieldCount()):
            field_value = input_feat.GetField(i)
            outFeature.SetField(i,field_value)
        
        # Add new feature to output Layer
        outFile.CreateFeature(outFeature)
    
    # set the input data source and layer to none
    del inMemory
    del inDataSource
    del outFile
    del outDataSource
    del outDriver
    
def ShapefileToMemory(shapefileFolder,inFileName,outFileName):
    """
    This tool will convert a shapefile into an ogr memory layer and return the memory data source
    and memory layer. Both are returned because the memory layer cannot be opened without having the data
    source. So keep these together as long as the memory layer needs to be accessed.
    
    Args:
        shapefileFolder: path to the folder where the input shapefile is located
        inFileName: name of the input shapefile (must end with .shp)
        outFileName: name for the output memory layer

    Returns: memory data source and memory layer

    """
    # open the inShapefile as the driver type
    inDriver = ogr.GetDriverByName('ESRI Shapefile')
    inDataSource = inDriver.Open(shapefileFolder + '\\' + inFileName, 0)
    inLayer = inDataSource.GetLayer()
    
    # create the output driver
    outDriver = ogr.GetDriverByName('MEMORY')
    
    print('Out driver set as ' + format(outDriver.GetName()))
    
    # create output shape file
    outDataSource = outDriver.CreateDataSource('memData_' + format(outFileName))
    outFile = outDataSource.CreateLayer(outFileName, inLayer.GetSpatialRef(), inLayer.GetGeomType())
    
    # Add input Layer Fields to the output Layer
    outFile.CreateFields(inLayer.schema)
    
    # Get the output Layer's Feature Definition
    outLayerDefn = outFile.GetLayerDefn()
    
    inLayer.ResetReading()
    
    # Add features to the output Layer
    for input_feat in inLayer:
        
        # Create output Feature
        outFeature = ogr.Feature(outLayerDefn)

        # Set geometry as centroid
        geom = input_feat.GetGeometryRef()
        outFeature.SetGeometry(geom)
        
        # Add field values from input Layer
        for i in range(0, outLayerDefn.GetFieldCount()):
            field_value = input_feat.GetField(i)
            outFeature.SetField(i, field_value)
    
        # Add new feature to output Layer
        outFile.CreateFeature(outFeature)
    
    # Save and close DataSources
    del input_feat
    del inLayer
    del inDataSource
    del inDriver
    
    return outDataSource,outFile

def ShapefileToMemory_ForceMultiPoint(shapefileFolder,inFileName,outFileName):
    """
    Use this function to take a point feature shapefile, convert it to memory, and force the geometry to
    multipoint. This will only work with point features!!!
    
    Args:
        shapefileFolder: path to the folder where the shapefile is located in
        inFileName: name of the input shapefile
        outFileName: name of the out memory layer

    Returns: outDataSource and outFile (really just a ogr data source and layer object)

    """
    
    # open the inShapefile as the driver type
    inDriver = ogr.GetDriverByName('ESRI Shapefile')
    inDataSource = inDriver.Open(shapefileFolder + '\\' + inFileName, 0)
    inLayer = inDataSource.GetLayer()
    
    # create the output driver
    outDriver = ogr.GetDriverByName('MEMORY')
    
    print('Out driver set as ' + format(outDriver.GetName()))
    
    # create output shape file
    outDataSource = outDriver.CreateDataSource('memData_' + format(outFileName))
    outFile = outDataSource.CreateLayer(outFileName, inLayer.GetSpatialRef(), ogr.wkbMultiPoint)
    
    # Add input Layer Fields to the output Layer
    outFile.CreateFields(inLayer.schema)
    
    # Get the output Layer's Feature Definition
    outLayerDefn = outFile.GetLayerDefn()
    
    inLayer.ResetReading()
    
    # Add features to the output Layer
    for input_feat in inLayer:
        # Create output Feature
        outFeature = ogr.Feature(outLayerDefn)

        # Set geometry as centroid
        geom = input_feat.GetGeometryRef()
        geom_name = geom.GetGeometryName()
        if geom_name == 'POINT':
            geom = ogr.ForceToMultiPoint(geom)
        outFeature.SetGeometry(geom)
        
        # Add field values from input Layer
        for i in range(0, outLayerDefn.GetFieldCount()):
            field_value = input_feat.GetField(i)
            outFeature.SetField(i, field_value)
        
        # Add new feature to output Layer
        outFile.CreateFeature(outFeature)
    
    # Save and close DataSources
    del inLayer
    del inDataSource
    del inDriver
    
    return outDataSource,outFile
    
def DissolveWithFiona_FromMemory(inDataSource,inMemory,inFileName,outFileName,shapefileFolder,dissolve_field):
    """
    This function uses a script found online that uses fiona to dissolve a shapefile.
    url: https://gis.stackexchange.com/questions/149959/dissolving-polygons-based-on-attributes-with-python-shapely-fiona
    
    This function takes an ogr memory layer as an input, converts its to a shapefile, dissolves, and
    converts the dissolved shapefile back into a memory layer.
    
    NOTE: Have ran into issues with this working. Look at the Dissolve_ShapefileToShapefile function that uses only OGR.
    
    OTHER NOTE: This function uses other created functions so also need to import MemoryToShapefile and ShapefileToMemory.
    
    Args:
        inDataSource: input data source ogr layer
        inMemory: input memory ogr layer
        inFileName: name of the input layer
        outFileName: name of the output layer
        shapefileFolder: path to the folder where the temporary shapefile will be created
        dissolve_field: attribute field to dissolve by

    Returns: dissolved memory data source and layer

    """

    import fiona
    import itertools
    from shapely.geometry import shape, mapping
    from shapely.ops import unary_union
    
    MemoryToShapefile(inDataSource,inMemory,shapefileFolder,inFileName)
    
    """use fiona to dissolve"""
    with fiona.open(shapefileFolder + '\\' + inFileName + '.shp') as input_layer:
        # preserve the schema of the original shapefile, including the crs
        meta = input_layer.meta
        with fiona.open(shapefileFolder + '\\' + outFileName + '.shp','w', **meta) as output:
            # groupby clusters consecutive elements of an iterable which have the same key so you must first sort the features by the 'STATEFP' field
            e = sorted(input_layer, key=lambda k: k['properties'][dissolve_field])
            # group by the dissolve field
            for key, group in itertools.groupby(e, key=lambda x: x['properties'][dissolve_field]):
                properties, geom = zip(*[(feature['properties'], shape(feature['geometry'])) for feature in group])
                # write the feature, computing the unary_union of the elements in the group with the properties of the first element in the group
                output.write({'geometry': mapping(unary_union(geom)), 'properties': properties[0]})
                
    outDataSource,outFile = ShapefileToMemory(shapefileFolder,outFileName + '.shp',outFileName)
    
    return outDataSource,outFile

def DissolveWithFiona(shapefileFolder, inFileName, outFileName, dissolveField):
    """
    This function uses a script found online that uses fiona to dissolve a shapefile.
    url: https://gis.stackexchange.com/questions/149959/dissolving-polygons-based-on-attributes-with-python-shapely-fiona
    
    
    NOTE: Have ran into issues with this working. Look at the Dissolve_ShapefileToShapefile function that uses only OGR.
    
    Args:
        shapefileFolder: path to the folder where the input shapefile is located
        inFileName: name of the input shapefile
        outFileName: name of the output shapefile
        dissolveField: attribute field to dissolve by

    Returns: N/A

    """
    
    import fiona
    import itertools
    from shapely.geometry import shape, mapping
    from shapely.ops import unary_union
    import os

    # remove output shape file if it already exists
    d_out = ogr.GetDriverByName('ESRI Shapefile')
    if os.path.exists(shapefileFolder + '\\' + outFileName + '.shp'):
        d_out.DeleteDataSource(shapefileFolder + '\\' + outFileName + '.shp')
    del d_out
    
    with fiona.open(shapefileFolder + '\\' + inFileName + '.shp') as input_layer:
        # preserve the schema of the original shapefile, including the crs
        meta = input_layer.meta
        with fiona.open(shapefileFolder + '\\' + outFileName + '.shp', 'w', **meta) as output:
            # groupby clusters consecutive elements of an iterable which have the same key so you must first sort the features by the 'STATEFP' field
            e = sorted(input_layer, key=lambda k: k['properties'][dissolveField])
            # group by the dissolve field
            for key, group in itertools.groupby(e, key=lambda x: x['properties'][dissolveField]):
                properties, geom = zip(
                    *[(fiona_feature['properties'], shape(fiona_feature['geometry'])) for fiona_feature in group])
                # write the feature, computing the unary_union of the elements in the group with the properties of the first element in the group
                output.write({'geometry': mapping(unary_union(geom)), 'properties': properties[0]})

def Dissolve_ShapefileToShapefile(shapefileFolder, inFileName, outFileName):
    """
    This function uses solely OGR to dissolve a shapefile based on an attribute field. The input must be a shapefile
    and the output will also be a shapefile. It will force all geometries to multi geometries (MulitPoint, MultiLineString,
    or MulitPolygon) and calculate the name length and area of the dissolved feature.
    
    NOTE: This script will not calculate the correct length for each feature if it is a point of polygon, if the
        length field is present. If the input features is a line, then it should work okay.
        
    
    Args:
        shapefileFolder: path to where the input shapefile is located
        inFileName: name of the input shapefile
        outFileName: name of the output shapefile

    Returns: N/A

    """
    
    from osgeo import ogr
    import os
    
    # get layer from data source
    d_in = ogr.GetDriverByName('ESRI Shapefile')
    ds_in = d_in.Open(shapefileFolder + '\\' + inFileName + '.shp',0)
    l_in = ds_in.GetLayer()
    
    # check the geometry of the layer
    check_geom = l_in.GetGeomType()
    
    if check_geom == 1:
        # crate multi point geometry
        multi_geom = ogr.Geometry(ogr.wkbMultiPoint)
        set_geom = ogr.wkbMultiPoint
    if check_geom == 2:
        # create multi line string geometry
        multi_geom = ogr.Geometry(ogr.wkbMultiLineString)
        set_geom = ogr.wkbMultiLineString
    if check_geom == 3:
        # create a multi polygon geometry
        multi_geom = ogr.Geometry(ogr.wkbMultiPolygon)
        set_geom = ogr.wkbMultiPolygon
    
    # loop through each feature until there are no more
    for input_feat in l_in:
        # get geometry from feature
        g = input_feat.GetGeometryRef()
        
        # add geometry to multi geometry
        multi_geom.AddGeometry(g)
        
        # delete geometry
        del g
    
    l_in.ResetReading()
    
    """
    # dissolve the multi geometry using union cascaded if not a point a layer
    if (check_geom == 2) or (check_geom == 3):
        new_geom = multi_geom.UnionCascaded()
    else:
        new_geom = multi_geom
    """
    d_out = ogr.GetDriverByName('ESRI Shapefile')
    
    # remove output shape file if it already exists
    if os.path.exists(shapefileFolder + '\\' + outFileName + '.shp'):
        d_out.DeleteDataSource(shapefileFolder + '\\' + outFileName + '.shp')
    
    # open new shapefile
    ds_out = d_out.CreateDataSource(shapefileFolder + '\\' + outFileName + '.shp')
    l_out = ds_out.CreateLayer(outFileName, l_in.GetSpatialRef(), set_geom)
    
    # add field schema to out layer
    l_out.CreateFields(l_in.schema)
    
    defn = l_in.GetLayerDefn()
    
    # create a new feature
    newFeat = ogr.Feature(l_out.GetLayerDefn())
    # add geometry to the new feature
    newFeat.SetGeometry(multi_geom)
    # add field values to the new feature
    for i in range(0, defn.GetFieldCount()):
        field_value = l_in.GetFeature(0).GetField(i)
        field_name = defn.GetFieldDefn(i).GetNameRef()
        # if the field name is 'ID', set that value to blank
        if field_name == 'ID':
            field_value = ""
        if (field_name == 'SHAPE_Leng') or (field_name == 'Shape_Leng'):
            # set the calculated length from above to the  field value
            # if geometry is point, set to blank
            if check_geom == 1:
                field_value = ''
            # if geom is line, calculate length
            if check_geom == 2:
                field_value = newFeat.GetGeometryRef().Length()
            # if geom is polygon, calculate the length of the boundary (perimeter)
            if check_geom == 3:
                field_value = newFeat.GetGeometryRef().Boundary().Length()
        if (field_name == 'SHAPE_Area') or (field_name == 'Shape_Area'):
            # if geometry is polygon, calculate the area
            if check_geom == 3:
                field_value = newFeat.GetGeometryRef().Area()
            else:
                # if not a polygon, set value to blank
                field_value = ''
        newFeat.SetField(i, field_value)
    # add new feature to the out layer
    l_out.CreateFeature(newFeat)
    
    # close data sources
    del ds_in
    del ds_out

def SortLayer(inGDB, layerName, field):
    """
    This function will sort a feature class by a certain field in ascending order. It works with numbered fields,
    but should work with string fields as well. This function will NOT create a new feature class.
    
    Requirement: 'FileGDB' driver for ogr
    
    Args:
        inGDB: geodatabase where the input feature class is located (must end with .gdb)
        layer: name of the feature class
        field: Name of the field to sort by

    Returns: N/A

    """
    # open input layer with driver
    inDriver = ogr.GetDriverByName('FileGDB')
    inDataSource = inDriver.Open(inGDB,1)
    inLayer = inDataSource.GetLayer(layerName)
    # fids are unique, fids may be sorted or unsorted, fids may be consecutive or have gaps
    # don't care about semantics, don't touch fids and their order, reuse fids
    fids = []
    vals = []
    inLayer.ResetReading()
    for f in inLayer:
        fid = f.GetFID()
        fids.append(fid)
        vals.append((f.GetField(field), fid))
    vals.sort()
    # index as dict: {newfid: oldfid, ...}
    ix = {fids[i]: vals[i][1] for i in xrange(len(fids))}

    # swap features around in groups/rings
    for fidstart in ix.keys():
        if fidstart not in ix: continue
        ftmp = inLayer.GetFeature(fidstart)
        fiddst = fidstart
        while True:
            fidsrc = ix.pop(fiddst)
            if fidsrc == fidstart: break
            f = inLayer.GetFeature(fidsrc)
            f.SetFID(fiddst)
            inLayer.SetFeature(f)
            fiddst = fidsrc
        ftmp.SetFID(fiddst)
        inLayer.SetFeature(ftmp)
        
    inLayer.ResetReading()

    # Save and close DataSources
    del f
    del inLayer
    del inDataSource
    del inDriver
    
def SortMemory(inDataSource,inMemory,field):
    """
        This function will sort a memory layer by a certain field in ascending order. It works with numbered fields,
        but should work with string fields as well.

        Requirement: ogr

        Args:
            inDataSource: data source of the memory layer
            inMemory: layer source of the memory
            field: Name of the field to sort by

        Returns: inDataSource, inMemory

        """
    # fids are unique, fids may be sorted or unsorted, fids may be consecutive or have gaps
    # don't care about semantics, don't touch fids and their order, reuse fids
    fids = []
    vals = []
    inMemory.ResetReading()
    for f in inMemory:
        fid = f.GetFID()
        fids.append(fid)
        vals.append((f.GetField(field), fid))
    vals.sort()
    # index as dict: {newfid: oldfid, ...}
    ix = {fids[i]: vals[i][1] for i in xrange(len(fids))}
    
    # swap features around in groups/rings
    for fidstart in ix.keys():
        if fidstart not in ix: continue
        ftmp = inMemory.GetFeature(fidstart)
        fiddst = fidstart
        while True:
            fidsrc = ix.pop(fiddst)
            if fidsrc == fidstart: break
            f = inMemory.GetFeature(fidsrc)
            f.SetFID(fiddst)
            inMemory.SetFeature(f)
            fiddst = fidsrc
        ftmp.SetFID(fiddst)
        inMemory.SetFeature(ftmp)
    
    inMemory.ResetReading()
    
    del f
    
    return inDataSource,inMemory

def GrabUniqueValuesFromMemory(inDataSource,inMemory,field):
    """
        This function will create and return a list of the unique values or strings from a single
        column of the input memory layer.

        Requirement: ogr

        Args:
            inDatasource: data source that holds the input memory layer
            inFileName: input memory layer
            field: name of the field to grab the values or strings from

        Returns: unique values list, inDataSource, inMemory

        """
    
    # reset reading
    inMemory.ResetReading()
    
    unique_values = []
    
    for feature in inMemory:
        value = feature.GetField(field)
        if value not in unique_values:
            unique_values.append(value)
    
    inMemory.ResetReading()
    
    return unique_values,inDataSource,inMemory

def AppendFeatureToFeature(inGDB, inFileName, appendingFileName, appendingFileGDB):
    """
    The function will append a feature class to another feature class. This will only work for feature classes
    in a geodatabase. At this point, it is unknown if this function will work with features that have different
    attributes. The appending file/GDB will be the feature that gets appended to the in file/GDB.
    
    Requirement: 'FileGDB' driver for ogr
    
    Args:
        inGDB: path to the geodatabase that contains the main feature class
        inFileName: name of the main feature class
        appendingFileName: name of the feature class that will be appended to the main feature class
        appendingFileGDB: path to the geodatabase that contains the feature that is going to be appended.

    Returns: N/A

    """
    
    # open in file which will be appended to
    inDriver = ogr.GetDriverByName('FileGDB')
    inDataSource = inDriver.Open(inGDB, 1)
    inLayer = inDataSource.GetLayer(inFileName)
    
    # open the file which will be appended to the other
    extraDriver = ogr.GetDriverByName('FileGDB')
    extraDataSource = extraDriver.Open(appendingFileGDB, 0)
    extraLayer = extraDataSource.GetLayer(appendingFileName)
    
    extraLayerDefn = extraLayer.GetLayerDefn()
    
    for input_feat in inLayer:
        
        # create new feature
        extraFeature = ogr.Feature(extraLayerDefn)
        
        # set geometry
        geom = input_feat.GetGeometryRef()
        extraFeature.SetGeometry(geom)
        
        # Add field values from input Layer
        for i in range(0, extraLayerDefn.GetFieldCount()):
            extraFeature.SetField(i,input_feat.GetField(i))
        
        # append extra layer to in layer
        inLayer.CreateFeature(extraFeature)
    
    # Save and close DataSources
    del extraFeature
    del inLayer
    del inDataSource
    del inDriver
    del extraLayer
    del extraDataSource
    del extraDriver
    
def AppendMemoryToShapefile(inFolder,inFileName,appendingDataSource,appendingMemory):
    """
    This function will append an ogr memory layer to an existing feature class. As of now, it is uncertain
    if this will work with layers that have different attributes. Both the appending memory data source and layer
    are both needed because the memory layer cannot be opened without the data source.
    
    Requirement: 'FileGDB' driver for ogr
    
    Args:
        inGDB: path to the geodatabase where the feature class is located
        inFileName: name of the feature class
        appendingDataSource: memory data source that will be appended to the feature class
        appendingMemory: memory layer that will be appended to the feature class

    Returns: N/A

    """
    
    # open in file which will be appended to
    inDriver = ogr.GetDriverByName('ESRI Shapefile')
    inDataSource = inDriver.Open(inFolder + '\\' + inFileName + '.shp', 1)
    inLayer = inDataSource.GetLayer()
    
    appendingMemory.ResetReading()
    
    inLayerDefn = inLayer.GetLayerDefn()
    
    for input_feat in appendingMemory:
        
        # create new feature
        extraFeature = ogr.Feature(inLayerDefn)
        
        # Set geometry
        geom = input_feat.GetGeometryRef()
        extraFeature.SetGeometry(geom)

        # Add field values from input Layer
        for i in range(0, inLayerDefn.GetFieldCount()):
            field_value = input_feat.GetField(i)
            extraFeature.SetField(i, field_value)
    
        # append extra layer to in layer
        inLayer.CreateFeature(extraFeature)
    

    # Save and close DataSources
    del input_feat
    del inLayer
    del inDataSource
    del inDriver
    del appendingMemory
    del appendingDataSource

def AppendOgrLayerToOgrLayer(inDataSource,inMemory, appendingDataSource,appendingMemory):
    """
    This function will append a memory layer to another memory layer, return the memory data source
    and layer that was appended, and delete the appended memory data source and layer. The two layers must
    have the same field names!!!
    
    Args:
        inDataSource: input memory data source
        inMemory: input memory layer
        appendingDataSource: memory data source that will be appended to the input
        appendingMemory: memory layer that will be appended to the input

    Returns: input memory data source and layer that was appended to as well as the appended data source and memory

    """
    
    inLayerDefn = inMemory.GetLayerDefn()
    
    appendingMemory.ResetReading()
    
    for input_feat in appendingMemory:
        
        extraFeature = ogr.Feature(inLayerDefn)
        
        # Set geometry
        geom = input_feat.GetGeometryRef()
        extraFeature.SetGeometry(geom.Clone())
        
        # Add field values from input Layer
        for i in range(0, inLayerDefn.GetFieldCount()):
            field_value = input_feat.GetField(i)
            extraFeature.SetField(i,field_value)
        
        # append extra layer to in layer
        inMemory.CreateFeature(extraFeature)
        
    del extraFeature
    
    inMemory.ResetReading()
    appendingMemory.ResetReading()
    
    return inDataSource, inMemory, appendingDataSource, appendingMemory
    
def AddFieldsFromFeatureToFeature(inGDB,inFileName,fieldsGDB,fieldsFeatureName):
    """
    This function will take the fields of a feature class and add them to another feature class. It will copy
    over all of the field names of the fields Feature.
    This function will only work with feature classes in a geodatabase.
    
    Requirement: 'FileGDB' driver for ogr
    
    Args:
        inGDB: path to geodatabase that contains the inFileName layer
        inFileName: name of the input feature class that will get the fields added to itself
        fieldsGDB: path to the geodatabase that contains the feature class with the wanted field names
        fieldsFeatureName: name of the feature class with the field names that are wanted for the in feature class

    Returns: N/A

    """
    # open in feature using the driver
    inDriver = ogr.GetDriverByName('FileGDB')
    inDataSource = inDriver.Open(inGDB,1)
    inLayer = inDataSource.GetLayer(inFileName)
    
    # open feature that has the fields wanted
    fieldsDriver = ogr.GetDriverByName('FileGDB')
    fieldsDataSource = fieldsDriver.Open(fieldsGDB,0)
    fieldsLayer = fieldsDataSource.GetLayer(fieldsFeatureName)
    
    # add field layer fields to the inLayer
    inLayer.CreateFields(fieldsLayer.schema)

    # Save and close DataSources
    del inLayer
    del inDataSource
    del inDriver
    del fieldsLayer
    del fieldsDataSource
    del fieldsDriver

def ListOGR_drivers():
    """
    This simple function will print a lost of all the OGR drivers in the current module.
    
    Returns: N/A

    """
    import ogr
    cnt = ogr.GetDriverCount()
    formatsList = []  # Empty List
    
    for i in range(cnt):
        driver = ogr.GetDriver(i)
        driverName = driver.GetName()
        if not driverName in formatsList:
            formatsList.append(driverName)
    
    formatsList.sort()  # Sorting the messy list of ogr drivers
    
    for i in formatsList:
        print i

def TableToCSV(inGDB, inTableName, outTablePath):
    """
    This function will convert an attribute table within a feature class into a CSV.
    Will only work with feature classes!
    
    Args:
        inGDB: path to geodatabase where the input feature is located
        inTableName: name of the input feature
        outTablePath: path to where the output CSV will be saved to

    Returns: N/A

    """
    
    from osgeo import ogr
    import csv
    
    # open table in geodatabase
    inDriver = ogr.GetDriverByName('FileGDB')
    inDataSource = inDriver.Open(inGDB, 0)
    inTable = inDataSource.GetLayer(inTableName)
    
    # pull header information
    header = []
    inTableDefn = inTable.GetLayerDefn()
    for i in range(0, inTableDefn.GetFieldCount()):
        header.append((inTableDefn.GetFieldDefn(i)).GetName())
    
    with open(outTablePath, 'wb') as csvFile:
        writer = csv.DictWriter(csvFile, fieldnames=header)
        
        writer.writeheader()
        
        for line in inTable:
            rowdict = {}
            for i in range(0, inTableDefn.GetFieldCount()):
                rowdict.update(
                    {inTableDefn.GetFieldDefn(i).GetNameRef(): line.GetField(inTableDefn.GetFieldDefn(i).GetNameRef())})
            
            line.Destroy()
            writer.writerow(rowdict)
        
        csvFile.close()
    
    del inTable
    del inDataSource
    del inDriver
    
def CheckFeatureCount_Shapefile(shapefileFolder, fileName):
    """
    use this function to calculate the number of features in a shapefile.
    
    Args:
        shapefileFolder: path to the folder where the shapefile is located
        fileName: name of the shapefile

    Returns: object containing a number representing the number of features in the shapefile

    """
    
    d = ogr.GetDriverByName('ESRI Shapefile')
    ds = d.Open(shapefileFolder + '\\' + fileName + '.shp', 0)
    l = ds.GetLayer()
    feat_num = l.GetFeatureCount()
    del l
    del ds
    del d
    
    return feat_num

def CheckFeatureCount_FeatureGDB(GDB,inFileName):
    """
    Use this function to calculate the number of features from a layer within a GDB.
    Args:
        GDB: path to the geodatabase
        inFileName: name of the layer

    Returns: object containing a number representing the number of features in the shapefile

    """
    
    # open in feature using the driver
    inDriver = ogr.GetDriverByName('FileGDB')
    inDataSource = inDriver.Open(GDB, 1)
    inLayer = inDataSource.GetLayer(inFileName)
    
    # get feature count from layer
    feat_num = inLayer.GetFeatureCount()
    del inLayer
    del inDataSource
    del inDriver
    
    return feat_num

def SplitIntoTwoLayers_Shapefile(shapefileFolder,shapefileName):
    """
    This function will take a shapefile and split it into 2 separate shapefiles. The first output will have the first half
    of the number of features, the second output will have the other half. The two outputs will have a '_A' and '_B'
    added to the names.
    
    Args:
        shapefileFolder:
        shapefileName:

    Returns: N/A

    """
    
    # Open input shapefile
    inDriver = ogr.GetDriverByName('ESRI Shapefile')
    inDataSource = inDriver.Open(shapefileFolder + '\\' + shapefileName + '.shp')
    inLayer = inDataSource.GetLayer()
    
    # Get feature count
    feat_count = inLayer.GetFeatureCount()
    
    # open first new shapefile
    outDriver_A = ogr.GetDriverByName('ESRI Shapefile')

    # remove output shape file if it already exists
    if os.path.exists(shapefileFolder + '\\' + shapefileName + '_A.shp'):
        outDriver_A.DeleteDataSource(shapefileFolder + '\\' + shapefileName + '_A.shp')

    # create output shape file
    outDataSource_A = outDriver_A.CreateDataSource(shapefileFolder + '\\' + shapefileName + '_A.shp')
    outFile_A = outDataSource_A.CreateLayer(shapefileName + '_A.shp', inLayer.GetSpatialRef(), inLayer.GetGeomType())

    # Add input Layer Fields to the output Layer
    outFile_A.CreateFields(inLayer.schema)

    # Get the output Layer's Feature Definition
    outLayerDefn = outFile_A.GetLayerDefn()

    inLayer.ResetReading()
    
    # now add first half of features from inLayer to shapefile A
    for i in range(0,int(feat_count/2)):
        
        input_feat = inLayer.GetFeature(i)
    
        # Create output Feature
        outFeature = ogr.Feature(outLayerDefn)
    
        # Set geometry as centroid
        geom = input_feat.GetGeometryRef()
        outFeature.SetGeometry(geom)
    
        # Add field values from input Layer
        for i in range(0, outLayerDefn.GetFieldCount()):
            field_value = input_feat.GetField(i)
            outFeature.SetField(i, field_value)
    
        # Add new feature to output Layer
        outFile_A.CreateFeature(outFeature)
        
    # close new shapefile
    del outFile_A
    del outDataSource_A
    del outDriver_A
    
    # reset reading
    inLayer.ResetReading()

    # open first new shapefile
    outDriver_B = ogr.GetDriverByName('ESRI Shapefile')

    # remove output shape file if it already exists
    if os.path.exists(shapefileFolder + '\\' + shapefileName + '_B.shp'):
        outDriver_B.DeleteDataSource(shapefileFolder + '\\' + shapefileName + '_B.shp')

    # create output shape file
    outDataSource_B = outDriver_B.CreateDataSource(shapefileFolder + '\\' + shapefileName + '_B.shp')
    outFile_B = outDataSource_B.CreateLayer(shapefileName + '_B.shp', inLayer.GetSpatialRef(), inLayer.GetGeomType())

    # Add input Layer Fields to the output Layer
    outFile_B.CreateFields(inLayer.schema)

    # Get the output Layer's Feature Definition
    outLayerDefn = outFile_B.GetLayerDefn()

    inLayer.ResetReading()

    # now add first half of features from inLayer to shapefile A
    for i in range(int(feat_count / 2),feat_count):
    
        input_feat = inLayer.GetFeature(i)
    
        # Create output Feature
        outFeature = ogr.Feature(outLayerDefn)
    
        # Set geometry as centroid
        geom = input_feat.GetGeometryRef()
        outFeature.SetGeometry(geom)
    
        # Add field values from input Layer
        for i in range(0, outLayerDefn.GetFieldCount()):
            field_value = input_feat.GetField(i)
            outFeature.SetField(i, field_value)
    
        # Add new feature to output Layer
        outFile_B.CreateFeature(outFeature)

    # close new shapefile
    del outFile_B
    del outDataSource_B
    del outDriver_B
    del inLayer
    del inDataSource
    del inDriver
    
def PullIndexFromFeature(GDB, inFileName, fieldName):
    """
    Simple function to grab the field index based off of a field name from a feature within a geodatabase.
    The field index of the first field matching the passed field name (case insensitively) is returned.
    
    Args:
        GDB: path to the geodatabase containing the feature (string)
        inFileName: name of the feature (string)
        fieldName: name of field for the index (string)

    Returns: field index (integer)

    """
    # open feature
    driver = ogr.GetDriverByName('FileGDB')
    dataSource = driver.Open(GDB, 0)
    layer = dataSource.GetLayer(inFileName)
    
    # get feature definition from the layer
    defn = layer.GetLayerDefn()
    
    # get field index based on field name
    index = defn.GetFieldIndex(fieldName)
    
    # delete objects
    del layer
    del dataSource
    del driver
    
    return index

def GetGeomType_OGR(folder, inFileName, driverType):
    """
    This function will take a feature within a geodatabase or a shapefile and return an integer indicating
    the geometry type of the layer.
    
    1: Point
    2: Polyline
    3: Polygon
    
    Args:
        folder: path to the folder or geodatabase
        inFileName: name of the layer
        driverType: OGR driver type, MUST BE 'ESRI Shapefile' or 'FileGDB'
        
    Requirement: 'FileGDB' driver for OGR, if using a feature within a geodatabase as the input

    Returns: integer indicating the geometry type of the input layer

    """
    # open layer
    if driverType == 'FileGDB':
        driver = ogr.GetDriverByName(driverType)
        dataSource = driver.Open(folder,0)
        layer = dataSource.GetLayer(inFileName)
    if driverType == 'ESRI Shapefile':
        driver = ogr.GetDriverByName(driverType)
        dataSource = driver.Open(folder + '\\' + inFileName + '.shp',0)
        layer = dataSource.GetLayer()
        
    # get the geometry type from the layer
    geometry_type = layer.GetGeomType()
    
    # return the geometry type integer
    return geometry_type

    # delete layers
    del layer
    del dataSource
    del driver
    
def CheckFeatureExistsInGDB(GDB,featureName):
    """
    This little function will check if a feature layer exists in a geodatabase using OGR.

    Args:
        GDB: path to the geodatabase
        featureName: name of the feature layer as a string

    Returns: True or False object

    """
    driver = ogr.GetDriverByName('FileGDB')
    dataSource = driver.Open(GDB,0)
    if dataSource.GetLayer(featureName):
        feat = True
    else:
        feat = False
        
    return feat

BaseTable_name = 'BIOFILE'
dissolve_field = "RARNUM"

# enable python exceptions for ogr/gdal
ogr.UseExceptions()

# List of feature classes related to 'biofile'
# NEED TO MAKE SURE ALL POSSIBLE FEATURE NAMES ARE HERE. Capitalization does not matter here. Keep point feature names here too.
PotentialFCs_biofile = ['benthic_polygon',"BENTHIC","BENTHICPT","BIRDS",'BIRDSL',"BIRDSPT","BIRDPT",'birds_polygon',"FISH","FISHL",'FISHPT','fish_polygon','fishp_polygon','fishl_arc','fishpt_point',"HABITATS",\
                        "HABITATSPT","habitats_polygon","HERP","HERPPT",'habpt_point',"invertebrates",\
                             "INVERT",'invert_polygon',"INVERTPT",'invertpt_point',"M_MAMMALS","M_MAMMAL",'M_MAMPT','marineMammals','m_mammal_polygon','m_mammal_polygon_1','m_mampt_point','nests','nests_point','nests_label',\
                         'reptiles_polygon','REPTILES','reptilel_arc','reptpt_point',"T_MAMMALS","T_MAMMAL",'t_mammal_polygon','terrestrial_mammals']
# add copy of names here if needed so you don't lose them #

ParentFolder = r'E:\ESI\Chesapeake_test'
ESI_GDB = r'E:\ESI\Chesapeake_test\ChesapeakeBay_2016_ESI.gdb'

# Grab index for dissolve field from the base table but the name
dissolveField_biofileIndex = PullIndexFromFeature(ESI_GDB,BaseTable_name,dissolve_field)

# Pull out base table for joining values
if os.path.exists(ParentFolder + '\\' + BaseTable_name + '.csv'):
    print(format(BaseTable_name) + '.csv already exists.')
else:
    print(format(BaseTable_name) + '.csv does not exists. Creating it now.')
    
    # convert the feature table to CSV
    TableToCSV(ESI_GDB, BaseTable_name, ParentFolder + '\\' + BaseTable_name + '.csv')
    
    print format(BaseTable_name) + ".csv created here: " + format(ParentFolder)

# Create list of rows and rarenums from csv
with open(format(ParentFolder) + '\\' + format(BaseTable_name) + ".csv", 'rb') as file:
    reader = csv.reader(file)
    Lines = []
    # set OID equal to False for now. If the header of the biofile has OID as the first field, then set OID equal to
    # true and index out this field from Lines
    OID = False
    for row in reader:
        if row[0] == 'OID':
            OID = True
        if OID == True:
            Lines.append(row[1:])
        else:
            Lines.append(row)
  
csv_fileInfo = format(ParentFolder) + '\\' + format(BaseTable_name) + ".csv"

print(Lines[0])

# create list of the full headers that will be appended into the new updated feature class later
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

# Run through user-defined list of feature classes to run through the geodatabase
for feature in PotentialFCs_biofile:  # run through each of the relevant feature classes
    
    # check if the feature exists. if not, continue to next feature
    if CheckFeatureExistsInGDB(ESI_GDB,feature):
        print(feature + ' exists. Commence updating process in \n5\n4\n3\n2\n1\nLAUNCH.')
    else:
        continue
    
    """Ran into scenario where the main layer did not have any features in is, which caused the script to crash.
            So, going to get the number of features in the layer. If it is zero, continue."""
    check_feat_count = CheckFeatureCount_FeatureGDB(ESI_GDB,feature)
    
    # if the feat count is zero, continue
    if check_feat_count == 0:
        print(format(feature) + ' has zero features, moving on to next.')
        continue
        
    # using this variable to keep track is an additional final shapefile needed to be created if the file size exceeds 2GB and fails to append new features to it
    additional_file = False
    additional_file_index = 0
    
    new_features_folder = format(ParentFolder) + '\\' + format(BaseTable_name) + '_UpdatedFeatures'
    shapefileFolder = format(ParentFolder) + '\\' + format(BaseTable_name) + '_' + format(feature)+ '_extraShapefiles'

    '''
    Add folder for the extra features and the updated features
    '''
    # create folder for extra feature classes within the geodatabase
    if not os.path.exists(new_features_folder):
        os.mkdir(new_features_folder)

    # create new folder to hold shapefiles within the parent folder if it does not already exist
    if not os.path.exists(shapefileFolder):
        os.mkdir(shapefileFolder)
    
    """Filter out dissolve values of zero from the input feature class. Convert it to memory to usage."""
    filterQuery = "{} <> 0".format(dissolve_field)

    # Open Feature Class and convert to a shapefile if is doesn't exist
    if os.path.exists(shapefileFolder + '\\' + feature + '.shp'):
        print(feature + ' shapefile already exists')
    else:
        FeatureToShapefile_withQuery(ESI_GDB,shapefileFolder,feature, filterQuery)
    
    # now open the new shapefile for editing
    FeatureDriver = ogr.GetDriverByName('ESRI Shapefile')
    FeatureDataSource = FeatureDriver.Open(shapefileFolder + '\\' + feature + '.shp',1)
    FeatureLayer = FeatureDataSource.GetLayer()
    
    # for this feature, delete field of the name 'ID'
    ID_field_check = FeatureLayer.FindFieldIndex('ID',True)
    if ID_field_check == -1:
        print('There is no ID field.')
    else:
        print('ID field found. Deleting.')
        FeatureLayer.DeleteField(ID_field_check)
    
    print('Feature filtered out ' + format(dissolve_field) + ' values equal to zero')

    """Sort using OGR"""
    FeatureDataSource,FeatureLayer = SortMemory(FeatureDataSource,FeatureLayer,dissolve_field)

    print('Feature sorted by ' + format(dissolve_field))

    # create list of RARNUM values in the new feature class
    uniqueValues_RARNUM,FeatureDataSource,FeatureLayer = GrabUniqueValuesFromMemory(FeatureDataSource,FeatureLayer,dissolve_field)

    print('unique ' + format(dissolve_field) + ' unique values pulled into list')

    # sort uniqueValues_RARNUM list from low to high, even though the list is probably already sorted
    uniqueValues_RARNUM = sorted(uniqueValues_RARNUM)
    
    """ Check the geometry type of the input layer. This will determine what geometry type the final layer needs to be set to. """
    input_geometry_type = FeatureLayer.GetGeomType()
    # set the needed geometry type to a type of MULTI geometry
    if input_geometry_type == 1:
        setGeomTo = ogr.wkbMultiPoint
    if input_geometry_type == 2:
        setGeomTo = ogr.wkbMultiLineString
    if input_geometry_type == 3:
        setGeomTo = ogr.wkbMultiPolygon
    
    """for each unique dissolve field value, extract the records that match, dissolve, look for the number of matches to the dissolve field value in the
    biofile while keeping a list of the matched rows. If number of matches is greater than 1, create copies of additional records to make the number of
    matched records even to the number of records that contain the dissolved feature calss for the dissolve value. Add the wanted field names and append
    the matched rows from the biofile to the records. Finally, add the records to the final output. Iterate over each unique rarnum value."""
    
    """ Also, check if the final layer already exists. If so, move on. if not, create a new one and add fields."""
    
    finalDriver = ogr.GetDriverByName('ESRI Shapefile')
    
    used_rarnums = []
    
    if os.path.exists(new_features_folder + '\\' + feature + '.shp'):
        
        print('Final ' + format(feature) + ' already exists.')
        
        # get set of rarnum values that are already in this feature
        finalDataSource = finalDriver.Open(new_features_folder + '\\' + feature + '.shp',1)
        finalLayer = finalDataSource.GetLayer()
        
        # get rarnum values from this shapefile and add to used rarnums list so they aren't duplicated
        for f in finalLayer:
            value = str(f.GetField(dissolve_field))
            if value not in used_rarnums:
                used_rarnums.append(value)
        
        del finalLayer
        del finalDataSource
        del finalDriver
        
    else:
        
        print('Creating new final data source')
        
        # open final output layer
        finalDataSource = finalDriver.CreateDataSource(new_features_folder + '\\' + feature + '.shp')
        finalLayer = finalDataSource.CreateLayer(feature, FeatureLayer.GetSpatialRef(), setGeomTo)
        
        # add fields from input feature to final feature
        # add field layer fields to the inLayer
        finalLayer.CreateFields(FeatureLayer.schema)
        
        # open base table and add fields from it to the final layer
        tableDriver = ogr.GetDriverByName('CSV')
        tableDataSource = tableDriver.Open(ParentFolder + '\\' + BaseTable_name + '.csv',0)
        tableLayer = tableDataSource.GetLayer()
        
        tableLayerDefn = tableLayer.GetLayerDefn()
        i = 0
        if OID == True:
            i = 1
        for i in range(i, tableLayerDefn.GetFieldCount()):
            new_field = tableLayerDefn.GetFieldDefn(i)
            new_field_name = new_field.GetNameRef()
            # to prevent duplicate columns, if the field name is the dissolve field, continue and don't add field.
            if new_field_name == dissolve_field:
                continue
            finalLayer.CreateField(new_field)
            name_check = finalLayer.GetLayerDefn().GetFieldDefn(i).GetNameRef()
            
    
        del tableLayer
        del tableDataSource
        del tableDriver
        print('Fields added to final feature')
        
        # close final Layer for now
        del finalLayer
        del finalDataSource
        del finalDriver
        
    # close feature layer
    del FeatureLayer
    del FeatureDataSource
    del FeatureDriver
    
    # loop through each unique RARNUM values
    for value in uniqueValues_RARNUM:
        
        RARNUM_master = str(int(value))

        # if the value has already been completed, continue to next
        if RARNUM_master in used_rarnums:
            continue

        RARNUMval_str = str(int(value))
        
        # if feature had to be separated, delete the additional letters in the rarnum/hunum variable
        if '_A' in RARNUMval_str:
            RARNUMval_str = RARNUMval_str.replace('_A','')
        if '_B' in RARNUMval_str:
            RARNUMval_str = RARNUMval_str.replace('_B','')
    
        print('Dissolving ' + format(RARNUMval_str))

        inFileName = format(feature) + '_separated_' + format(RARNUMval_str)
        outFileName = format(feature) + '_dissolved_' + format(RARNUMval_str)
        
        # check if the feature have already been selected out by dissolve field value
        shapefile_path = shapefileFolder + '\\' + feature + '_separated_' + RARNUMval_str + '.shp'
        print(shapefile_path)
        if os.path.exists(shapefileFolder + '\\' + feature + '_separated_' + RARNUMval_str + '.shp'):
            print(feature + ' already extracted by ' + dissolve_field + 'value')
        else:
            # set up query to extract from the main feature only features of a certain dissolve field value to a shapefile
            query = '{} = {}'.format(dissolve_field, RARNUMval_str)
            ExtractFeaturesInShapefile_ByAttribute_ToShapefile(shapefileFolder,feature,inFileName,query)
        
        """Need to check if this selected out shapefile from above has more than one feature. If not, move on. If these is more than one feature, than dissolve."""
        d_featCheck = ogr.GetDriverByName('ESRI Shapefile')
        ds_featCheck = d_featCheck.Open(shapefileFolder + '\\' + inFileName + '.shp',1)
        l_featCheck = ds_featCheck.GetLayer()
        
        number_of_features = l_featCheck.GetFeatureCount()
        
        del l_featCheck
        del ds_featCheck
        del d_featCheck
        
        if number_of_features == 1:
            print(feature + '_' + RARNUMval_str + ' has only 1 feature and does not need to be dissolved.')
            outFileName = format(feature) + '_separated_' + format(RARNUMval_str)
        
        if number_of_features > 1:
    
            print('features for dissolve value of ' + format(RARNUMval_str) + ' extracted from the input')
            
            """ Going to create a variable that will be set to False, then if the dissolve works and there is only
            one feature in the layer, it will be set to True. This will be a way of keeping track if the dissolved
            function worked and the script can move on. """
            
            dissolve_check = False
    
            # remove output shape file if it already exists
            outDriver = ogr.GetDriverByName('ESRI Shapefile')
            if os.path.exists(shapefileFolder + '\\' + outFileName + '.shp'):
                outDriver.DeleteDataSource(shapefileFolder + '\\' + outFileName + '.shp')
        
            """use fiona to dissolve!"""
            try:
                print('Trying to dissolve with OGR.')
                Dissolve_ShapefileToShapefile(shapefileFolder, inFileName, outFileName)
                # check if dissolve fully worked
                feat_num = CheckFeatureCount_Shapefile(shapefileFolder,outFileName)
                if feat_num == 1:
                    print('Dissolve with OGR worked. Continuing on.')
                    dissolve_check = True
                else:
                    print('Dissolve function did not work completely. Most likely because the file is too large. Going to split layer into 2 layers' + \
                                ' and append to uniqueValues_RARNUM list to be delt with at the end.')
    
                    SplitIntoTwoLayers_Shapefile(shapefileFolder, inFileName)
                    
                    # add new names to unique rarnum values list
                    uniqueValues_RARNUM.append(RARNUMval_str + '_A')
                    uniqueValues_RARNUM.append(RARNUMval_str + '_B')
                    
                    # add current RARNUM val string to used rarnum list so that it doesn't get stuck in a loop
                    used_rarnums.append(RARNUMval_str)
                    
                    continue
            
            except:
                
                print('Dissolve function failed. Most likely because the file is too large. Going to split layer into 2 layers' + \
                      ' and append to uniqueValues_RARNUM list to be delt with at the end.')
                
                SplitIntoTwoLayers_Shapefile(shapefileFolder,inFileName)
                
                uniqueValues_RARNUM.append(RARNUMval_str + '_A')
                uniqueValues_RARNUM.append(RARNUMval_str + '_B')

                # add current RARNUM val string to used rarnum list so that it doesn't get stuck in a loop
                used_rarnums.append(RARNUMval_str)
                
                continue
            
        # if the feature layer has a point geometry, open the shapefile with the function that forces the point geometry to a multi point geometry.
        # if not, open normally
        if input_geometry_type == 1:
            print('Layer contains points. Forcing to MultiPoint.')
            dissolvedDataSource,dissolvedMemory = ShapefileToMemory_ForceMultiPoint(shapefileFolder,outFileName + '.shp',outFileName)
        else:
            dissolvedDriver = ogr.GetDriverByName('ESRI Shapefile')
            dissolvedDataSource = dissolvedDriver.Open(shapefileFolder + '\\' + outFileName + '.shp',1)
            dissolvedMemory = dissolvedDataSource.GetLayer()

        # get the number of fields before adding new ones to be used later for filling in matched data in the correct location
        layer_field_count = dissolvedMemory.GetLayerDefn().GetFieldCount()

        # open base table and add fields from it to the dissolved layer
        tableDriver = ogr.GetDriverByName('CSV')
        tableDataSource = tableDriver.Open(ParentFolder + '\\' + BaseTable_name + '.csv', 0)
        tableLayer = tableDataSource.GetLayer()

        tableLayerDefn = tableLayer.GetLayerDefn()

        i = 0
        if OID == True:
            i = 1
        for i in range(i, tableLayerDefn.GetFieldCount()):
            new_field = tableLayerDefn.GetFieldDefn(i)
            new_field_name = new_field.GetNameRef()
            # to prevent duplicate columns, if the field name is the dissolve field, continue and don't add field.
            if new_field_name == dissolve_field:
                continue
            dissolvedMemory.CreateField(new_field)

        del tableLayer
        del tableDataSource
        del tableDriver
        print('Fields added to dissolved feature')
        
        """ Next section will loop through the biofile lines and look for RARNUM/HUNUM matches in each row. The script will keep track of
        how many matches are made, as well as appending all the rows that are matched to a list."""
    
        matchList = []
        biofileRow_matchList = []
        number_of_matches = 0
        biofile_index = 0
    
        for record in Lines:
            RARNUM_table = str(record[dissolveField_biofileIndex])
        
            # check if the RARNUM values match. If so, add to matched lists
            if RARNUMval_str == RARNUM_table:
                # add 1 to number of matches tally
                number_of_matches += 1
                print record
                matchList.append(RARNUMval_str)
                biofileRow_matchList.append(record)
            biofile_index += 1
    
        print(format(number_of_matches) + ' matches have been found.')
    
        # with the number of known matches, the geometry in the temporary feature needs to be copied a certain number
        # of times so that there are an equal number of matches and geometries.
        if number_of_matches > 1:
            
            """Create a copy of the feature in dissolved memory and add this feature back into the dissolved memory
            a certain number of times so that the number of features in the memory is equal to the number of matches."""
            
            # get layer defn of memory layer
            LayerDefn = dissolvedMemory.GetLayerDefn()
            
            # get a feature from the dissolved memory layer
            extra_input_feat = dissolvedMemory.GetFeature(0)
            
            # create new feature from dissolved memory layer defn
            extraFeature = ogr.Feature(LayerDefn)
            
            # Set geometry
            geom = extra_input_feat.GetGeometryRef()
            extraFeature.SetGeometry(geom)

            # Add field values from input Layer
            for i in range(0, LayerDefn.GetFieldCount()):
                extraFeature.SetField(i, extra_input_feat.GetField(i))
            
            # create a loop to add the feature a certain amount of times
            for i in range(1,number_of_matches):
                
                # Add feature to dissolved memory
                dissolvedMemory.CreateFeature(extraFeature)
                
            # now delete the extra feature and input feature
            #del extra_input_feat
            del extraFeature
            
            dissolvedMemory.ResetReading()
            
        """ This next section will add the field definitions to the dissolved layer """
    
        feat_index = 0
    
        inLayerDefn = dissolvedMemory.GetLayerDefn()
    
        # add matches rows to the memory layer
        for input_feat in dissolvedMemory:
            try:
                    
                ctl = biofileRow_matchList[feat_index]  # ctl = acronym for check _text_line
                print "updating using: " + format(ctl)
                
                # set field count from layer_field_count variable set earlier. This will ensure that the values are appending to the correct field
                field_count = layer_field_count
                
                try:
                    for i in range(0, len(FOI_fullList)):
                        # since the additional RARNUM column was taken out, need to skip over the rarnum field iteration here
                        if i == dissolveField_biofileIndex:
                            continue
                        field_name = inLayerDefn.GetFieldDefn(field_count).GetNameRef()
                        field_type = inLayerDefn.GetFieldDefn(field_count).GetTypeName()
                        field_value = ctl[i]
                        if (field_name == 'DATE_PUB'):
                            field_value = int(float(field_value))
                        input_feat.SetField(field_name,field_value)
                        field_count += 1
                except RuntimeError as e:
                    print(e)
                dissolvedMemory.SetFeature(input_feat)
                feat_index += 1
            except IndexError:
                print('biofileRow_matchList index is out of range')
    
        # Now that the dissolved RARNUM value has been duplicated if needed and has the field + values added,
        # it can be appended to the final layer memory
    
        try:
            if additional_file == False:
                AppendMemoryToShapefile(new_features_folder,feature,dissolvedDataSource,dissolvedMemory)
            if additional_file == True:
                AppendMemoryToShapefile(new_features_folder, feature + '_' + format(additional_file_index), dissolvedDataSource, dissolvedMemory)
                
        except RuntimeError as f:
            
            print(f)
            
            """ This Runtime Error should be caused if the final shapefile reaches over 2 GB in size and the script fails.
            If this happens, create a second part to this final shapefile. """
            
            additional_file = True

            if os.path.exists(new_features_folder + '\\' + feature + '_' + format(additional_file_index) + '.shp'):
                print('Additional final for ' + format(feature) + ' shapefile already exists.')
                # append the dissolved feature to the secondary final shapefile
                AppendMemoryToShapefile(new_features_folder, feature + '_' + format(additional_file_index), dissolvedDataSource, dissolvedMemory)
                
            else:
                
                """Go into previous final layer and delete any features with the current rarnum value so that there are no duplicates"""
                
                finalDriver = ogr.GetDriverByName('ESRI Shapefile')
                finalDataSource = finalDriver.Open(new_features_folder + '\\' + feature + '.shp',1)
                finalLayer = finalDataSource.GetLayer()
                
                # delete features from the final layer that have the current rarnum value
                for ff in finalLayer:
                    FID = ff.GetFID()
                    rarnum_value = str(ff.GetField(dissolve_field))
                    if rarnum_value == RARNUMval_str:
                        finalLayer.DeleteFeature(FID)
                        
                del finalLayer
                del finalDataSource
                del finalDriver
    
                print('Creating additional final data source')
    
                # add one to additional_file_index
                additional_file_index += 1

                # now open the old shapefile for copying structure
                FeatureDriver = ogr.GetDriverByName('ESRI Shapefile')
                FeatureDataSource = FeatureDriver.Open(shapefileFolder + '\\' + feature + '.shp', 1)
                FeatureLayer = FeatureDataSource.GetLayer()
    
                # open final output layer
                finalDriver = ogr.GetDriverByName('ESRI Shapefile')
                finalDataSource = finalDriver.CreateDataSource(new_features_folder + '\\' + feature + '_' + format(additional_file_index) + '.shp')
                finalLayer = finalDataSource.CreateLayer(feature + '_' + format(additional_file_index) + '.shp', FeatureLayer.GetSpatialRef(), setGeomTo)
    
                # add fields from input feature to final feature
                # add field layer fields to the inLayer
                finalLayer.CreateFields(FeatureLayer.schema)
                
                del FeatureLayer
                del FeatureDataSource
                del FeatureDriver
    
                # open base table and add fields from it to the final layer
                tableDriver = ogr.GetDriverByName('CSV')
                tableDataSource = tableDriver.Open(ParentFolder + '\\' + BaseTable_name + '.csv', 0)
                tableLayer = tableDataSource.GetLayer()
    
                tableLayerDefn = tableLayer.GetLayerDefn()
                i = 0
                if OID == True:
                    i = 1
                for i in range(i, tableLayerDefn.GetFieldCount()):
                    new_field = tableLayerDefn.GetFieldDefn(i)
                    new_field_name = new_field.GetNameRef()
                    # to prevent duplicate columns, if the field name is the dissolve field, continue and don't add field.
                    if new_field_name == dissolve_field:
                        continue
                    finalLayer.CreateField(new_field)
    
                del tableLayer
                del tableDataSource
                del tableDriver
                print('Fields added to final feature')
    
                # close final Layer for now
                del finalLayer
                del finalDataSource
                del finalDriver
                
                # now append the layer to the second final shapefile
                AppendMemoryToShapefile(new_features_folder, feature + '_' + format(additional_file_index), dissolvedDataSource, dissolvedMemory)
            
        
        # if PointLayer is true, the shapefile was opened into memory, and therefore must be written out to disc to save edits
        if input_geometry_type == 1:
            MemoryToShapefile(dissolvedDataSource,dissolvedMemory,shapefileFolder,outFileName + '.shp')
        
        # delete unneeded memory layers
        del dissolvedMemory
        del dissolvedDataSource
        
        # add rarnum to used_rarnums list if it is not already in it
        if RARNUMval_str not in used_rarnums:
            used_rarnums.append(RARNUM_master)
    
    # empty the garbage collected to open up memory
    gc.collect()

print('ESI processing complete')