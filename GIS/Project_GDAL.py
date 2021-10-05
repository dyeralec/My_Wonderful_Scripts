from osgeo import gdal

inputPath = r"P:\01_DataOriginals\GOM\Elevation\HR_Bathy_BOEM\BOEM_Bathymetry_East_meters_tiff\BOEMbathyE_m.tif"
outputPath = r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Bathy\BOEM bathymetry derivatives\BOEMbathyE_m_GomAlbers.tif"
srs = r"P:\03_DataFinal\GOM\!SpatialReference\GomAlbers84.prj"

inputRaster = gdal.Open(inputPath)
gdal.Warp(outputPath, inputRaster, dstSRS=srs)