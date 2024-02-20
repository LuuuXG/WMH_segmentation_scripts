#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/6/3 15:23
# @Author : SONG-LE
# @知乎 : https://www.zhihu.com/people/xiao-xue-sheng-ye-xiang-xie-shu
'''
封装画图的算法
'''
import matplotlib.pyplot as plt
import numpy as np
import os
import scienceplots

# 判断图片目录是否存在
#fdir = r'E:\Projects\WMH_segmentation\derivatives\sub-HC0151\shape_features'
#if not os.path.isdir(fdir):
#    os.mkdir(fdir)

def simple(MT,EPSILON):
    # 以EPSILON 行为一组,合并三维矩阵的行
    MT_BOX_0 = np.add.reduceat(MT,
                               np.arange(0, MT.shape[0], EPSILON),
                               axis=0)
    # 以EPSILON 列为一组,合并三维矩阵的列
    MT_BOX_1 = np.add.reduceat(MT_BOX_0,
                               np.arange(0, MT.shape[1], EPSILON),
                               axis=1)
    # 以EPSILON 为一组,合并三维矩阵的第三维度
    MT_BOX_2 = np.add.reduceat(MT_BOX_1,
                               np.arange(0, MT.shape[2], EPSILON),
                               axis=2)
    return MT_BOX_2

def Draw_SCI(para, path):
    '''
        画图用函数,将分维算法与 成图可视化 部分分开.
        para,[list],各种参数的列表,由下列参数组成:
            demon,[matrix],原图像二维矩阵
            Nrl,[matrix or list],盒子数一维矩阵或列表
            rl,[matrix or list],尺度数一维矩阵或列表
            x,[matrix or list],尺度对数化
            y,[matrix or list],盒子数对数化
            f,拟合出的函数
            coeff,一次多项式拟合后的参数,包括斜率和常数项
        '''
    # 参数传递
    x = para[0]
    y = para[1]
    f = para[2]
    coeff = para[3]
    Pearson_R2 = para[4]
    Z = para[6]

    with plt.style.context(['science','no-latex']):  # reference: https://blog.csdn.net/weixin_45896923/article/details/121143445 ; https://mp.weixin.qq.com/s/k3byVK4E_3_uYKIzTKxM_Q
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
        plt.rcParams['axes.unicode_minus'] = False

        # 创建一个画布窗口
        fig = plt.figure(figsize=(10, 6))

        # 图1: 三维曲面3d体素图
        ax1 = fig.add_subplot(121, projection='3d')
        epsilon = min(Z.shape)
        ax1.voxels(np.where(simple(Z, epsilon // 20) > 0, 1, 0),alpha=0.3)
        ax1.set_title('Solid Image 3D (Simplified)')
        ax1.axis('off')  # 不显示坐标轴
        # # 图1: 三维曲面3d点云图
        # ax1 = fig.add_subplot(121, projection='3d')
        # rr = simple(Z, 8)
        # cord = np.where(rr != 0)
        # c_ = rr[cord]
        # ax1.scatter(cord[0], cord[1], cord[2], c_, s=0.3, cmap='jet', c=c_)
        # ax1.set_facecolor((0.5, 0.5, 0.5))
        # ax1.axis('off')

        # 图2: 拟合图象
        ax2 = fig.add_subplot(122)
        # 画图
        ax2.grid(which="major", axis="both")
        ax2.plot(x, y, 'r^', label='Original Scatter', markerfacecolor='white')
        ax2.set_xlabel(r'$ \log ( \frac{1}{\epsilon} ) $', fontsize=14)
        ax2.set_ylabel('$ \log ( N_{\epsilon} )$', fontsize=12)
        ax2.plot(x, f(x), 'c', label='Fit curve')
        ax2.text(
            np.min(x) + 0.2 * (np.min(x) - np.min(x)),
            np.max(y) - 0.2 * (np.max(y) - np.min(y)),
            r'$ln(N_r)={:.4f}ln(\frac{{1}}{{r}})+{:.4f}${}$R^2= {:.4f} \qquad D={:.4f}$'.format(
                coeff[0], coeff[1], '\n', Pearson_R2, coeff[0]),
            fontsize=14,
            bbox={'facecolor': 'blue', 'alpha': 0.2}
        )
        ax2.legend()
        # 排版
        fig.tight_layout()
        # 保存图像
        fig.savefig(path, dpi=300)
    plt.close()

def Draw(para,name):
    '''
    画图用函数,将分维算法与 成图可视化 部分分开.
    para,[list],各种参数的列表,由下列参数组成:
        demon,[matrix],原图像二维矩阵
        Nrl,[matrix or list],盒子数一维矩阵或列表
        rl,[matrix or list],尺度数一维矩阵或列表
        x,[matrix or list],尺度对数化
        y,[matrix or list],盒子数对数化
        f,拟合出的函数
        coeff,一次多项式拟合后的参数,包括斜率和常数项
    '''
    # 参数传递
    x=para[0]
    y=para[1]
    f=para[2]
    coeff=para[3]
    Pearson_R2=para[4]
    Z=para[6]

    #### 显示用
    # 创建一个画布窗口
    fig = plt.figure(figsize=(14, 6))
    # # 图1: 三维曲面3d图
    ax1 = fig.add_subplot(121, projection='3d')
    epsilon = min(Z.shape)
    ax1.voxels(np.where(simple(Z, epsilon // 20) > 0, 1, 0), alpha=0.3)
    ax1.set_title('Solid Image 3D (Simplified)')
    ax1.axis('off')  # 不显示坐标轴
    # 图1: 三维曲面3d点云图
    # ax1 = fig.add_subplot(121, projection='3d')
    # rr = simple(Z, 8)
    # cord = np.where(rr != 0)
    # c_ = rr[cord]
    # ax1.scatter(cord[0], cord[1], cord[2], c_, s=0.3, cmap='jet', c=c_)
    # ax1.set_facecolor((0.5, 0.5, 0.5))
    # ax1.axis('off')

    # 图2: 拟合图象
    ax2 = fig.add_subplot(122)
    # 画图
    ax2.grid(which="major", axis="both")
    ax2.plot(x, y, 'r^',label='Original Scatter',markerfacecolor='white')
    ax2.set_xlabel(r'$ \log ( \frac{1}{\epsilon} ) $', fontsize=14)
    ax2.set_ylabel('$ \log ( N_{\epsilon} )$', fontsize=12)
    ax2.plot(x, f(x), 'c',label='Fit curve')
    ax2.text(
        np.min(x)+0.2*(np.min(x)-np.min(x)),
        np.max(y)-0.2*(np.max(y)-np.min(y)),
        r'$ln(N_r)={:.4f}ln(\frac{{1}}{{r}})+{:.4f}${}$R^2= {:.4f} \qquad D={:.4f}$'.format(
            coeff[0], coeff[1], '\n', Pearson_R2,coeff[0]),
        fontsize=14,
        bbox={'facecolor': 'blue', 'alpha': 0.2}
    )
    ax2.legend()
    # 显示图像
    #plt.show()
    #plt.close()