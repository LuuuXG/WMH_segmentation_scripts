#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/6/2 16:50
# @Author : SONG-LE
# @知乎 : https://www.zhihu.com/people/xiao-xue-sheng-ye-xiang-xie-shu
import xlwt
import os
# 判断数据目录是否存在
fdir='Data'
if not os.path.isdir(fdir):os.mkdir(fdir)

#保存数据
def data_save(data,name):
    '''
    data,[dict{<str>:<lsit>}],输出的数据,键为数据名,键值是数据列表
    name,[str],保存的文件名
    '''
    talbe=xlwt.Workbook(encoding='utf-8')
    sheet=talbe.add_sheet('name')
    for i,text in enumerate(data.keys()):
        # 行，列，数据
        sheet.write(0,i,text)
        for j,item in enumerate(data[text]):
            # 行，列，数据
            sheet.write(j+1,i,item)
    talbe.save('{}\\{}.xls'.format(fdir,name))

def figure_data_save(data,name,n):
    '''
    data,[list[dict{<str>:<lsit>}]],输出的数据,键为数据名,键值是数据列表
    name,[str],保存的文件名
    n,[int],画图数据数量
    '''
    talbe=xlwt.Workbook(encoding='utf-8')
    for i in range(n):
        data_=data[i]
        sheet=talbe.add_sheet('{}'.format(i+1))
        for i,text in enumerate(data_.keys()):
            # 行，列，数据
            sheet.write(0,i,text)
            for j,item in enumerate(data_[text]):
                # 行，列，数据
                sheet.write(j+1,i,item)
    talbe.save('{}\\画图数据_{}.xls'.format(fdir,name))