# to run on mesocenter server
# cd ~/projects/PredictEye/mri_analysis
# sh glm/run_glm.sh

#python glm/fit_glm.py /scratch/mszinte/data/PredictEye sub-01 ses-01 SacLoc T1w run-1 fmriprep_dct
#python glm/fit_glm.py /scratch/mszinte/data/PredictEye sub-01 ses-01 PurLoc T1w run-1 fmriprep_dct

python glm/fit_glm.py /scratch/mszinte/data/PredictEye sub-01 ses-03 SacVELoc T1w run-1 fmriprep_dct
python glm/fit_glm.py /scratch/mszinte/data/PredictEye sub-01 ses-03 PurVELoc T1w run-1 fmriprep_dct


for sub in sub-02 sub-03 sub-04 sub-05 sub-06 sub-07 sub-08 sub-09 sub-11 sub-12 sub-13 sub-14 sub-17 sub-20 sub-21 sub-22 sub-23 sub-24 sub-25
do
#python glm/fit_glm.py /scratch/mszinte/data/PredictEye $sub ses-02 SacLoc T1w run-1 fmriprep_dct
#python glm/fit_glm.py /scratch/mszinte/data/PredictEye $sub ses-02 PurLoc T1w run-1 fmriprep_dct
python glm/fit_glm.py /scratch/mszinte/data/PredictEye $sub ses-02 SacVELoc T1w run-1 fmriprep_dct
python glm/fit_glm.py /scratch/mszinte/data/PredictEye $sub ses-02 PurVELoc T1w run-1 fmriprep_dct

done
exit 0