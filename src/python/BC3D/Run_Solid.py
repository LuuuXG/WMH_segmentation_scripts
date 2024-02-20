#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/6/3 15:23
# @Author : SONG-LE
# @知乎 : https://www.zhihu.com/people/xiao-xue-sheng-ye-xiang-xie-shu

import time
import numpy as np
import BoxCountingMethod_Solid
import Draw
import data_excel
import nibabel as nib
import os
# import r_tif

# Set the directory containing the copied files
src_dir = r'F:\Projects\WMH_segmentation\src\python\BC3D'

if __name__ == "__main__":
    # Loop over each file in the directory
    for file_name in os.listdir(src_dir):
        # Check if the file ends with the specific suffix
        if file_name.endswith('HC0001_bbles_0.3_lpa_mFLAIR_periventricular_or_confluent_WMH_registered_to_MNI.nii.gz'):
            name = os.path.join(file_name)

            # 矩阵数据名称
            nii_data = nib.load(name)
            mt=nii_data.get_fdata()

            # name='crack'
            # mt=r_tif.read_tifs_and_stack(
            #     "crack-tif"
            # )

            # 计算分形维数
            start_time=time.time()
            para=BoxCountingMethod_Solid.BC_Solid(mt)
            #print(f'核心算法耗时： {time.time()-start_time}s')

            # 生成图像
            Draw.Draw_SCI(para,name)
            Draw.Draw(para,name)

            # 输出exce数据
            #data_excel.data_save(
            #    para[5],
            #    name
            #)

