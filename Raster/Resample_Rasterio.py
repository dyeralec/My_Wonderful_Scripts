"""
Resampling function for rasters using the Rasterio python module

From https://rasterio.readthedocs.io/en/latest/topics/resampling.html

"""

from contextlib import contextmanager
import rasterio
from rasterio import Affine, MemoryFile
from rasterio.enums import Resampling
import os

# use context manager so DatasetReader and MemoryFile get cleaned up automatically
@contextmanager
def resample_raster(raster, out_path, scale):

    t = raster.transform

    # rescale the metadata
    transform = Affine(t.a / scale, t.b, t.c, t.d, t.e / scale, t.f)
    height = raster.height * scale
    width = raster.width * scale

    profile = raster.profile
    profile.update(transform=transform, driver='GTiff', height=height, width=width)

    data = raster.read( # Note changed order of indexes, arrays are band, row, col order not row, col, band
            out_shape=(raster.count, int(height), int(width)),
            resampling=Resampling.bilinear,
        )

    with rasterio.open(out_path,'w', **profile) as dst:
        dst.write(data)
        yield data

# set scaling factor. use 1/2 for downsampling
upscale_factor = 1/8

# main directory
root_dir = r'C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\ML Testing\Multi Scale Testing\Data\Landslide Masks 500ft Res'
out_dir = r'C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\ML Testing\Multi Scale Testing\Data\Landslide Masks 4000ft Res'

if not os.path.exists(out_dir):
    os.makedirs(out_dir)

# loop through all files in a directory
for subdir, dirs, files in os.walk(root_dir):
    for file in files:
        if file.endswith('.tif'):

            print('Resampling {}...'.format(file))

            in_path = os.path.join(root_dir, file)
            out_path = os.path.join(out_dir, file) # .replace('.tif', '_Resampled_250ft.tif')

            with rasterio.open(in_path) as src:
                with resample_raster(src, scale=upscale_factor, out_path=out_path) as resampled:
                    print('Orig dims: {}, New dims: {}'.format(src.shape, resampled.shape))