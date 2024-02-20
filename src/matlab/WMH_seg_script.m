%% Include follwing usage:
% 0. Order the data
% 1. Use LPA to crate binary WMH mask
% 2. Create masterfile.txt needed in FSL BIANCA
% 3. Calculate shape features of WMH lesion (ref: SMART-MR study, doi: 10.1038/s41598-018-20084-y; 10.1177/0271678X18800463; 10.1093/rheumatology/keab823; 10.1016/j.neurobiolaging.2022.08.009; 10.1002/alz.13345)
clear

%% Set up paths
spm12_path = 'D:/Matlab_toolbox/spm12'; % spm12 path, ensure the LST toolbox has been placed in the spm12/toolbox folder
baseDir = 'E:/Projects/WMH_segmentation'; % with ordered "rawdata" folder in BIDS format
% Local environment: Windows10 + WSL2 Ubuntu 22.04
% set wsl path if the "masterfile.txt" is needed in BIANCA
%ubuntu_derivatives_path = '/mnt/f/Public_dataset/ADNI_test/derivatives';

% rawdataDir: BIDS format
% derivativesDir: save the results
rawdataDir = fullfile(baseDir, 'rawdata');
derivativesDir = fullfile(baseDir, 'derivatives');
if ~exist(derivativesDir, 'dir')
    mkdir(derivativesDir);
end

%% 00A Order the data in the format of ../<subject>/<session>/anat/<FLAIR>+<T1> (if there are multiple sessions under one subject, ie. longitudinal data)
subDirs = dir(fullfile(rawdataDir, 'sub*'));
subDirs = subDirs([subDirs.isdir]);

for i = 1:length(subDirs)
    subDirPath = fullfile(rawdataDir, subDirs(i).name);
    sesDirs = dir(fullfile(subDirPath, 'ses*')); % get all session directories
    sesDirs = sesDirs([sesDirs.isdir]);
    
    disp(['Processing subject: ' subDirs(i).name]);

    for j = 1:length(sesDirs)
        sesDirPath = fullfile(subDirPath, sesDirs(j).name);
        anatDirPath = fullfile(sesDirPath, 'anat');

        % Get the date part of the ses folder
        % Here the subject folder is not in standard BIDS format, see 0_dcm2nii.py
        sesDate = regexp(sesDirs(j).name, '\d{8}', 'match');
        if ~isempty(sesDate)
            sesDate = sesDate{1};
        else
            sesDate = 'UnknownDate';
        end

        % Create a derivatives subdirectory with the date
        derivativeSubDirPath = fullfile(derivativesDir, [subDirs(i).name '_' sprintf('%02d', j) '_' sesDate]);
        if ~exist(derivativeSubDirPath, 'dir')
            mkdir(derivativeSubDirPath);
        end

        % Define file types to search for
        fileTypes = {'*FLAIR*.nii*', '*T1*.nii*'};

        for k = 1:length(fileTypes)
            files = dir(fullfile(anatDirPath, fileTypes{k}));

            for m = 1:length(files)
                srcFilePath = fullfile(anatDirPath, files(m).name);
                if contains(files(m).name, 'FLAIR', 'IgnoreCase', true)
                    destFileName = 'FLAIR.nii';
                elseif contains(files(m).name, 'T1', 'IgnoreCase', true)
                    destFileName = 'T1.nii';
                else
                    continue;
                end
                destFilePath = fullfile(derivativeSubDirPath, destFileName);

                % Move file
                % in .nii format rather than .nii.gz because of the LST toolbox cannot handle .nii.gz
                if contains(files(m).name, '.gz')
                    gunzip(srcFilePath, derivativeSubDirPath);
                    unzippedFilePath = fullfile(derivativeSubDirPath, strrep(files(m).name, '.gz', ''));
                    movefile(unzippedFilePath, destFilePath);
                else
                    copyfile(srcFilePath, destFilePath);
                end
            end
        end
    end
end
disp(['done! ']);

%% 00B Order the data in the format of ../<subject>/anat/<FLAIR>+<T1> (if there are no session directories under one subject)
subDirs = dir(fullfile(rawdataDir, 'sub*'));
subDirs = subDirs([subDirs.isdir]);

for i = 1:length(subDirs)
    subDirPath = fullfile(rawdataDir, subDirs(i).name);
    anatDirPath = fullfile(subDirPath, 'anat');

    disp(['Processing subject: ' subDirs(i).name]);

    derivativeSubDirPath = fullfile(derivativesDir, subDirs(i).name);
    if ~exist(derivativeSubDirPath, 'dir')
        mkdir(derivativeSubDirPath);
    end

    fileTypes = {'*FLAIR*.nii*', '*T1*.nii*'};

    for k = 1:length(fileTypes)
        files = dir(fullfile(anatDirPath, fileTypes{k}));

        for m = 1:length(files)
            srcFilePath = fullfile(anatDirPath, files(m).name);
            if contains(files(m).name, 'FLAIR', 'IgnoreCase', true)
                destFileName = 'FLAIR.nii';
            elseif contains(files(m).name, 'T1', 'IgnoreCase', true)
                destFileName = 'T1.nii';
            else
                continue;
            end
            destFilePath = fullfile(derivativeSubDirPath, destFileName);

            if contains(files(m).name, '.gz')
                gunzip(srcFilePath, derivativeSubDirPath);
                unzippedFilePath = fullfile(derivativeSubDirPath, strrep(files(m).name, '.gz', ''));
                movefile(unzippedFilePath, destFilePath);
            else
                copyfile(srcFilePath, destFilePath);
            end
        end
    end
end
disp(['done! ']);

%% Check directories and update path arrays, while recording information of deleted directories
% exclude subjects without FLAIR or T1 images
validDirs = {};
deletedDirsInfo = {};

dersubDirs = dir(fullfile(derivativesDir, 'sub*'));
dersubDirs = dersubDirs([dersubDirs.isdir]);

for i = 1:length(dersubDirs)
    flairPath = fullfile(dersubDirs(i).folder, dersubDirs(i).name, 'FLAIR.nii');
    t1Path = fullfile(dersubDirs(i).folder, dersubDirs(i).name, 'T1.nii');
    missingFiles = '';

    % Check if both files exist
    if exist(flairPath, 'file') ~= 2
        missingFiles = [missingFiles 'FLAIR '];
    end
    if exist(t1Path, 'file') ~= 2
        missingFiles = [missingFiles 'T1 '];
    end

    if isempty(missingFiles)
        validDirs{end+1} = dersubDirs(i);
    else
        deletedDirsInfo{end+1} = {dersubDirs(i).name, missingFiles};
        rmdir(fullfile(dersubDirs(i).folder, dersubDirs(i).name), 's');
    end
end

% Update dersubDirs array to a new array that only contains valid directories
dersubDirs = validDirs;

flairPaths = {};
t1Paths = {};

for i = 1:length(dersubDirs)
    flairPaths{end+1} = fullfile(dersubDirs{i}.folder, dersubDirs{i}.name, 'FLAIR.nii');
    t1Paths{end+1} = fullfile(dersubDirs{i}.folder, dersubDirs{i}.name, 'T1.nii');
end

%% Write the deleted directory information to a text file
deletedInfoFilePath = fullfile(derivativesDir, 'delete_sessions.txt');
fileID = fopen(deletedInfoFilePath, 'w');
fprintf(fileID, 'Deleted Directory, Missing Files\n');
for i = 1:length(deletedDirsInfo)
    fprintf(fileID, '%s, %s\n', deletedDirsInfo{i}{1}, deletedDirsInfo{i}{2});
end
fclose(fileID);

%% 01A LPA (raw FLAIR only)
% Need to optimize: 1. parallel; 2. call SPM only once, add all FLAIR.nii (can output when encountering individual errors?)
% about 1min30s per subject

% It is neccessary to record the failed FLAIR paths
% https://www.applied-statistics.de/lst.html -> FAQs -> An error has occurred. Can you help me?
% breifly, set origin can solve the problem most of the time
failedFlairPaths = {};

addpath(spm12_path);

spm_get_defaults;
global defaults;
spm_jobman('initcfg');

for i = 1:numel(dersubDirs)
    flair_img = [flairPaths{i}, ',1'];
    
    spm('defaults', 'fmri');
    matlabbatch{1}.spm.tools.LST.lpa.data_F2 = {flair_img};
    matlabbatch{1}.spm.tools.LST.lpa.data_coreg = {''};
    matlabbatch{1}.spm.tools.LST.lpa.html_report = 0;
    
    try
        spm_jobman('run', matlabbatch);
    catch ME
        fprintf('Error processing %s: %s\n', flair_img, ME.message);
        failedFlairPaths{end+1} = flairPaths{i};
    end
    
    clear matlabbatch
end

if ~isempty(failedFlairPaths)
    fileId = fopen(fullfile(derivativesDir, 'failedFlairPaths.txt'), 'w');
    for i = 1:numel(failedFlairPaths)
        fprintf(fileId, '%s\n', failedFlairPaths{i});
    end
    fclose(fileId);
end

%% 02 Create binary lesion maps
addpath(spm12_path);

spm_get_defaults;
global defaults;
spm_jobman('initcfg');

% English: Define the thr variable to obtain binary templates at different thresholds
thr_values = 0.1:0.1:0.5;

for i = 1:length(dersubDirs)
    ples_img = [fullfile(dersubDirs{i}.folder, dersubDirs{i}.name, 'ples_lpa_mFLAIR.nii'), ',1'];
    
    for thr = thr_values
        spm('defaults', 'fmri');
        matlabbatch{1}.spm.tools.LST.thresholding.data_plm = {ples_img};
        matlabbatch{1}.spm.tools.LST.thresholding.bin_thresh = thr;
        
        spm_jobman('run', matlabbatch);
        clear matlabbatch
        
        output_nii = fullfile(dersubDirs{i}.folder, dersubDirs{i}.name, ['bles_', num2str(thr), '_lpa_mFLAIR.nii']);
        
        gzip(output_nii);
        delete(output_nii);
    end
end

%% 03 BIANCA file preparation: masterfile.txt
% create masterfile.txt for bianca analysis
masterfilePath = fullfile(derivativesDir, 'masterfile.txt');
fileID = fopen(masterfilePath, 'w');

for i = 1:length(dersubDirs)
    dersubDir = fullfile(ubuntu_derivatives_path,dersubDirs{i}.name);
    dersubDir = strrep(dersubDir, '\', '/');
    
    subjInfo = sprintf('%s/FLAIR_brain.nii.gz %s/T1_2_FLAIR.nii.gz %s/FLAIR_2_MNI_brain.mat %s/bles_0.3_lpa_mFLAIR.nii.gz', dersubDir, dersubDir, dersubDir, dersubDir);
    
    fprintf(fileID, '%s\n', subjInfo);
end
fclose(fileID);

fprintf("finished creating masterfile.txt\n")

%% 04 Shape features calculation
boxcount_path = 'boxcount\boxcount';
addpath(boxcount_path);

PWMH_results = table();
DWMH_results = table();

for i = 1:length(dersubDirs)
    shape_features_folder = fullfile(dersubDirs{i}.folder, dersubDirs{i}.name, 'shape_features');
    PWMH_labeled = fullfile(shape_features_folder, 'bles_0.1_lpa_mFLAIR_periventricular_or_confluent_WMH_2_MNI_labeled.nii.gz');
    DWMH_labeled = fullfile(shape_features_folder, 'bles_0.1_lpa_mFLAIR_deep_WMH_2_MNI_labeled.nii.gz');

    fprintf('Processing subject: %s\n', dersubDirs{i}.name);
    
    if isfile(PWMH_labeled)
        PWMH_array_labeled = niftiread(PWMH_labeled);
        PWMH_max_number = max(PWMH_array_labeled(:));

        for j = 1:PWMH_max_number
            region = PWMH_array_labeled == j;
            region_name = strcat('PWMH_region_', dersubDirs{i}.name, '_', num2str(j));

            [Surface_Area, Volume, Convex_Hull_Area, Convex_Hull_Volume, Convexity, Solidity, Concavity_Index, Inverse_Sphericity_Index, Eccentricity, Fractal_Dimension] = WMH_shape_features_calculation(region);

            tempT = table({region_name}, Surface_Area, Volume, Convex_Hull_Area, Convex_Hull_Volume, Convexity, Solidity, Concavity_Index, Inverse_Sphericity_Index, Eccentricity, Fractal_Dimension, ...
                'VariableNames', {'Region', 'Surface_Area', 'Volume', 'Convex_Hull_Area', 'Convex_Hull_Volume', 'Convexity', 'Solidity', 'Concavity_Index', 'Inverse_Sphericity_Index', 'Eccentricity', 'Fractal_Dimension'});

            % 将临时表格的结果追加到结果表格中
            PWMH_results = [PWMH_results; tempT];
        end        
    end
    
    if isfile(DWMH_labeled)
        DWMH_array_labeled = niftiread(DWMH_labeled);
        DWMH_max_number = max(DWMH_array_labeled(:));
        
        for j = 1:DWMH_max_number
            region = DWMH_array_labeled == j;
            region_name = strcat('DWMH_region_', dersubDirs{i}.name, '_', num2str(j));

            [Surface_Area, Volume, Convex_Hull_Area, Convex_Hull_Volume, Convexity, Solidity, Concavity_Index, Inverse_Sphericity_Index, Eccentricity, Fractal_Dimension] = WMH_shape_features_calculation(region);

            tempT = table({region_name}, Surface_Area, Volume, Convex_Hull_Area, Convex_Hull_Volume, Convexity, Solidity, Concavity_Index, Inverse_Sphericity_Index, Eccentricity, Fractal_Dimension, ...
                'VariableNames', {'Region', 'Surface_Area', 'Volume', 'Convex_Hull_Area', 'Convex_Hull_Volume', 'Convexity', 'Solidity', 'Concavity_Index', 'Inverse_Sphericity_Index', 'Eccentricity', 'Fractal_Dimension'});

            % 将临时表格的结果追加到结果表格中
            DWMH_results = [DWMH_results; tempT];
        end
    end
    
end

PWMH_output_filename = fullfile(derivativesDir, 'PWMH_shape_features_5voxels_matlab.xlsx');
DWMH_output_filename = fullfile(derivativesDir, 'DWMH_shape_features_5voxels_matlab.xlsx');

writetable(PWMH_results, PWMH_output_filename, 'Sheet', 1);
writetable(DWMH_results, DWMH_output_filename, 'Sheet', 1);