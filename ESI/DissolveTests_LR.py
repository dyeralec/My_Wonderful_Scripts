'''Python 3 via Anaconda'''

from osgeo import ogr
import os

def Dissolve_polygons(gdb_path, output_file):
    '''Dissolve polygons'''

    multipoly = False
    overwrite = True

    # Deal with reading filegdb data
    indriver = ogr.GetDriverByName('OpenFileGDB')
    gdb  = indriver.Open(gdb_path,0)
    
    # list to store layers'names
    featsClassList = []
    
    # parsing layers by index
    for featsClass_idx in range(gdb.GetLayerCount()):
        lyr = gdb.GetLayerByName("BENTHIC_filtered_separated_285000504")

        outdriver = ogr.GetDriverByName('ESRI Shapefile')
        output_datasource = outdriver.CreateDataSource(output_file)   
    
        out_name = output_file.replace('.shp','')
        if '\\' in out_name:
            out_name = out_name.split('\\')[-1]
    
        output_lyr = output_datasource.CreateLayer(str(out_name.encode('utf-8')), lyr.GetSpatialRef(), lyr.GetGeomType())
    
        defn = output_lyr.GetLayerDefn()
    
        multi = ogr.Geometry(ogr.wkbMultiPolygon)
        for feat in lyr:
            if feat.geometry():
                feat.geometry().CloseRings() # this copies the first point to the end
                wkt = feat.geometry().ExportToWkt()
                multi.AddGeometryDirectly(ogr.CreateGeometryFromWkt(wkt))
        union = multi.UnionCascaded()
        if multipoly is False:
            for geom in union:
                poly = ogr.CreateGeometryFromWkb(geom.ExportToWkb())
                feat = ogr.Feature(defn)
                feat.SetGeometry(poly)
                output_lyr.CreateFeature(feat)
        else:
            output_feat = ogr.Feature(defn)
            output_feat.SetGeometry(union)
            output_lyr.CreateFeature(output_feat)
    
        gdb.Destroy()
        output_datasource.Destroy()
    
        return out_name

inGDB = r'P:\02_DataWorking\Atlantic\Environmental Sensitivity Index\Feature4Lucy.gdb'
outFile = os.path.join(r"E:\Temp\BENTHIC_filtered_separated_285000504.shp")

Dissolve_polygons(inGDB, outFile)
