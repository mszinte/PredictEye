"""
-----------------------------------------------------------------------------------------
prf_fit.py
-----------------------------------------------------------------------------------------
Goal of the script:
Create pRF estimates
-----------------------------------------------------------------------------------------
Input(s):
sys.argv[1]: cluster name (e.g. skylake)
sys.argv[2]: subject name
sys.argv[3]: start voxel index 
sys.argv[4]: end voxel index
sys.argv[5]: data file path
sys.argv[6]: z slice number
sys.argv[7]: main directory   
-----------------------------------------------------------------------------------------
Output(s):
Nifti image files with fitting parameters per vertex
-----------------------------------------------------------------------------------------
"""

# Stop warnings
# -------------
import warnings
warnings.filterwarnings("ignore")

# General imports
# ---------------
import sys
import multiprocessing
import numpy as np
import scipy.io
import platform
from math import *
import os
import glob
import datetime
import json
import ipdb
deb = ipdb.set_trace
opj = os.path.join

# MRI analysis imports
# --------------------
import popeye.utilities as utils
from popeye.visual_stimulus import VisualStimulus
import popeye.css_neg as css
import popeye.og_neg as og
import nibabel as nb

# Get inputs
# ----------
cluster_name = sys.argv[1]
fit_model = sys.argv[2]
subject = sys.argv[3]
data_file = sys.argv[4]
mask_file = sys.argv[5]
slice_nb = int(sys.argv[6])
opfn = sys.argv[7]
start_time = datetime.datetime.now()

# Define analysis parameters
with open('settings.json') as f:
    json_s = f.read()
    analysis_info = json.loads(json_s)

# Define cluster/server specific parameters
base_dir = analysis_info['base_dir']
if cluster_name  == 'skylake':
    nb_procs = 32
elif cluster_name  == 'westmere':
    base_dir = analysis_info['base_dir_westmere'] 
    nb_procs = 12
elif cluster_name == 'debug':
    nb_procs = 1
fit_steps = analysis_info["fit_steps"]

# Load data
data_img = nb.load(data_file)
data = data_img.get_fdata()
mask_img = nb.load(mask_file)
mask = mask_img.get_fdata()
slice_mask = mask[:, :, slice_nb].astype(bool)
num_vox = np.sum(slice_mask)
data_slice = data[:,:,slice_nb,:]
data_to_analyse = data_slice[slice_mask]

# determine voxel indices
y, x = np.meshgrid( np.arange(data.shape[1]),np.arange(data.shape[0]))
x_vox,y_vox = x[slice_mask],y[slice_mask]
vox_indices = [(xx,yy,slice_nb) for xx,yy in zip(x_vox,y_vox)]

# Create stimulus design (create in matlab - see others/make_visual_dm.m)
visual_dm_file = scipy.io.loadmat(opj(base_dir,'pp_data','visual_dm','vis_design.mat'))
visual_dm = visual_dm_file['stim']
stimulus = VisualStimulus(  stim_arr = visual_dm,
                            viewing_distance = analysis_info["screen_distance"],
                            screen_width = analysis_info["screen_width"],
                            scale_factor = 1/10.0,
                            tr_length = analysis_info["TR"],
                            dtype = np.short)

# Initialize model
if fit_model == 'gauss':
    fit_func = og.GaussianFit
    num_est = 6
    model_func = og.GaussianModel(  stimulus = stimulus,
                                    hrf_model = utils.spm_hrf)
elif fit_model == 'css':
    fit_func = css.CompressiveSpatialSummationFit
    num_est = 7
    model_func = css.CompressiveSpatialSummationModel(  stimulus = stimulus,
                                                        hrf_model = utils.spm_hrf)

model_func.hrf_delay = 0
print('models and stimulus loaded')

# Fit: define search grids (1.5 time stimulus radius)
x_grid = (-15, 15)
y_grid = (-15, 15)
sigma_grid = (0.05, 15)
n_grid =  (0.01, 1.5)

# Fit: define search bounds (3 time stimulus radius)
x_bound = (-30.0, 30.0)
y_bound = (-30.0, 30.0)
sigma_bound = (0.001, 30.0)
n_bound = (0.01, 3)
beta_bound = (-1e3, 1e3)
baseline_bound = (-1e3, 1e3)

if fit_model == 'gauss':
    fit_model_grids =  (x_grid, y_grid, sigma_grid)
    fit_model_bounds = (x_bound, y_bound, sigma_bound, beta_bound, baseline_bound)
elif fit_model == 'css':
    fit_model_grids =  (x_grid, y_grid, sigma_grid, n_grid)
    fit_model_bounds = (x_bound, y_bound, sigma_bound, n_bound, beta_bound, baseline_bound)


# Fit: main loop
# --------------
print("Slice {slice_nb} containing {num_vox} brain mask voxels".format(slice_nb = slice_nb, num_vox = num_vox))

# Define multiprocess bundle
bundle = utils.multiprocess_bundle( Fit = fit_func,
                                    model = model_func,
                                    data = data_to_analyse,
                                    grids = fit_model_grids, 
                                    bounds = fit_model_bounds, 
                                    indices = vox_indices, 
                                    auto_fit = True, 
                                    verbose = 1, 
                                    Ns = fit_steps)
# Run fitting
pool = multiprocessing.Pool(processes = nb_procs)
output = pool.map(  func = utils.parallel_fit, 
                    iterable = bundle)

# Re-arrange data
estimates_mat = np.zeros((data.shape[0],data.shape[1],data.shape[2],num_est))
for fit in output:
    estimates_mat[fit.voxel_index[0],fit.voxel_index[1],fit.voxel_index[2],:num_est-1] = fit.estimate
    estimates_mat[fit.voxel_index[0],fit.voxel_index[1],fit.voxel_index[2],num_est-1] = fit.rsquared
    
# Free up memory
pool.close()
pool.join()

# Save estimates data
new_img = nb.Nifti1Image(dataobj = estimates_mat, affine = data_img.affine, header = data_img.header)
new_img.to_filename(opfn)

# Print duration
end_time = datetime.datetime.now()
print("\nStart time:\t{start_time}\nEnd time:\t{end_time}\nDuration:\t{dur}".format(
                start_time = start_time,
                end_time = end_time,
                dur  = end_time - start_time))