import os
import pandas as pd
from bs4 import BeautifulSoup

# Define the directory
dir_path = r'F:\Public_dataset\DM_20231127_dataset\derivatives'

# List sub-HC directories
sub_dirs = [d for d in os.listdir(dir_path) if d.startswith("sub-") and os.path.isdir(os.path.join(dir_path, d))]

data = []

# Function to extract numeric value from the string
def extract_numeric(value_str):
    return float(value_str.split()[0])

# Iterate over each sub-HC directory
for sub_dir in sub_dirs:
    file_path = os.path.join(dir_path, sub_dir, "report_LST_lpa_mFLAIR.html")

    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            content = file.read()
        soup = BeautifulSoup(content, 'html.parser')
        tables = soup.find_all('table')

        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                columns = row.find_all('td')
                if columns:
                    key = columns[0].get_text(strip=True).lower()
                    if "volume" in key:
                        value = extract_numeric(columns[1].get_text(strip=True))
                        data.append((sub_dir, key, value))
                    elif "number" in key:
                        value = columns[1].get_text(strip=True)
                        data.append((sub_dir, key, value))

# Convert the data to a DataFrame
df = pd.DataFrame(data, columns=["Subject", "Metric", "Value"])

# Pivot the table to have one row per subject
df_pivot = df.pivot(index="Subject", columns="Metric", values="Value").reset_index()

# Save the result to an Excel file
output_path = os.path.join(dir_path, "LST_result.xlsx")
df_pivot.to_excel(output_path, index=False)
