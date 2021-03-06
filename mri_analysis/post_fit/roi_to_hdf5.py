"""
-----------------------------------------------------------------------------------------
roi_to_hdf5.py
-----------------------------------------------------------------------------------------
Goal of the script:
Create roi-masks and save derivatives, tc and coord in hdf5 format
-----------------------------------------------------------------------------------------
Input(s):
sys.argv[1]: subject name (e.g. 'sub-001')
sys.argv[2]: pre-processing steps (fmriprep_dct or fmriprep_dct_pca)
sys.argv[3]: registration (e.g. T1w)
sys.argv[4]: task
sys.argv[5]: sub-task
-----------------------------------------------------------------------------------------
Output(s):
h5 file per rois
-----------------------------------------------------------------------------------------
To run:
>> cd to function
>> python post_fit/roi_to_hdf5.py [subject] [preproc] [reg] [task] [sub-task]
-----------------------------------------------------------------------------------------
Exemple:
cd /home/mszinte/projects/PredictEye/mri_analysis/
python post_fit/roi_to_hdf5.py sub-01 fmriprep_dct T1w pRF
python post_fit/roi_to_hdf5.py sub-01 fmriprep_dct T1w pMF sac
python post_fit/roi_to_hdf5.py sub-01 fmriprep_dct T1w pMF sp
-----------------------------------------------------------------------------------------
Written by Martin Szinte (martin.szinte@gmail.com)
-----------------------------------------------------------------------------------------
"""
import warnings
warnings.filterwarnings("ignore")

# General imports
# ---------------
import os
import sys
import json
import glob
import numpy as np
import scipy.io
import ipdb
deb = ipdb.set_trace

# MRI imports
# -----------
from model.prfpy.rf import *
from model.prfpy.timecourse import *
from model.prfpy.stimulus import PRFStimulus2D
from model.prfpy.model import Iso2DGaussianModel
from model.prfpy.fit import Iso2DGaussianFitter
import nibabel as nb
import cortex

# Function import
# ---------------
from utils import set_pycortex_config_file, mask_nifti_2_hdf5

# Get inputs
# ----------
subject = sys.argv[1]
preproc = sys.argv[2]
regist_type = sys.argv[3]
task = sys.argv[4]
if len(sys.argv) < 6: sub_task = ''
else: sub_task = sys.argv[5]

# Define analysis parameters
# --------------------------
with open('settings.json') as f:
    json_s = f.read()
    analysis_info = json.loads(json_s)

# Define folders and settings
# ---------------------------
base_dir = analysis_info['base_dir']
cortex_dir = "{}/pp_data/cortex/db/{}".format(base_dir, subject)
rois_mask_dir = "{}/pp_data/{}/gauss/roi_masks/".format(base_dir, subject)
h5_dir = "{}/pp_data/{}/gauss/h5/{}{}".format(base_dir, subject, task, sub_task)
deriv_dir = "{}/pp_data/{}/gauss/fit/{}".format(base_dir, subject,task)
xfm_name = "identity.fmriprep"
rois = analysis_info['rois']
cortical_mask = analysis_info['cortical_mask']

# Get task specific settings
if task == 'pRF':
    # to create stimulus design (create in matlab - see others/make_visual_dm.m)
    visual_dm_file = scipy.io.loadmat('{}/pp_data/visual_dm/pRF_vd.mat'.format(base_dir))

elif task == 'pMF':
    pmf_seq_num_all = analysis_info['pmf_seq_num']    # put by hand after looking randomly selected order in event file
    pmf_seq_num = pmf_seq_num_all[int(subject[-2:])-1]
    # to create stimulus design (create using fit/pmf_design.py)
    visual_dm_file = scipy.io.loadmat("{}/pp_data/visual_dm/{}{}_vd_{}.mat".format(base_dir,task,sub_task, pmf_seq_num))

# determine model
visual_dm = visual_dm_file['stim'].transpose([1,0,2])
stimulus = PRFStimulus2D(   screen_size_cm=analysis_info['screen_width'],
                            screen_distance_cm=analysis_info['screen_distance'],
                            design_matrix=visual_dm,
                            TR=analysis_info['TR'])

gauss_model = Iso2DGaussianModel(stimulus=stimulus)

# Set pycortex db and colormaps
# -----------------------------
set_pycortex_config_file(base_dir)

# Create ROI masks
# ----------------
ref_file = "{}/transforms/{}/reference.nii.gz".format(cortex_dir, xfm_name)
ref_img = nb.load(ref_file)
try: os.makedirs(rois_mask_dir)
except: pass

for roi in rois:
    roi_mask_file_L = "{}/{}_{}_L.nii.gz".format(rois_mask_dir, roi, cortical_mask)
    
    if not os.path.exists(roi_mask_file_L):
        print('creating {} {} mask'.format(roi, cortical_mask))
        
        roi_mask = cortex.utils.get_roi_masks(subject=subject, xfmname=xfm_name, gm_sampler=cortical_mask, roi_list=roi, return_dict=True, split_lr=True)
        
        for hemi in ['L','R']:
            roi_mask_file = "{}/{}_{}_{}.nii.gz".format(rois_mask_dir, roi, cortical_mask, hemi)
            roi_mask_img = nb.Nifti1Image(dataobj=roi_mask['{}_{}'.format(roi, hemi)].transpose((2,1,0)), affine=ref_img.affine, header=ref_img.header)
            roi_mask_img.to_filename(roi_mask_file)

# Create HDF5 files
# -----------------
try: os.makedirs(h5_dir)
except: pass

tc_file = "{base_dir}/pp_data/{subject}/func/{subject}_task-{task}_space-{reg}_{preproc}_avg.nii.gz".format(
    base_dir=base_dir, subject=subject, reg=regist_type, preproc=preproc, task=task)

for roi in rois:
    print('creating {} {} {} h5 files (deriv, tc, tc_model)'.format(roi, regist_type, preproc))

    h5_file = "{}/{}_{}_{}.h5".format(h5_dir, roi, preproc, regist_type)

    try: os.system('rm {}'.format(h5_file))
    except: pass

    mask_file_L = "{}/{}_{}_L.nii.gz".format(rois_mask_dir, roi, cortical_mask)
    mask_file_R = "{}/{}_{}_R.nii.gz".format(rois_mask_dir, roi, cortical_mask)
    
    deriv_file = "{}/{}_task-{}{}_space-{}_{}_deriv.nii.gz".format(deriv_dir, subject, task, sub_task, regist_type, preproc)

    mask_nifti_2_hdf5(deriv_file=deriv_file,
                      tc_file=tc_file,
                      mask_file_L=mask_file_L,
                      mask_file_R=mask_file_R,
                      hdf5_file=h5_file,
                      model=gauss_model,
                      folder_alias = '{}{}'.format(task,sub_task))