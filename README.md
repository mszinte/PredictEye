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

## MRI Analysis

# pre-processing
* get data from Xnat in bids format, check all data present, add fmap "IntendedFor" parameters, check BIDS validity
* run mriqc on mesocentre using mri_analysis/preproc/mriqc_sbatch.py<br/>
* run fmriprpep with anat-only option on mesocentre using mri_analysis/preproc/fmriprep_sbatch.py<br/>
* make a "before_edit" video of the fmriprep/freesurfer segmentation using mri_analysis/preproc/freeview.py<br>
* manual edition of the pial surface using freeview launched with /preproc/pial_edits.py and following the rules of http://surfer.nmr.mgh.harvard.edu/fswiki/FsTutorial/PialEditsV6.0 <br/>
* re-run freesurfer to include the manual change of the pial surface using preproc/freesurfer_pial.py<br/>
* make a "after_edit" video of the fmriprep/freesurfer segmentation using mri_analysis/preproc/freeview.py<br>
* Cut brains with https://docs.google.com/document/d/1mbx3EzTEYr4MIROWbgyklW_a7F6B4NX23bvk7VM7zeY/edit<br/>
* Flatten hemispheres with preproc/flatten_sbatch.py<br/>
* Import in pycortex and save t1w/t2w maps as pycortex webviewer
* run pybest (modified to save niftis) to high pass filter and denoised the data with /preproc/pybest_sbatch.py
* Save time courses as pycortex webviewer

## behav_analysis
1. RSexp:<br/>
2. pRFexp:<br/>
3. pMFexp:<br/>
4. locEMexp:<br/>
5. locVisEndEMexp:<br/>