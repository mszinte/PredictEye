"""
-----------------------------------------------------------------------------------------
fit_glm.py
-----------------------------------------------------------------------------------------
Goal of the script:
GLM alaysis of localisers tasks
-----------------------------------------------------------------------------------------
Input(s):
sys.argv[1]: base_dir (e.g. )
sys.argv[2]: subject name (e.g. sub-01)
sys.argv[3]: session (e.g. ses-01)
sys.argv[4]: task (e.g. PurLoc, PurVELoc)
sys.argv[5]: registration (e.g. T1w)
sys.argv[6]: run number containing localizer (e.g. run-1)
sys.argv[7]: pre-processing steps (fmriprep_dct or fmriprep_dct_pca)
-----------------------------------------------------------------------------------------
Output(s):
GLM output on a flatmap
-----------------------------------------------------------------------------------------
To run:
On mesocentre
>> cd to function
>> python glm/fit_glm.py [base_dir] [subject] [session] [task] [reg] [run] [preproc]
-----------------------------------------------------------------------------------------
Example:
cd ~/projects/PredictEye/mri_analysis/
python glm/fit_glm.py /scratch/mszinte/data/PredictEye sub-01 ses-01 SacLoc T1w run-1 fmriprep_dct
python glm/fit_glm.py /scratch/mszinte/data/PredictEye sub-01 ses-01 PurLoc T1w run-1 fmriprep_dct
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
import numpy as np
import pandas as pd
import scipy.stats as stats
import ipdb
deb = ipdb.set_trace

# MRI imports
# -----------
import nibabel as nb

# Functions import
# ----------------
import importlib.util
spec = importlib.util.spec_from_file_location("Utils", "./functions/utils.py") 
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)

# GLM imports
# -----------
from nilearn.glm.first_level import FirstLevelModel
from nilearn.glm import threshold_stats_img

# Get inputs
# ----------
base_dir =  sys.argv[1]
subject = sys.argv[2]
session = sys.argv[3]
task = sys.argv[4] 
space = sys.argv[5] 
run = sys.argv[6] 
preproc = sys.argv[7] 

# Define analysis parameters
# --------------------------
with open('settings.json') as f:
    json_s = f.read()
    analysis_info = json.loads(json_s)
    
# Define folder
# -------------
deriv_dir = "{}/pp_data/{}/glm/fit".format(base_dir,subject)

print('GLM analysis on {}...'.format(task))
task_name = [task[:3], 'Fix' ]
file_img = "{base_dir}/pp_data/{subject}/func/{subject}_task-{task}_space-{space}_{preproc}_avg.nii.gz".\
                format(base_dir=base_dir, subject=subject,task=task,space=space,preproc=preproc)
file_mask_img = '{base_dir}/deriv_data/fmriprep/fmriprep/{subject}/{session}/func/{subject}_{session}_task-{task}_run-1_space-{space}_desc-brain_mask.nii.gz'.\
                format(base_dir=base_dir, subject=subject, session=session, task=task, space=space)
glm_folder = '{base_dir}/pp_data/{subject}/glm/fit/'.format(base_dir=base_dir, subject=subject)

glm_alpha = analysis_info['glm_alpha']

try: os.makedirs(glm_folder)
except: pass

# create design table
design_file_run1 = '{base_dir}/bids_data/{subject}/{session}/func/{subject}_{session}_task-{task}_{run}_events.tsv'.\
                    format(base_dir=base_dir, subject=subject, session=session, task=task, run='run-01')
events_glm = utils.eventsMatrix(design_file_run1, task)

# first level GLM
mask_img = nb.load(file_mask_img)

fmri_glm = FirstLevelModel( t_r=analysis_info['TR'],
                            noise_model=analysis_info['glm_noise_model'],
                            standardize=False,
                            hrf_model='spm',
                            drift_model=None,
                            mask_img=mask_img)

fmri_glm = fmri_glm.fit(file_img, events_glm)
design_matrix = fmri_glm.design_matrices_[0]

# contrast
if task == 'SacLoc':
    exec('conditions = { task_name[1]: np.array([1., 0., 0.]), task_name[0]: np.array([0., 1., 0.])}')
    contrasts = {  'Sac-Fix':conditions[task_name[0]] - conditions[task_name[1]]}
elif task == 'PurLoc':
    exec('conditions = { task_name[1]: np.array([1., 0., 0.]), task_name[0]: np.array([0., 1., 0.])}')
    contrasts = {  'Pur-Fix':conditions[task_name[0]] - conditions[task_name[1]]}
else:
    conditions = {  'Fix': np.array([1., 0., 0., 0.]),
                    'Vis': np.array([0., 1., 0., 0.]),
                    'End': np.array([0., 0., 1., 0.])}
    contrasts = {   'Vis-End': conditions['Vis'] - conditions['End'],
                    'Vis-Fix': conditions['Vis'] - conditions['Fix'],
                    'End-Fix': conditions['End'] - conditions['Fix']}

# compute glm maps
for contrast in contrasts:
    
    output_fn = '{glm_folder}{subject}_task-{task}_space-{space}_{preproc}_glm-{contrast}.nii.gz'.\
            format(glm_folder=glm_folder, subject=subject,task=task,space=space,preproc=preproc,contrast=contrast)
    
    print('{}'.format(output_fn))
    
    # stats maps
    eff_map = fmri_glm.compute_contrast(contrasts[contrast],
                                        output_type='effect_size')
    
    z_map = fmri_glm.compute_contrast(contrasts[contrast],
                                        output_type='z_score')

    z_p_map = 2*(1 - stats.norm.cdf(abs(z_map.dataobj)))
        
    fdr_map, th = threshold_stats_img(z_map, alpha=glm_alpha, height_control='fdr')
    fdr_p_map = 2*(1 - stats.norm.cdf(abs(fdr_map.dataobj)))
    
    fdr_cluster10_map, th = threshold_stats_img(z_map, alpha=glm_alpha, height_control='fdr', cluster_threshold=10)
    fdr_cluster10_p_map = 2*(1 - stats.norm.cdf(abs(fdr_cluster10_map.dataobj)))
    
    fdr_cluster50_map, th = threshold_stats_img(z_map, alpha=glm_alpha, height_control='fdr', cluster_threshold=50)
    fdr_cluster50_p_map = 2*(1 - stats.norm.cdf(abs(fdr_cluster50_map.dataobj)))
                             
    fdr_cluster100_map, th = threshold_stats_img(z_map, alpha=glm_alpha, height_control='fdr', cluster_threshold=100)
    fdr_cluster100_p_map = 2*(1 - stats.norm.cdf(abs(fdr_cluster100_map.dataobj)))
                              
    # Save results
    img = nb.load(file_img)
    deriv = np.zeros((img.shape[0],img.shape[1],img.shape[2],11))*np.nan
    
    deriv[...,0]  = eff_map.dataobj
    deriv[...,1]  = z_map.dataobj
    deriv[...,2]  = z_p_map
    deriv[...,3]  = fdr_map.dataobj
    deriv[...,4]  = fdr_p_map
    deriv[...,5]  = fdr_cluster10_map.dataobj
    deriv[...,6]  = fdr_cluster10_p_map
    deriv[...,7]  = fdr_cluster50_map.dataobj
    deriv[...,8]  = fdr_cluster50_p_map
    deriv[...,9]  = fdr_cluster100_map.dataobj
    deriv[...,10] = fdr_cluster100_p_map
                              
    deriv = deriv.astype(np.float32)
    new_img = nb.Nifti1Image(dataobj = deriv, affine = img.affine, header = img.header)
    new_img.to_filename(output_fn)