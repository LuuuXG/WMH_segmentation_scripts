# 分割WMH病灶部位

import os
import nibabel as nib
import numpy as np
from scipy.ndimage import label

derivatives_dir = r'F:\Projects\WMH_segmentation\derivatives'

# 列出所有sub开头的子目录
sub_dirs = [d for d in os.listdir(derivatives_dir) if
            os.path.isdir(os.path.join(derivatives_dir, d)) and d.startswith('sub-')]

threshold = 0.1

for sub_dir in sub_dirs:
    wmh_path = os.path.join(derivatives_dir, sub_dir, f'bles_{threshold}_lpa_mFLAIR.nii.gz')
    masked_wmh_path = os.path.join(derivatives_dir, sub_dir, f'bles_{threshold}_lpa_mFLAIR_masked.nii.gz')
    mask_path = os.path.join(derivatives_dir, sub_dir, 'T1_2_FLAIR.anat', 'T1_biascorr_bianca_mask_orig.nii.gz')
    mask_3mm_nii_path = os.path.join(derivatives_dir, sub_dir, 'T1_2_FLAIR.anat', 'dist_to_vent_periventricular_3mm_orig.nii.gz')
    mask_10mm_nii_path = os.path.join(derivatives_dir, sub_dir, 'T1_2_FLAIR.anat', 'dist_to_vent_periventricular_10mm_orig.nii.gz')
    result_confluent_WMH_nii_path = os.path.join(derivatives_dir, sub_dir, f'bles_{threshold}_lpa_mFLAIR_confluent_WMH.nii.gz')
    result_periventricular_WMH_nii_path = os.path.join(derivatives_dir, sub_dir, f'bles_{threshold}_lpa_mFLAIR_periventricular_WMH.nii.gz')
    result_deep_WMH_nii_path = os.path.join(derivatives_dir, sub_dir, f'bles_{threshold}_lpa_mFLAIR_deep_WMH.nii.gz')
    result_periventricular_or_confluent_WMH_nii_path = os.path.join(derivatives_dir, sub_dir, f'bles_{threshold}_lpa_mFLAIR_periventricular_or_confluent_WMH.nii.gz')

    if os.path.exists(wmh_path):
        print('processing directory: {0}'.format(sub_dir))
        wmh_nii = nib.load(wmh_path)
        wmh_data = wmh_nii.get_fdata()
        wmh_data[np.isnan(wmh_data)] = 0

        bianca_mask_nii = nib.load(mask_path)
        bianca_mask_data = bianca_mask_nii.get_fdata()

        # 应用bianca_mask文件
        wmh_data = np.multiply(wmh_data, bianca_mask_data)

        mask_3mm_nii = nib.load(mask_3mm_nii_path)
        mask_3mm_data = mask_3mm_nii.get_fdata()
        mask_3mm_data[np.isnan(mask_3mm_data)] = 0
        mask_3mm_data = (mask_3mm_data > 0.5).astype(np.int32)

        mask_10mm_nii = nib.load(mask_10mm_nii_path)
        mask_10mm_data = mask_10mm_nii.get_fdata()
        mask_10mm_data[np.isnan(mask_10mm_data)] = 0
        mask_10mm_data = (mask_10mm_data > 0.5).astype(np.int32)

        # 使用scipy的label函数，找到原始WMH图像中的所有连续区域
        labeled_wmh, num_features = label(wmh_data)
        # print(num_features)

        '''
        # 移除小于或等于5个体素的连续区域
        for region_num in range(1, num_features + 1):
            region = (labeled_wmh == region_num)
            if np.sum(region) <= 5:
                wmh_data[region] = 0  # 移除小于或等于5个体素的区域

        labeled_wmh, num_features = label(wmh_data)
        '''

        # 初始化结果数组
        result_confluent_WMH = np.zeros_like(wmh_data)
        result_periventricular_WMH = np.zeros_like(wmh_data)
        result_deep_WMH = np.zeros_like(wmh_data)
        result_periventricular_or_confluent_WMH = np.zeros_like(wmh_data)

        for region_num in range(1, num_features + 1):
            # 提取当前连续区域
            region = (labeled_wmh == region_num).astype(np.int32)

            # 检查区域是否部分落在3mm mask内
            in_3mm = np.any(np.logical_and(region, mask_3mm_data))

            # 检查区域是否部分扩展到10mm mask之外
            out_10mm = np.any(np.logical_and(region, np.logical_not(mask_10mm_data)))

            # confluent WMH：区域部分落在3mm mask内，且部分扩展到10mm mask之外
            if in_3mm and out_10mm:
                result_confluent_WMH = np.logical_or(result_confluent_WMH, region)

            # periventricular WMH：区域部分落在3mm mask内，且没有扩展到10mm mask之外
            if in_3mm and not out_10mm:
                result_periventricular_WMH = np.logical_or(result_periventricular_WMH, region)

            # deep WMH：区域没有落在3mm mask内
            if not in_3mm:
                result_deep_WMH = np.logical_or(result_deep_WMH, region)

            result_periventricular_or_confluent_WMH = np.logical_or(result_confluent_WMH, result_periventricular_WMH)

        # 保存结果
        result_masked_WMH_nii = nib.Nifti1Image(wmh_data, wmh_nii.affine, wmh_nii.header)
        nib.save(result_masked_WMH_nii, masked_wmh_path)

        result_confluent_WMH_nii = nib.Nifti1Image(result_confluent_WMH.astype(np.int32), wmh_nii.affine, wmh_nii.header)
        nib.save(result_confluent_WMH_nii, result_confluent_WMH_nii_path)

        result_periventricular_WMH_nii = nib.Nifti1Image(result_periventricular_WMH.astype(np.int32), wmh_nii.affine, wmh_nii.header)
        nib.save(result_periventricular_WMH_nii, result_periventricular_WMH_nii_path)

        result_deep_WMH_nii = nib.Nifti1Image(result_deep_WMH.astype(np.int32), wmh_nii.affine, wmh_nii.header)
        nib.save(result_deep_WMH_nii, result_deep_WMH_nii_path)

        result_periventricular_or_confluent_WMH_nii = nib.Nifti1Image(result_periventricular_or_confluent_WMH.astype(np.int32), wmh_nii.affine, wmh_nii.header)
        nib.save(result_periventricular_or_confluent_WMH_nii, result_periventricular_or_confluent_WMH_nii_path)

    else:
        print(f"WMH lesion file does not exist in directory: {sub_dir}. Skipping...")
