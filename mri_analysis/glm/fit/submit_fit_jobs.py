"""
-----------------------------------------------------------------------------------------
submit_fit_jobs.py
-----------------------------------------------------------------------------------------
Goal of the script:
Create jobscript to fit GLM
-----------------------------------------------------------------------------------------
Input(s):
sys.argv[1]: subject name (e.g. sub-01)
sys.argv[2]: registration (e.g. T1w, fsLR_den-170k)
sys.argv[3]: pre-processing steps (fmriprep_dct or fmriprep_dct_pca)
sys.argv[4]: cifti data mode (subc: subcortical, surf: surface)
-----------------------------------------------------------------------------------------
Output(s):
.sh file to execute in server
-----------------------------------------------------------------------------------------
To run:
>> cd to function
>> python fit/submit_fit_jobs.py [subject] [registration] [preproc] [cifti-mode]
-----------------------------------------------------------------------------------------
Exemple:
cd /home/mszinte/projects/PredictEye/mri_analysis/
python glm/fit/submit_fit_jobs.py sub-01 T1w fmriprep_dct
python glm/fit/submit_fit_jobs.py sub-01 fsLR_den-170k fmriprep_dct surf
python glm/fit/submit_fit_jobs.py sub-01 fsLR_den-170k fmriprep_dct subc
python glm/fit/submit_fit_jobs.py sub-01 T1w fmriprep_dct_pca
python glm/fit/submit_fit_jobs.py sub-01 fsLR_den-170k fmriprep_dct_pca surf
python glm/fit/submit_fit_jobs.py sub-01 fsLR_den-170k fmriprep_dct_pca subc
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
import json
import sys
import nibabel as nb
import datetime
import ipdb
deb = ipdb.set_trace

# Settings
# --------
# Inputs
subject = sys.argv[1]
regist_type = sys.argv[2]
preproc = sys.argv[3]
if regist_type == 'fsLR_den-170k':
    cifti_mode= sys.argv[4]
    if cifti_mode == 'surf': file_ext,sh_end = '.npy','_surface'
    elif cifti_mode == 'subc': file_ext,sh_end = '_subc.npy','_subcortical'
else:
    file_ext = '.nii.gz'
    sh_end = ''

# Analysis parameters
with open('settings.json') as f:
    json_s = f.read()
    analysis_info = json.loads(json_s)

# Cluster settings
base_dir = analysis_info['base_dir']
sub_command = 'sbatch '
nb_procs = 8
job_dur = "00:30:00"
proj_name = 'b161'
glm_tasks = analysis_info['glm_task_names']

print("GLM analysis: running on Skylake")

# Create job and log output folders
for task in glm_tasks:
    if task == 'pMF':
        data_types = ['run-1','run-2','run-3','run-4','run-5','avg']
    else: 
        data_types = ['run-1','run-2','avg']
        
    for data_type in data_types:
    
        # define tc input / glm fit / glm tc prediction
        log_dir = '{base_dir}/pp_data_new/{sub}/glm/log_outputs'.format(base_dir=base_dir, sub=subject)

        if data_type == 'avg':
            input_fn = "{base_dir}/pp_data_new/{sub}/func/{sub}_task-{task}_space-{reg}_{preproc}_{data_type}{file_ext}".format(
                            base_dir=base_dir, sub=subject, reg=regist_type, preproc=preproc, data_type=data_type, file_ext=file_ext, task=task)
            fit_fn = "{base_dir}/pp_data_new/{sub}/glm/fit/{sub}_task-{task}_space-{reg}_{preproc}_glm-fit{file_ext}".format(
                            base_dir=base_dir, sub=subject, reg=regist_type, preproc=preproc, data_type=data_type, file_ext=file_ext, task=task)
            pred_fn = "{base_dir}/pp_data_new/{sub}/glm/fit/{sub}_task-{task}_space-{reg}_{preproc}_glm-pred{file_ext}".format(
                            base_dir=base_dir, sub=subject, reg=regist_type, preproc=preproc, data_type=data_type, file_ext=file_ext, task=task)
        
        else:
            input_fn = "{base_dir}/pp_data_new/{sub}/func/{preproc}/{sub}_task-{task}_{data_type}_space-{reg}_{preproc}{file_ext}".format(
                            base_dir=base_dir, sub=subject, reg=regist_type, preproc=preproc, data_type=data_type, file_ext=file_ext, task=task)
            fit_fn = "{base_dir}/pp_data_new/{sub}/glm/fit/{sub}_task-{task}_{data_type}_space-{reg}_{preproc}_glm-fit{file_ext}".format(
                            base_dir=base_dir, sub=subject, reg=regist_type, preproc=preproc, data_type=data_type, file_ext=file_ext, task=task)
            pred_fn = "{base_dir}/pp_data_new/{sub}/glm/fit/{sub}_task-{task}_{data_type}_space-{reg}_{preproc}_glm-pred{file_ext}".format(
                            base_dir=base_dir, sub=subject, reg=regist_type, preproc=preproc, data_type=data_type, file_ext=file_ext, task=task)
    
        if os.path.isfile(fit_fn):
            if os.path.getsize(fit_fn) != 0:
                print("output file {} already exists and is non-empty: aborting analysis".format(fit_fn))
                continue
    
        # create job shell
        slurm_cmd = """\
#!/bin/bash
#SBATCH -p skylake
#SBATCH -A {proj_name}
#SBATCH --nodes=1
#SBATCH --cpus-per-task={nb_procs}
#SBATCH --time={job_dur}
#SBATCH -e {log_dir}/{sub}_task-{task}_space-{reg}_{preproc}_{data_type}_fit_%N_%j_%a.err
#SBATCH -o {log_dir}/{sub}_task-{task}_space-{reg}_{preproc}_{data_type}_fit_%N_%j_%a.out
#SBATCH -J {sub}_task-{task}_space-{reg}_{preproc}_{data_type}_fit\n\n""".format(
        proj_name=proj_name, nb_procs=nb_procs, task=task,
        log_dir=log_dir, job_dur=job_dur, sub=subject,
        reg=regist_type, preproc=preproc, data_type=data_type)

        # define fit cmd
        fit_cmd = "python glm/fit/glm_fit.py {sub} {task} {reg} {preproc} {input_fn} {fit_fn} {pred_fn}".format(
                    sub=subject, reg=regist_type, preproc=preproc, input_fn=input_fn, 
                    fit_fn=fit_fn, pred_fn=pred_fn, task=task)
    
        # create sh folder and file
        sh_dir = "{base_dir}/pp_data_new/{sub}/glm/jobs/{sub}_task-{task}_space-{reg}_{preproc}_{data_type}{sh_end}.sh".format(
                    base_dir=base_dir, sub=subject, reg=regist_type, preproc=preproc, data_type=data_type, sh_end=sh_end, task=task)

        try:
            os.makedirs('{}/pp_data_new/{}/glm/fit/'.format(base_dir,subject))
            os.makedirs('{}/pp_data_new/{}/glm/jobs/'.format(base_dir,subject))
            os.makedirs('{}/pp_data_new/{}/glm/log_outputs/'.format(base_dir,subject))
        except:
            pass

        of = open(sh_dir, 'w')
        of.write("{slurm_cmd}{fit_cmd}".format(slurm_cmd=slurm_cmd, fit_cmd=fit_cmd))
        of.close()

        # Submit jobs
        print("Submitting {sh_dir} to queue".format(sh_dir=sh_dir))
        os.system("{sub_command} {sh_dir}".format(sub_command=sub_command, sh_dir=sh_dir))
    