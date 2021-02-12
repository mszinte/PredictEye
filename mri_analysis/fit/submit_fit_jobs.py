"""
-----------------------------------------------------------------------------------------
submit_fit_jobs.py
-----------------------------------------------------------------------------------------
Goal of the script:
Create jobscript to fit pRFs
-----------------------------------------------------------------------------------------
Input(s):
sys.argv[1]: subject name (e.g. sub-01)
sys.argv[2]: pre-processing steps (fmriprep_dct or fmriprep_dct_pca)
sys.argv[3]: registration type (e.g. T1w)
-----------------------------------------------------------------------------------------
Output(s):
.sh file to execute in server
-----------------------------------------------------------------------------------------
To run:
>> cd to function
>> python fit/submit_fit_fs_jobs.py [subject] [preproc] [registration]
-----------------------------------------------------------------------------------------
Exemple:
cd /home/mszinte/projects/PredictEye/mri_analysis/
python fit/submit_fit_jobs.py sub-01 fmriprep_dct T1w
python fit/submit_fit_jobs.py sub-01 fmriprep_dct_pca T1w
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
import numpy as np
import os
import glob
import json
import sys
import nibabel as nb
import platform
# import ipdb
import datetime
# deb = ipdb.set_trace
opj = os.path.join

# Settings
# --------
# Inputs
subject = sys.argv[1]
preproc = sys.argv[2]
regist_type = sys.argv[3]

# Analysis parameters
with open('settings.json') as f:
    json_s = f.read()
    analysis_info = json.loads(json_s)

# Cluster settings
base_dir = analysis_info['base_dir']
sub_command = 'sbatch '
fit_per_hour = 6000.0
nb_procs = 32
memory_val = 48
proj_name = 'b161'

print("pRF analysis: running on Skylake")

# Create job and log output folders
try:
    os.makedirs(opj(base_dir, 'pp_data', subject, 'gauss', 'jobs'))
    os.makedirs(opj(base_dir, 'pp_data', subject, 'gauss', 'log_outputs'))
except:
    pass

# Determine data to analyse
data_file = "{base_dir}/pp_data/{sub}/func/{sub}_task-pRF_space-{reg}_{preproc}_avg.nii.gz".format(
                        base_dir = base_dir, sub = subject, reg = regist_type, preproc = preproc)

img_data = nb.load(data_file)
data = img_data.get_fdata()
data_var = np.var(data,axis=3)
mask = data_var!=0.0
slices = np.arange(mask.shape[2])[mask.sum(axis=(0,1))>0]



for slice_nb in slices:

    num_vox = mask[:, :, slice_nb].sum()
    job_dur = str(datetime.timedelta(hours = np.ceil(num_vox/fit_per_hour)))

    # Define output file
    opfn = "{base_dir}/pp_data/{subject}/gauss/fit/{subject}_task-pRF_space-{reg}_{preproc}_avg_est_z_{slice_nb}.nii.gz".format(
                                base_dir = base_dir,
                                subject = subject,
                                reg = regist_type,
                                preproc = preproc,             
                                slice_nb = slice_nb)
    log_dir = opj(base_dir,'pp_data',subject,'gauss','log_outputs')

    if os.path.isfile(opfn):
        if os.path.getsize(opfn) != 0:
            print("output file {opfn} already exists and is non-empty. aborting analysis of slice {slice_nb}".format(
                                opfn = opfn,
                                slice_nb = slice_nb))
            continue

        # create job shell

    slurm_cmd = """\
#!/bin/bash
#SBATCH -p skylake
#SBATCH -A {proj_name}
#SBATCH --nodes=1
#SBATCH --mem={memory_val}gb
#SBATCH --cpus-per-task={nb_procs}
#SBATCH --time={job_dur}
#SBATCH -e {log_dir}/{subject}_task-pRF_space-{reg}_{preproc}_fit_slice_{slice_nb}_%N_%j_%a.err
#SBATCH -o {log_dir}/{subject}_task-pRF_space-{preproc}_fit_slice_{slice_nb}_%N_%j_%a.out
#SBATCH -J {subject}_task-pRF_space-{reg}_{preproc}_fit_slice_{slice_nb}\n\n""".format(
                                            proj_name = proj_name,
                                            nb_procs = nb_procs,
                                            memory_val = memory_val,
                                            log_dir = log_dir,
                                            job_dur = job_dur,
                                            subject = subject,
                                            reg = regist_type,
                                            preproc = preproc,
                                            slice_nb = slice_nb)

    
    # define fit cmd
    fit_cmd = "python fit/prf_fit.py {subject} {preproc} {slice_nb} {reg} {opfn}".format(
                subject = subject,
                preproc = preproc,
                slice_nb = slice_nb,
                reg = regist_type,
                opfn = opfn)
    
    # create sh folder and file
    sh_dir = "{base_dir}/pp_data/{subject}/gauss/jobs/{subject}_task-pRF_space-{reg}_{preproc}_fit_slice_{slice_nb}.sh".format(
                base_dir = base_dir,
                subject = subject,
                reg = regist_type,
                preproc = preproc,
                slice_nb = slice_nb)

    try:
        os.makedirs(opj(base_dir,'pp_data',subject,'gauss','fit'))
        os.makedirs(opj(base_dir,'pp_data',subject,'gauss','jobs'))
        os.makedirs(opj(base_dir,'pp_data',subject,'gauss','log_outputs'))
    except:
        pass

    of = open(sh_dir, 'w')
    of.write("{slurm_cmd}{fit_cmd}".format(slurm_cmd = slurm_cmd,fit_cmd = fit_cmd))
    of.close()

    # Submit jobs
    print("Submitting {sh_dir} to queue".format(sh_dir = sh_dir))
    os.system("{sub_command} {sh_dir}".format(sub_command = sub_command, sh_dir = sh_dir))
    
    