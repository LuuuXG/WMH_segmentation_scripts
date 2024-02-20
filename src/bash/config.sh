#!/bin/bash
# config.sh
# for the SynthSeg pipeline

# Set the path of the parent directory
PARENT_DIR="/mnt/f/Public_dataset/ADNI_WMH_seg/DM_20231127/derivatives"
Freesurfer_SUBJECTS_DIR="/usr/local/freesurfer/7-dev/subjects"
SPECIFIED_FILE_NAME="T1_2_FLAIR.nii.gz"
RESULT_CSV_NAME="WMH_SynthSeg_result.csv"
BATCH_SIZE=4
FINAL_CSV="$PARENT_DIR/Final_$RESULT_CSV_NAME"