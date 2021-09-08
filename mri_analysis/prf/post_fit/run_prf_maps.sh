# to run in invibe server
# cd ~/disks/meso_H/projects/PredictEye/mri_analysis/
# sh post_fit/run_prf_maps.sh

for sub in sub-01 sub-02 sub-03 sub-04 sub-05 sub-06 sub-07 sub-08 sub-09 sub-11 sub-12 sub-13 sub-14 sub-17 sub-20 sub-21 sub-22 sub-23 sub-24 sub-25
do
echo $sub
python post_fit/pycortex_maps.py ~/disks/meso_S $sub pRF fmriprep_dct T1w 0

done
exit 0