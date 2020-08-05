"""
-----------------------------------------------------------------------------------------
pp_roi.py
-----------------------------------------------------------------------------------------
Goal of the script:
Display cortical data with pycortex 
-----------------------------------------------------------------------------------------
Input(s):
sys.argv[1]: subject number
sys.argv[2]: acquisition ('acq-2p5mm','acq-2mm')
sys.argv[3]: fit model ('gauss','css')
sys.argv[4]: save roi in svg file
sys.argv[5]: save time course
-----------------------------------------------------------------------------------------
Output(s):
None
-----------------------------------------------------------------------------------------
To run:
python post_fit/pp_roi.py sub-01 acq-2p5mm gauss 1 0 
python post_fit/pp_roi.py sub-01 acq-2mm gauss 1 0
> to run localy
-----------------------------------------------------------------------------------------
"""

# Stop warnings
# -------------
import warnings
warnings.filterwarnings("ignore")

# General imports
# ---------------
import os
import shutil
import sys
import json
import numpy as np
import ipdb
import matplotlib.pyplot as plt
opj = os.path.join
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
subject = sys.argv[1]
acq = sys.argv[2]
fit_model = sys.argv[3]
save_svg = int(sys.argv[4])
if save_svg == 1: save_svg = True
else: save_svg = False
plot_tc = int(sys.argv[5])

# Define analysis parameters
# --------------------------
with open('settings.json') as f:
    json_s = f.read()
    analysis_info = json.loads(json_s)

# Define folder
# -------------
xfm_name = "identity.{acq}".format(acq = acq)
base_dir = analysis_info['base_dir_local']
prf_signs = analysis_info['prf_signs']
deriv_dir = "{base_dir}/pp_data/{subject}/{fit_model}/deriv".format(base_dir = base_dir,subject = subject, fit_model = fit_model)
cortex_dir = "{base_dir}/pp_data/cortex/db/{subject}".format(base_dir = base_dir, subject = subject)
fs_dir = "{base_dir}/deriv_data/fmriprep/freesurfer/".format(base_dir = base_dir)
fmriprep_dir = "{base_dir}/deriv_data/fmriprep/".format(base_dir = base_dir)
bids_dir = "{base_dir}/bids_data/".format(base_dir = base_dir)

# Set pycortex db and colormaps
# -----------------------------
set_pycortex_config_file(base_dir)

# Pycortex plots
# --------------
sign_idx, rsq_idx, ecc_idx, polar_real_idx, polar_imag_idx , size_idx, \
            non_lin_idx, amp_idx, baseline_idx, cov_idx, x_idx, y_idx = 0,1,2,3,4,5,6,7,8,9,10,11

cmap_neg_pos = 'RdBu_r'
cmap_polar = 'hsv'
cmap_uni = 'Reds'
cmap_ecc_size = 'Spectral'
col_offset = 1/14.0
cmap_steps = 255.0

for prf_sign in prf_signs:
    print('save pycortex flatmaps: {prf_sign}'.format(prf_sign = prf_sign))
    # Create figure folders
    maps_names = []
    exec('flatmaps_dir_{prf_sign} = opj(base_dir,"pp_data",subject,fit_model,"pycortex_outputs","flatmaps","{prf_sign}")'.format(prf_sign = prf_sign))
    exec('dataset_dir_{prf_sign} = opj(base_dir,"pp_data",subject,fit_model,"pycortex_outputs","dataset","{prf_sign}")'.format(prf_sign = prf_sign))
    exec('webviewer_dir_{prf_sign} = opj(base_dir,"pp_data",subject,fit_model,"pycortex_outputs","webviewer","{prf_sign}","{acq}")'.format(prf_sign = prf_sign, acq = acq)) 
        
    try:
        exec('os.makedirs(flatmaps_dir_{prf_sign})'.format(prf_sign = prf_sign))
        exec('os.makedirs(dataset_dir_{prf_sign})'.format(prf_sign = prf_sign))
        exec('os.makedirs(webviewer_dir_{prf_sign})'.format(prf_sign = prf_sign))
    except:
        pass

    # Load data
    deriv_mat_file = "{deriv_dir}/{prf_sign}/prf_deriv_{acq}_{prf_sign}.nii.gz".format(deriv_dir = deriv_dir,acq = acq, prf_sign = prf_sign)
    img_deriv_mat = nb.load(deriv_mat_file)
    deriv_mat = img_deriv_mat.get_data()
    
    # R-square
    rsq_data = deriv_mat[...,rsq_idx]
    alpha = rsq_data
    param_rsq = {'data': rsq_data, 'cmap': cmap_uni, 'alpha': alpha, 'vmin': 0,'vmax': 1,'cbar': 'discrete',
                 'description': '{acq}: pRF rsquare'.format(acq = acq), 'curv_brightness': 1, 'curv_contrast': 0.1, 'add_roi': False}
    maps_names.append('rsq')

    # Polar angle
    pol_comp_num = deriv_mat[...,polar_real_idx] + 1j * deriv_mat[...,polar_imag_idx]
    polar_ang = np.angle(pol_comp_num)
    ang_norm = (polar_ang + np.pi) / (np.pi * 2.0)
    ang_norm = np.fmod(ang_norm + col_offset,1)
    
    param_polar = {'data': ang_norm, 'cmap': cmap_polar, 'alpha': alpha, 'vmin': 0, 'vmax': 1, 'cmap_steps': cmap_steps,
                   'cbar': 'polar', 'col_offset': col_offset, 'description': '{acq}: pRF polar:{cmap_steps:3.0f} steps'.format(cmap_steps = cmap_steps, acq = acq), 
                   'curv_brightness': 0.1, 'curv_contrast': 0.25, 'add_roi': save_svg}
    exec('param_polar_{cmap_steps} = param_polar'.format(cmap_steps = int(cmap_steps)))
    exec('maps_names.append("polar_{cmap_steps}")'.format(cmap_steps = int(cmap_steps)))

    # Eccentricity
    ecc_data = deriv_mat[...,ecc_idx]
    param_ecc = {'data': ecc_data, 'cmap': cmap_ecc_size, 'alpha': alpha, 'vmin': 0, 'vmax': 15,'cbar': 'ecc', 
                 'description': '{acq}: pRF eccentricity'.format(acq = acq), 'curv_brightness': 1, 'curv_contrast': 0.1, 'add_roi': save_svg}
    maps_names.append('ecc')
    add_roi = True

    # Sign
    sign_data = deriv_mat[...,sign_idx]
    param_sign = {'data': sign_data, 'cmap': cmap_neg_pos, 'alpha': alpha, 'vmin': -1, 'vmax': 1, 'cbar': 'discrete', 
                  'description': '{acq}: pRF sign'.format(acq = acq), 'curv_brightness': 1, 'curv_contrast': 0.1, 'add_roi': False}
    maps_names.append('sign')
    add_roi = False

    # Size
    size_data = deriv_mat[...,size_idx]
    param_size = {'data': size_data, 'cmap': cmap_ecc_size, 'alpha': alpha, 'vmin': 0, 'vmax': 8, 'cbar': 'discrete', 
                  'description': '{acq}: pRF size'.format(acq = acq), 'curv_brightness': 1, 'curv_contrast': 0.1, 'add_roi': False}
    maps_names.append('size')
    add_roi = False

    # Coverage
    cov_data = deriv_mat[...,cov_idx]
    param_cov = {'data': cov_data, 'cmap': cmap_uni, 'alpha': alpha,'vmin': 0, 'vmax': 1, 'cbar': 'discrete', 
                 'description': '{acq}: pRF coverage'.format(acq = acq), 'curv_brightness': 1, 'curv_contrast': 0.1, 'add_roi': False}
    maps_names.append('cov')
    add_roi = False

    # Draw flatmaps
    volumes = {}
    
    for maps_name in maps_names:
        roi_name = '{maps_name}_{acq}_{prf_sign}'.format(maps_name = maps_name, acq = acq, prf_sign = prf_sign)

        if prf_sign == 'pos':
            roi_param = {'subject': subject, 'xfmname': xfm_name, 'roi_name': roi_name}
        else:
            roi_param = {'subject': subject, 'xfmname': xfm_name, 'add_roi': False, 'roi_name': roi_name}
        
        exec('param_{maps_name}.update(roi_param)'.format(maps_name = maps_name))
        exec('volume_{maps_name} = draw_cortex_vertex(**param_{maps_name})'.format(maps_name=maps_name))
        exec('plt.savefig(opj(flatmaps_dir_{prf_sign}, "{maps_name}_{acq}_{prf_sign}.pdf"),facecolor="w")'.format(prf_sign = prf_sign,maps_name = maps_name, acq = acq))
        plt.close()
        exec('vol_description = param_{maps_name}["description"]'.format(maps_name = maps_name))
        exec('volume = volume_{maps_name}'.format(maps_name = maps_name))
        volumes.update({vol_description:volume})
    
    print('save pycortex dataset: {prf_sign}'.format(prf_sign = prf_sign))
    exec('dataset_{prf_sign} = cortex.Dataset(data = volumes)'.format(prf_sign = prf_sign))
    exec('dataset_{prf_sign}_file = opj(dataset_dir_{prf_sign}, "{acq}_{prf_sign}.hdf")'.format(acq = acq, prf_sign = prf_sign))
    
    try: exec('os.remove(dataset_{prf_sign}_file)'.format(prf_sign = prf_sign))
    except: pass
    exec('dataset_{prf_sign}.save(dataset_{prf_sign}_file)'.format(acq = acq, prf_sign = prf_sign))
    print('save pycortex webviewer: {prf_sign}'.format(prf_sign = prf_sign))
    exec('cortex.webgl.make_static(outpath = webviewer_dir_{prf_sign}, data = volumes)'.format(prf_sign = prf_sign))
    
# TC data
# -------
if plot_tc == 1:
   
    # load volume
    print('load: time course')
    tc_file = "{base_dir}/pp_data/{subject}/func/{subject}_task-AttendStim_{acq}_fmriprep_sg_psc_avg.nii.gz".format(base_dir = base_dir, subject = subject, acq = acq)
    img_tc = nb.load(tc_file)
    tc = img_tc.get_data()

    # create directory
    dataset_dir = "{base_dir}/pp_data/{subject}/{fit_model}/pycortex_outputs/dataset/tc/".format(
                            base_dir = base_dir, subject = subject, fit_model = fit_model)
    webviewer_dir = "{base_dir}/pp_data/{subject}/{fit_model}/pycortex_outputs/webviewer/tc/".format(
                            base_dir = base_dir, subject = subject, fit_model = fit_model)

    try: 
        os.makedirs(dataset_dir)
        os.makedirs(webviewer_dir)
    except: 
        pass
    
    # create volume
    volume_tc = cortex.Volume(data = tc.transpose((3,2,1,0)), subject = subject,xfmname = xfm_name, cmap = 'BuBkRd', description = 'BOLD')

    # create dataset
    print('save pycortex dataset: time course')
    dataset_tc = cortex.Dataset(data = volume_tc)
    dataset_tc.save("{dataset_dir}{acq}_tc.hdf".format(dataset_dir = dataset_dir, acq = acq))

    # create webgl
    print('save pycortex webviewer: time course')
    cortex.webgl.make_static(outpath = webviewer_dir, data = volume_tc)