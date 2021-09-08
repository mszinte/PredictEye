"""
-----------------------------------------------------------------------------------------
post_fit.py
-----------------------------------------------------------------------------------------
Goal of the script:
Combine fit files, compute pRF/pMF derivatives
-----------------------------------------------------------------------------------------
Input(s):
sys.argv[1]: subject name (e.g. sub-01)
sys.argv[2]: task (e.g. pRF, pMF)
sys.argv[3]: pre-processing steps (fmriprep_dct or fmriprep_dct_pca)
sys.argv[4]: registration (e.g. T1w)
sys.argv[5]: sub-task (e.g. 'sp', 'sac')
-----------------------------------------------------------------------------------------
Output(s):
Combined estimate nifti file and pRF derivative nifti file
-----------------------------------------------------------------------------------------
To run:
>> cd to function
>> python post_fit/post_fit.py [subject] [task] [preproc] [reg]
-----------------------------------------------------------------------------------------
Exemple:
cd /home/mszinte/projects/PredictEye/mri_analysis/
python post_fit/post_fit.py sub-01 pRF fmriprep_dct T1w
python post_fit/post_fit.py sub-01 pMF fmriprep_dct T1w sac
python post_fit/post_fit.py sub-01 pMF fmriprep_dct T1w sp
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
import platform
opj = os.path.join

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
task = sys.argv[2]
preproc = sys.argv[3]
regist_type = sys.argv[4]
if len(sys.argv) < 6: sub_task = ''
else: sub_task = sys.argv[5]

# Define analysis parameters
# --------------------------
with open('settings.json') as f:
    json_s = f.read()
    analysis_info = json.loads(json_s)

# Define folder
# -------------
base_dir = analysis_info['base_dir']

# Check if all slices are present
# -------------------------------
# Original data to analyse
data_file = "{base_dir}/pp_data/{sub}/func/{sub}_task-{task}_space-{reg}_{preproc}_avg.nii.gz".format(
                        base_dir=base_dir, 
                        sub=subject, 
                        task=task,
                        reg=regist_type, 
                        preproc=preproc)

img_data = nb.load(data_file)
data = img_data.get_fdata()
data_var = np.var(data,axis=3)
mask = data_var!=0.0
slices = np.arange(mask.shape[2])[mask.sum(axis=(0,1))>0]

est_files = []
miss_files_nb = 0
for slice_nb in slices:
    est_file = "{base_dir}/pp_data/{subject}/gauss/fit/{task}/{subject}_task-{task}{sub_task}_space-{reg}_{preproc}_avg_est_z_{slice_nb}.nii.gz".format(
                                base_dir=base_dir,
                                subject=subject,
                                task=task,
                                sub_task=sub_task,
                                reg=regist_type,
                                preproc=preproc,
                                slice_nb=slice_nb)

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
estfn = "{base_dir}/pp_data/{subject}/gauss/fit/{task}/{subject}_task-{task}{sub_task}_space-{reg}_{preproc}_avg_est.nii.gz".format(
                                base_dir=base_dir,
                                subject=subject,
                                task=task,
                                sub_task=sub_task,
                                reg=regist_type,
                                preproc=preproc)

new_img = nb.Nifti1Image(dataobj=ests, affine=img_data.affine, header=img_data.header)
new_img.to_filename(estfn)

# Compute derived measures from prfs
# ----------------------------------
print('extracting {} derivatives'.format(task))
outfn = "{base_dir}/pp_data/{subject}/gauss/fit/{task}/{subject}_task-{task}{sub_task}_space-{reg}_{preproc}_deriv.nii.gz".format(
                                base_dir=base_dir,
                                subject=subject,
                                task=task,
                                sub_task=sub_task,
                                reg=regist_type,
                                preproc=preproc)

convert_fit_results(est_fn= estfn,
                    output_fn=outfn,
                    task=task,
                    stim_width=analysis_info['stim_width'],
                    stim_height=analysis_info['stim_height'])
