"""
-----------------------------------------------------------------------------------------
fmriprep_sbatch.py
-----------------------------------------------------------------------------------------
Goal of the script:
Run fMRIprep on mesocentre using job mode
-----------------------------------------------------------------------------------------
Input(s):
sys.argv[1]: project name (correspond to directory)
sys.argv[2]: subject (e.g. sub-001)
sys.argv[3]: server nb of hour to request (e.g 10)
sys.argv[4]: anat only (1) or not (0)
sys.argv[5]: use of aroma (1) or not (0)
sys.argv[6]: use Use fieldmap-free distortion correction
sys.argv[7]: skip BIDS validation (1) or not (0)
-----------------------------------------------------------------------------------------
Output(s):
preprocessed files
-----------------------------------------------------------------------------------------
To run:
cd /home/mszinte/projects/PredictEye/mri_analysis/
python pre_fit/fmriprep_sbatch.py PredictEye sub-01 20 0 0 0 1
python pre_fit/fmriprep_sbatch.py PredictEye sub-02 20 0 0 0 1
python pre_fit/fmriprep_sbatch.py PredictEye sub-03 20 0 0 0 1
python pre_fit/fmriprep_sbatch.py PredictEye sub-04 20 0 0 0 1
-----------------------------------------------------------------------------------------
Written by Martin Szinte (martin.szinte@gmail.com)
-----------------------------------------------------------------------------------------
"""

# imports modules
import sys
import os
import time
import ipdb
import json
import ipdb
opj = os.path.join
deb = ipdb.set_trace

# inputs
project_dir = sys.argv[1]
subject = sys.argv[2]
sub_num = subject[-2:]
hour_proc = int(sys.argv[3])
anat = int(sys.argv[4])
aroma = int(sys.argv[5])
fmapfree = int(sys.argv[6])
skip_bids_val = int(sys.argv[7])

# Analysis parameters
with open('settings.json') as f:
    json_s = f.read()
    analysis_info = json.loads(json_s)

# Define cluster/server specific parameters
if cluster_name  == 'skylake':
	base_dir = analysis_info['base_dir']
	main_dir = '/scratch/mszinte/data/'
	singularity_dir = '/scratch/mszinte/softwares/fmriprep-20.0.4.simg'
	nb_procs = 32
	memory_val = 48
	proj_name = 'b161'
	# os.system("rsync -az --no-g --no-p --progress {scratchw}/ {scratch}".format(
	# 			scratch = analysis_info['base_dir'],
	# 			scratchw  = analysis_info['base_dir_westmere']))

elif cluster_name  == 'westmere':
	base_dir = analysis_info['base_dir_westmere'] 
	main_dir = '/scratchw/mszinte/data/'
	singularity_dir = '/scratchw/mszinte/softwares/fmriprep-1.5.0.simg'
	nb_procs = 12
	memory_val = 24
	proj_name = 'westmere'
	# os.system("rsync -az --no-g --no-p --progress {scratch}/ {scratchw}".format(
	# 			scratch = analysis_info['base_dir'],
	# 			scratchw  = base_dir))
log_dir = opj(main_dir,project_dir,'deriv_data','fmriprep','log_outputs')

# special input
anat_only, use_aroma, use_fmapfree, anat_only_end, use_skip_bids_val = '','','','',''
if anat == 1:
	anat_only = ' --anat-only'
	anat_only_end = '_anat'
	nb_procs = 8
if aroma == 1:
	use_aroma = ' --use-aroma'
if fmapfree == 1:
	use_fmapfree= ' --use-syn-sdc'
if skip_bids_val == 1:
	use_skip_bids_val = ' --skip_bids_validation'

# define SLURM cmd
slurm_cmd = """\
#!/bin/bash
#SBATCH --mail-type=ALL
#SBATCH -p skylake
#SBATCH --mail-user=martin.szinte@univ-amu.fr
#SBATCH -A {proj_name}
#SBATCH --nodes=1
#SBATCH --mem={memory_val}gb
#SBATCH --cpus-per-task={nb_procs}
#SBATCH --time={hour_proc}:00:00
#SBATCH -e {log_dir}/{subject}_fmriprep{anat_only_end}_%N_%j_%a.err
#SBATCH -o {log_dir}/{subject}_fmriprep{anat_only_end}_%N_%j_%a.out
#SBATCH -J {subject}_fmriprep{anat_only_end}
#SBATCH --mail-type=BEGIN,END\n\n""".format(proj_name = proj_name, nb_procs = nb_procs, hour_proc = hour_proc, subject = subject,
											anat_only_end = anat_only_end, memory_val = memory_val, log_dir = log_dir)

# define singularity cmd
singularity_cmd = "singularity run --cleanenv -B {main_dir}:/work_dir {simg} --fs-license-file /work_dir/freesurfer/license.txt /work_dir/{project_dir}/bids_data/ /work_dir/{project_dir}/deriv_data/fmriprep/ participant --participant-label {sub_num} -w /work_dir/{project_dir}/temp_data/ --bold2t1w-dof 12 --output-spaces T1w fsaverage MNI152NLin2009cAsym --cifti-output --low-mem --mem-mb 32000 --nthreads {nb_procs:.0f}{anat_only}{use_aroma}{use_fmapfree}{use_skip_bids_val}".format(
									main_dir = main_dir,
									project_dir = project_dir,
									simg = singularity_dir,
									sub_num = sub_num,
									nb_procs = nb_procs,
									anat_only = anat_only,
									use_aroma = use_aroma,
									use_fmapfree = use_fmapfree,
									use_skip_bids_val = use_skip_bids_val)

# create sh folder and file
sh_dir = "{main_dir}/{project_dir}/deriv_data/fmriprep/jobs/sub-{sub_num}_fmriprep.sh".format(main_dir = main_dir, sub_num = sub_num,project_dir = project_dir,)

try:
	os.makedirs(opj(main_dir,project_dir,'deriv_data','fmriprep','jobs'))
	os.makedirs(opj(main_dir,project_dir,'deriv_data','fmriprep','log_outputs'))
except:
	pass
of = open(sh_dir, 'w')
of.write("{slurm_cmd}{singularity_cmd}".format(slurm_cmd = slurm_cmd,singularity_cmd = singularity_cmd))
of.close()

# Submit jobs
print("Submitting {sh_dir} to queue".format(sh_dir = sh_dir))
os.chdir(log_dir)
os.system("sbatch {sh_dir}".format(sh_dir = sh_dir))

