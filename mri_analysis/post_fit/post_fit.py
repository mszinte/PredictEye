"""
-----------------------------------------------------------------------------------------
post_fit.py
-----------------------------------------------------------------------------------------
Goal of the script:
Combine fit files, compute pRF derivatives
-----------------------------------------------------------------------------------------
Input(s):
sys.argv[1]: subject name (e.g. sub-01)
sys.argv[2]: pre-processing steps (fmriprep_dct or fmriprep_dct_pca)
sys.argv[3]: registration (e.g. T1w)
-----------------------------------------------------------------------------------------
Output(s):
Combined estimate nifti file and pRF derivative nifti file
-----------------------------------------------------------------------------------------
To run:
>> cd to function
>> python post_fit/post_fit.py [subject] [preproc] [reg]
-----------------------------------------------------------------------------------------
Exemple:
cd /home/mszinte/projects/PredictEye/mri_analysis/
python post_fit/post_fit.py sub-01 fmriprep_dct T1w
python post_fit/post_fit.py sub-01 fmriprep_dct_pca T1w
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
import os
import sys
import json
import glob
import numpy as np
import ipdb
import platform
opj = os.path.join
deb = ipdb.set_trace

# MRI imports
# -----------
import nibabel as nb
import cortex
from cortex.fmriprep import *
from nilearn import image

# Functions import
# ----------------
from utils import convert_fit_results

# Get inputs
# ----------
subject = sys.argv[1]
preproc = sys.argv[2]
regist_type = sys.argv[3]

# Define analysis parameters
# --------------------------
with open('settings.json') as f:
    json_s = f.read()
    analysis_info = json.loads(json_s)

# Define folder
# -------------
base_dir = analysis_info['base_dir']
deriv_dir = opj(base_dir,'pp_data',subject,'gauss','deriv')

# Check if all slices are present
# -------------------------------
# Original data to analyse
data_file = "{base_dir}/pp_data/{sub}/func/{sub}_task-pRF_space-{reg}_{preproc}_avg.nii.gz".format(
                        base_dir = base_dir, sub = subject, reg = regist_type, preproc = preproc)

img_data = nb.load(data_file)
data = img_data.get_fdata()
data_var = np.var(data,axis=3)
mask = data_var!=0.0
slices = np.arange(mask.shape[2])[mask.sum(axis=(0,1))>0]

est_files = []
miss_files_nb = 0
for slice_nb in slices:
    est_file = "{base_dir}/pp_data/{subject}/gauss/fit/{subject}_task-pRF_space-{reg}_{preproc}_avg_est_z_{slice_nb}.nii.gz".format(
                                base_dir = base_dir,
                                subject = subject,
                                reg = regist_type,
                                preproc = preproc,
                                slice_nb = slice_nb)

    if os.path.isfile(est_file):
        if os.path.getsize(est_file) == 0:
            num_miss_part += 1 
        else:
            est_files.append(est_file)
    else:
        miss_files_nb += 1

if miss_files_nb != 0:
    sys.exit('%i missing files, analysis stopped'%miss_files_nb)


# Combine and save estimates
# --------------------------
print('Combining est files')
ests = np.zeros((data.shape[0],data.shape[1],data.shape[2],6))
for est_file in est_files:
    img_est = nb.load(est_file)
    est = img_est.get_fdata()
    ests = ests + est

# Save estimates data
estfn = "{base_dir}/pp_data/{subject}/gauss/fit/{subject}_task-pRF_space-{reg}_{preproc}_avg_est.nii.gz".format(
                                base_dir = base_dir,
                                subject = subject,
                                reg = regist_type,
                                preproc = preproc)

new_img = nb.Nifti1Image(dataobj = ests, affine = img_data.affine, header = img_data.header)
new_img.to_filename(estfn)

# Compute derived measures from prfs
# ----------------------------------
print('extracting pRF derivatives')
outfn = "{base_dir}/pp_data/{subject}/gauss/fit/{subject}_task-pRF_space-{reg}_{preproc}_deriv.nii.gz".format(
                                base_dir = base_dir,
                                subject = subject,
                                reg = regist_type,
                                preproc = preproc)

convert_fit_results(est_fn = estfn,
                    output_fn = outfn,
                    stim_width = analysis_info['stim_width'],
                    stim_height = analysis_info['stim_height'])