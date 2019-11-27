import os
from osgeo import ogr
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
import fiona
import itertools

"""
def createDS(ds_name, ds_format, geom_type, srs, overwrite=False):
    drv = ogr.GetDriverByName(ds_format)
    if os.path.exists(ds_name) and overwrite is True:
        deleteDS(ds_name)
    ds = drv.CreateDataSource(ds_name)
    lyr_name = os.path.splitext(os.path.basename(ds_name))[0]
    lyr = ds.CreateLayer(lyr_name, srs, geom_type)
    return ds, lyr

def dissolve(input, output, multipoly=False, overwrite=False):
    driver = ogr.GetDriverByName("ESRI Shapefile")
    ds = driver.Open(input,0)
    lyr = ds.GetLayer()
    out_ds, out_lyr = createDS(output, ds.GetDriver().GetName(), lyr.GetGeomType(), lyr.GetSpatialRef(), overwrite)
    defn = out_lyr.GetLayerDefn()
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
            out_lyr.CreateFeature(feat)
    else:
        out_feat = ogr.Feature(defn)
        out_feat.SetGeometry(union)
        out_lyr.CreateFeature(out_feat)
        out_ds.Destroy()
    ds.Destroy()
    return True

input = r'R:\GEO Workspace\D_Users\81_Dyer\Environmental Sensitivity Index\BIRDS_filtered_separated_285000001.shp'
output = r'R:\GEO Workspace\D_Users\81_Dyer\Environmental Sensitivity Index\BIRDS_dissolved_285000001.shp'

dissolve(input, output, multipoly=False, overwrite=False)

"""

inGDB = r'R:\GEO Workspace\D_Users\81_Dyer\Environmental Sensitivity Index\ChesapeakeBay\ChesapeakeBay_2016_ESI.gdb'
outGDB = r'R:\GEO Workspace\D_Users\81_Dyer\Environmental Sensitivity Index\ChesapeakeBay\biofile_ExtraFeatures.gdb'

"""
with fiona.open(inGDB, layer='FISH') as ds_in:
	crs = ds_in.crs
	drv = ds_in.driver
	
	filtered = filter(lambda x: shape(x["geometry"]).is_valid, list(ds_in))
	
	e = sorted(ds_in, key=lambda k: k['properties']['RARNUM'])
	
	geoms = [shape(x["geometry"]) for x in e]
	dissolved = unary_union(geoms)

schema = {
	"geometry": "Polygon",
	"properties": {"id": "int"}
}

with fiona.open(outGDB, 'w', layer='fish_dissolved', driver=drv, schema=schema, crs=crs) as ds_dst:
	for i, g in enumerate(dissolved):
		ds_dst.write({"geometry": mapping(g), "properties": {"id": i}})
"""

# works only with shapefiles
with fiona.open(r'R:\GEO Workspace\D_Users\81_Dyer\Environmental Sensitivity Index\ChesapeakeBay\biofile_ExtraFeatures.gdb\BIRDS_filtered_dissolvePart_285000001.shp') as input:
    # preserve the schema of the original shapefile, including the crs
    meta = input.meta
    with fiona.open(r'R:\GEO Workspace\D_Users\81_Dyer\Environmental Sensitivity Index\ChesapeakeBay\biofile_ExtraFeatures.gdb\BENTHIC_dissolved_285000504', 'w', **meta) as output:
        # groupby clusters consecutive elements of an iterable which have the same key so you must first sort the features by the 'STATEFP' field
        e = sorted(input, key=lambda k: k['properties']['RARNUM'])
        # group by the 'STATEFP' field
        for key, group in itertools.groupby(e, key=lambda x:x['properties']['RARNUM']):
            properties, geom = zip(*[(feature['properties'],shape(feature['geometry'])) for feature in group])
            # write the feature, computing the unary_union of the elements in the group with the properties of the first element in the group
            output.write({'geometry': mapping(unary_union(geom)), 'properties': properties[0]})