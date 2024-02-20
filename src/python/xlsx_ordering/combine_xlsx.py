import pandas as pd

def merge_excel_files(base_file_path, additional_file_path, match_column_base, match_column_additional, columns_range_start, columns_range_end, prefix=""):
    """
    Merges two Excel files based on a matching column and a specified range of columns from the additional file.
    Adds a prefix to the column names from the additional file.

    :param base_file_path: Path to the base Excel file.
    :param additional_file_path: Path to the Excel file containing additional data.
    :param match_column_base: Column name in the base file used for matching.
    :param match_column_additional: Column name in the additional file used for matching.
    :param columns_range_start: Start index of the column range from the additional file to be added.
    :param columns_range_end: End index of the column range from the additional file to be added.
    :param prefix: Prefix to be added to the column names from the additional file.
    """
    # Load the base and additional data
    base_df = pd.read_excel(base_file_path)
    additional_df = pd.read_excel(additional_file_path)

    # Merge the dataframes
    merged_df = pd.merge(base_df, additional_df, left_on=match_column_base, right_on=match_column_additional, how='left')

    # Add prefix to the column names from the additional file
    for col in additional_df.columns[columns_range_start:columns_range_end]:
        if col in merged_df:
            merged_df.rename(columns={col: prefix + col}, inplace=True)

    return merged_df

# Example usage
base_file_path = r'E:\Projects\WMH_segmentation\data_analysis\data\sourcedata\overall\overall_data.xlsx'
additional_file_path = r'E:\Projects\WMH_segmentation\derivatives\DWMH_shape_features_per_subject_horizontal.xlsx'
match_column_base = 'MRI ID'
match_column_additional = 'subject'
columns_range_start = 1  # Start index of the column range (0-indexed)
columns_range_end = 61  # End index of the column range (0-indexed)
prefix = "DWMH_"  # Prefix to be added to the column names from the additional file

# Merging the files
merged_data = merge_excel_files(base_file_path, additional_file_path, match_column_base, match_column_additional, columns_range_start, columns_range_end, prefix)

# Optionally, save the merged data to a new Excel file
output_file_path = base_file_path
merged_data.to_excel(output_file_path, index=False)
