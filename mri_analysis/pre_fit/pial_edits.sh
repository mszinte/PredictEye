# rsync to desktop (faster processing)
rsync -az --no-g --no-p --progress mszinte@login.mesocentre.univ-amu.fr:/scratch/mszinte/data/pRFseqTest/deriv_data/ ~/Desktop/temp_data/

# Check + edit pial surface
# https://surfer.nmr.mgh.harvard.edu/fswiki/FsTutorial/PialEdits_freeview

# sub-01
freeview -v ~/Desktop/temp_data/fmriprep/freesurfer/sub-01/mri/T1.mgz \
~/Desktop/temp_data/fmriprep/freesurfer/sub-01/mri/T2.mgz \
~/Desktop/temp_data/fmriprep/freesurfer/sub-01/mri/brainmask.mgz \
-f ~/Desktop/temp_data/fmriprep/freesurfer/sub-01/surf/lh.white:edgecolor=yellow \
~/Desktop/temp_data/fmriprep/freesurfer/sub-01/surf/lh.pial:edgecolor=red \
~/Desktop/temp_data/fmriprep/freesurfer/sub-01/surf/rh.white:edgecolor=yellow \
~/Desktop/temp_data/fmriprep/freesurfer/sub-01/surf/rh.pial:edgecolor=red

# sub-02
freeview -v ~/Desktop/temp_data/fmriprep/freesurfer/sub-02/mri/T1.mgz \
~/Desktop/temp_data/fmriprep/freesurfer/sub-02/mri/T2.mgz \
~/Desktop/temp_data/fmriprep/freesurfer/sub-02/mri/brainmask.mgz \
-f ~/Desktop/temp_data/fmriprep/freesurfer/sub-02/surf/lh.white:edgecolor=yellow \
~/Desktop/temp_data/fmriprep/freesurfer/sub-02/surf/lh.pial:edgecolor=red \
~/Desktop/temp_data/fmriprep/freesurfer/sub-02/surf/rh.white:edgecolor=yellow \
~/Desktop/temp_data/fmriprep/freesurfer/sub-02/surf/rh.pial:edgecolor=red

# conclusion: 
# -----------
# Very good segmentation, few problems with cerebelum but nothing much
# no correction for the pre-test, to edit for future project