import os
import nibabel as nib
import numpy as np
import pandas as pd
from scipy.ndimage import label, sum

# Load the list of subjects from the Excel file
subjects_file = r'E:\Projects\WMH_segmentation\data_analysis\data\ALL_for_analysis.xlsx'
subjects_df = pd.read_excel(subjects_file)
mapped_real_names = subjects_df['MRI ID'].tolist()

derivatives_dir = r'E:\Projects\WMH_segmentation\derivatives'
sub_dirs = [d for d in os.listdir(derivatives_dir) if
            os.path.isdir(os.path.join(derivatives_dir, d)) and d in mapped_real_names]

# create a 'Population' directory if it doesn't exist
if not os.path.exists(os.path.join(derivatives_dir, 'Population')):
    os.makedirs(os.path.join(derivatives_dir, 'Population'))
population_dir = os.path.join(derivatives_dir, 'Population')

# Initialize arrays to accumulate the data
PWMH_sum = None
DWMH_sum = None
count = 0
min_voxels = 5

for sub_dir in sub_dirs:
    PWMH_path = os.path.join(derivatives_dir, sub_dir, 'bles_0.1_lpa_mFLAIR_periventricular_or_confluent_WMH_2_MNI.nii.gz')
    PWMH_nii = nib.load(PWMH_path)
    PWMH_data = PWMH_nii.get_fdata()
    labeled_PWMH, num_features_PWMH = label(PWMH_data)
    volume = sum(PWMH_data, labeled_PWMH, range(num_features_PWMH + 1))
    remove = volume < min_voxels
    remove_indices = np.where(remove)[0]
    for idx in remove_indices:
        PWMH_data[labeled_PWMH == idx] = 0


    DWMH_path = os.path.join(derivatives_dir, sub_dir, 'bles_0.1_lpa_mFLAIR_deep_WMH_2_MNI.nii.gz')
    DWMH_nii = nib.load(DWMH_path)
    DWMH_data = DWMH_nii.get_fdata()
    labeled_DWMH, num_features_DWMH = label(DWMH_data)
    volume = sum(DWMH_data, labeled_DWMH, range(num_features_DWMH + 1))
    remove = volume < min_voxels
    remove_indices = np.where(remove)[0]
    for idx in remove_indices:
        DWMH_data[labeled_DWMH == idx] = 0

    if PWMH_sum is None:
        PWMH_sum = PWMH_data
        DWMH_sum = DWMH_data
    else:
        PWMH_sum += PWMH_data
        DWMH_sum += DWMH_data

    count += 1

# Calculate the average
PWMH_avg = PWMH_sum / count
DWMH_avg = DWMH_sum / count

# Save the average data as a new NIfTI file
avg_PWMH_nii = nib.Nifti1Image(PWMH_avg, PWMH_nii.affine)
nib.save(avg_PWMH_nii, os.path.join(population_dir, 'average_PWMH.nii.gz'))

sum_PWMH_nii = nib.Nifti1Image(PWMH_sum, PWMH_nii.affine)
nib.save(sum_PWMH_nii, os.path.join(population_dir, 'sum_PWMH.nii.gz'))

avg_DWMH_nii = nib.Nifti1Image(DWMH_avg, DWMH_nii.affine)
nib.save(avg_DWMH_nii, os.path.join(population_dir, 'average_DWMH.nii.gz'))

sum_DWMH_nii = nib.Nifti1Image(DWMH_sum, DWMH_nii.affine)
nib.save(sum_DWMH_nii, os.path.join(population_dir, 'sum_DWMH.nii.gz'))
