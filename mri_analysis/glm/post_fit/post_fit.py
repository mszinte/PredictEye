"""
-----------------------------------------------------------------------------------------
post_fit.py
-----------------------------------------------------------------------------------------
Goal of the script:
Compute CV R2 of GLM outputs
-----------------------------------------------------------------------------------------
Input(s):
sys.argv[1]: subject name (e.g. sub-01)
sys.argv[2]: registration (e.g. T1w)
sys.argv[3]: pre-processing steps (fmriprep_dct or fmriprep_dct_pca)
sys.argv[4]: cifti data mode (subc: subcortical, surf: surface)
-----------------------------------------------------------------------------------------
Output(s):
GLM derivative nifti file
-----------------------------------------------------------------------------------------
To run:
>> cd to function
>> python post_fit/post_fit.py [subject] [reg] [preproc] [cifti-mode]
-----------------------------------------------------------------------------------------
Exemple:
cd /home/mszinte/projects/PredictEye/mri_analysis/
python glm/post_fit/post_fit.py sub-01 T1w fmriprep_dct
python glm/post_fit/post_fit.py sub-01 fsLR_den-170k fmriprep_dct surf
python glm/post_fit/post_fit.py sub-01 fsLR_den-170k fmriprep_dct subc
python glm/post_fit/post_fit.py sub-01 T1w fmriprep_dct_pca
python glm/post_fit/post_fit.py sub-01 fsLR_den-170k fmriprep_dct_pca surf
python glm/post_fit/post_fit.py sub-01 fsLR_den-170k fmriprep_dct_pca subc
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

# MRI analysis imports
# --------------------
import nibabel as nb
from sklearn.metrics import r2_score

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
glm_tasks = analysis_info['glm_task_names']

# Create job and log output folders
for task in glm_tasks:
    if task == 'pMF':
        data_types_avg = ['avg-1','avg-2','avg-3','avg-4','avg-5','avg']
        data_types_loo = ['loo-1','loo-2','loo-3','loo-4','loo-5','avg']
    else: 
        data_types_avg = ['avg-1','avg-2','avg']
        data_types_loo = ['loo-1','loo-2','avg']

    for data_type_avg, data_type_loo in zip(data_types_avg,data_types_loo):

        if data_type_avg == 'avg':
            fit_fn = "{base_dir}/pp_data_new/{sub}/glm/fit/{sub}_task-{task}_space-{reg}_{preproc}_{data_type_avg}_glm-fit{file_ext}".format(
                            base_dir=base_dir, sub=subject, reg=regist_type, preproc=preproc, data_type_avg=data_type_avg, file_ext=file_ext, task=task)
            deriv_fn = "{base_dir}/pp_data_new/{sub}/glm/fit/{sub}_task-{task}_space-{reg}_{preproc}_{data_type_avg}_glm-deriv{file_ext}".format(
                            base_dir=base_dir, sub=subject, reg=regist_type, preproc=preproc, data_type_avg=data_type_avg, file_ext=file_ext, task=task)

            pred_fn = "{base_dir}/pp_data_new/{sub}/glm/fit/{sub}_task-{task}_space-{reg}_{preproc}_{data_type_avg}_glm-pred{file_ext}".format(
                            base_dir=base_dir, sub=subject, reg=regist_type, preproc=preproc, data_type_avg=data_type_avg, file_ext=file_ext, task=task)
            test_fn = "{base_dir}/pp_data_new/{sub}/func/{sub}_task-{task}_space-{reg}_{preproc}_{data_type_avg}{file_ext}".format(
                            base_dir=base_dir, sub=subject, reg=regist_type, preproc=preproc, data_type_avg=data_type_avg, file_ext=file_ext, task=task)

        else:
            fit_fn = "{base_dir}/pp_data_new/{sub}/glm/fit/{sub}_task-{task}_space-{reg}_{preproc}_{data_type_avg}_glm-fit{file_ext}".format(
                            base_dir=base_dir, sub=subject, reg=regist_type, preproc=preproc, data_type_avg=data_type_avg, file_ext=file_ext, task=task)
            deriv_fn = "{base_dir}/pp_data_new/{sub}/glm/fit/{sub}_task-{task}_space-{reg}_{preproc}_{data_type_avg}_glm-deriv{file_ext}".format(
                            base_dir=base_dir, sub=subject, reg=regist_type, preproc=preproc, data_type_avg=data_type_avg, file_ext=file_ext, task=task)
            pred_fn = "{base_dir}/pp_data_new/{sub}/glm/fit/{sub}_task-{task}_space-{reg}_{preproc}_{data_type_avg}_glm-pred{file_ext}".format(
                            base_dir=base_dir, sub=subject, reg=regist_type, preproc=preproc, data_type_avg=data_type_avg, file_ext=file_ext, task=task)
            test_fn = "{base_dir}/pp_data_new/{sub}/loo/{preproc}/{sub}_task-{task}_space-{reg}_{preproc}_{data_type_loo}{file_ext}".format(
                            base_dir=base_dir, sub=subject, reg=regist_type, preproc=preproc, data_type_loo=data_type_loo, file_ext=file_ext, task=task)

        if os.path.isfile(fit_fn) == False:
            sys.exit('Missing files, analysis stopped : %s'%fit_fn)
        else:
            print('Computing derivatives: %s'%deriv_fn)

        # Load data
        if regist_type == 'fsLR_den-170k': 
            fit_mat = np.load(fit_fn)
            pred_mat = np.load(pred_fn)
            test_mat = np.load(test_fn)
            if cifti_mode == 'surf': num_elmt = test_mat.shape[0]
            elif cifti_mode == 'subc': num_elmt = test_mat.shape[0]*test_mat.shape[1]*test_mat.shape[2]
        else: 
            fit_img = nb.load(fit_fn)
            fit_mat = fit_img.get_fdata()
            pred_img = nb.load(pred_fn)
            pred_mat = pred_img.get_fdata()
            test_img = nb.load(test_fn)
            test_mat = test_img.get_fdata()
            num_elmt = test_mat.shape[0]*test_mat.shape[1]*test_mat.shape[2]
        
        # Compute leave-one-out cross-validated r2
        flat_test_mat = test_mat.reshape((num_elmt,test_mat.shape[-1]))
        flat_pred_mat = pred_mat.reshape((num_elmt,pred_mat.shape[-1]))
        flat_pred_mat[np.isnan(flat_pred_mat)]=0

        r2_mat = r2_score(flat_test_mat.T, flat_pred_mat.T, multioutput='raw_values')
        r2_mat = np.power(r2_mat,2)

        if np.ndim(fit_mat) == 4:
            deriv_mat = np.zeros((fit_mat.shape[0],fit_mat.shape[1],fit_mat.shape[2],fit_mat.shape[-1]+1))*np.nan
        elif np.ndim(fit_mat) == 2:
            deriv_mat = np.zeros((fit_mat.shape[0],fit_mat.shape[-1]+1))*np.nan

        deriv_mat[...,0:fit_mat.shape[-1]] = fit_mat
        deriv_mat[...,fit_mat.shape[-1]] = r2_mat.reshape(deriv_mat.shape[:-1])
        
        # save data
        if regist_type == 'fsLR_den-170k':
            np.save(deriv_fn, deriv_mat)
        else: 
            deriv_img = nb.Nifti1Image(dataobj=deriv_mat, affine=fit_img.affine, header=fit_img.header)
            deriv_img.to_filename(deriv_fn)

        if data_type_avg != 'avg':
            if data_type_avg == 'avg-1':
                deriv_mat_avg = np.zeros(deriv_mat.shape)
            # compute average of loo derivatives
            deriv_mat_avg += deriv_mat/(len(data_types_avg)-1)

    # save average of derivatives
    deriv_loo_fn = "{base_dir}/pp_data_new/{sub}/glm/fit/{sub}_task-{task}_space-{reg}_{preproc}_avg-loo_glm-deriv{file_ext}".format(
                        base_dir=base_dir, sub=subject, reg=regist_type, preproc=preproc, data_type_avg=data_type_avg, file_ext=file_ext, task=task)

    print('Computing derivatives: %s'%deriv_loo_fn)
    if regist_type == 'fsLR_den-170k':
        np.save(deriv_loo_fn, deriv_mat_avg)
    else: 
        deriv_img = nb.Nifti1Image(dataobj=deriv_mat_avg, affine=fit_img.affine, header=fit_img.header)
        deriv_img.to_filename(deriv_loo_fn)