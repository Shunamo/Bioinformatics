import os
import shutil
import csv

mmgbsa_results_directory = "./haddock_H5_IL4R/mmgbsa_results/H5_IL4R_2"
structure_files_directory = "./haddock_H5_IL4R/prep_files/H5_IL4R_2"
top_50_directory = "./haddock_H5_IL4R/H5_IL4R_2_TOP50"
output_directory = "./haddock_H5_IL4R/mmgbsa_results/H5_IL4R_2"

os.makedirs(top_50_directory, exist_ok=True)
os.makedirs(output_directory, exist_ok=True)

all_results = []

for filename in os.listdir(mmgbsa_results_directory):
    if filename.endswith("-out.csv"):
        file_path = os.path.join(mmgbsa_results_directory, filename)
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            next(reader)  
            for row in reader:
                binding_affinity = float(row[-1]) 
                all_results.append((filename, binding_affinity))

all_results.sort(key=lambda x: x[1])

top_50_results = all_results[:50]

for result in top_50_results:
    filename = result[0].replace("-out_prime_mmgbsa-out.csv", "-out.maegz")
    source_file = os.path.join(structure_files_directory, filename)
    destination_file = os.path.join(top_50_directory, filename)
    if os.path.exists(source_file):
        shutil.copy(source_file, destination_file)
        print(f"Successfully copied {source_file} to {destination_file}")
    else:
        print(f"File not found: {source_file}")
with open(os.path.join(output_directory, "all_results.csv"), 'w', newline='') as f_all:
    writer = csv.writer(f_all)
    writer.writerow(["Filename", "Binding_Affinity"])
    writer.writerows(all_results)

with open(os.path.join(output_directory, "top_50_results.csv"), 'w', newline='') as f_top:
    writer = csv.writer(f_top)
    writer.writerow(["Filename", "Binding_Affinity"])
    writer.writerows(top_50_results)

print("작업이 완료되었습니다.")
