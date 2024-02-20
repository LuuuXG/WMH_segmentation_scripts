#!/bin/bash

# Load the shared configuration
source /mnt/f/Codes/WMH_segmentation/src/bash/config.sh

# Find the lowest numbered batch input directory that still exists
lowest_batch_num=$(find "$Freesurfer_SUBJECTS_DIR" -type d -name 'sub-input-temp-*' | sed -E 's/.*sub-input-temp-([0-9]+)/\1/' | sort -n | head -1)
BATCH_NUM=${lowest_batch_num:-1} # Start from 1 if no directories are found

# Process each batch starting from the lowest existing batch number
while true; do
    BATCH_INPUT_DIR="$Freesurfer_SUBJECTS_DIR/sub-input-temp-$BATCH_NUM"
    if [ -d "$BATCH_INPUT_DIR" ]; then
        echo "Processing $BATCH_INPUT_DIR..."
        # Run mri_WMHsynthseg for the current batch
        mri_WMHsynthseg --i "$BATCH_INPUT_DIR" \
                        --o "$Freesurfer_SUBJECTS_DIR/sub-output-temp" \
                        --device cuda --crop \
                        --save_lesion_probabilities \
                        --csv_vols "$Freesurfer_SUBJECTS_DIR/sub-output-temp/${BATCH_NUM}_$RESULT_CSV_NAME"
        
        # Remove the processed batch input directory
        rm -rf "$BATCH_INPUT_DIR"
        
        BATCH_NUM=$((BATCH_NUM+1))
    else
        # If the directory does not exist, check if we have processed all batches
        if [ -z "$lowest_batch_num" ] || [ $BATCH_NUM -gt $lowest_batch_num ]; then
            echo "No more batches to process or missing batch folders starting from batch number $BATCH_NUM."
            break
        fi
        # If some batches are missing, increment BATCH_NUM to check the next one
        BATCH_NUM=$((BATCH_NUM+1))
    fi
done
