import os
import subprocess
import openpyxl
from datetime import datetime

# 指定数据根目录，请确保数据目录下有sourcedata文件夹
root_folder = r'F:\Public_dataset\ADNI_test'
group_id = 'test'

# 定义原始数据文件夹和rawdata文件夹的路径
sourcedata_folder = os.path.join(root_folder, 'sourcedata')
rawdata_folder = os.path.join(root_folder, 'rawdata')
derivatives_folder = os.path.join(root_folder, 'derivatives')

# 指定要转换的序列名称和对应的名称及输出文件夹
sequence_mapping = {
    'MPRAGE': {'output_name': 'T1w', 'output_folder': 'anat'},
    'SPGR_w_acceleration': {'output_name': 'T1w', 'output_folder': 'anat'},
    'FSPGR': {'output_name': 'T1w', 'output_folder': 'anat'},
    'FLAIR': {'output_name': 'FLAIR', 'output_folder': 'anat'}
}

# 排除的字符
exclude_strings = ['ND', 'ORIG', 'GRAPPA']

# 创建相关文件夹
os.makedirs(rawdata_folder, exist_ok=True)
os.makedirs(derivatives_folder, exist_ok=True)
excel_file_folder = os.path.join(derivatives_folder, 'dcm2nii')
os.makedirs(excel_file_folder, exist_ok=True)
excel_file_path = os.path.join(excel_file_folder, 'conversion_info.xlsx')

# 创建日志文件
log_file_path = os.path.join(excel_file_folder, 'conversion_log.txt')
log_file = open(log_file_path, 'w')

# 创建Excel工作簿和工作表
wb = openpyxl.Workbook()
ws = wb.active
ws.append(["Subject ID", "Original Folder", "Sequence Name", "Timepoint Folder Names"])

# 计数器用于重新编号被试
subject_counter = 1

# 遍历原始数据文件夹
for subject_folder in os.listdir(sourcedata_folder):
    if os.path.isdir(os.path.join(sourcedata_folder, subject_folder)):
        # 重新编号被试
        subject_id = f'sub-{group_id}{str(subject_counter).zfill(4)}'
        subject_counter += 1

        # 初始化记录信息
        original_folder = os.path.join(sourcedata_folder, subject_folder)
        subject_source_folder = os.path.join(sourcedata_folder, subject_folder)

        # 用于收集和排序日期的字典
        date_to_session = {}

        # 第一次遍历：收集特定序列的所有日期
        for sequence_folder in os.listdir(subject_source_folder):
            if any(ex_str in sequence_folder for ex_str in exclude_strings):
                continue

            sequence_folder_path = os.path.join(subject_source_folder, sequence_folder)
            if os.path.isdir(sequence_folder_path):
                for target_sequence in sequence_mapping:
                    if target_sequence in sequence_folder:
                        for check_result_folder in os.listdir(sequence_folder_path):
                            check_result_folder_path = os.path.join(sequence_folder_path, check_result_folder)
                            if os.path.isdir(check_result_folder_path):
                                check_date_str = check_result_folder.split('_')[0]
                                try:
                                    check_date = datetime.strptime(check_date_str, '%Y-%m-%d').date()
                                    date_to_session[check_date] = None
                                except ValueError:
                                    continue
                        break

        # 对日期进行排序并分配session编号
        sorted_dates = sorted(date_to_session.keys())
        for i, date in enumerate(sorted_dates):
            date_to_session[date] = i + 1

        # 第二次遍历：进行数据转换
        for sequence_folder in os.listdir(subject_source_folder):
            if any(ex_str in sequence_folder for ex_str in exclude_strings):
                continue

            sequence_folder_path = os.path.join(subject_source_folder, sequence_folder)
            if os.path.isdir(sequence_folder_path):
                for target_sequence, mapping_info in sequence_mapping.items():
                    if target_sequence in sequence_folder:
                        converted_timepoint_folders = []
                        for check_result_folder in os.listdir(sequence_folder_path):
                            check_result_folder_path = os.path.join(sequence_folder_path, check_result_folder)
                            if os.path.isdir(check_result_folder_path):
                                check_date_str = check_result_folder.split('_')[0]
                                try:
                                    check_date = datetime.strptime(check_date_str, '%Y-%m-%d').date()
                                    if check_date in date_to_session:
                                        session_id = date_to_session[check_date]
                                        formatted_date = check_date.strftime('%Y%m%d')  # 格式化日期
                                    else:
                                        continue
                                except ValueError:
                                    continue

                                session_folder = f'ses-{str(session_id).zfill(2)}_{formatted_date}'
                                output_folder = os.path.join(rawdata_folder, subject_id, session_folder, mapping_info['output_folder'])
                                os.makedirs(output_folder, exist_ok=True)
                                output_file_name = f'{subject_id}_ses-{str(session_id).zfill(2)}_{mapping_info["output_name"]}'
                                dcm2niix_cmd = f'dcm2niix -o {output_folder} -f {output_file_name} -z y {check_result_folder_path}'

                                try:
                                    subprocess.run(dcm2niix_cmd, shell=True, check=True)
                                    converted_timepoint_folders.append(check_result_folder)
                                    log_file.write(f"已将 {check_result_folder} 转换为NIfTI格式，文件名为 {output_file_name}\n")
                                except subprocess.CalledProcessError as e:
                                    log_file.write(f"转换失败，错误信息：{e}\n")

                        timepoint_folders_str = ', '.join(converted_timepoint_folders)
                        ws.append([subject_id, original_folder, sequence_folder, timepoint_folders_str])

# 保存Excel文件和关闭日志文件
wb.save(excel_file_path)
log_file.write(f"批量DICOM转NIfTI转换完成。转换信息已保存到 {excel_file_path}\n")
log_file.close()
print(f"批量DICOM转NIfTI转换完成。转换信息已保存到 {excel_file_path}")
