"""
-----------------------------------------------------------------------------------------
fit_second_level_glm.py
-----------------------------------------------------------------------------------------
Goal of the script:
GLM alaysis of localisers tasks
-----------------------------------------------------------------------------------------
Input(s):
sys.argv[1]: base_dir (e.g. )
sys.argv[2]: task (e.g. PurLoc, PurVELoc)
sys.argv[3]: registration (e.g. MNI152NLin2009cAsym)
sys.argv[4]: pre-processing steps (fmriprep_dct or fmriprep_dct_pca)
sys.argv[5]: contrast (Sac-Fix, Pur-Fix)
-----------------------------------------------------------------------------------------
Output(s):
GLM output on a flatmap
-----------------------------------------------------------------------------------------
To run:
On mesocentre
>> cd to function
>> python glm/fit_glm.py [base_dir] [task] [reg] [preproc] [contrast]
-----------------------------------------------------------------------------------------
Example:
cd ~/projects/PredictEye/mri_analysis/
python glm/fit_second_level_glm.py /scratch/mszinte/data/PredictEye SacLoc MNI152NLin2009cAsym fmriprep_dct Sac-Fix
python glm/fit_second_level_glm.py /scratch/mszinte/data/PredictEye PurLoc MNI152NLin2009cAsym fmriprep_dct Pur-Fix
python glm/fit_second_level_glm.py /scratch/mszinte/data/PredictEye SacVELoc MNI152NLin2009cAsym fmriprep_dct SacExo-Fix
python glm/fit_second_level_glm.py /scratch/mszinte/data/PredictEye SacVELoc MNI152NLin2009cAsym fmriprep_dct SacEndo-Fix
python glm/fit_second_level_glm.py /scratch/mszinte/data/PredictEye SacVELoc MNI152NLin2009cAsym fmriprep_dct SacExo-SacEndo
python glm/fit_second_level_glm.py /scratch/mszinte/data/PredictEye PurVELoc MNI152NLin2009cAsym fmriprep_dct PurExo-Fix
python glm/fit_second_level_glm.py /scratch/mszinte/data/PredictEye PurVELoc MNI152NLin2009cAsym fmriprep_dct PurEndo-Fix
python glm/fit_second_level_glm.py /scratch/mszinte/data/PredictEye PurVELoc MNI152NLin2009cAsym fmriprep_dct PurExo-PurEndo
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
import matplotlib.pyplot as plt
import scipy.stats as stats
from scipy.stats import norm

# MRI imports
# -----------
import nibabel as nb
import cortex
from cortex import mni

# GLM imports
# ----------------
from nilearn import image, plotting, surface
from nilearn.glm import threshold_stats_img
from nilearn.glm.second_level import make_second_level_design_matrix, SecondLevelModel, non_parametric_inference
from nilearn.plotting import plot_design_matrix, plot_stat_map, plot_anat, plot_img
from nilearn.image import get_data, math_img

mount_dir =  sys.argv[1]
task = sys.argv[2] 
space = sys.argv[3] 
preproc = sys.argv[4] 
contrast = sys.argv[5] 

subjects_label = ['sub-01_mni', 'sub-02_mni', 'sub-03_mni', 'sub-04_mni', 'sub-05_mni',
                  'sub-06_mni', 'sub-07_mni', 'sub-08_mni', 'sub-09_mni', 'sub-11_mni',
                  'sub-12_mni', 'sub-13_mni', 'sub-14_mni', 'sub-17_mni', 'sub-20_mni',
                  'sub-21_mni', 'sub-22_mni', 'sub-23_mni', 'sub-24_mni', 'sub-25_mni',
                 ]

# Define folder
# -------------
base_dir = "{}".format(mount_dir)
output_dir = '{base_dir}/pp_data/sub-00/glm/second_level/'.format(base_dir=base_dir)
try: os.makedirs(output_dir)
except: pass

output_fn = '{output_dir}/sub-00_task-{task}_space-{space}_{preproc}_glm-{contrast}.nii.gz'.format(output_dir=output_dir,task=task,space=space,preproc=preproc,contrast=contrast)

# Define analysis parameters
# --------------------------
with open('settings.json') as f:
    json_s = f.read()
    analysis_info = json.loads(json_s)

maps_names = {'z_map':1, 'fdr_map':3, 'fdr_c10_map':5, 'fdr_c50_map':7, 'fdr_c100_map':9}

# create design matrix
design_matrix = make_second_level_design_matrix(subjects_label, confounds=None)

print('Second Level GLM \nReading files')
# get data from each participant and put together in a list
# create second level model
imgs = {x:[] for x in maps_names.keys()}
for subject in subjects_label:
    glm_folder = '{base_dir}/pp_data/{subject}/glm/fit/'.format(base_dir=base_dir, subject=subject)
    
    effects_map_path = '{glm_folder}{subject}_task-{task}_space-{space}_{preproc}_glm-{contrast}.nii.gz'.\
            format(glm_folder=glm_folder, subject=subject[:-4],task=task,space=space,preproc=preproc,contrast=contrast)
    effects_map_tmp = nb.load(effects_map_path)
    
    for map_name in maps_names:
        idx = maps_names[map_name]
        effects_map = nb.Nifti1Image(dataobj = effects_map_tmp.dataobj[...,idx], affine = effects_map_tmp.affine, header = effects_map_tmp.header)
    
        imgs[map_name].append(effects_map)

model = SecondLevelModel(smoothing_fwhm=0.0)

# To save results
img = nb.load(effects_map_path)
deriv = np.zeros((img.shape[0],img.shape[1],img.shape[2],len(maps_names.keys())*5))*np.nan

print('Computing contrasts and saving data')
k=0
for map_name in maps_names:

    model.fit(imgs[map_name], design_matrix=design_matrix)
    outputs = model.compute_contrast(output_type='all')
    # ‘z_score’, ‘p_value’, ‘effect_size’
    
    n_voxels = np.sum(get_data(model.masker_.mask_img_))
    p_parametric = math_img("-np.log10(np.minimum(1, img * {}))"
                        .format(str(n_voxels)),
                        img=outputs['p_value'])
    
    p_permutation = non_parametric_inference(imgs[map_name],
                                             design_matrix = design_matrix,
                                             model_intercept = True, n_perm = 10000,
                                             two_sided_test = True,
                                             smoothing_fwhm = 0.0, n_jobs = 1)

    outputs['effect_size'].shape
    deriv[...,(k*5)+0]  = outputs['effect_size'].dataobj #eff_map.dataobj
    deriv[...,(k*5)+1]  = outputs['z_score'].dataobj #z_map.dataobj
    deriv[...,(k*5)+2]  = outputs['p_value'].dataobj #z_p_map
    deriv[...,(k*5)+3]  = p_parametric.dataobj # corrected p-map (parametric test)
    deriv[...,(k*5)+4]  = p_permutation.dataobj # corrected p-map (non-param test)
    
    k+=1
    
deriv = deriv.astype(np.float32)
new_img = nb.Nifti1Image(dataobj = deriv, affine = img.affine, header = img.header)
new_img.to_filename(output_fn)