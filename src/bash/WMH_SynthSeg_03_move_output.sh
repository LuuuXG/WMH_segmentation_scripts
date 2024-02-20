#!/bin/bash

# Load the shared configuration
source /mnt/f/Codes/WMH_segmentation/src/bash/config.sh

# Combine all CSV files into one
first=true
BATCH_NUM=1

while true; do
    BATCH_CSV="$Freesurfer_SUBJECTS_DIR/sub-output-temp/${BATCH_NUM}_$RESULT_CSV_NAME"
    if [ -f "$BATCH_CSV" ]; then
        if $first; then
            cat "$BATCH_CSV" > "$FINAL_CSV"
            first=false
        else
            tail -n +2 "$BATCH_CSV" >> "$FINAL_CSV"
        fi
        BATCH_NUM=$((BATCH_NUM+1))
    else
        break
    fi
done

# Move other output files to their respective directories
for OUTPUT_FILE in "$Freesurfer_SUBJECTS_DIR/sub-output-temp"/*; do
    FILE_NAME=$(basename "$OUTPUT_FILE")

    # Skip the result CSV files
    if [[ "$FILE_NAME" == *"_${RESULT_CSV_NAME}" ]]; then
        continue
    fi
    
    # Extract the original directory name
    ORIGINAL_DIR_NAME=$(echo "$FILE_NAME" | cut -d '_' -f 1,2,3)

    # Define the original directory path
    ORIGINAL_DIR="$PARENT_DIR/$ORIGINAL_DIR_NAME"

    # Check if the original directory exists
    if [ -d "$ORIGINAL_DIR" ]; then
        # Define the new file name
        NEW_FILE_NAME=$(echo "$FILE_NAME" | sed "s/${ORIGINAL_DIR_NAME}_//")

        # Copy the file to the original directory and rename it
        cp "$OUTPUT_FILE" "$ORIGINAL_DIR/$NEW_FILE_NAME"
    else
        echo "Original directory $ORIGINAL_DIR does not exist"
    fi
done

# Clean up the sub-output-temp directory
rm -rf "$Freesurfer_SUBJECTS_DIR/sub-output-temp"

echo "Processing complete. Output files moved and temporary folders removed."
