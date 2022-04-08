import os, subprocess, sys
from osgeo import gdal, gdalconst
import numpy as np
import scipy.ndimage
import rasterio
from rasterio.fill import fillnodata


def exportGdalRaster(outputPath, array, x, y, geotransform, projection, nodata):

    """
    Exports an array and raster properties to file (.tif)

    Args:
        outputPath: path to export raster, ending in .tif extension
        array: numpy array
        x: dimension of raster in X direction
        y: dimension of raster in Y direction
        geotransform: geotransform property from a raster
        projection: gdal projection object from a raster or peojection file

    Returns: N/A

    """

    from osgeo import gdal
    import numpy as np

    # save to output GeoTIFF
    driver = gdal.GetDriverByName('GTiff')
    out = driver.Create(outputPath, x, y, 1, gdal.GDT_Int32)
    out.SetGeoTransform(geotransform)
    out.SetProjection(projection)
    bandOut = out.GetRasterBand(1)
    bandOut.SetNoDataValue(nodata)
    bandOut.WriteArray(array)

# main_dir = r'C:\Users\dyera\Documents\Task 6\Data\Elevation\NCEI Bathymetry\Merged Rasters'
main_dir = r'P:\01_DataOriginals\GOM\Elevation\NOAA NCEI NOS Hydrographic Survey Bathymetry\Mass Processing'
out_dir = r'P:\01_DataOriginals\GOM\Elevation\NOAA NCEI NOS Hydrographic Survey Bathymetry\Mass Processing\Single Band Elevation Rasters'
# gdal_merge_dir = r'C:\OSGeo4W64\apps\Python37\Scripts'

os.chdir(main_dir)

tiff_file_string = None
tiffs_paths = []
prj = r"P:\03_DataFinal\GOM\!SpatialReference\GomAlbers84.prj"

for subdir, dirs, files in os.walk(main_dir):
    for file in files:
        # if file.endswith('.tif') or (file.endswith('.tiff')):
        if file.endswith('H11816_VB_4m_MLLW_1of2.bag'):
            print(file)
            full_path = os.path.join(subdir, file)
            # gdal_info_command = f'gdalinfo "{full_path}" -oo MODE=LIST_SUPERGRIDS'
            # subprocess.call(gdal_info_command, shell=True)
            # r = gdal.Open(full_path, gdalconst.GA_ReadOnly)
            # arr = r.ReadAsArray()[0]
            # shape = arr.shape
            # sys.exit()
            # gt = r.GetGeoTransform()
            # xmin = gt[0]
            # ymin = gt[3] + gt[5] * r.RasterYSize
            out_path = os.path.join(main_dir, out_dir, file.replace('.bag', '.tif'))
            # exportGdalRaster(out_path, arr, shape[1], shape[0], r.GetGeoTransform(), r.GetProjection(), r.GetRasterBand(1).GetNoDataValue())
            tiffs_paths.append(full_path)
            bag_command = f'gdal_translate "{full_path}" "{out_path}" -b 1 -oo MODE=RESAMPLED_GRID -r bilinear' # -r bilinear -a_srs "{}" -srcwin 0 0 {66370/2} {int(74661/2)} -oo RESX=3048 -oo RESY=3048
            print(bag_command)
            subprocess.call(bag_command, shell=True)
            # sys.exit(1)
            # # check if the output tif exists, if not, it failed and need to split it by half
            if not os.path.exists(out_path):
                continue
            # # os.chdir(gdal_merge_dir)
            # # fill_command = f'python gdal_fillnodata.py "{out_path}" "{out_path.replace(".tif", "_Filled.tif")}"'
            # # subprocess.call(fill_command, shell=True)
            with rasterio.open(out_path) as src:
                profile = src.profile
                arr = src.read(1)
                arr_filled = fillnodata(arr, mask=src.read_masks(1), max_search_distance=50, smoothing_iterations=0)

            with rasterio.open(out_path.replace('.tif', '_Filled_50PixelSearch.tif'), 'w', **profile) as dest:
                dest.write_band(1, arr_filled)

# for subdir, dirs, files in os.walk(main_dir):
#     for file in files:
#         if 'NCEI_Bathymetry_Merged' in file:
#             continue
#         if file.endswith('.tif') and ('1m' in file):
#             print(file)
#             full_path = os.path.join(subdir, file)
#             tiffs_paths.append(full_path)
#             if tiff_file_string is None:
#                 tiff_file_string = '"' + full_path + '"'
#             else:
#                 tiff_file_string = tiff_file_string + ' "' + full_path + '"'

# for r in tiffs_paths:
#     name = os.path.basename(r)
#     print(name)
#     raster = gdal.Open(r)
#     arr = raster.ReadAsArray()
#     band = raster.GetRasterBand(1)
#     nodata = band.GetNoDataValue()
#     print("band count: " + str(raster.RasterCount))
#     # resample raster from 0.5 meters to 30.48 m (100 ft) using bilinear interpolation
#     arr_resampled = scipy.ndimage.zoom(arr[0], (1/60.96), order=1)
#     outputPath = os.path.join(out_dir, name.replace('.bag', '.tif'))
#     exportGdalRaster(outputPath, arr_resampled, arr_resampled.shape[1], arr_resampled.shape[0], raster.GetGeoTransform(), raster.GetProjection(), nodata)

# # set up output tif name and directory
# os.chdir(gdal_merge_dir)
# out_file = os.path.join(out_dir, 'NCEI_Bathymetry_Merged_1m.tif')
# # run gdal merge function
# sys_command = 'python gdal_bag_to_tiff.py -o "{}" -of gtiff -co BIGTIFF=YES {}'.format(out_file, tiff_file_string)
# subprocess.call(sys_command, shell=True)
# print(os.popen(sys_command).read())