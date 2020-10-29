# -----------------------------------------------------------------------------------------
# cortex_cuts.sh
# -----------------------------------------------------------------------------------------
# Goal of the script:
# Run tksurfer to cut the cortex
# -----------------------------------------------------------------------------------------
# Input(s):
# $1: project directory
# $2: subject name (e.g. sub-01)
# $3: hemisphere (lh or rh)
# $3: mesocentre login ID
# -----------------------------------------------------------------------------------------
# Output(s):
# edited brainmask.mgz and orignal brainmask_orog.mgz
# -----------------------------------------------------------------------------------------
# To run:
# 1. cd to function
# >> cd ~/disks/meso_H/projects/PredictEye/mri_analysis/
# 2. run shell command
# sh preproc/cortex_cuts.sh [main directory] [subject name] [hemisphere] [mesocentre_ID]
# -----------------------------------------------------------------------------------------
# Exemple:
# cd ~/disks/meso_H/projects/PredictEye/mri_analysis/
# sh preproc/cortex_cuts.sh /scratch/mszinte/data/PredictEye sub-01 rh mszinte
# -----------------------------------------------------------------------------------------
# Written by Martin Szinte (martin.szinte@gmail.com)
# -----------------------------------------------------------------------------------------

# rsync to desktop (faster processing)
echo "\n>> Copying the files to the desktop"
rsync -azuv  --progress $4@login.mesocentre.univ-amu.fr:$1/deriv_data/fmriprep/freesurfer/$2 ~/Desktop/temp_data/

# Check + edit pial surface
echo "\n>> Proceed to the cortex cuts : https://docs.google.com/document/d/1mbx3EzTEYr4MIROWbgyklW_a7F6B4NX23bvk7VM7zeY/edit"
echo "\n>> When you are done, save the patch as '$3.full.patch.3d'\n"

# on local computer with freeview 6 and 7 install
export FREESURFER_HOME=/Applications/freesurfer/
export SUBJECTS_DIR=~/Desktop/temp_data/
source $FREESURFER_HOME/SetUpFreeSurfer.sh

tksurfer $2 $3 inflated -curv -annotation aparc.a2009s