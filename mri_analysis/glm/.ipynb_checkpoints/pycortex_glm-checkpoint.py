"""
-----------------------------------------------------------------------------------------
pycortex_glm.py
-----------------------------------------------------------------------------------------
Goal of the script:
Generate flatmaps for glm analysis
-----------------------------------------------------------------------------------------
Input(s):
sys.argv[1]: base_dir (e.g. )
sys.argv[2]: subject name (e.g. sub-01)
sys.argv[3]: registration (e.g. T1w)
sys.argv[4]: pre-processing steps (fmriprep_dct or fmriprep_dct_pca)
-----------------------------------------------------------------------------------------
Output(s):
GLM output on a flatmap
-----------------------------------------------------------------------------------------
To run:
On invibe server
>> cd to function
>> python glm/pycortex_glm.py [base_dir] [subject] [task] [reg] [preproc]
-----------------------------------------------------------------------------------------
Example:
cd ~/disks/meso_H/projects/PredictEye/mri_analysis/
python glm/pycortex_glm.py ~/disks/meso_S/data/PredictEye sub-01 T1w fmriprep_dct
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
from utils import draw_cortex_vertex, set_pycortex_config_file

# Get inputs
# ----------
base_dir =  sys.argv[1]
subject = sys.argv[2]
regist_type = sys.argv[3]
preproc = sys.argv[4]

glm_dir = '{base_dir}/pp_data/{subject}/glm/fit'.format(base_dir=base_dir, subject=subject)
glm_files = os.listdir(glm_dir)

# Define analysis parameters
# --------------------------
with open('settings.json') as f:
    json_s = f.read()
    analysis_info = json.loads(json_s)

# Set pycortex db and colormaps
# -----------------------------
set_pycortex_config_file(base_dir)

# Pycortex plots
# --------------
xfm_name = analysis_info["xfm_name"]
cmap = 'RdBu_r'
cmap_steps = 255
glm_vmin = analysis_info["glm_vmin"]
glm_vmax = analysis_info["glm_vmax"]
maps_names = {'z_map':1, 'fdr_map':3, 'fdr_c10_map':5, 'fdr_c50_map':7, 'fdr_c100_map':9}

volumes = {}
for glm_file in glm_files:
    print('Maps : {}'.format(glm_file))

    # Load data
    img_deriv_mat = nb.load('{}/{}'.format(glm_dir,glm_file))
    glm_mat = img_deriv_mat.get_fdata()
    
    contrast = glm_file.split("_")[-1][4:-7]

    
    
    flatmaps_dir = '{}/pp_data/{}/glm/pycortex_outputs/flatmaps/{}'.format(base_dir, subject, contrast)
    try: os.makedirs(flatmaps_dir)
    except: pass
    
    volumes = {}
    param = dict()
    for map_name in maps_names:
        
        # compute alpha
        pval = glm_mat[...,maps_names[map_name]+1]
        pval_range = (pval - glm_vmin[1])/ (glm_vmax[1] - glm_vmin[1])
        pval_range[pval_range<0] = 0
        alpha = pval_range

        data  = glm_mat[...,maps_names[map_name]]
        param[map_name] = {'subject':subject, 'data': data, 'xfmname': xfm_name, 'cmap': cmap, 'alpha': alpha,\
                           'vmin': glm_vmin[0],'vmax': glm_vmax[0], 'cbar': 'discrete', \
                           'description': '{}: {}'.format(contrast,map_name), 'curv_brightness': 1, 'curv_contrast': 0.1, 'add_roi': False}

        # create flatmap
        exec('volume_{map_name} = draw_cortex_vertex(**param[\'{map_name}\'])'.format(map_name=map_name))
        exec("plt.savefig('{}/{}_space-{}_{}_glm_{}_{}.pdf')".format(flatmaps_dir, subject, regist_type, preproc, contrast, map_name))
        plt.close()
        
        # save flatmap as dataset
        exec('vol_description = param[\'{map_name}\']["description"]'.format(map_name=map_name))
        exec('volume = volume_{map_name}'.format(map_name = map_name))
        volumes.update({vol_description:volume})
    
    # save dataset
    dataset_file = "{}/{}_space-{}_{}_glm_{}.hdf".format(flatmaps_dir, subject, regist_type, preproc, contrast)
    dataset = cortex.Dataset(data = volumes)
    dataset.save(dataset_file)