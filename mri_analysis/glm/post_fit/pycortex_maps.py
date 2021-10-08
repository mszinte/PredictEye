"""
-----------------------------------------------------------------------------------------
pycortex_maps.py
-----------------------------------------------------------------------------------------
Goal of the script:
Create flatmap plots and dataset
-----------------------------------------------------------------------------------------
Input(s):
sys.argv[1]: subject name (e.g. sub-01)
sys.argv[2]: registration (e.g. T1w)
sys.argv[3]: pre-processing steps (fmriprep_dct or fmriprep_dct_pca)
sys.argv[4]: save in SVG file (0  = No, 1 = Yes)
-----------------------------------------------------------------------------------------
Output(s):
Pycortex flatmaps figures
-----------------------------------------------------------------------------------------
To run:
On invibe server
>> cd to function
>> python glm/post_fit/pycortex_maps.py [subject] [reg] [preproc] [svg]
-----------------------------------------------------------------------------------------
Exemple:
[TO RUN LOCALLY OR ON INVIBE SERVER]
cd ~/disks/meso_H/projects/PredictEye/mri_analysis/
ipython glm/post_fit/pycortex_maps.py sub-01 T1w fmriprep_dct 0
ipython glm/post_fit/pycortex_maps.py sub-01 fsLR_den-170k fmriprep_dct 0
ipython glm/post_fit/pycortex_maps.py sub-01 T1w fmriprep_dct_pca 0
ipython glm/post_fit/pycortex_maps.py sub-01 fsLR_den-170k fmriprep_dct_pca 0
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
import numpy as np
import matplotlib.pyplot as plt
import ipdb
deb = ipdb.set_trace

# MRI imports
# -----------
import nibabel as nb
import cortex

# Functions import
# ----------------
from utils.utils import draw_cortex_vertex, set_pycortex_config_file

# Get inputs
# ----------
subject = sys.argv[1]
regist_type = sys.argv[2]
if regist_type == 'fsLR_den-170k':
    file_ext = '.npy'
    cifti_mode= 'surf'
    cortex_type = 'VertexRGB'
    subject2draw = 'hcp'
else:
    file_ext = '.nii.gz'
    sh_end = ''
    cortex_type = 'VolumeRGB'
    subject2draw = subject

preproc = sys.argv[3]
save_svg = int(sys.argv[4])
if save_svg == 1: save_svg = True
else: save_svg = False

# Define analysis parameters
# --------------------------
with open('settings.json') as f:
    json_s = f.read()
    analysis_info = json.loads(json_s)

# Define settings
# ---------------
xfm_name = analysis_info["xfm_name"]
base_dir = analysis_info["base_dir_local"]
deriv_dir = "{}/pp_data_new/{}/glm/fit".format(base_dir,subject)
glm_tasks = analysis_info['glm_task_names']
glm_vmin = analysis_info["glm_vmin"]
glm_vmax = analysis_info["glm_vmax"]
data_types = ['avg','avg-loo']
cvrsq_val = analysis_info["cvr2_range"]

# Create folder
# -------------
flatmaps_dir = '{}/pp_data_new/{}/glm/pycortex/flatmaps'.format(base_dir, subject)
datasets_dir = '{}/pp_data_new/{}/glm/pycortex/datasets'.format(base_dir, subject)
try: os.makedirs(flatmaps_dir); 
except: pass
try: os.makedirs(datasets_dir)
except: pass

# Set pycortex db and colormaps
# -----------------------------
set_pycortex_config_file(base_dir)

# Pycortex plots
# --------------
cmap, cmap_uni= 'RdBu_r', 'Reds'
cmap_steps = 255

print('save flatmaps')
for task in glm_tasks:
    if task == 'SacLoc':
        cond1_label, cond2_label = ['Sac'], ['Fix']
        z_idx, z_p_idx, fdr_idx, fdr_p_idx, cv_rsq_idx = [0],[1],[2],[3],4
    elif task == 'PurLoc':
        cond1_label, cond2_label = ['Pur'], ['Fix']
        z_idx, z_p_idx, fdr_idx, fdr_p_idx, cv_rsq_idx = [0],[1],[2],[3],4
    elif task == 'SacVELoc':
        cond1_label, cond2_label = ['SacExo','SacExo','SacEndo'], ['SacEndo','Fix','Fix']
        z_idx, z_p_idx, fdr_idx, fdr_p_idx, cv_rsq_idx = [0,4,8],[1,5,9],[2,6,10],[3,7,11],12
    elif task == 'PurVELoc':
        cond1_label, cond2_label = ['PurExo','PurExo','PurEndo'], ['PurEndo','Fix','Fix']
        z_idx, z_p_idx, fdr_idx, fdr_p_idx, cv_rsq_idx = [0,4,8],[1,5,9],[2,6,10],[3,7,11],12
    elif task == 'pMF':
        cond1_label, cond2_label = ['PurSac'], ['Fix']
        z_idx, z_p_idx, fdr_idx, fdr_p_idx, cv_rsq_idx = [0],[1],[2],[3],4

    maps_names = []
    for data_type in data_types:

        # Load data
        deriv_fn = "{}/{}_task-{}_space-{}_{}_{}_glm-deriv{}".format(deriv_dir, subject, task, regist_type, preproc, data_type, file_ext)

        if regist_type == 'fsLR_den-170k': deriv_mat = np.load(deriv_fn)
        else: deriv_mat = nb.load(deriv_fn).get_fdata()
        
        for contrast_num, contrast in enumerate(zip(cond1_label,cond2_label)):

#             # Z map
#             z_data = deriv_mat[...,z_idx[contrast_num]]
#             z_p_data = deriv_mat[...,z_p_idx[contrast_num]]
#             z_p_data_range = (z_p_data - glm_vmin[1])/ (glm_vmax[1] - glm_vmin[1])
#             z_p_data_range[z_p_data_range<0] = 0
#             z_alpha = z_p_data_range
#             param_z = {'data': z_data, 'cmap': cmap, 'alpha': z_alpha, 'vmin': glm_vmin[0],'vmax': glm_vmax[0],'cbar': 'discrete', 'cortex_type': cortex_type,
#                        'description': 'z map: {} vs. {}'.format(contrast[0],contrast[1]), 'curv_brightness': 1, 'curv_contrast': 0.1, 'add_roi': False}
#             exec('param_z_{}{} = param_z'.format(contrast[0],contrast[1]))
#             maps_names.append('z_{}{}'.format(contrast[0],contrast[1]))

            # FDR map
            fdr_data = deriv_mat[...,fdr_idx[contrast_num]]
            fdr_p_data = deriv_mat[...,fdr_p_idx[contrast_num]]
            fdr_p_data_range = (fdr_p_data - glm_vmin[1])/ (glm_vmax[1] - glm_vmin[1])
            fdr_p_data_range[fdr_p_data_range<0] = 0
            fdr_alpha = fdr_p_data_range
            param_fdr = {'data': fdr_data, 'cmap': cmap, 'alpha': fdr_alpha, 'vmin': glm_vmin[0],'vmax': glm_vmax[0],'cbar': 'discrete', 'cortex_type': cortex_type,
                         'description': 'z map: {} vs. {}'.format(contrast[0],contrast[1]), 'curv_brightness': 1, 'curv_contrast': 0.1, 'add_roi': False}
            exec('param_fdr_{}{} = param_fdr'.format(contrast[0],contrast[1]))
            maps_names.append('fdr_{}{}'.format(contrast[0],contrast[1]))
        
        ## CV-R-square
        cv_rsq_data = deriv_mat[...,cv_rsq_idx]
        cv_rsq_data[cv_rsq_data==1]=0
        cv_rsq_alpha = (cv_rsq_data - np.nanmin(cv_rsq_data))/ (np.nanmax(cv_rsq_data) - np.nanmin(cv_rsq_data))
        param_cv_rsq = {'data': cv_rsq_data, 'cmap': cmap_uni, 'alpha': cv_rsq_alpha, 'vmin': cvrsq_val[0],'vmax': cvrsq_val[1],'cbar': 'discrete', 'cortex_type': cortex_type,
                        'description': 'CV-R2 {}'.format(task), 'curv_brightness': 1, 'curv_contrast': 0.1, 'add_roi': False}
        maps_names.append('cv_rsq')

        # Draw flatmaps
        volumes = {}
        for maps_name in maps_names:

            # create flatmap
            roi_name = '{}_{}_{}_{}_{}'.format(task, regist_type, preproc, data_type, maps_name)
            roi_param = {'subject': subject2draw, 'xfmname': xfm_name, 'roi_name': roi_name}
            print(roi_name)
            exec('param_{}.update(roi_param)'.format(maps_name))
            exec('volume_{maps_name} = draw_cortex_vertex(**param_{maps_name})'.format(maps_name=maps_name))
            exec("plt.savefig('{}/{}_task-{}_space-{}_{}_{}_glm-{}.pdf')".format(flatmaps_dir, subject, task, regist_type, preproc, data_type, maps_name))
            plt.close()
            
            # save flatmap as dataset
            exec('vol_description = param_{}["description"]'.format(maps_name))
            exec('volume = volume_{}'.format(maps_name))
            volumes.update({vol_description:volume})
        
        

        # save dataset
        dataset_file = "{}/{}_task-{}_space-{}_{}_{}.hdf".format(datasets_dir, subject, task, regist_type, preproc, data_type)
        dataset = cortex.Dataset(data = volumes)
        dataset.save(dataset_file)
        