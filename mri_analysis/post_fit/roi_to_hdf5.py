"""
-----------------------------------------------------------------------------------------
roi_to_hdf5.py
-----------------------------------------------------------------------------------------
Goal of the script:
Create roi-masks and save derivatives, tc and coord in hdf5 format
-----------------------------------------------------------------------------------------
Input(s):
sys.argv[1]: subject name (e.g. 'sub-001')
sys.argv[2]: task (ex: GazeCenterFS)
sys.argv[3]: pre-processing steps (fmriprep_dct or fmriprep_dct_pca)
-----------------------------------------------------------------------------------------
Output(s):
h5 file per rois
-----------------------------------------------------------------------------------------
To run:
>> cd to function
>> python post_fit/roi_to_hdf5.py [subject] [task] [preproc]
-----------------------------------------------------------------------------------------
Exemple:
cd /home/mszinte/projects/pRFgazeMod/mri_analysis/
python post_fit/roi_to_hdf5.py sub-001 GazeCenterFS fmriprep_dct
-----------------------------------------------------------------------------------------
Written by Martin Szinte (martin.szinte@gmail.com)
-----------------------------------------------------------------------------------------
"""

# General imports
# ---------------
import os
import shutil
import sys
import json
import numpy as np
import ipdb
import scipy.io
import matplotlib.pyplot as plt
opj = os.path.join
deb = ipdb.set_trace

# MRI imports
# -----------
from prfpy.rf import *
from prfpy.timecourse import *
from prfpy.stimulus import PRFStimulus2D
from prfpy.model import Iso2DGaussianModel
from prfpy.fit import Iso2DGaussianFitter
import nibabel as nb
import cortex

# Function import
# ---------------
from utils import set_pycortex_config_file, mask_nifti_2_hdf5

# Get inputs
# ----------
subject = sys.argv[1]
task = sys.argv[2]
preproc = sys.argv[3]


# Define analysis parameters
# --------------------------
with open('settings.json') as f:
    json_s = f.read()
    analysis_info = json.loads(json_s)

# Define folders and settings
# ---------------------------
base_dir = analysis_info['base_dir']
prf_signs = analysis_info['prf_signs']
cortex_dir = "{base_dir}/pp_data/cortex/db/{subject}".format(base_dir = base_dir, subject = subject)
rois_mask_dir = "{base_dir}/pp_data/{subject}/gauss/masks".format(base_dir = base_dir, subject = subject)
h5_dir = "{base_dir}/pp_data/{subject}/gauss/h5".format(base_dir = base_dir, subject = subject)
deriv_dir = "{base_dir}/pp_data/{subject}/gauss/fit".format(base_dir = base_dir, subject = subject)
xfm_name = "identity.fmriprep"
rois = analysis_info['rois']
cortical_mask = analysis_info['cortical_mask']

# Define visual design & model
# ----------------------------

# Create stimulus design (create in matlab - see others/make_visual_dm.m)
visual_dm_file = scipy.io.loadmat(opj(base_dir,'pp_data','visual_dm',"{task}_vd.mat".format(task = task)))
visual_dm = visual_dm_file['stim'].transpose([1,0,2])

stimulus = PRFStimulus2D(screen_width_cm = analysis_info['screen_width'],
                         screen_height_cm = analysis_info['screen_height'],
                         screen_distance_cm = analysis_info['screen_distance'],
                         design_matrix = visual_dm,
                         TR = analysis_info['TR'])

gauss_model = Iso2DGaussianModel(stimulus = stimulus)

# Set pycortex db and colormaps
# -----------------------------
set_pycortex_config_file(base_dir)

# Create ROI masks
# ----------------
ref_file = "{cortex_dir}/transforms/{xfm_name}/reference.nii.gz".format(cortex_dir = cortex_dir, xfm_name = xfm_name)
ref_img = nb.load(ref_file)
try: os.makedirs(rois_mask_dir)
except: pass

for roi in rois:
    roi_mask_file_L = "{rois_mask_dir}/{roi}_{cortical_mask}_L.nii.gz".format(rois_mask_dir = rois_mask_dir, roi = roi, cortical_mask = cortical_mask)
    if os.path.getsize(roi_mask_file_L) != 0:
        continue
    else:
        print('creating {roi} {cortical_mask} mask'.format(roi = roi, cortical_mask = cortical_mask))
        roi_mask = cortex.utils.get_roi_masks(subject = subject, xfmname = xfm_name, gm_sampler = cortical_mask, roi_list = roi, return_dict = True, split_lr = True)
        for hemi in ['L','R']:
            roi_mask_file = "{rois_mask_dir}/{roi}_{cortical_mask}_{hemi}.nii.gz".format(rois_mask_dir = rois_mask_dir, roi = roi, cortical_mask = cortical_mask, hemi = hemi)
            roi_mask_img = nb.Nifti1Image(dataobj = roi_mask['{roi}_{hemi}'.format(roi = roi, hemi = hemi)].transpose((2,1,0)), affine = ref_img.affine, header = ref_img.header)
            roi_mask_img.to_filename(roi_mask_file)


# Create HDF5 files
# -----------------
try: os.makedirs(h5_dir)
except: pass

tc_file = "{base_dir}/pp_data/{subject}/func/{subject}_task-{task}_{preproc}_avg.nii.gz".format(base_dir = base_dir, subject = subject, task = task, preproc = preproc)
for roi in rois:
    print('creating {roi} {task} {preproc} h5 files (deriv, tc, tc_model)'.format(roi = roi, task = task, preproc = preproc))

    h5_file = "{h5_dir}/{roi}_{task}_{preproc}.h5".format(h5_dir = h5_dir, roi = roi, task = task, preproc = preproc)

    try: os.system('rm {h5_file}'.format(h5_file = h5_file))
    except: pass

    mask_file_L = "{rois_mask_dir}/{roi}_{cortical_mask}_L.nii.gz".format(rois_mask_dir = rois_mask_dir, roi = roi, cortical_mask = cortical_mask)
    mask_file_R = "{rois_mask_dir}/{roi}_{cortical_mask}_R.nii.gz".format(rois_mask_dir = rois_mask_dir, roi = roi, cortical_mask = cortical_mask)
    
    outfn = "{base_dir}/pp_data/{subject}/gauss/fit/{subject}_task-{task}_{preproc}_deriv.nii.gz".format(
                                base_dir = base_dir,
                                subject = subject,
                                task = task,
                                preproc = preproc)

    deriv_file = "{deriv_dir}/{subject}_task-{task}_{preproc}_deriv.nii.gz".format(deriv_dir = deriv_dir,subject = subject, task = task, preproc = preproc)

    mask_nifti_2_hdf5(deriv_file = deriv_file,
                      tc_file = tc_file,
                      mask_file_L = mask_file_L,
                      mask_file_R = mask_file_R,
                      hdf5_file = h5_file,
                      model = gauss_model,
                      folder_alias = 'pRF')

