import os
import shutil
import csv

# 디렉토리 경로 설정
residue_scan_dir = "./residue_scanning/existing_structures"
output_dir = "./content_structures/existing_structures"
results_csv_path = "./content_structures/existing_structures/results_summary.csv"

# 결과 디렉토리 생성
os.makedirs(output_dir, exist_ok=True)

# 조건에 맞는 구조 저장할 리스트
matching_structures = []

# 결과 요약 리스트
results_summary = []

# 각 조건을 확인하는 함수
def check_conditions(rows):
    conditions_met = []

    # 조건 초기화
    condition_1_met = False
    condition_2_met = False
    condition_3_met = False
    condition_4_met = False
    condition_5_met = False
    delta_affinity_A110Y = None

    for row in rows:
        mutation = row['Mutations']
        delta_affinity = float(row['delta Affinity'])

        if 'B:110(ALA->TYR)' in mutation:
            if delta_affinity < 0:
                condition_1_met = True
                delta_affinity_A110Y = delta_affinity

        if 'B:104(GLU->ARG)' in mutation and delta_affinity < 0:
            if delta_affinity_A110Y is not None and abs(delta_affinity) < abs(delta_affinity_A110Y):
                condition_2_met = True

        if 'B:108(ALA->ARG)' in mutation:
            condition_3_met = delta_affinity > 0

        if 'B:108(ALA->TYR)' in mutation:
            condition_4_met = delta_affinity > 0

        if 'B:110(ALA->ARG)' in mutation:
            condition_5_met = delta_affinity > 0

    if condition_1_met:
        conditions_met.append(1)
    if condition_2_met:
        conditions_met.append(2)
    if condition_3_met:
        conditions_met.append(3)
    if condition_4_met:
        conditions_met.append(4)
    if condition_5_met:
        conditions_met.append(5)

    return conditions_met

# CSV 파일을 순회하며 조건을 확인
for filename in os.listdir(residue_scan_dir):
    if filename.endswith("_residue_scan-results.csv"):
        file_path = os.path.join(residue_scan_dir, filename)
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = [row for row in reader]
            conditions_met = check_conditions(rows)
            structure_name = filename.replace("_residue_scan-results.csv", "")

            # 조건을 만족하는 구조를 리스트에 추가
            if len(conditions_met) == 5:
                matching_structures.append(structure_name)
            
            # 결과 요약을 리스트에 추가
            results_summary.append({
                "Structure": structure_name,
                "Conditions_Met": len(conditions_met),
                "Condition_Details": ",".join(map(str, conditions_met))
            })

# 조건을 모두 만족하는 구조를 지정된 디렉토리로 이동
for structure_name in matching_structures:
    source_file = os.path.join(residue_scan_dir, f"{structure_name}_out.maegz")
    if os.path.exists(source_file):
        shutil.copy(source_file, output_dir)

# 결과 요약을 CSV 파일로 저장
with open(results_csv_path, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=["Structure", "Conditions_Met", "Condition_Details"])
    writer.writeheader()
    for summary in results_summary:
        writer.writerow(summary)

print(f"Finished processing. Found {len(matching_structures)} structures that meet all conditions.")
