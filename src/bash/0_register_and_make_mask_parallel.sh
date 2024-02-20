#!/bin/bash

# This script performs the following operations in parallel for each subject directory:
# 1. Register the T1 image to the FLAIR image
# 2. Generate the anatomical-related images and files using "fsl_anat"
# 3. Create a binary mask (using "make_bianca_mask") which is used to exclude areas of the brain that WMH are unlikely to be found
# 4. Generate the dist_to_vent_periventricular mask and transform it to the original space
# 5. Register the T1, FLAIR, and ventricle mask images to the MNI template

# set the directories
PARENT_DIR="/mnt/f/Projects/WMH_segmentation/derivatives" # base directory
MNI_PATH="/usr/local/fsl/data/standard/MNI152_T1_1mm_brain.nii.gz" # MNI template path

# set the maximum number of jobs to run in parallel
MAX_JOBS=12

# set the range of time to run the job
START_HOUR=7
START_MINUTE=31
END_HOUR=7
END_MINUTE=30

job_count=0

for SUB_DIR in "$PARENT_DIR"/*; do
    if [[ $(basename "$SUB_DIR") == sub-* ]]; then
        while true; do
            # calculate the current time and check if it is in the specified time range
            current_total_minutes=$((current_hour * 60 + current_minute))
            start_total_minutes=$((START_HOUR * 60 + START_MINUTE))
            end_total_minutes=$((END_HOUR * 60 + END_MINUTE))

            if (( end_total_minutes < start_total_minutes )); then
                end_total_minutes=$((end_total_minutes + 1440))
            fi

            if (( current_total_minutes < start_total_minutes )); then
                current_total_minutes=$((current_total_minutes + 1440))
            fi

            if (( current_total_minutes >= start_total_minutes && current_total_minutes <= end_total_minutes )); then
                (
                    echo "Processing directory $SUB_DIR"
                    cd "$SUB_DIR"

                    # register the T1 image to the FLAIR image
                    flirt -ref FLAIR.nii -in T1.nii -out T1_2_FLAIR -omat T1_2_FLAIR.mat

                    rt1AnatDir="$SUB_DIR/T1_2_FLAIR.anat"
                    if [[ ! -d $rt1AnatDir ]]; then
                        echo "T1_2_FLAIR_brain.anat directory not found in $SUB_DIR, performing the operation"
                        # fsl_anat: generate anatomical-related images and files
                        fsl_anat -i T1_2_FLAIR --clobber

                        cd $rt1AnatDir
                        # make_bianca_mask: create a binary mask which is used to exclude araes of the brain that WMH are unlikely to be found
                        make_bianca_mask T1_biascorr T1_fast_pve_0 MNI_to_T1_nonlin_field.nii.gz
                        
                        # generate the dist_to_vent_periventricular mask and transform it to the original space
                        distancemap -i T1_biascorr_ventmask.nii.gz -o dist_to_vent
                        fslmaths dist_to_vent -uthr 10 -bin dist_to_vent_periventricular_10mm
                        fslmaths dist_to_vent -uthr 5 -bin dist_to_vent_periventricular_5mm
                        fslmaths dist_to_vent -uthr 3 -bin dist_to_vent_periventricular_3mm
                        fslmaths dist_to_vent -uthr 1 -bin dist_to_vent_periventricular_1mm

                        flirt -in T1_biascorr_bianca_mask -ref T1_orig -out T1_biascorr_bianca_mask_orig -applyxfm -init T1_roi2orig.mat
                        flirt -in T1_biascorr_ventmask -ref T1_orig -out T1_biascorr_ventmask_orig -applyxfm -init T1_roi2orig.mat
                        flirt -in dist_to_vent_periventricular_10mm -ref T1_orig -out dist_to_vent_periventricular_10mm_orig -applyxfm -init T1_roi2orig.mat
                        flirt -in dist_to_vent_periventricular_5mm -ref T1_orig -out dist_to_vent_periventricular_5mm_orig -applyxfm -init T1_roi2orig.mat
                        flirt -in dist_to_vent_periventricular_3mm -ref T1_orig -out dist_to_vent_periventricular_3mm_orig -applyxfm -init T1_roi2orig.mat
                        flirt -in dist_to_vent_periventricular_1mm -ref T1_orig -out dist_to_vent_periventricular_1mm_orig -applyxfm -init T1_roi2orig.mat

                        flirt -in "T1_biascorr_brain_mask.nii.gz" -ref "T1_orig.nii.gz" -out "$SUB_DIR/T1_2_FLAIR_brain_mask.nii.gz" -applyxfm -init T1_roi2orig.mat
                        flirt -in T1_biascorr_ventmask -ref T1_orig -out "$SUB_DIR/T1_biascorr_ventmask_orig.nii.gz" -applyxfm -init T1_roi2orig.mat
                    else
                        echo "T1_2_FLAIR.anat directory already exists in $SUB_DIR, skipping this directory"
                    fi
                    
                    # register the T1, FLAIR, and ventricle mask images to the MNI template
                    cd "$SUB_DIR"
                    fslmaths T1_2_FLAIR -mas T1_2_FLAIR_brain_mask T1_2_FLAIR_brain
                    fslmaths FLAIR.nii -mas T1_2_FLAIR_brain_mask FLAIR_brain
                    
                    flirt -ref $MNI_PATH -in T1_2_FLAIR_brain -out T1_2_MNI_brain -omat FLAIR_2_MNI_brain.mat
                    flirt -ref $MNI_PATH -in FLAIR_brain -applyxfm -init FLAIR_2_MNI_brain.mat -out FLAIR_2_MNI_brain

                    flirt -in T1_biascorr_ventmask_orig -ref $MNI_PATH -out T1_biascorr_ventmask_orig_2_MNI -applyxfm -init FLAIR_2_MNI_brain.mat
                    fslmaths T1_biascorr_ventmask_orig_2_MNI -thr 0.9 -bin T1_biascorr_ventmask_orig_2_MNI
                ) &

                let job_count+=1
                if (( job_count >= MAX_JOBS )); then
                    wait -n
                    let job_count-=1
                fi

                break
            else
                # pall for 10 minutes if not in the specified time range
                echo "Current time is $current_hour. Pausing for 10 minutes..."
                sleep 10m
            fi
        done
    fi
done

wait
echo "All processing complete."
