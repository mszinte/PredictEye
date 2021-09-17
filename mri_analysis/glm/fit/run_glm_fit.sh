# to run in mesocenter server
# cd ~/projects/PredictEye/mri_analysis/
# sh glm/fit/run_glm_fit.sh sub-01

echo $1
python glm/fit/submit_fit_jobs.py $1 T1w fmriprep_dct
python glm/fit/submit_fit_jobs.py $1 fsLR_den-170k fmriprep_dct surf
python glm/fit/submit_fit_jobs.py $1 fsLR_den-170k fmriprep_dct subc
python glm/fit/submit_fit_jobs.py $1 T1w fmriprep_dct_pca
python glm/fit/submit_fit_jobs.py $1 fsLR_den-170k fmriprep_dct_pca surf
python glm/fit/submit_fit_jobs.py $1 fsLR_den-170k fmriprep_dct_pca subc
