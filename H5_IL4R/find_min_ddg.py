import os
import csv
import shutil

il4r_num = input("H5_IL4R 번호를 입력하세요 (1~5): ")

residue_scan_dir = f"./residue_scanning/existing_structures"
structure_dir = "./residue_scanning/existing_structures"
mmgbsa_dir = f"./mmgbsa_results/existing_structures" 
output_dir = f"./lowest_value_structures/existing_structures"

os.makedirs(output_dir, exist_ok=True)

min_delta_affinity = float('inf')
min_affinity_structure = None
min_mmgbsa_energy = float('inf')
min_mmgbsa_structure = None

affinities = []

for filename in os.listdir(residue_scan_dir):
    if filename.endswith("_residue_scan-results.csv"):
        file_path = os.path.join(residue_scan_dir, filename)
        with open(file_path, mode='r') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                if 'B:110(ALA->TYR)' in row['Mutations']:
                    delta_affinity = float(row['delta Affinity'])
                    affinities.append((filename, delta_affinity))
                    
                    if delta_affinity < min_delta_affinity:
                        min_delta_affinity = delta_affinity
                        min_affinity_structure = filename

# MM-GBSA 최저값 찾기
for filename in os.listdir(mmgbsa_dir):
    if filename.endswith(".csv"):  
        file_path = os.path.join(mmgbsa_dir, filename)
        with open(file_path, mode='r') as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames 
            print(f"Processing file: {filename}")
            print(f"Headers: {headers}")
            
            for row in reader:
                if 'r_psp_MMGBSA_dG_Bind' in row:
                    mmgbsa_energy = float(row['r_psp_MMGBSA_dG_Bind'])
                    if mmgbsa_energy < min_mmgbsa_energy:
                        min_mmgbsa_energy = mmgbsa_energy
                        min_mmgbsa_structure = filename
                else:
                    print("Expected header not found in the CSV file.")

if min_affinity_structure:
    structure_file = min_affinity_structure.replace("-results.csv", "-out.maegz")
    source_structure_file = os.path.join(structure_dir, structure_file)
    if os.path.exists(source_structure_file):
        shutil.copy(source_structure_file, output_dir)
        print(f"최저 delta Affinity 값을 가진 구조 파일 {structure_file}이 {output_dir}로 복사되었습니다.")
    
    source_residue_file = os.path.join(residue_scan_dir, min_affinity_structure)
    if os.path.exists(source_residue_file):
        shutil.copy(source_residue_file, output_dir)
        print(f"최저 delta Affinity 값을 가진 residue_scanning 결과 파일 {min_affinity_structure}이 {output_dir}로 복사되었습니다.")

if min_mmgbsa_structure:
    source_mmgbsa_file = os.path.join(mmgbsa_dir, min_mmgbsa_structure)
    if os.path.exists(source_mmgbsa_file):
        shutil.copy(source_mmgbsa_file, output_dir)
        print(f"최저 MM-GBSA ΔG binding 값을 가진 결과 파일 {min_mmgbsa_structure}이 {output_dir}로 복사되었습니다.")

sorted_affinities = sorted(affinities, key=lambda x: x[1])
sorted_affinity_file = os.path.join(output_dir, "sorted_affinity.csv")

with open(sorted_affinity_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Structure", "Delta Affinity"])
    writer.writerows(sorted_affinities)

print(f"All delta Affinity values have been sorted and saved to {sorted_affinity_file}")

