dissolve_polygons(inputdata shapefile..., otupout dataset, field to be dissolved by)

def dissolve_polygons(inFeat,outFeat,dissolve_field):
        with fiona.open(inFeat) as input:
                # preserve the schema of the original shapefile, including the crs
                meta = input.meta
                with fiona.open(outFeat, 'w', **meta) as output:
                        # groupby clusters consecutive elements of an iterable which have the same key so you must first sort the features by the 'STATEFP' field
                        e = sorted(input, key=lambda k: k['properties'][dissolve_field])
                        # group by the 'STATEFP' field 
                        for key, group in itertools.groupby(e, key=lambda x:x['properties'][dissolve_field]):
                                properties, geom = zip(*[(feature['properties'],shape(feature['geometry'])) for feature in group])
                                # write the feature, computing the unary_union of the elements in the group with the properties of the first element in the group
                                output.write({'geometry': mapping(unary_union(geom)), 'properties': properties[0]})
        input.close()
        output.close()