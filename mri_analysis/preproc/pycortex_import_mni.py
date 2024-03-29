"""
-----------------------------------------------------------------------------------------
pycortex_import_mni.py
-----------------------------------------------------------------------------------------
Goal of the script:
Import MNI subject in pycortex
-----------------------------------------------------------------------------------------
Input(s):
None
-----------------------------------------------------------------------------------------
Output(s):
None
-----------------------------------------------------------------------------------------
To run:
cd /home/mszinte/projects/PredictEye/mri_analysis/
python preproc/pycortex_import_mni.py 
-----------------------------------------------------------------------------------------
Written by Martin Szinte (martin.szinte@gmail.com), adapted by Vanessa M
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
import pdb
import platform
opj = os.path.join
deb = pdb.set_trace

# MRI imports
# -----------
import cortex
from cortex.fmriprep import *
import nibabel as nb

# Functions import
# ----------------
from utils import set_pycortex_config_file

# Get inputs
# ----------
subject = 'sub-00'
mni_subject = 'sub-00'

# Define analysis parameters
# --------------------------
with open('settings.json') as f:
    json_s = f.read()
    analysis_info = json.loads(json_s)
base_dir = analysis_info['base_dir']

# Define folder
# -------------
fmriprep_dir = "{base_dir}/deriv_data/fmriprep/".format(base_dir = base_dir)
fs_dir = "{base_dir}/deriv_data/fmriprep/freesurfer/".format(base_dir = base_dir)
temp_dir = "{base_dir}/temp_data/{subject}_rand_ds/".format(base_dir = base_dir, subject = mni_subject)
xfm_name = "identity_mni.fmriprep"
cortex_dir = "{base_dir}/pp_data/cortex/db/{subject}".format(base_dir = base_dir, subject = mni_subject)

# Set pycortex db and colormaps
# -----------------------------
set_pycortex_config_file(base_dir)

# Add participant to pycortex db
# ------------------------------
print('import subject in pycortex')
try: cortex.freesurfer.import_subj(fs_subject = subject, cx_subject = mni_subject, freesurfer_subject_dir = fs_dir, whitematter_surf = 'smoothwm')
except: pass

# Add participant flat maps
# -------------------------
print('import subject flatmaps')
try: cortex.freesurfer.import_flat(fs_subject = subject, cx_subject = mni_subject, freesurfer_subject_dir = fs_dir, patch = 'full', auto_overwrite=True)
except: pass

# Add transform to pycortex db
# ----------------------------
file_list = sorted(glob.glob("{base_dir}/pp_data/sub-01/func/*.nii.gz".format(base_dir = base_dir, sub = subject)))
file_list = [x for x in file_list if 'MNI152NLin2009cAsym' in x]
ref_file = file_list[0]
 
transform = cortex.xfm.Transform(np.identity(4), ref_file)
transform.save(mni_subject, xfm_name, 'magnet')

# Add masks to pycortex transform
# -------------------------------
print('create pycortex transform')
xfm_masks = analysis_info['xfm_masks']
ref = nb.load(ref_file)
for xfm_mask in xfm_masks:
    
    mask = cortex.get_cortical_mask(subject = mni_subject, xfmname = xfm_name, type = xfm_mask)
    mask_img = nb.Nifti1Image(dataobj=mask.transpose((2,1,0)), affine=ref.affine, header=ref.header)
    mask_file = "{cortex_dir}/transforms/{xfm_name}/mask_{xfm_mask}.nii.gz".format(
                            cortex_dir = cortex_dir, xfm_name = xfm_name, xfm_mask = xfm_mask)
    mask_img.to_filename(mask_file)

# Create participant pycortex overlays
# ------------------------------------
print('create subject pycortex overlays to check')
voxel_vol = cortex.Volume(np.random.randn(mask.shape[0], mask.shape[1], mask.shape[2]), subject = mni_subject, xfmname = xfm_name)
ds = cortex.Dataset(rand=voxel_vol)
cortex.webgl.make_static(outpath = temp_dir, data = ds)
