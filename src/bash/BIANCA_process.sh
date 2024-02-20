#!/bin/bash

# Use FSL BIANCA to perform the WMH segmentation

# set the directories
PARENT_DIR="/mnt/f/Public_dataset/ADNI_test/derivatives"
cd $PARENT_DIR

subject_dirs=($(ls -d $PARENT_DIR/sub*))

# set the training set subjects (1-indexed)
train_subjects=(1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20)

training_nums=$(IFS=,; echo "${train_subjects[*]}")

subject_num=0

for subject_dir in "${subject_dirs[@]}"; do
    ((subject_num++))
    echo "Processing directory $subject_dir"
    
    # check if the subject is in the training set
    # currently, BIANCA can only be performed on one single subject at a time 
    if [[ ! " ${train_subjects[@]} " =~ " ${subject_num} " ]]; then
        output_dir="${subject_dir}/bianca_output"
        bianca_cmd="bianca --singlefile="$PARENT_DIR/masterfile.txt" --querysubjectnum=${subject_num} --brainmaskfeaturenum=2 --labelfeaturenum=4 --trainingnums=${training_nums} --featuresubset=1,2 --matfeaturenum=3 --trainingpts=2000 --nonlespts=10000 --selectpts=noborder -o ${output_dir} –v"
        eval $bianca_cmd
    fi
done