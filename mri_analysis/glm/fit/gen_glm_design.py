"""
-----------------------------------------------------------------------------------------
gen_glm_design.py
-----------------------------------------------------------------------------------------
Goal of the script:
Create GLM design of each tasks
-----------------------------------------------------------------------------------------
Input(s):
none
-----------------------------------------------------------------------------------------
Output(s):
.tsv glm design files
-----------------------------------------------------------------------------------------
To run:
>> cd to function directory
>> python glm/fit/gen_glm_design.py
-----------------------------------------------------------------------------------------
Exemple:
cd /home/mszinte/projects/PredictEye/mri_analysis/
python glm/fit/gen_glm_design.py
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
import os
import json
import ipdb
deb = ipdb.set_trace

# Utils import
# ------------
from utils.utils import eventsMatrix

# Define analysis parameters
# --------------------------
with open('settings.json') as f:
    json_s = f.read()
    analysis_info = json.loads(json_s)

base_dir = analysis_info['base_dir']
subject = 'sub-02' # example subject
session = 'ses-02' # session for all subjects
tr = analysis_info['TR']

glm_tasks = analysis_info['glm_task_names']
for task in glm_tasks:
    design_file = '{base_dir}/bids_data/{subject}/{session}/func/{subject}_{session}_task-{task}_run-01_events.tsv'.\
                    format(base_dir=base_dir, subject=subject, session=session, task=task)
        
    events_glm = eventsMatrix(design_file=design_file, task=task, tr=tr)
    output_fn = '{base_dir}/pp_data_new/glm_dm/{task}_dm.tsv'.format(base_dir=base_dir, task=task)
    events_glm.to_csv(output_fn, sep = '\t', float_format='%.1f')
        