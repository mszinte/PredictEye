"""
-----------------------------------------------------------------------------------------
preproc_end.py
-----------------------------------------------------------------------------------------
Goal of the script:
Arrange and average runs
-----------------------------------------------------------------------------------------
Input(s):
sys.argv[1]: subject name
-----------------------------------------------------------------------------------------
Output(s):
# Preprocessed timeseries files
-----------------------------------------------------------------------------------------
To run:
1. cd to function
>> cd /home/mszinte/projects/PredictEye/mri_analysis/
2. run python command
python preproc/preproc_end.py [subject name] [registration_type]
-----------------------------------------------------------------------------------------
Exemple:
python preproc/preproc_end.py sub-01 MNI152NLin2009cAsym
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
import json
import sys
import os
import glob
#import ipdb
import platform
import numpy as np
opj = os.path.join
#deb = ipdb.set_trace

sub_name = sys.argv[1]
regist_type = sys.argv[2]

# MRI analysis imports
# --------------------
import nibabel as nb
from scipy.signal import savgol_filter

with open('settings.json') as f:
    json_s = f.read()
    analysis_info = json.loads(json_s)
trans_cmd = 'rsync -avuz --progress'

# Define cluster/server specific parameters
# -----------------------------------------
base_dir = analysis_info['base_dir'] 

# Copy files in pp_data folder
# ----------------------------
dest_folder1 = "{base_dir}/pp_data/{sub}/func/fmriprep_dct".format(base_dir = base_dir, sub = sub_name)
try: os.makedirs(dest_folder1)
except: pass

dest_folder2 = "{base_dir}/pp_data/{sub}/func/fmriprep_dct_pca".format(base_dir = base_dir, sub = sub_name)
try: os.makedirs(dest_folder2)
except: pass

orig_folder = "{base_dir}/deriv_data/pybest/{sub}".format(base_dir = base_dir, sub = sub_name)


for task_num, task_name in enumerate(analysis_info['task_names']):
    for task_run in np.arange(0,analysis_info['task_runs'][task_num],1):
        for ses_num,ses_name in enumerate(next(os.walk(orig_folder))[1]):
            # dct func
            orig_file1 = "{orig_fold}/{ses}/preproc/{sub}_{ses}_task-{task_name}_space-{reg}_run-{task_run}_desc-preproc_bold.nii.gz".format(
                                    orig_fold = orig_folder, sub = sub_name, ses = ses_name, task_name = task_name, reg = regist_type, task_run = task_run+1)
            dest_file1 = "{dest_fold}/{sub}_task-{task_name}_space-{reg}_run-{task_run}_fmriprep_dct.nii.gz".format(
                                    dest_fold = dest_folder1, sub = sub_name, task_name = task_name, reg = regist_type, task_run = task_run+1)

            if os.path.isfile(orig_file1):
                os.system("{cmd} {orig} {dest}".format(cmd = trans_cmd, orig = orig_file1, dest = dest_file1))

            # dct + denoised func
            orig_file2 = "{orig_fold}/{ses}/denoising/{sub}_{ses}_task-{task_name}_space-{reg}_run-{task_run}_desc-denoised_bold.nii.gz".format(
                                    orig_fold = orig_folder, sub = sub_name, ses = ses_name, task_name = task_name, reg = regist_type, task_run = task_run+1)
            dest_file2 = "{dest_fold}/{sub}_task-{task_name}_space-{reg}_run-{task_run}_fmriprep_dct_pca.nii.gz".format(
                                    dest_fold = dest_folder2, sub = sub_name, task_name = task_name, reg = regist_type, task_run = task_run+1)

            if os.path.isfile(orig_file2):
                os.system("{cmd} {orig} {dest}".format(cmd = trans_cmd, orig = orig_file2, dest = dest_file2))

# Average tasks runs
for preproc in analysis_info['preproc']:
    for task_name in analysis_info['task_names']:

        file_list = sorted(glob.glob("{base_dir}/pp_data/{sub}/func/{preproc}/*{task_name}_space-{reg}_*.nii.gz".format(
                                     base_dir = base_dir, sub = sub_name, preproc = preproc,task_name = task_name, reg = regist_type)))

        img = nb.load(file_list[0])
        data_avg = np.zeros(img.shape)

        print('avg: '+task_name)
        for file in file_list:
            print('add: '+file)

            # load
            data_psc = []
            data_psc_img = nb.load(file)
            data_psc = data_psc_img.get_fdata()
            data_avg += data_psc/len(file_list)

            # save
            new_file = "{base_dir}/pp_data/{sub}/func/{sub}_task-{task_name}_space-{reg}_{preproc}_avg.nii.gz".format(
                        base_dir = base_dir, sub = sub_name, preproc = preproc, task_name = task_name, reg = regist_type)
            new_img = nb.Nifti1Image(dataobj = data_avg, affine = img.affine, header = img.header)
            new_img.to_filename(new_file)
