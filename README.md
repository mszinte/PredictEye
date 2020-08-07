## PredictEye
By :      Martin SZINTE<br/>
With :    Vanessa Morita, Anna Montagnini & Guillaume Masson<br/>
Version:  1.0<br/>

## Version description
Set of 5 experiments to determine the retinotopic organisation of the human<br/>
brain visual and oculomotor retinotopy in order to determine predictive process of<br/>
the ocumotor system.<br/>

## Task
1. RSexp: resting state task<br/>
2. pRFexp: population receptive field task<br/>
3. pMFexp: population motor field task<br/>
4. locEMexp: saccade and smooth pursuit localiser task<br/>

## mri_analysis
* run mriqc on mesocentre using mri_analysis/pre_fit/mriqc_sbatch<br/>
* run fmriprpep with anat-only option on mesocentre using mri_analysis/pre_fit/fmriprep_sbatch.py<br/>
* make a "before_edit" video of the fmriprep/freesurfer segmentation using mri_analysis/pre_fit/freeview.py<br>
* run freesurfer-dev version to use t2w image for the pial surface using pre_fit/freesurfer_dev.py<br/>
* make a "after_fs_dev" video of the fmriprep/freesurfer segmentation using mri_analysis/pre_fit/freeview.py<br>
* manual edition of the pial surface using freeview launched with /pre_fit/pial_edits.py and following the rules of http://surfer.nmr.mgh.harvard.edu/fswiki/FsTutorial/PialEditsV6.0 <br/>
* re-run freesurfer-dev version to use t2w image for the pial surface using pre_fit/freesurfer_dev.py<br/>


* make a "after_manual" video of the fmriprep/freesurfer segmentation using mri_analysis/pre_fit/freeview.py<br>
* run fmriprpep on mesocentre using mri_analysis/pre_fit/fmriprep_sbatch.py<br/>

## behav_analysis
1. RSexp:<br/>
2. pRFexp:<br/> 
3. pMFexp:<br/>
4. locEMexp:<br/>