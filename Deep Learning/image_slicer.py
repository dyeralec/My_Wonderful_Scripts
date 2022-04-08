"""
File for image splitting functions
"""

import os, glob, numpy, argparse
from contextlib import contextmanager
import numpy as np

from osgeo import gdal


def MaskToTiff(image_path, mask):
    # set name for output file
    location = "./Results/"
    ext = "_Mask.tif"

    file = location + os.path.splitext(os.path.basename(image_path))[0] + ext

    # Depending on how the 'mask' comes in...
    bands = 1
    shp = mask.shape
    print("Mask Shape: {}".format(shp))
    if len(shp) == 3:
        bands, y_size, x_size = shp  # after Cody's update, bands will not exists or will be 1
    else:
        y_size, x_size = shp

    image = gdal.Open(image_path)

    driver = gdal.GetDriverByName("GTiff")
    out = driver.Create(file, x_size, y_size, bands, gdal.GDT_Byte)  # switched x_size and y_size placement in function
    out.SetGeoTransform(image.GetGeoTransform())
    out.SetProjection(image.GetProjectionRef())
    if bands != 1:
        for band in range(bands):
            out.GetRasterBand(band + 1).WriteArray(mask[band])
    else:
        out.GetRasterBand(1).WriteArray(mask)
    out.FlushCache()
    out = None
    image = None


def ImageToTiff(save_path, image):
    shp = image.shape
    if len(shp) == 3:
        bands, y_size, x_size = shp
    else:
        bands = 1
        y_size, x_size = shp

    driver = gdal.GetDriverByName("GTiff")
    out = driver.Create(save_path + '.tif', xsize=x_size, ysize=y_size, bands=bands, eType=gdal.GDT_Int32)

    for band in range(bands):
        if bands > 1:
            out.GetRasterBand(band + 1).WriteArray(image[band])
        else:
            out.GetRasterBand(band + 1).WriteArray(image)

    out.FlushCache()
    del out, image


def slice_to_folder(image_path, mask_path=None, output_path=r'./AugmentedImages', region=1000):
    """
    Read bounds from CSV, use them to slice image and mask into regions of interest

    Args:
        image_path: (str)Path to image for slicing
        mask_path: (str) Path to mask image matching x/y size of image from image_path (default: None)
        output_path: (str) Folder to output image/mask set to (default: ./AugmentedImages)
        region: (int) size for image to grab

    Returns: (list) of image names that have been saved to the folder.
    """
    print("- ImagePath:{}\n- MaskPath:{}\n- OutPath:{}\n- Region:{}".format(image_path, mask_path, output_path, region))
    image_ref = gdal.Open(image_path)
    image_tiff = image_ref.ReadAsArray()
    ## X/Y dims are flipped, actually comes in as z/y/x:
    _, Iymax, Ixmax = image_tiff.shape

    Ixmin, Iymin = 0, 0
    mask_tiff = None
    if mask_path:
        mask_tiff = gdal.Open(mask_path).ReadAsArray()
        maskymax, maskxmax = mask_tiff.shape
        if maskxmax != Ixmax or maskymax != Iymax:
            raise Exception("Dimensions of image do not match dimensions of mask (x/y)")

    if not os.path.exists(output_path):
        print("- Creating output folder")
        os.makedirs(output_path)

    x_list = [*range(Ixmin, Ixmax, region)]
    y_list = [*range(Iymin, Iymax, region)]

    img_count = 0

    for xmin in x_list:
        for ymin in y_list:
            image_xMin = xmin
            image_yMin = ymin

            # Size of known region
            image_xMax = xmin + region
            image_yMax = ymin + region

            # Verify regions do not surpass extent of the image, if they do, keep them square
            if image_xMax > Ixmax:
                image_xMax = Ixmax
                image_xMin = Ixmax - region
            if image_yMax > Iymax:
                image_yMax = Iymax
                image_yMin = Iymax - region


            # Access image and mask, again arrays are in z/y/x and y/x formats:
            image = numpy.copy(image_tiff[:, image_yMin:image_yMax, image_xMin:image_xMax])
            if mask_path:
                mask = numpy.copy(mask_tiff[image_yMin:image_yMax, image_xMin:image_xMax])

                # Skip this image if the mask doesnt contain class values
                if not numpy.any(mask):
                    continue

            ImageToTiff(output_path + "/" + str(img_count) + "_image", image)

            if mask_path:
                ImageToTiff(output_path + "/" + str(img_count)+'_mask', mask)
            img_count += 1

    # Close both files
    image_tiff = None
    mask_tiff = None

    return images_masks_from_folder_list(output_path, bool(mask_path))


def slice_to_folder_mk2(image_path, mask_path, output_path, size=1000, nodata=None):
    params = {}
    big_image = gdal.Open(image_path)
    big_mask = gdal.Open(mask_path)

    params['Z'], params['IyMax'], params['IxMax'] = \
        big_image.RasterCount, big_image.RasterYSize, big_image.RasterXSize
    params['IyMin'], params['IxMin'] = 0,0

    x_list = [*range(params['IxMin'], params['IxMax'], size)]
    y_list = [*range(params['IyMin'], params['IyMax'], size)]

    img_count = 0

    if not os.path.exists(output_path):
        print("- Creating output folder")
        os.makedirs(output_path)

    for xmin in x_list:
        for ymin in y_list:
            image_xMin = xmin
            image_yMin = ymin

            image_xMax = xmin + size
            image_yMax = ymin + size

            # Verify regions dont surpass image extents, keep it square if they do.
            if image_xMax > params['IxMax']:
                image_xMax = params['IxMax']
                image_xMin = image_xMax - size
            if image_yMax > params['IyMax']:
                image_yMax = params['IyMax']
                image_yMin = image_yMax - size

            sub_img_path = output_path+'/'+str(img_count)+"_image.tif"
            sub_mask_path = output_path+'/'+str(img_count)+"_mask.tif"

            # gdal.Translate will save out the dataset
            sub_image = gdal.Translate(sub_img_path, big_image,
                                       format="GTiff", srcWin=[image_xMin, image_yMin, size, size])
            sub_mask = gdal.Translate(sub_mask_path, big_mask,
                                      format="GTiff", srcWin=[image_xMin, image_yMin, size, size])

            # # edit the mask file to match no data location in the image
            # si_array = sub_image.ReadAsArray()
            # si_nodata = sub_image.GetRasterBand(1).GetNoDataValue()
            # sm_array = sub_mask.ReadAsArray()
            # sm_array = np.where(si_array[0] == si_nodata, nodata, sm_array)
            #
            # # Write the new array back out to the gdal dataset
            # sub_mask.GetRasterBand(1).WriteArray(sm_array)

            # Remove this image if the mask doesnt contain class values
            if not numpy.any(sub_mask.ReadAsArray()):
                # Close the dataset and remove
                sub_image = None
                sub_mask = None
                os.remove(sub_img_path)
                os.remove(sub_mask_path)

            # Remove this image if the mask only contains the no data value
            if numpy.unique(sub_mask.ReadAsArray()).tolist()[0] == nodata:
                # Close the dataset and remove
                sub_image = None
                sub_mask = None
                os.remove(sub_img_path)
                os.remove(sub_mask_path)

            # Remove this image if the mask only contains the no data value
            if 1 not in numpy.unique(sub_mask.ReadAsArray()).tolist():
                # Close the dataset and remove
                sub_image = None
                sub_mask = None
                os.remove(sub_img_path)
                os.remove(sub_mask_path)

            # elif nodata:
            #     # Add a no-data mask at index 0
            #     si_array = sub_image.ReadAsArray()
            #     sm_array = sub_mask.ReadAsArray()
            #
            #     # Where nodata values exist in the image, force the mask to 0, otherwise increase the index of non
            #     #  masked regions by 1 so index 0 does not overlap
            #     #TODO: When we do as Jeremy suggested and let unknown regions exist in the dataset we may need to remove
            #     # the +1 if we want nodata and unknown to be represented by the same index.
            #     sm_array = np.where(si_array != nodata, sm_array+1, sm_array)
            #
            #     # Write the new array back out to the gdal dataset
            #     sub_mask.WriteArray(sm_array)
            #
            #     # Close and save the new datasets
            #     sub_image = None
            #     sub_mask = None

            else:
                # Close and save the new datasets
                sub_image = None
                sub_mask = None

            img_count += 1



# Function to temporarily change directory to given path
@contextmanager
def cwd(path):
    oldpwd = os.getcwd()
    os.chdir(path)
    print(os.getcwd())
    try:
        yield
    finally:
        os.chdir(oldpwd)
        print(os.getcwd())


def images_masks_from_folder_list(folder:str, masks=False, extra_str=''):
    """
    Lists image and mask names from a given folder. Image names must contain _image and mask names must match
    image names with '_image' replaced by '_mask'. Files should all have the same extension.

    Args:
        folder: folder to look for image & optional mask pairs
        masks: bool using masks or not. If enabled, every image must have a mask paired to it.

    Returns: lists of [image_path], [mask_paths]. In format 'folder/imageName' & 'folder/maskName'
    """

    image_files = None

    # Move into folder
    with cwd(folder):
        # create generator for image filenames
        image_files = glob.glob("*_image*")

    i_list = []
    m_list = []

    for i_file in image_files:
        # pull index from before '_' to create mask name matching image
        i_part = i_file.partition("_image")
        m_file = i_part[0] + "_mask" + i_part[2]

        i_list.append(folder + '/' + i_file)
        if masks:
            m_list.append(folder + '/' + m_file)
    return i_list, m_list


def images_from_folder_generator(folder:str, type:str):
    """
    Generator pulls image names from given folder until no more images are found.
    Args:
        folder: str path to folder
        type: file type to search for
    Returns: path iterator for files matching 'type' in 'folder'
    """
    for filename in os.listdir(folder):
        if filename.endswith(type):
            file_path = folder + '/' + filename
            yield file_path

def images_masks_from_folder_generator(folder:str):
    """
    Generator pulls image and mask names from a given folder until no more are found.
    Args:
        folder: folder to look for image & mask pairs
    Returns: Generator for tuple pair of (image_path, mask_path). In format ('folder/imageName', 'folder/maskName')
    NOTE: call next(generator) to get first tuple.
    """

    # Move into folder
    with cwd(folder):
        # create generator for image filenames
        image_files = glob.iglob("*_image")

    for i_file in image_files:
        # pull index from before '_' to create mask name matching image
        m_file = i_file.partition("_")[0] + "_mask"

        i_path = folder + '/' + i_file
        m_path = folder + '/' + m_file
        yield i_path, m_path


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description="Process an image and cut it to smaller sizes")
    # parser.add_argument('imagepath', type=str, help='path to image file for slicing')
    # parser.add_argument('--size', type=int, default=1000,
    #                     help='size to slice images to (default: 1000)')
    # parser.add_argument('--maskpath', type=str,
    #                     help='path to mask file to slice alongside image file (optional)',
    #                     required=False)
    # parser.add_argument('--outpath', type=str,
    #                     help='folder path for output (default: ./SlicedImages)',
    #                     default=r'./SlicedImages')
    # parser.add_argument('--nodata', type=float, help='No Data value to mask')
    # args = parser.parse_args()
    # arg_dict = vars(args)
    arg_dict = {}
    arg_dict['imagepath'] = r"C:\Users\dyera\Documents\Task 6\Landslide Detection\Data\GOM\Confirmed Landslide Data\Area 1\Area1_Composite_BHASCPPr_16bitSigned.tif"
    arg_dict['maskpath'] = r"C:\Users\dyera\Documents\Task 6\Landslide Detection\Data\GOM\Confirmed Landslide Data\Area 1\Area1_LandslideMask_Major_Reclassify_8bit.tif"
    arg_dict['outpath'] = r"C:\Users\dyera\Documents\Task 6\Landslide Detection\Data\GOM\Confirmed Landslide Data\Area 1\Major landslide slices 8bit 1024x1024 Run2"
    arg_dict['size'] = 1024
    arg_dict['nodata'] = 3
    slice_to_folder_mk2(arg_dict['imagepath'], arg_dict['maskpath'], arg_dict['outpath'], arg_dict['size'], arg_dict['nodata'])
    print("Complete!")
