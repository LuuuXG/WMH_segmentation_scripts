#!/bin/bash

# This script performs the following operations for each subject directory:
# 1. Save the WMH volume quantification results to a txt file
# 2. Register the WMH mask image to the MNI template

# set the directories
PARENT_DIR="/mnt/f/Projects/WMH_segmentation/derivatives"
MNI_PATH="/usr/local/fsl/data/standard/MNI152_T1_1mm_brain.nii.gz"

for SUB_DIR in "$PARENT_DIR"/*; do
    if [[ $(basename "$SUB_DIR") == sub* ]]; then
        echo "Processing directory $SUB_DIR"
        cd "$SUB_DIR" || exit

        WMH_Dir="$SUB_DIR/bles_0.1_lpa_mFLAIR.nii.gz" # WMH file path, generated by LST
        if [[ -f $WMH_Dir ]]; then
            resultsFile="$SUB_DIR/WMH_volume_quantification_results_5_voxels.txt"

            # save the WMH volume quantification results to a txt file
            echo -e "\nTotal WMH (masked)" >> "$resultsFile"
            TWMH=$(bianca_cluster_stats bles_0.1_lpa_mFLAIR_masked.nii.gz 0.9 5)
            echo "$TWMH" >> "$resultsFile"

            echo -e "\nPWMH" >> "$resultsFile"
            PWMH=$(bianca_cluster_stats bles_0.1_lpa_mFLAIR_periventricular_or_confluent_WMH.nii.gz 0.9 5)
            echo "$PWMH" >> "$resultsFile"

            echo -e "\nDWMH" >> "$resultsFile"
            DWMH=$(bianca_cluster_stats bles_0.1_lpa_mFLAIR_deep_WMH.nii.gz 0.9 5)
            echo "$DWMH" >> "$resultsFile"

            # register the WMH mask image to the MNI template
            flirt -in bles_0.1_lpa_mFLAIR_masked -ref $MNI_PATH -out bles_0.1_lpa_mFLAIR_masked_2_MNI -applyxfm -init FLAIR_2_MNI_brain.mat
            fslmaths bles_0.1_lpa_mFLAIR_masked_2_MNI -thr 0.5 -bin bles_0.1_lpa_mFLAIR_masked_2_MNI

            flirt -in bles_0.1_lpa_mFLAIR_periventricular_or_confluent_WMH -ref $MNI_PATH -out bles_0.1_lpa_mFLAIR_periventricular_or_confluent_WMH_2_MNI -applyxfm -init FLAIR_2_MNI_brain.mat
            fslmaths bles_0.1_lpa_mFLAIR_periventricular_or_confluent_WMH_2_MNI -thr 0.5 -bin bles_0.1_lpa_mFLAIR_periventricular_or_confluent_WMH_2_MNI

            flirt -in bles_0.1_lpa_mFLAIR_deep_WMH -ref $MNI_PATH -out bles_0.1_lpa_mFLAIR_deep_WMH_2_MNI -applyxfm -init FLAIR_2_MNI_brain.mat
            fslmaths bles_0.1_lpa_mFLAIR_deep_WMH_2_MNI -thr 0.5 -bin bles_0.1_lpa_mFLAIR_deep_WMH_2_MNI

            fslmaths bles_0.1_lpa_mFLAIR_periventricular_or_confluent_WMH_2_MNI -mul T1_biascorr_ventmask_orig_2_MNI overlap
            fslmaths T1_biascorr_ventmask_orig_2_MNI -sub overlap T1_biascorr_ventmask_orig_2_MNI
            rm overlap.nii.gz
        else
            echo "WMH file not found in $SUB_DIR" >&2
        fi
    fi
done
