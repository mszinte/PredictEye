"""
-----------------------------------------------------------------------------------------
prf_fit.py
-----------------------------------------------------------------------------------------
Goal of the script:
Create pRF estimates
-----------------------------------------------------------------------------------------
Input(s):
sys.argv[1]: subject name
sys.argv[2]: pre-processing steps (fmriprep_dct or fmriprep_dct_pca)
sys.argv[3]: slice number
sys.argv[4]: registration type
sys.argv[5]: output filename
-----------------------------------------------------------------------------------------
Output(s):
Nifti image files with fit parameters for a z slice
-----------------------------------------------------------------------------------------
To run:
>> cd to function directory
>> python fit/prf_fit.py [subject] [preproc] [slice_nb] [registration] [output file]
-----------------------------------------------------------------------------------------
Exemple:
cd /home/mszinte/projects/PredictEye/mri_analysis/
python fit/prf_fit.py sub-01 fmriprep_dct 10 T1w /path_to/sub-01....nii.gz
-----------------------------------------------------------------------------------------
Written by Martin Szinte (martin.szinte@gmail.com)
-----------------------------------------------------------------------------------------
"""

# Stop warnings
# -------------
import warnings
warnings.filterwarnings("ignore")

# General imports
# ---------------
import sys
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
from prfpy.rf import *
from prfpy.timecourse import *
from prfpy.stimulus import PRFStimulus2D
from prfpy.model import Iso2DGaussianModel
from prfpy.fit import Iso2DGaussianFitter
import nibabel as nb

# Get inputs
# ----------
subject = sys.argv[1]
preproc = sys.argv[2]
slice_nb = int(sys.argv[3])
regist_type = sys.argv[4]
opfn = sys.argv[5]
start_time = datetime.datetime.now()

# Define analysis parameters
with open('settings.json') as f:
    json_s = f.read()
    analysis_info = json.loads(json_s)

# Define cluster/server specific parameters
base_dir = analysis_info['base_dir']
nb_procs = 32

# Load data
data_file = "{base_dir}/pp_data/{sub}/func/{sub}_task-pRF_space-{reg}_{preproc}_avg.nii.gz".format(
                        base_dir = base_dir, sub = subject, reg = regist_type, preproc = preproc)
data_img = nb.load(data_file)
data = data_img.get_fdata()
data_var = np.var(data,axis=3)
mask = data_var!=0.0

slice_mask = mask[:,:,slice_nb].astype(bool)
num_vox = np.sum(slice_mask)
data_slice = data[:,:,slice_nb,:]
data_to_analyse = data_slice[slice_mask]

# determine voxel indices
y, x = np.meshgrid( np.arange(data.shape[1]),np.arange(data.shape[0]))
x_vox,y_vox = x[slice_mask],y[slice_mask]
vox_indices = [(xx,yy,slice_nb) for xx,yy in zip(x_vox,y_vox)]

# Create stimulus design (create in matlab - see others/make_visual_dm.m)
visual_dm_file = scipy.io.loadmat(opj(base_dir,'pp_data','visual_dm',"pRF_vd.mat"))
visual_dm = visual_dm_file['stim'].transpose([1,0,2])


stimulus = PRFStimulus2D(screen_width_cm = analysis_info['screen_width'],
                         screen_height_cm = analysis_info['screen_height'],
                         screen_distance_cm = analysis_info['screen_distance'],
                         design_matrix = visual_dm,
                         TR = analysis_info['TR'])

# define model and parameters
gauss_model = Iso2DGaussianModel(stimulus = stimulus)
grid_nr = analysis_info['grid_nr']
max_ecc_size = analysis_info['max_ecc_size']
sizes = max_ecc_size * np.linspace(0.25,1,grid_nr)**2
eccs = max_ecc_size * np.linspace(0.1,1,grid_nr)**2
polars = np.linspace(0, 2*np.pi, grid_nr)


print("Slice {slice_nb} containing {num_vox} brain mask voxels".format(slice_nb = slice_nb, num_vox = num_vox))

# grid fit
print("Grid fit")
gauss_fitter = Iso2DGaussianFitter(data = data_to_analyse, model = gauss_model, n_jobs = nb_procs)
gauss_fitter.grid_fit(ecc_grid = eccs, polar_grid = polars, size_grid = sizes, pos_prfs_only = True)

# iterative fit
print("Iterative fit")
gauss_fitter.iterative_fit(rsq_threshold = 0.0001, verbose = False)
estimates_fit = gauss_fitter.iterative_search_params

# Re-arrange data
estimates_mat = np.zeros((data.shape[0],data.shape[1],data.shape[2],6))
for est,vox in enumerate(vox_indices):
    estimates_mat[vox] = estimates_fit[est]

# Save estimates data
new_img = nb.Nifti1Image(dataobj = estimates_mat, affine = data_img.affine, header = data_img.header)
new_img.to_filename(opfn)

# Print duration
end_time = datetime.datetime.now()
print("\nStart time:\t{start_time}\nEnd time:\t{end_time}\nDuration:\t{dur}".format(
                start_time = start_time,
                end_time = end_time,
                dur  = end_time - start_time))