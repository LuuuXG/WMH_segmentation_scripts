function [Surface_Area, Volume, Convex_Hull_Area, Convex_Hull_Volume, Convexity, Solidity, Concavity_Index, Inverse_Sphericity_Index, Eccentricity, Fractal_Dimension] = WMH_shape_features_calculation(region)
%WMH_SHAPE_FEATURES_CALCULATION
        
[lesion_x, lesion_y, lesion_z] = ind2sub(size(region), find(region == 1));
points = [lesion_x, lesion_y, lesion_z];

% Convex hull: convhull()
try
    [K, hull_volume] = convhull(lesion_x, lesion_y, lesion_z);
    
    hull_surface_area = 0;
    for i = 1:size(K, 1)
        v0 = [lesion_x(K(i, 2)) - lesion_x(K(i, 1)), lesion_y(K(i, 2)) - lesion_y(K(i, 1)), lesion_z(K(i, 2)) - lesion_z(K(i, 1))];
        v1 = [lesion_x(K(i, 3)) - lesion_x(K(i, 1)), lesion_y(K(i, 3)) - lesion_y(K(i, 1)), lesion_z(K(i, 3)) - lesion_z(K(i, 1))];
        hull_surface_area = hull_surface_area + (1/2) * norm(cross(v0, v1));
    end
catch
    disp('convhull calculation failed due to colinearity or coplanarity of points.');
    
    hull_volume = [];
    hull_surface_area = [];
end

% Calculate lesion volume: sum of voxels
lesion_volume = sum(region(:));
        
% Calculate lesion surface area: marching cubes
threshold = 0.5;
[faces, vertices] = isosurface(region, threshold);
lesion_surface_area_MC = 0;
for k = 1:size(faces, 1)
	v1 = vertices(faces(k, 1), :);
	v2 = vertices(faces(k, 2), :);
	v3 = vertices(faces(k, 3), :);

	a = norm(v1 - v2);
	b = norm(v2 - v3);
	c = norm(v3 - v1);
	s = (a + b + c) / 2;

	lesion_surface_area_MC = lesion_surface_area_MC + sqrt(s * (s - a) * (s - b) * (s - c));
end

% Eccentricity
distances = squareform(pdist(points, 'euclidean'));

% long axis
[~, max_dist_idx] = max(distances(:));
[i_row, i_col] = ind2sub(size(distances), max_dist_idx);

point1 = points(i_row, :);
point2 = points(i_col, :);

long_axis_direction = (point2 - point1) / norm(point2 - point1);
long_axis_length = norm(point2 - point1);

% short axis
short_axis_length = 0;
short_axis_end_points = zeros(2, 3);
min_dot_product = inf;

for i = 1:length(points)
    for m = i+1:length(points)
        vector_between_points = points(m, :) - points(i, :);
        projection_length = dot(vector_between_points, long_axis_direction);

        if abs(projection_length) < 1e-5  % 检查正交性
            current_distance = norm(vector_between_points);
            if current_distance > short_axis_length
                short_axis_length = current_distance;
                short_axis_end_points = [points(i, :); points(m, :)];
            end
        else  % 如果没有正交的向量，则寻找最接近正交的
            line_direction = vector_between_points / norm(vector_between_points);
            dot_product = abs(dot(line_direction, long_axis_direction));

            if dot_product < min_dot_product
                min_dot_product = dot_product;
                short_axis_length = norm(vector_between_points);
                short_axis_end_points = [points(i, :); points(m, :)];
            end
        end
    end
end

%point_short_axis_1 = short_axis_end_points(1, :);
%point_short_axis_2 = short_axis_end_points(2, :);
        
% FD: box counting
[n, r] = boxcount(region);
df = -diff(log(n))./diff(log(r));

Surface_Area = lesion_surface_area_MC;
Volume = lesion_volume;
Convex_Hull_Area = hull_surface_area;
Convex_Hull_Volume = hull_volume;
if isempty(hull_surface_area) || isempty(lesion_surface_area_MC)
    Convexity = NaN;
    Solidity = NaN;
    Convex_Hull_Area = NaN;
    Convex_Hull_Volume = NaN;
else
    Convexity = hull_surface_area / lesion_surface_area_MC;
    Solidity = lesion_volume / hull_volume;
end
Concavity_Index = ((2 - Convexity)^2 + (1 - Solidity)^2)^(0.5);
Inverse_Sphericity_Index = (lesion_surface_area_MC^1.5) / (6 * lesion_volume * (pi)^0.5);
Eccentricity = short_axis_length / long_axis_length;  
Fractal_Dimension = mean(df(1:6));

end