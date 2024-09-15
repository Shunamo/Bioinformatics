import csv
import os
import re

folders = ["H5_IL4R_1", "H5_IL4R_2", "H5_IL4R_3", "H5_IL4R_4", "H5_IL4R_5"]
existing_folder = "existing_structures"
base_dir = "./mmgbsa_results"
output_file = "formatted_comparison_mmgbsa.csv"

results_existing = []
results_new = {folder: [] for folder in folders}

def extract_number(file_name):
    match = re.search(r'emref_(\d+)', file_name)
    if match:
        return match.group(1)
    return file_name

folder_path = os.path.join(base_dir, existing_folder)
for file in os.listdir(folder_path):
    if file.endswith(".csv") and "all" not in file and "top" not in file:
        file_path = os.path.join(folder_path, file)
        with open(file_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                r_psp_MMGBSA_dG_Bind_value = float(row[1]) if len(row) > 1 else None
                results_existing.append((file, r_psp_MMGBSA_dG_Bind_value))

for folder in folders:
    folder_path = os.path.join(base_dir, folder)
    for file in os.listdir(folder_path):
        if file.endswith(".csv") and "all" not in file and "top" not in file:
            file_path = os.path.join(folder_path, file)
            with open(file_path, 'r') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)
                for row in reader:
                    r_psp_MMGBSA_dG_Bind_value = float(row[1]) if len(row) > 1 else None
                    file_name = extract_number(file)
                    results_new[folder].append((file_name, r_psp_MMGBSA_dG_Bind_value))

results_existing.sort(key=lambda x: x[1])
for folder in folders:
    results_new[folder].sort(key=lambda x: x[1])

with open(output_file, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    
    headers = ["Order", "Existing Structures", "Binding Energy"]
    for folder in folders:
        headers += [f"{folder} Name", "Binding Energy"]
    writer.writerow(headers)
    
    max_len = max(len(results_existing), *[len(results_new[folder]) for folder in folders])
    for i in range(max_len):
        row = [i+1]
        if i < len(results_existing):
            row += results_existing[i]
        else:
            row += ["", ""]
        
        for folder in folders:
            if i < len(results_new[folder]):
                row += results_new[folder][i]
            else:
                row += ["", ""]
        
        writer.writerow(row)

print(f"Formatted comparison file has been saved as {output_file}")
