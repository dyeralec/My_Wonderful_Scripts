from osgeo import gdal
import numpy as np

input_grid = r"C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\ML Testing\SMART Tool Ready\Input Data\DistanceToHydrates_WGS84.tif"
output_grid = r"C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\ML Testing\SMART Tool Ready\Input Data\BlankGrid_WGS84.tif"

tif_dataset = gdal.Open(input_grid)
tif_band = tif_dataset.GetRasterBand(1)

(upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size) = tif_dataset.GetGeoTransform()
tif_transform = tif_dataset.GetGeoTransform()

proj = tif_dataset.GetProjectionRef()

tif_cols = tif_dataset.RasterXSize
tif_rows = tif_dataset.RasterYSize

xOrigin = tif_transform[0]
yOrigin = tif_transform[3]
pixelWidth = tif_transform[1]
pixelHeight = -tif_transform[5]

data = tif_band.ReadAsArray()

arr_empty = np.ones(data.shape)

# save to output GeoTIFF
driver = gdal.GetDriverByName('GTiff')
out = driver.Create(output_grid, data.shape[1], data.shape[0], 1, gdal.GDT_Byte)
out.SetGeoTransform(tif_transform)
out.SetProjection(proj)
bandOut = out.GetRasterBand(1)
outNoData = np.iinfo(gdal.GDT_Float32).max
bandOut.SetNoDataValue(outNoData)
bandOut.WriteArray(arr_empty)