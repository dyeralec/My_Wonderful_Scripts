"""
Relief Visualization Toolbox
Website - https://rvt-py.readthedocs.io/en/latest/
GitHub - https://github.com/EarthObservation/RVT_py
"""

import rvt.vis  # fro calculating visualizations
import rvt.default  # for loading/saving rasters
import numpy as np
import os

dem_path = r"C:\Users\dyera\Documents\Task 6\Geomorphology\Relief Visualization Toolbox\Outputs\Atlantic\AMBath10m_V2_Clip2.tif"
main_dir = r'C:\Users\dyera\Documents\Task 6\Geomorphology\Relief Visualization Toolbox\Outputs\Atlantic'

dict_dem = rvt.default.get_raster_arr(dem_path)
dem_arr = dict_dem["array"]  # numpy array of DEM
dem_resolution = dict_dem["resolution"]
dem_res_x = dem_resolution[0]  # resolution in X direction
dem_res_y = dem_resolution[1]  # resolution in Y direction
dem_no_data = dict_dem["no_data"]

# run multiple direction hillshade and save
nr_directions = 3  # Number of solar azimuth angles (clockwise from North) (number of directions, number of bands)
sun_elevation = 45  # Solar vertical angle (above the horizon) in degrees
multi_hillshade_arr = rvt.vis.multi_hillshade(dem=dem_arr, resolution_x=dem_res_x, resolution_y=dem_res_y,
                                              nr_directions=nr_directions, sun_elevation=sun_elevation, ve_factor=1,
                                              no_data=dem_no_data)
multi_hillshade_path = os.path.join(main_dir, os.path.basename(dem_path).replace('.tif', '_MultiHillshade.tif'))
rvt.default.save_raster(src_raster_path=dem_path, out_raster_path=multi_hillshade_path, out_raster_arr=multi_hillshade_arr,
                        no_data=np.nan, e_type=6)
print('Multi-Direction Hillshade complete')

# Run Simple Local Relief Model (SLRM)
radius_cell = 15  # radius to consider in pixels (not in meters)
slrm_arr = rvt.vis.slrm(dem=dem_arr, radius_cell=radius_cell, ve_factor=1, no_data=dem_no_data)
slrm_path = os.path.join(main_dir, os.path.basename(dem_path).replace('.tif', '_SLRM.tif'))
rvt.default.save_raster(src_raster_path=dem_path, out_raster_path=slrm_path, out_raster_arr=slrm_arr,
                        no_data=np.nan, e_type=6)
print('Simple Local Relief Model complete')

# # Run Multi-Scale Relief Model (MSRM)
# feature_min = 1  # minimum size of the feature you want to detect in meters
# feature_max = 5  # maximum size of the feature you want to detect in meters
# scaling_factor = 3  # scaling factor
# msrm_arr = rvt.vis.msrm(dem=dem_arr, resolution=dem_res_x, feature_min=feature_min, feature_max=feature_max,
#                         scaling_factor=scaling_factor, ve_factor=1, no_data=dem_no_data)
# msrm_path = os.path.join(main_dir, os.path.basename(dem_path).replace('.tif', '_MSRM.tif'))
# rvt.default.save_raster(src_raster_path=dem_path, out_raster_path=msrm_path, out_raster_arr=msrm_arr,
#                         no_data=np.nan, e_type=6)
# print('Multi-Scale Relief Model (MSRM) complete')

# Run Sky-view factor, Anisotropic sky-view factor, and Positive - openness
# svf, sky-view factor parameters which also applies to asvf and opns
svf_n_dir = 16  # number of directions
svf_r_max = 10  # max search radius in pixels
svf_noise = 0  # level of noise remove (0-don't remove, 1-low, 2-med, 3-high)
# asvf, anisotropic svf parameters
asvf_level = 1  # level of anisotropy (1-low, 2-high)
asvf_dir = 315  # dirction of anisotropy in degrees
dict_svf = rvt.vis.sky_view_factor(dem=dem_arr, resolution=dem_res_x, compute_svf=True, compute_asvf=True, compute_opns=True,
                                   svf_n_dir=svf_n_dir, svf_r_max=svf_r_max, svf_noise=svf_noise,
                                   asvf_level=asvf_level, asvf_dir=asvf_dir,
                                   no_data=dem_no_data)
svf_arr = dict_svf["svf"]  # sky-view factor
asvf_arr = dict_svf["asvf"]  # anisotropic sky-view factor
opns_arr = dict_svf["opns"]  # positive openness
svf_path = os.path.join(main_dir, os.path.basename(dem_path).replace('.tif', '_SVF.tif'))
rvt.default.save_raster(src_raster_path=dem_path, out_raster_path=svf_path, out_raster_arr=svf_arr,
                        no_data=np.nan, e_type=6)
asvf_path = os.path.join(main_dir, os.path.basename(dem_path).replace('.tif', '_ASVF.tif'))
rvt.default.save_raster(src_raster_path=dem_path, out_raster_path=asvf_path, out_raster_arr=asvf_arr,
                        no_data=np.nan, e_type=6)
opns_path = os.path.join(main_dir, os.path.basename(dem_path).replace('.tif', '_PosOpns.tif'))
rvt.default.save_raster(src_raster_path=dem_path, out_raster_path=opns_path, out_raster_arr=opns_arr,
                        no_data=np.nan, e_type=6)
print('Sky-view factor, Anisotropic sky-view factor, and Positive - openness complete')

# Run Negative Openness
# svf, sky-view factor parameters which also applies to asvf and opns
svf_n_dir = 16  # number of directions
svf_r_max = 10  # max search radius in pixels
svf_noise = 0  # level of noise remove (0-don't remove, 1-low, 2-med, 3-high)
dem_arr_neg_opns = dem_arr * -1  # dem * -1 for neg opns
# we don't need to calculate svf and asvf (compute_svf=False, compute_asvf=False)
dict_svf = rvt.vis.sky_view_factor(dem=dem_arr_neg_opns, resolution=dem_res_x, compute_svf=False, compute_asvf=False, compute_opns=True,
                                   svf_n_dir=svf_n_dir, svf_r_max=svf_r_max, svf_noise=svf_noise,
                                   no_data=dem_no_data)
neg_opns_arr = dict_svf["opns"]
neg_opns_path = os.path.join(main_dir, os.path.basename(dem_path).replace('.tif', '_NegOpns.tif'))
rvt.default.save_raster(src_raster_path=dem_path, out_raster_path=neg_opns_path, out_raster_arr=neg_opns_arr,
                        no_data=np.nan, e_type=6)
print('Negative Openness complete')

# Run Local Dominance
min_rad = 10  # minimum radial distance
max_rad = 20  # maximum radial distance
rad_inc = 1  # radial distance steps in pixels
angular_res = 15 # angular step for determination of number of angular directions
observer_height = 1.7  # height at which we observe the terrain
local_dom_arr = rvt.vis.local_dominance(dem=dem_arr, min_rad=min_rad, max_rad=max_rad, rad_inc=rad_inc, angular_res=angular_res,
                                       observer_height=observer_height, ve_factor=1,
                                       no_data=dem_no_data)
local_dom_path = os.path.join(main_dir, os.path.basename(dem_path).replace('.tif', '_LocalDom.tif'))
rvt.default.save_raster(src_raster_path=dem_path, out_raster_path=local_dom_path, out_raster_arr=local_dom_arr,
                        no_data=np.nan, e_type=6)
print('Local Dominance complete')

# Run Sky Illumination
sky_model = "uniform"  # could also be overcast
max_fine_radius = 100
num_directions = 32
compute_shadow = True
shadow_az = 315
shadow_el = 35
sky_illum_arr = rvt.vis.sky_illumination(dem=dem_arr, resolution=dem_res_x, sky_model=sky_model,
                                         max_fine_radius=max_fine_radius, num_directions=num_directions,
                                         shadow_az=shadow_az, shadow_el=shadow_el, ve_factor=1,
                                         no_data=dem_no_data)
sky_illum_path = os.path.join(main_dir, os.path.basename(dem_path).replace('.tif', '_SkyIllum.tif'))
rvt.default.save_raster(src_raster_path=dem_path, out_raster_path=sky_illum_path, out_raster_arr=sky_illum_arr,
                        no_data=np.nan, e_type=6)
print('Sky Illumination complete')

# Run Multi-Scale Topographic Position (MSTP)
local_scale=(1, 5, 1)  # min, max, step
meso_scale=(5, 50, 5)  # min, max, step
broad_scale=(50, 500, 50)  # min, max, step
lightness=1.2  # best results from 0.8 to 1.6
mstp_arr = rvt.vis.mstp(dem=dem_arr, local_scale=local_scale, meso_scale=meso_scale,
                        broad_scale=broad_scale, lightness=lightness, ve_factor=1, no_data=dem_no_data)
mstp_path = os.path.join(main_dir, os.path.basename(dem_path).replace('.tif', '_MSTP.tif'))
rvt.default.save_raster(src_raster_path=dem_path, out_raster_path=mstp_path, out_raster_arr=mstp_arr,
                        no_data=np.nan, e_type=1)  # e_type has to be 1 because visualization is 8-bit (0-255)
print('Multi-Scale Topographic Position complete')