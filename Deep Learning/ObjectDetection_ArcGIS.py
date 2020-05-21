"""
From: https://developers.arcgis.com/python/guide/object-detection/
"""

from arcgis.gis import GIS
from arcgis.raster.functions import extract_band
from arcgis.learn import export_training_data

gis = GIS("E:\Machine Learning\All Feature ")
# layers we need - The input to generate training samples and the imagery
well_pads = gis.content.get('ae6f1c62027c42b8a88c4cf5deb86bbf') # Well pads layer
well_pads