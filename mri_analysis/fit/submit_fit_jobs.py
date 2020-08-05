"""
-----------------------------------------------------------------------------------------
submit_fit_jobs
-----------------------------------------------------------------------------------------
Goal of the script:
create jobscript to run locally or in a cluster
-----------------------------------------------------------------------------------------
Input(s):
sys.argv[1]: cluster name ('skylake','westmere','debug')
sys.argv[2]: subject name (e.g. 'sub-01')
sys.argv[3]: acquisition (e.g. 'acq-2p5mm','acq-2mm')
sys.argv[4]: fit model ('gauss','css')
-----------------------------------------------------------------------------------------
Output(s):
.sh file to execute in server
-----------------------------------------------------------------------------------------
Exemple:
cd /scratch/mszinte/projects/pRFseqTest/mri_analysis/
python fit/submit_fit_jobs.py debug sub-01 acq-2p5mm gauss
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
import ipdb
import datetime
deb = ipdb.set_trace
opj = os.path.join

# Settings
# ----------
# Inputs
cluster_name = sys.argv[1]
subject = sys.argv[2]
acq = sys.argv[3]
fit_model = sys.argv[4]

# Analysis parameters
with open('settings.json') as f:
    json_s = f.read()
    analysis_info = json.loads(json_s)

# Cluster settings
base_dir = analysis_info['base_dir']
sub_command = 'sbatch '
if cluster_name  == 'skylake':
    fit_per_hour = 1250.0
    nb_procs = 32
    proj_name = 'a161'
    # copy data from /scratchw to /scratch
    os.system("rsync -az --no-g --no-p --progress {scratchw}/ {scratch}".format(
                scratch = analysis_info['base_dir'],
                scratchw  = analysis_info['base_dir_westmere']))
elif cluster_name  == 'westmere':
    base_dir = analysis_info['base_dir_westmere'] 
    fit_per_hour = 800.0
    nb_procs = 12
    proj_name = 'westmere'
    # copy data from /scratch to /scratchw
    os.system("rsync -az --no-g --no-p --progress {scratch}/ {scratchw}".format(
        scratch = analysis_info['base_dir'],
        scratchw  = base_dir))
    
elif cluster_name == 'debug':
    sub_command = 'sh '
    fit_per_hour = 200.0
    nb_procs = 1

jobscript__file = opj(os.getcwd(),'fit',"{}_jobscript_template.sh".format(cluster_name))
print("pRF analysis: running on {}".format(cluster_name))

# Create job and log output folders
try:
    os.makedirs(opj(base_dir, 'pp_data', subject, fit_model, 'jobs'))
    os.makedirs(opj(base_dir, 'pp_data', subject, fit_model, 'log_outputs'))
except:
    pass


# Determine data to analyse
data_file  =  "{base_dir}/pp_data/{sub}/func/{sub}_task-AttendStim_{acq}_fmriprep_sg_psc_avg.nii.gz".format(
                                base_dir = base_dir,
                                sub = subject,
                                acq = acq)
img_data = nb.load(data_file)
data = img_data.get_fdata()

mask_file  =  "{base_dir}/pp_data/{sub}/func/{sub}_task-AttendStim_{acq}_fmriprep_mask_avg.nii.gz".format(
                                base_dir = base_dir,
                                sub = subject,
                                acq = acq)

img_mask = nb.load(mask_file)
mask = img_mask.get_fdata()
slices = np.arange(mask.shape[2])[mask.mean(axis=(0,1))>0]


for slice_nb in slices:

    num_vox = mask[:, :, slice_nb].sum()
    job_dur = str(datetime.timedelta(hours = np.ceil(num_vox/fit_per_hour)))

    # Define output file
    opfn = "{base_dir}/pp_data/{subject}/{fit_model}/fit/{subject}_task-AttendStim_{acq}_est_z_{slice_nb}.nii.gz".format(
                                base_dir = base_dir,
                                subject = subject,
                                fit_model = fit_model,
                                acq = acq,
                                slice_nb = slice_nb
                                )
    log_dir = opj(base_dir,'pp_data',subject,fit_model,'log_outputs')

    if os.path.isfile(opfn):
        if os.path.getsize(opfn) != 0:
            print("output file {opfn} already exists and is non-empty. aborting analysis of slice {slice_nb}".format(
                                opfn = opfn,
                                slice_nb = slice_nb))
            continue

    # create job shell
    if cluster_name != 'debug':
        slurm_cmd = """\
#!/bin/bash
#SBATCH -p {cluster_name}
#SBATCH -A {proj_name}
#SBATCH --nodes=1
#SBATCH --cpus-per-task={nb_procs}
#SBATCH --time={job_dur}
#SBATCH -e {log_dir}/{subject}_{acq}_fit_slice_{slice_nb}_%N_%j_%a.err
#SBATCH -o {log_dir}/{subject}_{acq}_fit_slice_{slice_nb}_%N_%j_%a.out
#SBATCH -J {subject}_{acq}_fit_slice_{slice_nb}\n\n""".format(
                    cluster_name = cluster_name,        proj_name = proj_name,
                    nb_procs = nb_procs,                log_dir = log_dir,
                    job_dur = job_dur,                  subject = subject,
                    acq = acq,                          slice_nb = slice_nb)

    else:
        slurm_cmd = ""

    # define fit cmd
    fit_cmd = "python fit/prf_fit.py {cluster_name} {fit_model} {subject} {data_file} {mask_file} {slice_nb} {opfn}".format(
                cluster_name = cluster_name,
                fit_model = fit_model,
                subject = subject,
                data_file = data_file,
                mask_file = mask_file,
                slice_nb = slice_nb,
                opfn = opfn)

    
    # create sh folder and file
    sh_dir = "{base_dir}/pp_data/{subject}/{fit_model}/jobs/{subject}_{acq}_fit_slice_{slice_nb}.sh".format(
                base_dir = base_dir,
                subject = subject,
                fit_model = fit_model,
                acq = acq,
                slice_nb = slice_nb)

    try:
        os.makedirs(opj(base_dir,'pp_data',subject,fit_model,'fit'))
        os.makedirs(opj(base_dir,'pp_data',subject,fit_model,'jobs'))
        os.makedirs(opj(base_dir,'pp_data',subject,fit_model,'log_outputs'))
    except:
        pass

    of = open(sh_dir, 'w')
    of.write("{slurm_cmd}{fit_cmd}".format(slurm_cmd = slurm_cmd,fit_cmd = fit_cmd))
    of.close()

    # Submit jobs
    print("Submitting {sh_dir} to queue".format(sh_dir = sh_dir))
    os.system("{sub_command} {sh_dir}".format(sub_command = sub_command, sh_dir = sh_dir))
    