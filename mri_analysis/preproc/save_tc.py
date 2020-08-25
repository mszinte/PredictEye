"""
-----------------------------------------------------------------------------------------
save_tc.py
-----------------------------------------------------------------------------------------
Goal of the script:
Save time course as pycortex webviewer
-----------------------------------------------------------------------------------------
Input(s):
sys.argv[1]: subject name
sys.argv[2]: Nifti files name end part
-----------------------------------------------------------------------------------------
Output(s):
None
-----------------------------------------------------------------------------------------
To run:
python preproc/save_tc.py sub-01 AttendFixGazeCenterFS_fmriprep_dct_avg
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
import ipdb
opj = os.path.join
deb = ipdb.set_trace

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
subject = sys.argv[1]
tc_file_end = sys.argv[2]

# Define analysis parameters
# --------------------------
with open('settings.json') as f:
    json_s = f.read()
    analysis_info = json.loads(json_s)
base_dir = analysis_info['base_dir']
xfm_name = analysis_info['xfm_name']

# create directory
dataset_dir = "{base_dir}/pp_data/{subject}/pycortex/dataset/tc/".format(
                        base_dir = base_dir, subject = subject)
webviewer_dir = "{base_dir}/pp_data/{subject}/pycortex/webviewer/tc/{tc_file_end}/".format(
                        base_dir = base_dir, subject = subject, tc_file_end = tc_file_end)

try: 
    os.makedirs(dataset_dir)
    os.makedirs(webviewer_dir)
except: pass

tc_file = "{base_dir}/pp_data/{subject}/func/{subject}_task-{tc_file_end}.nii.gz".format(
                        base_dir = base_dir, subject = subject, tc_file_end = tc_file_end)
print('load: {} {}'.format(subject, tc_file_end))

img_tc = nb.load(tc_file)
tc = img_tc.get_data()

# create volume
volume_tc = cortex.Volume(data = tc.transpose((3,2,1,0)), subject = subject,xfmname = xfm_name, cmap = 'BuBkRd', description = 'BOLD')

# create dataset
print('save pycortex dataset: time course')
dataset_tc = cortex.Dataset(data = volume_tc)
dataset_tc.save("{dataset_dir}{tc_file_end}_tc.hdf".format(tc_file_end = tc_file_end,dataset_dir = dataset_dir))
deb()
# create webgl
print('save pycortex webviewer: time course')
cortex.webgl.make_static(outpath = webviewer_dir, data = volume_tc)
