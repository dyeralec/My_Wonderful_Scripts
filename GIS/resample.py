import arcpy
import os

def resample_raster(inputRaster, outputRaster, xres, yres, resample_alg='near'):

    ds = gdal.Warp(outputRaster, inputRaster, xRes=xres, yRes=yres, resampleAlg=resample_alg)
    ds = None


if __name__ == '__main__':

    layers = [
        r"C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\Data Prep\Elevation & Derivatives\BOEM_Bathymetry\BOEM_Bathymetry_m_Elevation.tif",
        r"C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\Data Prep\Elevation & Derivatives\BOEM_Bathymetry\BOEM_Bathymetry_m_Aspect.tif",
        r"C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\Data Prep\Elevation & Derivatives\BOEM_Bathymetry\BOEM_Bathymetry_m_Slope.tif",
        r"C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\Data Prep\Elevation & Derivatives\BOEM_Bathymetry\BOEM_Bathymetry_m_Curvature.tif",
        r"C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\Data Prep\Elevation & Derivatives\BOEM_Bathymetry\BOEM_Bathymetry_m_PlanCurvature.tif",
        r"C:\Users\dyera\Documents\Task 6\Landslide Susceptibility Mapping\Data Prep\Elevation & Derivatives\BOEM_Bathymetry\BOEM_Bathymetry_m_ProfileCurvature.tif",

    ]

    sizes = [100, 250, 500, 1000, 2000]

    for s in sizes:

        for l in layers:

            outputRaster = l.replace('.tif', '_{}m.tif'.format(str(s)))

            arcpy.management.Resample(l, outputRaster, cell_size=s, resampling_type='BILINEAR')