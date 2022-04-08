import arcpy
from arcpy import management
import os

main_dir = r'C:\Users\dyera\Documents\Task 6\Data\Elevation\NCEI Bathymetry\Merged Rasters'

in_rasters = []
for file in os.listdir(main_dir):
    in_rasters.append(os.path.join(main_dir, file))

management.MosaicToNewRaster(input_rasters=in_rasters,
                                   output_location=main_dir,
                                   raster_dataset_name_with_extension='NCEI_Bathymetry_Merged_Max.tif',
                                   # {coordinate_system_for_the_raster},
                                   pixel_type='16_BIT_SIGNED',
                                   # {cellsize},
                                   number_of_bands=1,
                                   mosaic_method='MAXIMUM',
                                   # {mosaic_colormap_mode}
                             )