"""
-----------------------------------------------------------------------------------------
mriqc_srun.py
-----------------------------------------------------------------------------------------
Goal of the script:
Run frmiqc on tmux on mesocentre with tmux using an interactive mode
-----------------------------------------------------------------------------------------
Input(s):
sys.argv[1]: main project directory
sys.argv[2]: bids subject num (e.g. 01)
sys.argv[3]: server nb of processor to use (e.g 4)
-----------------------------------------------------------------------------------------
Output(s):
QC html files
-----------------------------------------------------------------------------------------
To run:
1. connect to interactive node on skylake
>> srun -p skylake --time=10:00:0 --pty bash -i
2. tmux the session
>> tmux
2. cd to function
>> cd /scratch/mszinte/projects/pRFseqTest/mri_analysis/pre_fit/
3. run python command
python mriqc_srun.py [main directory] [subject num] [nb processors]
-----------------------------------------------------------------------------------------
Written by Martin Szinte (martin.szinte@gmail.com)
-----------------------------------------------------------------------------------------
"""

# imports modules
import sys
import os
import time
import platform

# inputs
main_dir = sys.argv[1]
sub_num = sys.argv[2]
nb_procs = int(sys.argv[3])
singularity_dir = '/scratch/mszinte/softwares/mriqc-0.15.1.simg'

# define singularity command
singularity_cmd = "singularity run --bind {main_dir}:/work_dir {dir} /work_dir/bids_data/ /work_dir/deriv_data/mriqc/ participant --participant_label {sub_num} -w /work_dir/temp_data/ --n_procs {nb_procs:.0f} --verbose-reports --mem_gb 64 -m bold T1w T2w --no-sub".format(
									main_dir = main_dir,
									dir =singularity_dir, 
									sub_num = sub_num,
									nb_procs = nb_procs,
									)

# run singularity
print('run MRIQC singularity on {plaform}'.format(plaform = platform.node()))
os.system("{cmd}".format(cmd = singularity_cmd))
time.sleep(2)
