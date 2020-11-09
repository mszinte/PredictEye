## PredictEye
By :      Martin SZINTE & Vanessa MORITA <br/>
With :    Anna MONTAGNINI & Guillaume MASSON<br/>
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
5. locVisEndEMexp: saccade and smooth pursuit without stimulus localiser task<br/>

## MRI Analysis

# data curation
1. transfer behavioral to XNAT<br/>
2. convert to BIDS in XNAT<br/>
3. edit fmap json files<br/>
4. transfer data to server<br/>
4. check BIDS validity<br/>

# pre-processing
1. run mriqc on mesocentre using mri_analysis/preproc/mriqc_sbatch.py<br/>
3. run fmriprpep with anat-only option on mesocentre using mri_analysis/preproc/fmriprep_sbatch.py<br/>
4. make a "before_edit" video of the fmriprep/freesurfer segmentation using mri_analysis/preproc/freeview.py<br>
5. manual edition of the pial surface using freeview launched with /preproc/pial_edits.sh and following the rules of http://surfer.nmr.mgh.harvard.edu/fswiki/FsTutorial/PialEditsV6.0 <br/>
6. re-run freesurfer to include the manual change of the pial surface using preproc/freesurfer_pial.py<br/>
7. make a "after_edit" video of the fmriprep/freesurfer segmentation using mri_analysis/preproc/freeview.py<br>
8. Cut brainsflat with https://docs.google.com/document/d/1mbx3EzTEYr4MIROWbgyklW_a7F6B4NX23bvk7VM7zeY/edit<br/>
9. Flatten hemispheres with preproc/flatten_sbatch.py<br/>
10. Import in pycortex with preproc/pycortex_import.py<br/>
11. run pybest (modified to save niftis) to high pass filter and denoised the data with /preproc/pybest_sbatch.py<br/>
12. Save time courses as pycortex webviewer<br/>


## behav_analysis
1. RSexp:<br/>
2. pRFexp:<br/>
3. pMFexp:<br/>
4. locEMexp:<br/>
5. locVisEndEMexp:<br/>