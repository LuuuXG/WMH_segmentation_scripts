#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/6/3 15:20
# @Author : SONG-LE
# @知乎 : https://www.zhihu.com/people/xiao-xue-sheng-ye-xiang-xie-shu
import numpy as np
from numpy import poly1d
from numpy import polyfit


def BoxCounting(MT, EPSILON):
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
    return len(
        np.where((MT_BOX_2 > 0) & (MT_BOX_2 < EPSILON ** 3))[0]
    )

def BC_Solid(mt):
    '''
    :param mt:三维实体的空间矩阵,0代表孔隙,1代表实体
    :return:
    '''

    #
    # 2.盒子(立方体)覆盖算法
    #
    # 盒子数列表
    Nl=[]
    # 矩阵最短边
    M=np.min(mt.shape)
    # 循环算法
    epsilonl=[2**i for i in range(1,int(np.log(M/2)/np.log(2))+1)]
    for epsilon in epsilonl:
        # 三个维度循环
        N=BoxCounting(mt,epsilon)
        # 累计数据
        Nl.append(N)

    #
    # 3. 输出并处理数据
    #
    x = np.log(
        np.array([1 / epsilon for epsilon in epsilonl])
    )
    y = np.log(Nl)
    coeff = polyfit(x,y,1)
    f = poly1d(coeff)
    #print('拟合方程: {}'.format(f))
    #print(coeff[0])
    Pearson_R=np.corrcoef(y, f(x))[0, 1]
    Pearson_R2=Pearson_R**2

    out_data={
        '盒子数N':Nl,
        'log(N)': y,
        '尺度数epsilon':epsilonl,
        '1/epsilon':[1 / epsilon for epsilon in epsilonl],
        'log(1/epsilon)':x,
        '拟合曲线一次项系数':[coeff[0]],
        '拟合曲线常数项':[coeff[1]],
        '拟合曲线皮尔逊相关系数R':[Pearson_R],
        '拟合曲线皮尔逊相关系数R^2': [Pearson_R2],

    }
    #for item in out_data.items():print(item)

    return [
        x,
        y,
        f,
        coeff,
        Pearson_R2,
        out_data,
        mt
    ]