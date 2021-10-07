# __*PredictEye*__
By :      Martin SZINTE & Vanessa MORITA <br>
With :    Anna MONTAGNINI & Guillaume MASSON<br>
Version:  1.0<br>

# Version description
Set of 5 experiments to determine the retinotopic organisation of the human
brain visual and oculomotor retinotopy in order to determine predictive process of
the ocumotor system.

# Task
1. RSexp: resting state task
2. pRFexp: population receptive field task
3. pMFexp: population motor field task
4. locEMexp: saccade and smooth pursuit localiser task
5. locVisEndEMexp: saccade and smooth pursuit without stimulus localiser task

# MRI Analysis

## Data curation
1. transfer behavioral to XNAT
2. convert to BIDS in XNAT
3. edit fmap json files
4. transfer data to server
4. check BIDS validity

## Pre-processing
1. run mriqc on mesocentre using _mri_analysis/preproc/mriqc_sbatch.py_
3. run fmriprpep with anat-only option on mesocentre using _mri_analysis/preproc/fmriprep_sbatch.py_
4. make a "before_edit" video of the fmriprep/freesurfer segmentation using _mri_analysis/preproc/freeview.py_<br>
5. manual edition of the pial surface using freeview launched with /preproc/pial_edits.sh and following these [rules](http://surfer.nmr.mgh.harvard.edu/fswiki/FsTutorial/PialEditsV6.0) 
6. re-run freesurfer to include the manual change of the pial surface using _preproc/freesurfer_pial.py_
7. make a "after_edit" video of the fmriprep/freesurfer segmentation using _mri_analysis/preproc/freeview.py_<br>
8. Cut brainsflat following this [document](https://docs.google.com/document/d/1mbx3EzTEYr4MIROWbgyklW_a7F6B4NX23bvk7VM7zeY/edit)
9. Flatten hemispheres with _preproc/flatten_sbatch.py_
10. Import in pycortex with _preproc/pycortex_import.py_
11. run pybest (modified to save niftis) to high pass filter and denoised the data with _/preproc/pybest_sbatch.py_
12. copy files in pp_data and average task runs (including leave-one-out procedure) together with _preproc/preproc_end.py_
13. (optional) Save time courses as pycortex webviewer with _preproc/save_tc.py_

## Post-processing

### pRF
  1. run the prf fit with _prf/fit/run_prf_fit.sh_
  2. compute pRF parameters and leave-one-out cross-validated r2 with _prf/post_fit/run_post_fit.sh_
  3. make pycortex maps using with _prf/post_fit/run_prf_maps.sh_
  4. draw ROIs using on overlays using Inkscape
  5. create hdf files per roi using _post_fit/roi_to_hdf5.py_
  6. create pandas files per roi using _post_fit/hdf5_to_pandas.py_

### pMF/PurLoc/SacLoc/SacVELoc/PurVELoc
  1. compute motor design with _glm/fit/pmf_design.py_ 
  2. run the prf fit with _glm/fit/submit_fit.py_
  3. combine fits and compute pRF parameters with _glm/post_fit/post_fit.py_
  4. make pycortex maps using _post_fit/pycortex_maps.py_
  5. adjust ROIs using on overlays using Inkscape
  6. create hdf files per roi using _post_fit/roi_to_hdf5.py_
  7. create pandas files per roi using _post_fit/hdf5_to_pandas.py_

## Behaviral_analysis
  1. RSexp:
  2. pRFexp:
  3. pMFexp:
  4. locEMexp:
  5. locVisEndEMexp:

### GLMs
  0. compute glm design with _glm/fit/gen_glm_design.py_
  1. run the prf fit with _fit/run_prf_fit.sh_ 
  2. compute pRF parameters and leave-one-out cross-validated r2 with _post_fit/run_post_fit.sh_
  3. make pycortex maps using with _post_fit/run_prf_maps.sh_
  
  1. Compute GLM for each tasks with _glm/fit_glm.py_ or with _glm/run_glm.sh_
  2. Plot and save flatmaps with _glm/pycortex_glm.py_ or with _glm/run_glm_maps.sh_

### Webgl
  1. Combine PRF and GLM analysis in single webgl per subject using _webgl/pycortex_webgl.py_ or _webgl/run_webgl.sh_
  2. send index.py to webapp using _webgl/send_index.sh_
  