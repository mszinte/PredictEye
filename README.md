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
* make a "before_edit" video of the fmriprep/freesurfer segmentation using mri_analysis/pre_fit/freeview.py<br/>

## behav_analysis
1. RSexp:<br/>
2. pRFexp:<br/> 
3. pMFexp:<br/>
4. locEMexp:<br/>