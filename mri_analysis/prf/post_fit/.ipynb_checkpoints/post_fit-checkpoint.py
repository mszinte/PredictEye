"""
-----------------------------------------------------------------------------------------
post_fit.py
-----------------------------------------------------------------------------------------
Goal of the script:
Combine fit files, compute pRF derivatives, compute CV R2
-----------------------------------------------------------------------------------------
Input(s):
sys.argv[1]: subject name (e.g. sub-01)
sys.argv[3]: pre-processing steps (fmriprep_dct or fmriprep_dct_pca)
sys.argv[4]: registration (e.g. T1w)
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
python prf/post_fit/post_fit.py sub-01 T1w fmriprep_dct
python prf/post_fit/post_fit.py sub-01 fsLR_den-170k fmriprep_dct surf
python prf/post_fit/post_fit.py sub-01 fsLR_den-170k fmriprep_dct subc
python prf/post_fit/post_fit.py sub-01 T1w fmriprep_dct_pca
python prf/post_fit/post_fit.py sub-01 fsLR_den-170k fmriprep_dct_pca surf
python prf/post_fit/post_fit.py sub-01 fsLR_den-170k fmriprep_dct_pca subc
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
deb = ipdb.set_trace

# Functions import
# ----------------
from utils.utils import prf_fit2deriv

# MRI analysis imports
# --------------------
import nibabel as nb
from sklearn.metrics import r2_score
import itertools as it

# Define analysis parameters
# --------------------------
with open('settings.json') as f:
    json_s = f.read()
    analysis_info = json.loads(json_s)

# Settings
# --------
# Inputs
subject = sys.argv[1]
regist_type = sys.argv[2]
preproc = sys.argv[3]
if regist_type == 'fsLR_den-170k':
    cifti_mode= sys.argv[4]
    if cifti_mode == 'surf': file_ext,sh_end = '.npy','_surface'
    elif cifti_mode == 'subc': file_ext,sh_end = '_subc.npy','_subcortical'
else:
    file_ext = '.nii.gz'
    sh_end = ''

base_dir = analysis_info['base_dir']
stim_width = analysis_info['stim_width']
stim_height = analysis_info['stim_height']

# Create job and log output folders
data_types = ['run-1','run-2','run-3','run-4','run-5','avg']
for data_type in data_types:
    if data_type == 'avg':
        fit_fn = "{base_dir}/pp_data_new/{sub}/prf/fit/{sub}_task-pRF_space-{reg}_{preproc}_prf-fit{file_ext}".format(
                        base_dir=base_dir, sub=subject, reg=regist_type, preproc=preproc, data_type=data_type, file_ext=file_ext)
        deriv_fn = "{base_dir}/pp_data_new/{sub}/prf/fit/{sub}_task-pRF_space-{reg}_{preproc}_prf-deriv{file_ext}".format(
                        base_dir=base_dir, sub=subject, reg=regist_type, preproc=preproc, data_type=data_type, file_ext=file_ext)
    else:
        fit_fn = "{base_dir}/pp_data_new/{sub}/prf/fit/{sub}_task-pRF_{data_type}_space-{reg}_{preproc}_prf-fit{file_ext}".format(
                        base_dir=base_dir, sub=subject, reg=regist_type, preproc=preproc, data_type=data_type, file_ext=file_ext)
        deriv_fn = "{base_dir}/pp_data_new/{sub}/prf/fit/{sub}_task-pRF_{data_type}_space-{reg}_{preproc}_prf-deriv{file_ext}".format(
                        base_dir=base_dir, sub=subject, reg=regist_type, preproc=preproc, data_type=data_type, file_ext=file_ext)
    
    if os.path.isfile(fit_fn) == False:
        sys.exit('Missing files, analysis stopped : %s'%fit_fn)
    else:
        print('Computing derivatives: %s'%deriv_fn)
    
    
    # Load data
    if regist_type == 'fsLR_den-170k': 
        input_mat = np.load(fit_fn)
    else: 
        input_img = nb.load(fit_fn)
        input_mat = input_img.get_fdata()
    
    deriv_mat = prf_fit2deriv(input_mat=input_mat, stim_width=stim_width, stim_height=stim_height)

    # save data
    if regist_type == 'fsLR_den-170k':
        np.save(deriv_fn, deriv_mat)
    else: 
        deriv_img = nb.Nifti1Image(dataobj=deriv_mat, affine=input_img.affine, header=input_img.header)
        deriv_img.to_filename(deriv_fn)
        


combi = list(it.combinations([1,2,3,4,5], 2))
for i,(train_idx, test_idx) in enumerate(combi):
    mat_test = 
    mat_pred = 
    r2_score(, preds[test_idx, :], multioutput='raw_values')