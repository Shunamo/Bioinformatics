import os
import csv
import shutil

# 사용자로부터 숫자 입력 받기
il4r_num = input("H5_IL4R 번호를 입력하세요 (1~5): ")

# 디렉토리 경로 설정
residue_scan_dir = f"./residue_scanning/existing_structures"
structure_dir = "./residue_scanning/existing_structures"
mmgbsa_dir = f"./mmgbsa_results/existing_structures"  # MM-GBSA 결과 파일이 저장된 경로
output_dir = f"./lowest_value_structures/existing_structures"

# 결과 디렉토리 생성
os.makedirs(output_dir, exist_ok=True)

# 변수 초기화
min_delta_affinity = float('inf')
min_affinity_structure = None
min_mmgbsa_energy = float('inf')
min_mmgbsa_structure = None

affinities = []

# CSV 파일을 순회하며 조건을 확인
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
            headers = reader.fieldnames  # 현재 CSV 파일의 헤더를 출력합니다.
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

# 최저값을 가진 구조 파일과 residue_scanning 결과 파일을 복사
if min_affinity_structure:
    # 구조 파일 복사
    structure_file = min_affinity_structure.replace("-results.csv", "-out.maegz")
    source_structure_file = os.path.join(structure_dir, structure_file)
    if os.path.exists(source_structure_file):
        shutil.copy(source_structure_file, output_dir)
        print(f"최저 delta Affinity 값을 가진 구조 파일 {structure_file}이 {output_dir}로 복사되었습니다.")
    
    # residue_scanning 결과 파일 복사
    source_residue_file = os.path.join(residue_scan_dir, min_affinity_structure)
    if os.path.exists(source_residue_file):
        shutil.copy(source_residue_file, output_dir)
        print(f"최저 delta Affinity 값을 가진 residue_scanning 결과 파일 {min_affinity_structure}이 {output_dir}로 복사되었습니다.")

# MM-GBSA 최저값을 가진 구조 파일 복사
if min_mmgbsa_structure:
    source_mmgbsa_file = os.path.join(mmgbsa_dir, min_mmgbsa_structure)
    if os.path.exists(source_mmgbsa_file):
        shutil.copy(source_mmgbsa_file, output_dir)
        print(f"최저 MM-GBSA ΔG binding 값을 가진 결과 파일 {min_mmgbsa_structure}이 {output_dir}로 복사되었습니다.")

# 모든 delta Affinity를 정렬하고 CSV로 저장
sorted_affinities = sorted(affinities, key=lambda x: x[1])
sorted_affinity_file = os.path.join(output_dir, "sorted_affinity.csv")

with open(sorted_affinity_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Structure", "Delta Affinity"])
    writer.writerows(sorted_affinities)

print(f"All delta Affinity values have been sorted and saved to {sorted_affinity_file}")

