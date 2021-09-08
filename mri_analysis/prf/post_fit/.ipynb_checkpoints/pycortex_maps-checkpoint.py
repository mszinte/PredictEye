"""
-----------------------------------------------------------------------------------------
pycortex_maps.py
-----------------------------------------------------------------------------------------
Goal of the script:
Create flatmap plots and dataset
-----------------------------------------------------------------------------------------
Input(s):
sys.argv[1]: local mount of mesocentre disk (e.g. ~/disks/meso_S/)
sys.argv[2]: subject name (e.g. 'sub-001')
sys.argv[3]: task (e.g. pRF, pMF)
sys.argv[4]: pre-processing steps (fmriprep_dct or fmriprep_dct_pca)
sys.argv[5]: registration (e.g. T1w)
sys.argv[6]: save in SVG file (0  = No, 1 = Yes)
sys.argv[7]: sub_task (e.g. 'sac', 'sp')
-----------------------------------------------------------------------------------------
Output(s):
pycortex flat maps figures
-----------------------------------------------------------------------------------------
To run:
On invibe server
>> cd to function
>> python post_fit/pycortex_maps.py [base_dir] [subject] [task] [preproc] 
                                                          [reg] [svg] [sub_task]
-----------------------------------------------------------------------------------------
Exemple:
cd ~/disks/meso_H/projects/PredictEye/mri_analysis/
python post_fit/pycortex_maps.py ~/disks/meso_S sub-01 pRF fmriprep_dct T1w 0
python post_fit/pycortex_maps.py ~/disks/meso_S sub-01 pMF fmriprep_dct T1w 0 sac
python post_fit/pycortex_maps.py ~/disks/meso_S sub-01 pMF fmriprep_dct T1w 0 sp
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
from utils import draw_cortex_vertex, set_pycortex_config_file

# Get inputs
# ----------
base_dir = sys.argv[1]
subject = sys.argv[2]
task = sys.argv[3]
preproc = sys.argv[4]
regist_type = sys.argv[5]
save_svg = int(sys.argv[6])
if save_svg == 1: save_svg = True
else: save_svg = False
if len(sys.argv) < 8: sub_task = ''
else: sub_task = sys.argv[7]

# Define analysis parameters
# --------------------------
with open('settings.json') as f:
    json_s = f.read()
    analysis_info = json.loads(json_s)

# Define folder
# -------------
xfm_name = analysis_info["xfm_name"]
base_dir = "{}/data/PredictEye".format(base_dir)
deriv_dir = "{}/pp_data/{}/gauss/fit/{}".format(base_dir,subject, task)

# Set pycortex db and colormaps
# -----------------------------
set_pycortex_config_file(base_dir)

# Pycortex plots
# --------------
rsq_idx, ecc_idx, polar_real_idx, polar_imag_idx , size_idx, \
    amp_idx, baseline_idx, cov_idx, x_idx, y_idx = 0,1,2,3,4,5,6,7,8,9

cmap_polar = 'hsv'
cmap_uni = 'Reds'
cmap_ecc_size = 'Spectral'
col_offset = 1.0/14.0
cmap_steps = 255

print('save pycortex flatmaps')
maps_names = []
flatmaps_dir = '{}/pp_data/{}/gauss/pycortex_outputs/flatmaps/prf'.format(base_dir, subject)
webviewer_dir = '{base_dir}/pp_data/{subject}/gauss/pycortex_outputs/webviewer/{subject}_{task}{sub_task}_{reg}_{preproc}'.format(
    base_dir=base_dir, subject=subject, task=task, sub_task=sub_task, reg=regist_type, preproc=preproc)

try:
    os.makedirs(flatmaps_dir)
    os.makedirs(webviewer_dir)
except:
    pass

# Load data
deriv_mat_file = "{deriv_dir}/{subject}_task-{task}{sub_task}_space-{reg}_{preproc}_deriv.nii.gz".format(
                  deriv_dir=deriv_dir, subject=subject, task=task, sub_task=sub_task, reg=regist_type, preproc=preproc)

img_deriv_mat = nb.load(deriv_mat_file)
deriv_mat = img_deriv_mat.get_fdata()

# R-square
rsq_data = deriv_mat[...,rsq_idx]
alpha = rsq_data
param_rsq = {'data': rsq_data, 'cmap': cmap_uni, 'alpha': alpha, 'vmin': 0,'vmax': 1,'cbar': 'discrete',
             'description': '{}{} rsquare'.format(task, sub_task), 'curv_brightness': 1, 'curv_contrast': 0.1, 'add_roi': False}
maps_names.append('rsq')

# Polar angle
pol_comp_num = deriv_mat[...,polar_real_idx] + 1j * deriv_mat[...,polar_imag_idx]
polar_ang = np.angle(pol_comp_num)
ang_norm = (polar_ang + np.pi) / (np.pi * 2.0)
ang_norm = np.fmod(ang_norm + col_offset,1)
param_polar = { 'data': ang_norm, 'cmap': cmap_polar, 'alpha': alpha, 'vmin': 0, 'vmax': 1, 'cmap_steps': cmap_steps,
                'cbar': 'polar', 'col_offset': col_offset, 'description': '{task}{sub_task} polar:{cmap_steps:3.0f} steps'.format(task=task, sub_task=sub_task, cmap_steps=cmap_steps), 
                'curv_brightness': 0.1, 'curv_contrast': 0.25, 'add_roi': save_svg}
exec('param_polar_{cmap_steps} = param_polar'.format(cmap_steps = int(cmap_steps)))
exec('maps_names.append("polar_{cmap_steps}")'.format(cmap_steps = int(cmap_steps)))

# Eccentricity
ecc_data = deriv_mat[...,ecc_idx]
param_ecc = {'data': ecc_data, 'cmap': cmap_ecc_size, 'alpha': alpha, 'vmin': 0, 'vmax': 15,'cbar': 'ecc', 
             'description': '{}{} eccentricity'.format(task, sub_task), 'curv_brightness': 1, 'curv_contrast': 0.1, 'add_roi': save_svg}
maps_names.append('ecc')

# Size
size_data = deriv_mat[...,size_idx]
param_size = {'data': size_data, 'cmap': cmap_ecc_size, 'alpha': alpha, 'vmin': 0, 'vmax': 8, 'cbar': 'discrete', 
              'description': '{}{} size'.format(task, sub_task), 'curv_brightness': 1, 'curv_contrast': 0.1, 'add_roi': False}
maps_names.append('size')

# Coverage
if task == 'pRF':
    cov_data = deriv_mat[...,cov_idx]
    param_cov = {'data': cov_data, 'cmap': cmap_uni, 'alpha': alpha,'vmin': 0, 'vmax': 1, 'cbar': 'discrete', 
                'description': '{}{} coverage'.format(task, sub_task), 'curv_brightness': 1, 'curv_contrast': 0.1, 'add_roi': False}
    maps_names.append('cov')

# Draw flatmaps
volumes = {}
for maps_name in maps_names:

    # create flatmap
    roi_name = '{}_{}{}_{}_{}'.format(maps_name, task, sub_task, regist_type, preproc)
    roi_param = {'subject': subject, 'xfmname': xfm_name, 'roi_name': roi_name}
    print(roi_name)
    exec('param_{}.update(roi_param)'.format(maps_name))
    exec('volume_{maps_name} = draw_cortex_vertex(**param_{maps_name})'.format(maps_name=maps_name))
    exec("plt.savefig('{}/{}_space-{}_{}_prf_{}.pdf')".format(flatmaps_dir, subject, regist_type, preproc, maps_name))
    plt.close()
    
    # save flatmap as dataset
    exec('vol_description = param_{}["description"]'.format(maps_name))
    exec('volume = volume_{}'.format(maps_name))
    volumes.update({vol_description:volume})

# save dataset
dataset_file = "{}/{}_space-{}_prf.hdf".format(flatmaps_dir, subject, regist_type, preproc)
dataset = cortex.Dataset(data = volumes)
dataset.save(dataset_file)