#!/bin/bash

# Load the shared configuration
source /mnt/f/Codes/WMH_segmentation/src/bash/config.sh

# Create sub-output-temp directory
mkdir -p "$Freesurfer_SUBJECTS_DIR/sub-output-temp"

# Initialize a counter and batch number
COUNT=0
BATCH_NUM=1

# Process each sub-directory and distribute them into different batch folders
for SUB_DIR in "$PARENT_DIR"/*; do
    if [[ $(basename "$SUB_DIR") == sub* ]]; then
        # Define the source file path
        echo "Processing directory $SUB_DIR"
        SOURCE_FILE="$SUB_DIR/$SPECIFIED_FILE_NAME"
        if [ -f "$SOURCE_FILE" ]; then
            # Create a sub-input-temp directory for the batch
            BATCH_INPUT_DIR="$Freesurfer_SUBJECTS_DIR/sub-input-temp-$BATCH_NUM"
            mkdir -p "$BATCH_INPUT_DIR"
            
            # Copy the file into the batch input directory
            DIR_NAME=$(basename "$SUB_DIR")
            DEST_FILE="$BATCH_INPUT_DIR/${DIR_NAME}_$SPECIFIED_FILE_NAME"
            cp "$SOURCE_FILE" "$DEST_FILE"
            
            ((COUNT++))
            if [ $COUNT -eq $BATCH_SIZE ]; then
                COUNT=0
                BATCH_NUM=$((BATCH_NUM+1))
            fi
        else
            echo "File not found in $SUB_DIR"
        fi
    fi
done