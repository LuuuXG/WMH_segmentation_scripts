#%%
# set parameters
import nibabel as nib
import matplotlib.pyplot as plt
import numpy as np
import os

derivatives_dir = r'F:\Public_dataset\ADNI_WMH_seg\NDM_20231127\derivatives'
sub_dirs = [d for d in os.listdir(derivatives_dir) if
            os.path.isdir(os.path.join(derivatives_dir, d)) and d.startswith('sub-')]

for sub_dir in sub_dirs:
    QC_dir = os.path.join(derivatives_dir, 'QC')
    # 如果QC文件夹不存在，则创建
    if not os.path.exists(QC_dir):
        os.makedirs(QC_dir)

#%%
# 展示FLAIR和WMH
# QC

for sub_dir in sub_dirs:
    flair_path = os.path.join(derivatives_dir, sub_dir, 'FLAIR.nii')
    flair_image = nib.load(flair_path)
    flair_data = flair_image.get_fdata()

    wmh_path = os.path.join(derivatives_dir, sub_dir, 'bles_0.3_lpa_mFLAIR_masked.nii.gz')
    wmh_image = nib.load(wmh_path)
    wmh_data = wmh_image.get_fdata()

    WMH_sum = np.sum(wmh_data, axis=(0, 1))  # 1,2是x,y轴，相当于把x,y轴压缩，WMH_sum只有一维
    max_sum_slice_index = np.argmax(WMH_sum)  # 找到值最大的层面

    # 选择具有最大WMH总和的切片
    flair_slice = flair_data[:, :, max_sum_slice_index]
    wmh_slice = wmh_data[:, :, max_sum_slice_index]

    # 创建RGBA颜色图层
    wmh_overlay = np.zeros((wmh_slice.shape[0], wmh_slice.shape[1], 4))  # 4代表RGBA
    wmh_overlay[:, :, 0] = 1  # R通道为红色
    wmh_overlay[:, :, 3] = wmh_slice  # A通道，透明度，病灶部分为1

    # 调整数组的维度
    wmh_overlay = np.transpose(wmh_overlay, (1, 0, 2))

    # 创建一个图形来显示两个子图
    fig, axs = plt.subplots(1, 2, figsize=(12, 6), facecolor='black',
                            gridspec_kw={'wspace': 0.05, 'hspace': 0})

    # 子图1：原始FLAIR图像
    axs[0].imshow(flair_slice.T, cmap='gray', origin='lower')
    axs[0].set_title(f'Original FLAIR - Slice {max_sum_slice_index}', color='white', size = 20)
    axs[0].axis('off')

    # 子图2：带有病灶高亮的FLAIR图像
    axs[1].imshow(flair_slice.T, cmap='gray', origin='lower')
    axs[1].imshow(wmh_overlay, origin='lower')  # 叠加病灶高亮
    axs[1].set_title(f'FLAIR with WMH Overlay - Slice {max_sum_slice_index}', color='white', size = 20)
    axs[1].axis('off')

    #plt.show()

    save_path = os.path.join(QC_dir, f'{sub_dir}_FLAIR_and_WMH.png')
    plt.savefig(save_path)

    plt.close()

#%%
#----------------------------------------------
# 展示T1
'''
file_path = r'F:\Projects\WMH_segmentation\derivatives\sub-HC0151\rT1.nii'
image = nib.load(file_path)
data = image.get_fdata()
slice_index = 78 # T1L86

min_display_intensity = 10
max_display_intensity = 550

plt.imshow(data[:, :, slice_index].T, cmap='gray', origin='lower',
           vmin=min_display_intensity, vmax=max_display_intensity)
plt.title(f'Slice at z={slice_index} with adjusted contrast')
plt.axis('off')

save_path = r'F:\Projects\WMH_segmentation\data_analysis\output\figure\rT1_slice_image.png' # 请替换为您希望保存的路径和文件名

plt.savefig(save_path, bbox_inches='tight', pad_inches=0)
'''