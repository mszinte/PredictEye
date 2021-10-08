# to run in invibe server
# cd ~/disks/meso_H/projects/PredictEye/mri_analysis/
# sh glm/post_fit/run_pycortex_maps.sh sub-01

echo $1
ipython glm/post_fit/pycortex_maps.py $1 T1w fmriprep_dct 0
ipython glm/post_fit/pycortex_maps.py $1 fsLR_den-170k fmriprep_dct 0
ipython glm/post_fit/pycortex_maps.py $1 T1w fmriprep_dct_pca 0
ipython glm/post_fit/pycortex_maps.py $1 fsLR_den-170k fmriprep_dct_pca 0