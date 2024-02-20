import numpy as np
from scipy.spatial import ConvexHull, Delaunay
from skimage.measure import marching_cubes, mesh_surface_area
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import nibabel as nib
import os
import pandas as pd
from scipy.ndimage import label, sum
import math
from BC3D import BoxCountingMethod_Solid, FD_plot

# Function to plot three views in a row without axes 病灶可视化
# 可视化PWMH、DWMH、和脑室的三维图像
# 1：PWMH，2：DWMH，3：侧脑室
def plot_three_views_in_row(vertices1, faces1, vertices2, faces2, vertices3, faces3, angles):
    fig = plt.figure(figsize=(30, 10))
    for i, angle in enumerate(angles):
        ax = fig.add_subplot(1, 3, i+1, projection='3d')
        mesh1 = Poly3DCollection(vertices1[faces1], alpha=0.2, edgecolor='darkorange', facecolor='orange') # 设置PWMH的颜色
        ax.add_collection3d(mesh1)

        mesh2 = Poly3DCollection(vertices2[faces2], alpha=0.2, edgecolor='olivedrab', facecolor='yellowgreen') # 设置DWMH的颜色
        ax.add_collection3d(mesh2)

        mesh3 = Poly3DCollection(vertices3[faces3], alpha=0.2, edgecolor='dimgray', facecolor='grey') # 设置脑室的颜色
        ax.add_collection3d(mesh3)

        ax.view_init(azim=angle[0], elev=angle[1])
        #ax.grid(False)
        ax.axis('off') # 关闭坐标轴

        # Auto scaling to the mesh size
        scale = np.concatenate([vertices1[:, 0], vertices1[:, 1], vertices1[:, 2], vertices2[:, 0], vertices2[:, 1],
                                vertices2[:, 2], vertices3[:, 0], vertices3[:, 1], vertices3[:, 2]]).flatten()
        ax.auto_scale_xyz(scale, scale, scale)

    plt.subplots_adjust(wspace=0, hspace=0)
    #plt.show()

# 目前的主要问题：1.算出来solidity和convexity显著负相关，但理论上是正相关（至少在2D图像上是）；
# 2.concavity index的计算公式和文献中不一致（1-改成了2-），是否是因为3D图像的原因？；3. 分形维数r->0或1有区别吗？
# Function to calculate the shape features
# SHAPE FEATURES:
## solidity = volume / convex hull volume
## convexity = convex hull area / area
## concavity index = ((2 - convexity) ** 2 + (1 - solidity) ** 2) ** (1 / 2)
## inverse shape index = (area ** 3) ** 0.5 / (6 * volume * (pi) ** 0.5))
## fractal dimension (FD): box counting
## eccentricity = minor axis / major axis
def calculate_shape_features(data):
    verts, faces, normals, values = marching_cubes(data)

    mc_surface_area = mesh_surface_area(verts, faces)
    mc_volume = np.count_nonzero(data)

    hull = ConvexHull(verts)
    convex_hull_area = hull.area
    convex_hull_volume = hull.volume

    convexity = convex_hull_area / mc_surface_area
    solidity = mc_volume / convex_hull_volume
    4
    inverse_sphericity_index = (mc_surface_area ** 3) ** 0.5 / (6 * mc_volume * (math.pi) ** 0.5)

    # Eccentricity: minor axis / major axis
    hull_points = hull.points[hull.vertices]
    diameters = np.sqrt(((hull_points[:, None, :] - hull_points) ** 2).sum(axis=2)) # 计算凸包中各点之间的距离
    max_diameter = np.max(diameters) # 凸包中最大的距离（major axis）
    end_points = np.unravel_index(np.argmax(diameters), diameters.shape) # 最大距离的两个点的索引
    direction_long = hull_points[end_points[1]] - hull_points[end_points[0]] # 最大距离的方向向量
    direction_long /= np.linalg.norm(direction_long) # 最大距离的方向向量的单位向量

    max_length = 0 # 初始化最大长度（minor axis）
    short_axis_points = (None, None)
    for i in range(len(hull_points)):
        for j in range(i + 1, len(hull_points)):
            line_direction = hull_points[j] - hull_points[i]
            line_direction /= np.linalg.norm(line_direction)
            if np.abs(np.dot(line_direction, direction_long)) < 1e-5: # 如果两个向量的夹角小于1e-5，则认为两个向量正交
                length = np.linalg.norm(hull_points[i] - hull_points[j])
                if length > max_length:
                    max_length = length
                    short_axis_points = (hull_points[i], hull_points[j])

    # 如果没有完全正交的两个向量，则选择点乘最小的两个向量（最接近正交）
    min_dot_product = np.inf
    if short_axis_points[0] is None or short_axis_points[1] is None:
        for i in range(len(hull_points)):
            for j in range(i + 1, len(hull_points)):
                line_direction = hull_points[j] - hull_points[i]
                line_length = np.linalg.norm(line_direction)
                if line_length > 0:
                    line_direction /= line_length  # 计算单位方向向量
                    dot_product = np.abs(np.dot(line_direction, direction_long))  # 计算点积的绝对值

                    if dot_product < min_dot_product:
                        min_dot_product = dot_product
                        max_length = line_length
                        #short_axis_points = (hull_points[i], hull_points[j])
    eccentricity = max_length / max_diameter

    # Fractal Dimension (FD): box counting
    _, _, _, coeff, _, _, _ = BoxCountingMethod_Solid.BC_Solid(data)
    fractal_dimension = coeff[0]

    return mc_surface_area, mc_volume, convex_hull_area, convex_hull_volume, convexity, solidity, concavity_index, \
        inverse_sphericity_index, eccentricity, fractal_dimension

def shape_features_plot(data, name):
    ## Fractal Dimension Plot
    para = BoxCountingMethod_Solid.BC_Solid(data)
    path = os.path.join(shape_features_plot_dir, '{0}_FD.png'.format(name))
    FD_plot.Draw_SCI(para, path)

    ## Lesion Plot
    vertices, faces, _, _ = marching_cubes(data)
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_trisurf(vertices[:, 0], vertices[:, 1], faces, vertices[:, 2], color='red', alpha=0.8)
    ax.axis('off')
    path = os.path.join(shape_features_plot_dir, '{0}_lesion_plot.png'.format(name))
    plt.savefig(path, dpi=300)
    plt.close('all')

    ## Convex Hull Plot
    fig = plt.figure(figsize=(12, 12))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_axis_off()  # Remove the axes
    ax.plot_trisurf(vertices[:, 0], vertices[:, 1], faces, vertices[:, 2], color='blue', alpha=0.3)

    hull = ConvexHull(vertices)
    for simplex in hull.simplices:
        ax.plot(vertices[simplex, 0], vertices[simplex, 1], vertices[simplex, 2], color='red', linewidth=2)
    path = os.path.join(shape_features_plot_dir, '{0}_convex_hull_plot.png'.format(name))
    plt.savefig(path, dpi=300)
    plt.close('all')

    ## Eccentricity Plot
    hull_points = hull.points[hull.vertices]
    diameters = np.sqrt(((hull_points[:, None, :] - hull_points) ** 2).sum(axis=2))  # 计算凸包中各点之间的距离
    max_diameter = np.max(diameters)  # 凸包中最大的距离（major axis）
    end_points = np.unravel_index(np.argmax(diameters), diameters.shape)  # 最大距离的两个点的索引
    direction_long = hull_points[end_points[1]] - hull_points[end_points[0]]  # 最大距离的方向向量
    direction_long /= np.linalg.norm(direction_long)  # 最大距离的方向向量的单位向量

    max_length = 0  # 初始化最大长度（minor axis）
    short_axis_points = (None, None)
    for i in range(len(hull_points)):
        for j in range(i + 1, len(hull_points)):
            line_direction = hull_points[j] - hull_points[i]
            line_direction /= np.linalg.norm(line_direction)
            if np.abs(np.dot(line_direction, direction_long)) < 1e-5:  # 如果两个向量的夹角小于1e-5，则认为两个向量正交
                length = np.linalg.norm(hull_points[i] - hull_points[j])
                if length > max_length:
                    max_length = length
                    short_axis_points = (hull_points[i], hull_points[j])

    # 如果没有完全正交的两个向量，则选择点乘最小的两个向量（最接近正交）
    min_dot_product = np.inf
    if short_axis_points[0] is None or short_axis_points[1] is None:
        for i in range(len(hull_points)):
            for j in range(i + 1, len(hull_points)):
                line_direction = hull_points[j] - hull_points[i]
                line_length = np.linalg.norm(line_direction)
                if line_length > 0:
                    line_direction /= line_length  # 计算单位方向向量
                    dot_product = np.abs(np.dot(line_direction, direction_long))  # 计算点积的绝对值

                    if dot_product < min_dot_product:
                        min_dot_product = dot_product
                        max_length = line_length
                        short_axis_points = (hull_points[i], hull_points[j])

    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_trisurf(vertices[:, 0], vertices[:, 1], faces, vertices[:, 2], color='blue', alpha=0.3)
    ax.plot(*zip(hull_points[end_points[0]], hull_points[end_points[1]]), color='r', linewidth=3)
    ax.plot(*zip(short_axis_points[0], short_axis_points[1]), color='lime', linewidth=3)
    azimuth, elevation = np.arctan2(hull_points[end_points[1]][1] - hull_points[end_points[0]][1],
                                    hull_points[end_points[1]][0] - hull_points[end_points[0]][
                                        0]) * 180 / np.pi, np.arctan2(
        hull_points[end_points[1]][2] - hull_points[end_points[0]][2], np.sqrt(
            (hull_points[end_points[1]][0] - hull_points[end_points[0]][0]) ** 2 + (
                        hull_points[end_points[1]][1] - hull_points[end_points[0]][1]) ** 2)) * 180 / np.pi
    ax.view_init(elev=elevation, azim=azimuth)
    ax.axis('off')
    path = os.path.join(shape_features_plot_dir, '{0}_eccentricity_plot.png'.format(name))
    plt.savefig(path)
    plt.close('all')

#%%
derivatives_dir = r'F:\Projects\WMH_segmentation\derivatives'
na_placeholder = "NA"  # 定义表示空值的占位符
vent_mask_name = 'T1_biascorr_ventmask_orig_2_MNI.nii.gz'
DWMH_name = 'bles_0.1_lpa_mFLAIR_deep_WMH_2_MNI.nii.gz'
DWMH_labeled_name = 'bles_0.1_lpa_mFLAIR_deep_WMH_2_MNI_labeled.nii.gz'
PWMH_name = 'bles_0.1_lpa_mFLAIR_periventricular_or_confluent_WMH_2_MNI.nii.gz'
PWMH_labeled_name = 'bles_0.1_lpa_mFLAIR_periventricular_or_confluent_WMH_2_MNI_labeled.nii.gz'
min_voxels = 5 # 定义最小的体素数
plot = True # 是否绘制图像
sub_dirs = [d for d in os.listdir(derivatives_dir) if
            os.path.isdir(os.path.join(derivatives_dir, d)) and d.startswith('sub-')]

# 初始化一个用于存储所有被试平均值的DataFrame
avg_columns = ['Subject']
columns_order = ['Subject', 'Convexity', 'Solidity', 'Concavity Index', 'Inverse Sphericity Index', 'Eccentricity', 'Fractal Dimension']
all_subjects_PWMH_avg_df = pd.DataFrame(columns=avg_columns)
all_subjects_DWMH_avg_df = pd.DataFrame(columns=avg_columns)

columns = ['Region', 'Surface Area', 'Volume', 'Convex Hull Area', 'Convex Hull Volume', 'Convexity', 'Solidity',
               'Concavity Index', 'Inverse Shape Index', 'Eccentricity', 'Fractal Dimension']
all_subjects_DWMH_df = pd.DataFrame(columns=columns)
all_subjects_PWMH_df = pd.DataFrame(columns=columns)

for sub_dir in sub_dirs:
    print('processing directory: {0}'.format(sub_dir))
    shape_features_dir = os.path.join(derivatives_dir, sub_dir, 'shape_features')
    os.makedirs(shape_features_dir, exist_ok=True)

    shape_features_plot_dir = os.path.join(shape_features_dir, 'plot')
    os.makedirs(shape_features_plot_dir, exist_ok=True)

    PWMH_shape_features_df = pd.DataFrame(columns=columns)
    DWMH_shape_features_df = pd.DataFrame(columns=columns)

    vent_mask_path = os.path.join(derivatives_dir, sub_dir, vent_mask_name)
    vent_img = nib.load(vent_mask_path)
    vent_data = vent_img.get_fdata()

    DWMH_path = os.path.join(derivatives_dir, sub_dir, DWMH_name)
    DWMH_img = nib.load(DWMH_path)
    DWMH_data = DWMH_img.get_fdata()
    labeled_DWMH, num_features_DWMH = label(DWMH_data)
    volume = sum(DWMH_data, labeled_DWMH, range(num_features_DWMH + 1))
    remove = volume < min_voxels
    remove_indices = np.where(remove)[0]
    for idx in remove_indices:
        DWMH_data[labeled_DWMH == idx] = 0
    labeled_DWMH, num_features_DWMH = label(DWMH_data)
    print('{0} DWMH regions detected'.format(num_features_DWMH))

    PWMH_path = os.path.join(derivatives_dir, sub_dir, PWMH_name)
    PWMH_img = nib.load(PWMH_path)
    PWMH_data = PWMH_img.get_fdata()
    labeled_PWMH, num_features_PWMH = label(PWMH_data)
    volume = sum(PWMH_data, labeled_PWMH, range(num_features_PWMH + 1))
    remove = volume < min_voxels
    remove_indices = np.where(remove)[0]
    for idx in remove_indices:
        PWMH_data[labeled_PWMH == idx] = 0
    labeled_PWMH, num_features_PWMH = label(PWMH_data)
    print('{0} PWMH regions detected'.format(num_features_PWMH))

    # labeled WMH
    PWMH_labeled = np.zeros_like(PWMH_data, dtype=np.int32)
    DWMH_labeled = np.zeros_like(DWMH_data, dtype=np.int32)

    # Total lesion plot
    if not DWMH_data.any() or not PWMH_data.any() or not vent_data.any():
        print(f"At least one of DWMH or PWMH data is empty in {sub_dir}. Skipping total lesion plot")
    else:
        unique_part_PWMH = np.logical_and(PWMH_data, np.logical_not(vent_data)).astype(np.uint8)
        unique_part_DWMH = np.logical_and(DWMH_data, np.logical_not(vent_data)).astype(np.uint8)
        unique_part_vent = np.logical_and(vent_data, np.logical_not(PWMH_data), np.logical_not(DWMH_data)).astype(np.uint8)

        vertices1, faces1, _, _ = marching_cubes(unique_part_PWMH, level=0)
        vertices2, faces2, _, _ = marching_cubes(unique_part_DWMH, level=0)
        vertices3, faces3, _, _ = marching_cubes(unique_part_vent, level=0)

        angles_three_views = [(30, 30), (210, 60), (-90, 90)]

        plot_three_views_in_row(vertices1, faces1, vertices2, faces2, vertices3, faces3, angles_three_views)
        plt.savefig(os.path.join(shape_features_dir, 'Total_lesion_3D_plot.png'))
        plt.close('all')

    # PWMH shape features calculation
    if PWMH_data.any():
        for region_num in range(1, num_features_PWMH + 1):
            region = (labeled_PWMH == region_num).astype(np.int32)
            region[region != 0] = 1

            # Calculate the shape features of the region/cluster
            mc_surface_area, mc_volume, convex_hull_area, convex_hull_volume, convexity, solidity, concavity_index, \
                inverse_sphericity_index, eccentricity, fractal_dimension = calculate_shape_features(region)
            #print(mc_surface_area, mc_volume, convex_hull_area, convex_hull_volume, convexity, solidity, concavity_index, inverse_shape_index, eccentricity, fractal_dimension)

            PWMH_labeled[labeled_PWMH == region_num] = region_num

            if plot:
                # Save the shape features plots
                name = 'PWMH_region_{}'.format(region_num)
                shape_features_plot(region, name)

            # 将形态学特征添加到DataFrame
            shape_features = calculate_shape_features(region)
            PWMH_shape_features_df.loc[len(PWMH_shape_features_df)] = [f'PWMH_region_{region_num}'] + list(shape_features)
            all_subjects_PWMH_df.loc[len(all_subjects_PWMH_df)] = [f'PWMH_region_{sub_dir}_{region_num}'] + list(shape_features)

        PWMH_labeled_nii_path = os.path.join(derivatives_dir, sub_dir, 'shape_features', PWMH_labeled_name)
        PWMH_labeled_nii = nib.Nifti1Image(PWMH_labeled, PWMH_img.affine, PWMH_img.header)
        nib.save(PWMH_labeled_nii, PWMH_labeled_nii_path)

        excel_path = os.path.join(shape_features_dir, f'{sub_dir}_PWMH_shape_features_{min_voxels}voxels.xlsx')
        PWMH_shape_features_df.to_excel(excel_path, index=False)

        # 计算指定指标的平均值
        subject_averages = PWMH_shape_features_df.iloc[:, 5:11].mean()  # 选择从 'Convexity' 到 'Fractal Dimension' 的列
        subject_avg_data = {'Subject': sub_dir}
        subject_avg_data.update(subject_averages.to_dict())
        all_subjects_PWMH_avg_df = all_subjects_PWMH_avg_df.append(subject_avg_data, ignore_index=True)

        # 将每个被试的平均值保存到其文件夹下
        #subject_avg_df = pd.DataFrame([subject_avg_data])
        #subject_avg_path = os.path.join(shape_features_dir, f'{sub_dir}_average_PWMH_shape_features_{min_voxels}voxels.xlsx')
        #subject_avg_df.to_excel(subject_avg_path, index=False)
    else:
        print('no PWMH lesion detected')
        excel_path = os.path.join(shape_features_dir, f'{sub_dir}_PWMH_shape_features_{min_voxels}voxels.xlsx')
        DWMH_shape_features_df.loc[len(DWMH_shape_features_df)] = [na_placeholder] * len(columns)
        DWMH_shape_features_df.to_excel(excel_path, index=False)

        subject_avg_data = {
            'Subject': sub_dir,
            'Convexity': na_placeholder,
            'Solidity': na_placeholder,
            'Concavity Index': na_placeholder,
            'Inverse Sphericity Index': na_placeholder,
            'Eccentricity': na_placeholder,
            'Fractal Dimension': na_placeholder
        }

        all_subjects_PWMH_avg_df = all_subjects_PWMH_avg_df.append(subject_avg_data, ignore_index=True)

        #subject_avg_df = pd.DataFrame([subject_avg_data])
        #subject_avg_path = os.path.join(shape_features_dir, f'{sub_dir}_average_PWMH_shape_features_{min_voxels}voxels.xlsx')
        #subject_avg_df.to_excel(subject_avg_path, index=False)

    # DWMH shape features calculation
    if DWMH_data.any():
        for region_num in range(1, num_features_DWMH + 1):
            region = (labeled_DWMH == region_num).astype(np.int32)
            region[region != 0] = 1

            # Calculate the shape features of the region/cluster
            mc_surface_area, mc_volume, convex_hull_area, convex_hull_volume, convexity, solidity, concavity_index, \
                inverse_sphericity_index, eccentricity, fractal_dimension = calculate_shape_features(region)
            #print(mc_surface_area, mc_volume, convex_hull_area, convex_hull_volume, convexity, solidity, concavity_index, inverse_shape_index, eccentricity, fractal_dimension)

            DWMH_labeled[labeled_DWMH == region_num] = region_num

            if plot:
                # Save the shape features plots
                name = 'DWMH_region_{}'.format(region_num)
                shape_features_plot(region, name)

            # 将形态学特征添加到DataFrame
            shape_features = calculate_shape_features(region)
            DWMH_shape_features_df.loc[len(DWMH_shape_features_df)] = [f'DWMH_region_{region_num}'] + list(shape_features)
            all_subjects_DWMH_df.loc[len(all_subjects_DWMH_df)] = [f'DWMH_region_{sub_dir}_{region_num}'] + list(shape_features)

        DWMH_labeled_nii_path = os.path.join(derivatives_dir, sub_dir, 'shape_features', DWMH_labeled_name)
        DWMH_labeled_nii = nib.Nifti1Image(DWMH_labeled, DWMH_img.affine, DWMH_img.header)
        nib.save(DWMH_labeled_nii, DWMH_labeled_nii_path)

        excel_path = os.path.join(shape_features_dir, f'{sub_dir}_DWMH_shape_features_{min_voxels}voxels.xlsx')
        DWMH_shape_features_df.to_excel(excel_path, index=False)

        # 计算指定指标的平均值
        subject_averages = DWMH_shape_features_df.iloc[:, 5:11].mean()  # 选择从 'Convexity' 到 'Fractal Dimension' 的列
        subject_avg_data = {'Subject': sub_dir}
        subject_avg_data.update(subject_averages.to_dict())
        all_subjects_DWMH_avg_df = all_subjects_DWMH_avg_df.append(subject_avg_data, ignore_index=True)

        # 将每个被试的平均值保存到其文件夹下
        #subject_avg_df = pd.DataFrame([subject_avg_data])
        #subject_avg_path = os.path.join(shape_features_dir, f'{sub_dir}_average_DWMH_shape_features_{min_voxels}voxels.xlsx')
        #subject_avg_df.to_excel(subject_avg_path, index=False)
    else:
        print('no DWMH lesion detected')
        excel_path = os.path.join(shape_features_dir, f'{sub_dir}_DWMH_shape_features_{min_voxels}voxels.xlsx')
        DWMH_shape_features_df.loc[len(DWMH_shape_features_df)] = [na_placeholder] * len(columns)
        DWMH_shape_features_df.to_excel(excel_path, index=False)

        subject_avg_data = {
            'Subject': sub_dir,
            'Convexity': na_placeholder,
            'Solidity': na_placeholder,
            'Concavity Index': na_placeholder,
            'Inverse Sphericity Index': na_placeholder,
            'Eccentricity': na_placeholder,
            'Fractal Dimension': na_placeholder
        }

        all_subjects_DWMH_avg_df = all_subjects_DWMH_avg_df.append(subject_avg_data, ignore_index=True)

        #subject_avg_df = pd.DataFrame([subject_avg_data])
        #subject_avg_path = os.path.join(shape_features_dir, f'{sub_dir}_average_DWMH_shape_features_{min_voxels}voxels.xlsx')
        #subject_avg_df.to_excel(subject_avg_path, index=False)

# 保存所有被试平均值的汇总DataFrame为一个新的Excel文件
#all_subjects_PWMH_avg_df = all_subjects_PWMH_avg_df[columns_order]
#all_subjects_PWMH_average_excel_path = os.path.join(derivatives_dir, f'PWMH_shape_features_per_subject_{min_voxels}voxels.xlsx')
#all_subjects_PWMH_avg_df.to_excel(all_subjects_PWMH_average_excel_path, index=False)

#all_subjects_DWMH_avg_df = all_subjects_DWMH_avg_df[columns_order]
#all_subjects_DWMH_average_excel_path = os.path.join(derivatives_dir, f'DWMH_shape_features_per_subject_{min_voxels}voxels.xlsx')
#all_subjects_DWMH_avg_df.to_excel(all_subjects_DWMH_average_excel_path, index=False)

all_subjects_PWMH_excel_path = os.path.join(derivatives_dir, f'PWMH_shape_features_{min_voxels}voxels.xlsx')
all_subjects_PWMH_df.to_excel(all_subjects_PWMH_excel_path, index=False)

all_subjects_DWMH_excel_path = os.path.join(derivatives_dir, f'DWMH_shape_features_{min_voxels}voxels.xlsx')
all_subjects_DWMH_df.to_excel(all_subjects_DWMH_excel_path, index=False)