#!/bin/bash

# Set the path of the parent directory
PARENT_DIR="/mnt/f/Public_dataset/ADNI_WMH_seg/DM_20231127/derivatives"
Freesurfer_SUBJECTS_DIR="/usr/local/freesurfer/7-dev/subjects"
SPECIFIED_FILE_NAME="T1_2_FLAIR.nii.gz"
RESULT_CSV_NAME="WMH_SynthSeg_result.csv"
BATCH_SIZE=4

# Create the sub-input-temp and sub-output-temp directories
mkdir -p "$Freesurfer_SUBJECTS_DIR/sub-input-temp"
mkdir -p "$Freesurfer_SUBJECTS_DIR/sub-output-temp"

# Initialize a counter and batch number
COUNT=0
BATCH_NUM=1
FINAL_CSV="$PARENT_DIR/Final_$RESULT_CSV_NAME"

# Process each sub-directory
for SUB_DIR in "$PARENT_DIR"/*; do
    if [[ $(basename "$SUB_DIR") == sub* ]]; then
        echo "Processing directory $SUB_DIR"
        SOURCE_FILE="$SUB_DIR/$SPECIFIED_FILE_NAME"
        if [ -f "$SOURCE_FILE" ]; then
            DIR_NAME=$(basename "$SUB_DIR")
            DEST_FILE="$Freesurfer_SUBJECTS_DIR/sub-input-temp/${DIR_NAME}_$SPECIFIED_FILE_NAME"
            cp "$SOURCE_FILE" "$DEST_FILE"
            ((COUNT++))

            if [ $COUNT -eq $BATCH_SIZE ]; then
                # Run mri_WMHsynthseg for the batch
                mri_WMHsynthseg --i "$Freesurfer_SUBJECTS_DIR/sub-input-temp" \
                                --o "$Freesurfer_SUBJECTS_DIR/sub-output-temp" \
                                --device cuda --crop \
                                --save_lesion_probabilities \
                                --csv_vols "$Freesurfer_SUBJECTS_DIR/sub-output-temp/$RESULT_CSV_NAME"
                
                BATCH_CSV="$Freesurfer_SUBJECTS_DIR/sub-output-temp/${BATCH_NUM}_$RESULT_CSV_NAME"
                mv "$Freesurfer_SUBJECTS_DIR/sub-output-temp/$RESULT_CSV_NAME" "$BATCH_CSV"

                # Clear the sub-input-temp for the next batch
                rm -rf "$Freesurfer_SUBJECTS_DIR/sub-input-temp"
                mkdir -p "$Freesurfer_SUBJECTS_DIR/sub-input-temp"

                # Increment batch number
                BATCH_NUM=$((BATCH_NUM+1))
                COUNT=0
            fi
        else
            echo "File not found in $SUB_DIR"
        fi
    fi
done

# Process the remaining files in the last batch if any
if [ $COUNT -gt 0 ]; then
    mri_WMHsynthseg --i "$Freesurfer_SUBJECTS_DIR/sub-input-temp" \
                    --o "$Freesurfer_SUBJECTS_DIR/sub-output-temp" \
                    --device cuda --crop \
                    --save_lesion_probabilities \
                    --csv_vols "$Freesurfer_SUBJECTS_DIR/sub-output-temp/$RESULT_CSV_NAME"

    # Rename and move the last batch result CSV
    BATCH_CSV="$Freesurfer_SUBJECTS_DIR/sub-output-temp/${BATCH_NUM}_$RESULT_CSV_NAME"
    mv "$Freesurfer_SUBJECTS_DIR/sub-output-temp/$RESULT_CSV_NAME" "$BATCH_CSV"
fi

# Combine all CSV files into one
first=true
for i in $(seq 1 $BATCH_NUM); do
    BATCH_CSV="$Freesurfer_SUBJECTS_DIR/sub-output-temp/${i}_$RESULT_CSV_NAME"
    if [ -f "$BATCH_CSV" ]; then
        if $first; then
            cat "$BATCH_CSV" > "$FINAL_CSV"
            first=false
        else
            tail -n +2 "$BATCH_CSV" >> "$FINAL_CSV"
        fi
    fi
done

# 遍历sub-output-temp目录中的每个输出文件
for OUTPUT_FILE in "$Freesurfer_SUBJECTS_DIR/sub-output-temp"/*; do
    FILE_NAME=$(basename "$OUTPUT_FILE")

    # Skip the batch result CSV files
    if [[ "$FILE_NAME" == *"_$RESULT_CSV_NAME" ]]; then
        continue # Skip the iteration if it's a result CSV file
    fi
    
    # Extract the original directory name
    ORIGINAL_DIR_NAME=$(echo "$FILE_NAME" | cut -d '_' -f 1,2,3) #需要修改！！！

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

rm -rf "$Freesurfer_SUBJECTS_DIR/sub-input-temp"
rm -rf "$Freesurfer_SUBJECTS_DIR/sub-output-temp"

echo "Processing complete. Temporary folders removed."