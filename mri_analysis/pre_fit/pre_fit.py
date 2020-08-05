"""
-----------------------------------------------------------------------------------------
pre_fit.py
-----------------------------------------------------------------------------------------
Goal of the script:
SG filter, PSC, AVG runs and combine data of both hemisphere
-----------------------------------------------------------------------------------------
Input(s):
sys.argv[1]: subject name
sys.argv[2]: start voxel index
sys.argv[3]: end voxel index
sys.argv[4]: data file path
sys.argv[5]: main directory
-----------------------------------------------------------------------------------------
Output(s):
# Preprocessed timeseries files
-----------------------------------------------------------------------------------------
To run:
python pre_fit/pre_fit.py
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
import ipdb
import platform
import numpy as np
opj = os.path.join
deb = ipdb.set_trace

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
for sub_name in analysis_info['subject_list'] :

    dest_folder = "{base_dir}/pp_data/{sub}/func".format(base_dir = base_dir, sub = sub_name)
    try: os.makedirs(dest_folder)
    except: pass

    orig_folder = "{base_dir}/deriv_data/fmriprep/fmriprep/{sub}/func".format(base_dir = base_dir, sub = sub_name)
            
    for acq in analysis_info['acq']:
        for run in analysis_info['runs']:
            # func
            orig_file1 = "{orig_fold}/{sub}_task-AttendStim_{acq}_{run}_space-T1w_desc-preproc_bold.nii.gz".format(
                                            orig_fold = orig_folder, sub = sub_name, acq = acq, run = run)
            dest_file1 = "{dest_fold}/{sub}_task-AttendStim_{acq}_{run}_fmriprep.nii.gz".format(
                                            dest_fold = dest_folder, sub = sub_name, acq = acq, run = run)

            os.system("{cmd} {orig} {dest}".format(cmd = trans_cmd, orig = orig_file1, dest = dest_file1))
            
            # mask
            orig_file2 = "{orig_fold}/{sub}_task-AttendStim_{acq}_{run}_space-T1w_desc-brain_mask.nii.gz".format(
                                            orig_fold = orig_folder, sub = sub_name, acq = acq, run = run)
            dest_file2 = "{dest_fold}/{sub}_task-AttendStim_{acq}_{run}_mask.nii.gz".format(
                                            dest_fold = dest_folder, sub = sub_name, acq = acq, run = run)

            os.system("{cmd} {orig} {dest}".format(cmd = trans_cmd, orig = orig_file2, dest = dest_file2))


# SG_PSC_AVG + MASK_AVG
# ---------------------

for sub_name in analysis_info['subject_list'] :
    for acq in analysis_info['acq']:
        print("{sub}-{acq}: sg + psc".format(sub = sub_name, acq = acq))
        # SG + PSC
        # --------
        file_list1 = sorted(glob.glob("{base_dir}/pp_data/{sub}/func/*{acq}*fmriprep.nii.gz".format(
                                            base_dir = base_dir, sub = sub_name, acq = acq)))


        for file1 in file_list1:
        
            print(file1)
            # load
            img = nb.load(file1)
            pp_data = img.get_fdata()
        
            # sg filter
            pp_data_filt = savgol_filter(   x = pp_data,
                                            window_length = analysis_info['sg_filt_window_length'],
                                            polyorder = analysis_info['sg_filt_polyorder'],
                                            deriv = analysis_info['sg_filt_deriv'],
                                            axis = 3, 
                                            mode = 'nearest')
            
            pp_data_filt_mean = pp_data_filt.mean(axis=3)
            pp_data_filt_mean = np.repeat(pp_data_filt_mean[:, :, :, np.newaxis], analysis_info['TRs'], axis=3)
            pp_data_sg = pp_data - pp_data_filt + pp_data_filt_mean
            
            # percent signal change
            pp_data_sg_median = np.median(pp_data_sg, axis=3)
            pp_data_sg_median = np.repeat(pp_data_sg_median[:, :, :, np.newaxis], analysis_info['TRs'], axis=3)
            pp_data_sg_psc = 100.0 * (pp_data_sg - pp_data_sg_median)/pp_data_sg_median
            
            # save
            new_file = "{file}_sg_psc.nii.gz".format(file = file1[:-7])
            new_img = nb.Nifti1Image(dataobj = pp_data_sg_psc, affine = img.affine, header = img.header)
            new_img.to_filename(new_file)
    
        
        # AVERAGE RUNS
        # ------------
        print("{sub}-{acq}: average runs".format(sub = sub_name, acq = acq))
        file_list = sorted(glob.glob("{base_dir}/pp_data/{sub}/func/*{acq}*_sg_psc.nii.gz".format(base_dir = base_dir, sub = sub_name, acq = acq)))
        img = nb.load(file_list[0])
        pp_data_sg_psc_avg = np.zeros(img.shape)
    
        for file in file_list:
            print(file)
            # load
            pp_data_sg_psc = []
            pp_data_sg_psc_img = nb.load(file)
            pp_data_sg_psc = pp_data_sg_psc_img.get_fdata()
            pp_data_sg_psc_avg += pp_data_sg_psc/len(file_list)
        
        # save
        new_file = "{file}_fmriprep_sg_psc_avg.nii.gz".format(file = file[:-30])
        
        new_img = nb.Nifti1Image(dataobj = pp_data_sg_psc_avg, affine = img.affine, header = img.header)
        new_img.to_filename(new_file)

        # AVERAGE MASKS
        # -------------
        file_list2 = sorted(glob.glob("{base_dir}/pp_data/{sub}/func/*{acq}*mask.nii.gz".format(
                                            base_dir = base_dir, sub = sub_name, acq = acq)))

        img_mask = nb.load(file_list2[0])
        mask_avg = np.zeros(img_mask.shape)
        for file2 in file_list2:
            print(file2)

            mask = []
            mask_img = nb.load(file2)
            mask = mask_img.get_fdata()
            mask_avg += mask/len(file_list2)

        mask_avg = np.round(mask_avg)

        # save
        new_file2 = "{file}_fmriprep_mask_avg.nii.gz".format(file = file2[:-19])
        new_img2 = nb.Nifti1Image(dataobj = mask_avg, affine = img_mask.affine, header = img_mask.header)
        new_img2.to_filename(new_file2)