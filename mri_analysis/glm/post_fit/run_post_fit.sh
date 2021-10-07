# to run in mesocenter server
# cd ~/projects/PredictEye/mri_analysis/
# sh glm/post_fit/run_post_fit.sh sub-01

echo $1
python glm/post_fit/post_fit.py $1 T1w fmriprep_dct
python glm/post_fit/post_fit.py $1 fsLR_den-170k fmriprep_dct surf
python glm/post_fit/post_fit.py $1 fsLR_den-170k fmriprep_dct subc
python glm/post_fit/post_fit.py $1 T1w fmriprep_dct_pca
python glm/post_fit/post_fit.py $1 fsLR_den-170k fmriprep_dct_pca surf
python glm/post_fit/post_fit.py $1 fsLR_den-170k fmriprep_dct_pca subc