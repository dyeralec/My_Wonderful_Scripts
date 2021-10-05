import os
import rioxarray
import xarray


# main directory
root_dir = r'P:\01_DataOriginals\GOM\Elevation\NAVD88 Coastal Digital Elevation Model\Southern Louisiana'
out_dir = r'P:\01_DataOriginals\GOM\Elevation\NAVD88 Coastal Digital Elevation Model\Southern Louisiana'

# loop through all files in a directory
for subdir, dirs, files in os.walk(root_dir):
    if 'MACOSX' in subdir:
        continue
    else:
        print(subdir)
    for file in files:
        if file.endswith('.nc'):
            # check if output folder exists
            folder_name = os.path.basename(subdir)
            out_folder = os.path.join(out_dir, folder_name)
            if not os.path.exists(out_folder):
                os.makedirs(out_folder)
            full_path = os.path.join(subdir, file)
            print(full_path)

            # open netcdf
            xds = xarray.open_dataset(full_path)
            #xds = rioxarray.open_rasterio(full_path)

            print(xds)

            # set spatial dimensions
            xds.z.rio.set_spatial_dims(x_dim='x', y_dim='y', inplace=True) \
                .rio.write_crs("EPSG:4326", inplace=True) \
                .rio.to_raster(os.path.join(out_folder, file.replace('.nc', '.tif')))

            # set coordinate system
            #xds.z.rio.write_crs("EPSG:4326", inplace=True)

            # set sim order to as expected by riocarray i.e. (band, y, x)
            #xds.z.squeeze().transpose('lat', 'lon')

            # write netcdf to geotiff
            #xds.z.rio.to_raster(os.path.join(out_folder, file.replace('.nc', '.tif')))
