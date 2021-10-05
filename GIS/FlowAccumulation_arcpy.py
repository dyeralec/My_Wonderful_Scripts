import arcpy
from arcpy import env
from arcpy.sa import *

inputRaster = r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Arc Image Analyst\boem_composite-gdb\BOEMbathy_CompositeMosaic_BHASCPPr_16bitSigned.tif"

env.workspace = r"P:\05_AnalysisProjects_Working\Offshore_geohaz\Arc Image Analyst\FlowAnalysis.gdb"

# Set local variables
inSurfaceRaster = inputRaster
outDropRaster = "dropraster"

# Execute FlowDirection
outFlowDirection = FlowDirection(inSurfaceRaster, "NORMAL", outDropRaster, "MFD")

# Save the output
outFlowDirection.save("FlowDir")

print('Flow Direction tool compelete.')

# Set local variables
inFlowDirectionRaster = outFlowDirection

# Execute FlowDirection
outSink = Sink(inFlowDirectionRaster)

# Save the output
outSink.save("Sink")

print('Sink tool compelete.')

# Set local variables
inSurfaceRaster = outSink
#zLimit = 3.28

# Execute FlowDirection
outFill = Fill(inSurfaceRaster)

# Save the output
outFill.save("Fill")

print('Fill tool compelete.')

# # Set local variables
# inFlowDirection = outFlowDirection
# inPourPointData = "pourpoint"
# inPourPointField = "VALUE"
#
# # Execute Watershed
# outWatershed = Watershed(inFlowDirection, inPourPointData, inPourPointField)
#
# # Save the output
# outWatershed.save("C:/sapyexamples/output/outwtrshd02.tif")

# Set local variables
inFlowDirRaster = outFlowDirection
inWeightRaster = ""
dataType = "FLOAT"
flow_direction_type = 'MFD'

# Execute FlowDirection
outFlowAccumulation = FlowAccumulation(inFlowDirRaster, inWeightRaster, dataType, flow_direction_type)

# Save the output
outFlowAccumulation.save("FlowAccumulation")

print('Flow Accumulation tool compelete.')