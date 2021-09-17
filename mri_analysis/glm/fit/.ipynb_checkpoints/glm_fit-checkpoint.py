"""
-----------------------------------------------------------------------------------------
glm_fit.py
-----------------------------------------------------------------------------------------
Goal of the script:
GLM fit code
-----------------------------------------------------------------------------------------
Input(s):
sys.argv[1]: subject name
sys.argv[2]: registration type
sys.argv[3]: pre-processing steps (fmriprep_dct or fmriprep_dct_pca)
sys.argv[4]: recorded time series filename and path
sys.argv[5]: glm derivatives filename and path
sys.argv[5]: glm predicted time series filename and path
-----------------------------------------------------------------------------------------
Output(s):
Nifti image files with fit parameters for a z slice
-----------------------------------------------------------------------------------------
To run:
>> cd to function directory
>> python glm/fit/glm_fit.py [subject] [registration] [preproc]
                             [intput file] [deriv file] [predic file]
-----------------------------------------------------------------------------------------
Exemple:
cd /home/mszinte/projects/PredictEye/mri_analysis/
python glm/fit/glm_fit.py sub-01 T1w fmriprep_dct /path_to... /path_to... /path_to...
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
import sys, os
import numpy as np
import scipy.io
import glob
import datetime
import json
import pandas as pd
import scipy.stats as stats
import ipdb
deb = ipdb.set_trace

# MRI analysis imports
# --------------------
from nilearn.glm.first_level import FirstLevelModel, make_first_level_design_matrix, run_glm
from nilearn.glm import compute_contrast
from nilearn.glm.thresholding import fdr_threshold


from nilearn.glm import threshold_stats_img
import nibabel as nb

# Get inputs
# ----------
start_time = datetime.datetime.now()
subject = sys.argv[1]
task = sys.argv[2]
regist_type = sys.argv[3]
preproc = sys.argv[4]
input_fn = sys.argv[5]
deriv_fn = sys.argv[6]
pred_fn = sys.argv[7]

# Define analysis parameters
with open('settings.json') as f:
    json_s = f.read()
    analysis_info = json.loads(json_s)

# Define specific parameters
base_dir = analysis_info['base_dir']
glm_alpha = analysis_info['glm_alpha']
if task == 'SacLoc':
    cond1_label, cond2_label = ['Sac'], ['Fix']
    comp_num = 1
elif task == 'PurLoc':
    cond1_label, cond2_label = ['Pur'], ['Fix']
    comp_num = 1
elif task == 'SacVELoc':
    cond1_label, cond2_label = ['SacExo','SacExo','SacEndo'], ['SacEndo','Fix','Fix']
    comp_num = 3
elif task == 'PurVELoc':
    cond1_label, cond2_label = ['PurExo','PurExo','PurEndo'], ['PurEndo','Fix','Fix']
    comp_num = 3
elif task == 'pMF':
    cond1_label, cond2_label = ['PurSac'], ['Fix']
    comp_num = 1

# Load events matrix
dm_fn = '{base_dir}/pp_data_new/glm_dm/{task}_dm.tsv'.format(base_dir=base_dir, task=task)
events_glm = pd.read_csv(dm_fn, sep = '\t')

# Load data
if regist_type == 'fsLR_den-170k': 
    data = np.load(input_fn)
else: 
    data_img = nb.load(input_fn)
    data = data_img.get_fdata()
data_var = np.var(data,axis=-1)
mask = data_var!=0.0    
num_vox = mask[...].sum()
data_to_analyse = data[mask]
data_where = np.where(data_var!=0.0)
data_indices = []
if data.ndim == 4:
    for x,y,z in zip(data_where[0],data_where[1],data_where[2]):
        data_indices.append((x,y,z))
    deriv_mat = np.zeros((data.shape[0],data.shape[1],data.shape[2],4*comp_num))
elif data.ndim == 2:
    for gray_ordinate in data_where[0]:
        data_indices.append((gray_ordinate))
    deriv_mat = np.zeros((data.shape[0],4*comp_num))
pred_mat = np.zeros(data.shape)

# run GLM
frame_times = analysis_info['TR']*(np.arange(data_to_analyse.shape[1]))
design_matrix = make_first_level_design_matrix(frame_times=frame_times, events=events_glm, hrf_model='spm', drift_model=None,)
labels, estimates = run_glm(data_to_analyse.T, design_matrix.values, noise_model=analysis_info['glm_noise_model'])

# get rsquare and predicted time series
data_to_analyse_pred = np.zeros(data_to_analyse.T.shape)
data_to_analyse_rsquare = np.zeros_like(labels)
for lab in np.unique(labels):
    data_to_analyse_pred[..., labels == lab] = getattr(estimates[lab], 'predicted')
    data_to_analyse_rsquare[..., labels == lab] = getattr(estimates[lab], 'r_square')
    
data_pred = data_to_analyse_pred.T
data_rsquare = data_to_analyse_rsquare.T

for contrast_num, contrast in enumerate(zip(cond1_label,cond2_label)):
    
    contrast_values = (design_matrix.columns == contrast[0]) * 1.0 -(design_matrix.columns == contrast[1])
    
    eff = compute_contrast(labels, estimates, contrast_values)
    z_map = eff.z_score()
    z_p_map = 2*(1 - stats.norm.cdf(abs(z_map)))
    fdr_th = fdr_threshold(z_map, glm_alpha)
    fdr = z_map
    fdr *= (z_map > fdr_th)
    fdr_p_map = 2*(1 - stats.norm.cdf(abs(fdr)))

    
    if contrast_num:
        deriv = np.vstack((deriv,z_map,z_p_map,fdr,fdr_p_map))
    else:                 
        deriv = np.vstack((z_map,z_p_map,fdr,fdr_p_map))

for est,vox in enumerate(data_indices):
    deriv_mat[vox] = deriv.T[est]
    pred_mat[vox] = data_pred[est]

# Save derivatives and prediction data
if regist_type == 'fsLR_den-170k':
    np.save(deriv_fn, deriv_mat)
    np.save(pred_fn, pred_mat)
else: 
    deriv_img = nb.Nifti1Image(dataobj=deriv_mat, affine=data_img.affine, header=data_img.header)
    deriv_img.to_filename(deriv_fn)
    pred_img = nb.Nifti1Image(dataobj=pred_mat, affine=data_img.affine, header=data_img.header)
    pred_img.to_filename(pred_fn)

# Print duration
end_time = datetime.datetime.now()
print("\nStart time:\t{start_time}\nEnd time:\t{end_time}\nDuration:\t{dur}".format(
            start_time=start_time,
            end_time=end_time,
            dur=end_time - start_time))
