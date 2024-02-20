import os
import re
import pandas as pd

# Function to extract the required information based on the pattern observed in the file.
def extract_quantification_data(text_content):
    data_dict = {}
    # Regular expressions for each section
    patterns = {
        'Total WMH (masked)': re.compile(r'Total WMH \(masked\)\s+.*?is (\d+)\s+.*?is ([\d\.]+)'),
        'PWMH': re.compile(r'PWMH\s+.*?is (\d+)\s+.*?is ([\d\.]+)'),
        'DWMH': re.compile(r'DWMH\s+.*?is (\d+)\s+.*?is ([\d\.]+)')
    }
    # Extracting data using the patterns
    for key, pattern in patterns.items():
        match = pattern.search(text_content)
        if match:
            # Store the extracted numbers as integers and floats respectively
            data_dict[key + ' number'] = int(match.group(1))
            data_dict[key + ' volume'] = float(match.group(2))
        else:
            # If no match is found, store 0 for both number and volume
            data_dict[key + ' number'] = 0
            data_dict[key + ' volume'] = 0.0
    return data_dict

# Initialize a dictionary to hold all the data.
all_data = {}

# Define the base directory where the subject folders are located.
base_dir = r'F:\Projects\WMH_segmentation\derivatives'

# Walk through the base directory to find subject folders and extract data.
for subject_folder in os.listdir(base_dir):
    if subject_folder.startswith('sub'):
        subject_path = os.path.join(base_dir, subject_folder)
        for file_name in os.listdir(subject_path):
            # Check if the file is a .txt file.
            if file_name.endswith('.txt'):
                file_path = os.path.join(subject_path, file_name)
                # Read the file content.
                with open(file_path, 'r') as file:
                    content = file.read()
                # Use the function to extract data from the content.
                subject_data = extract_quantification_data(content)
                # Store the data using the subject folder name as the key.
                all_data[subject_folder] = subject_data

# Convert the all_data dictionary to a pandas DataFrame.
df = pd.DataFrame.from_dict(all_data, orient='index')

# Define the output path for the Excel file.
output_excel_path = os.path.join(base_dir, r'WMH_volume_quantification_results.xlsx')

# Save the DataFrame to an Excel file.
df.to_excel(output_excel_path, header=True)

print(f"Quantification results saved to {output_excel_path}")
