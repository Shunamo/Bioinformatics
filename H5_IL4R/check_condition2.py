import os
import csv

# 디렉토리 경로 설정
residue_scan_dir = "./residue_scanning_result/existing_structures/"
output_dir = "./content_structures/existing_structures/residue_scanning_result"
results_csv_path = "./content_structures/existing_structures_residue_scan_result.csv"

# 결과 디렉토리 생성
os.makedirs(output_dir, exist_ok=True)

# 조건에 맞는 구조 저장할 리스트
matching_structures = []

# 결과 요약 리스트
results_summary = []

# 1번 조건 (B:110(ALA->TYR))을 가장 많이 감소시키는 구조 저장
condition_1_structures = []

# 각 조건을 확인하는 함수
def check_conditions(rows, structure_name):
    conditions_met = []
    condition_affinities = {}

    # 초기 상태 변수
    condition_1_met = False  # 1번: A110->Y에서 ddG가 감소
    condition_2_met = False  # 2번: E104->R에서 ddG가 음수
    condition_3_met = False  # 3번: A108->R에서 ddG가 증가
    condition_4_met = False  # 4번: A108->Y에서 ddG가 증가
    condition_5_met = False  # 5번: A110->R에서 ddG가 증가

    # 각 row(변이)에서 조건을 체크
    for row in rows:
        mutation = row[0]  # 0번째 열이 Mutations
        delta_affinity = float(row[1])  # 1번째 열이 delta Affinity

        # 모든 조건의 delta Affinity 값 저장 (만족 여부와 관계없이)
        if 'B:110(ALA->TYR)' in mutation:
            condition_affinities[1] = delta_affinity
            if delta_affinity < 0:  # ddG가 감소하는지 확인
                condition_1_met = True
                print(f"Condition 1 met (A110->Y), delta Affinity: {delta_affinity}")
                condition_1_structures.append((structure_name, delta_affinity))  # 1번 조건을 만족하는 구조 저장

        if 'B:104(GLU->ARG)' in mutation:
            condition_affinities[2] = delta_affinity
            if delta_affinity < 0:  # 음수 확인
                condition_2_met = True
                print(f"Condition 2 met (E104->R), delta Affinity: {delta_affinity}")

        if 'B:108(ALA->ARG)' in mutation:
            condition_affinities[3] = delta_affinity
            if delta_affinity > 0:  # ddG가 증가하는지 확인
                condition_3_met = True
                print(f"Condition 3 met (A108->R), delta Affinity: {delta_affinity}")

        if 'B:108(ALA->TYR)' in mutation:
            condition_affinities[4] = delta_affinity
            if delta_affinity > 0:  # ddG가 증가하는지 확인
                condition_4_met = True
                print(f"Condition 4 met (A108->Y), delta Affinity: {delta_affinity}")

        if 'B:110(ALA->ARG)' in mutation:
            condition_affinities[5] = delta_affinity
            if delta_affinity > 0:  # ddG가 증가하는지 확인
                condition_5_met = True
                print(f"Condition 5 met (A110->R), delta Affinity: {delta_affinity}")

    # 조건이 충족된 경우 기록
    print(f"Conditions met for structure {structure_name}:")
    if condition_1_met:
        conditions_met.append(1)  # 조건 1 무조건 만족해야 함
        print(f" -> Condition 1 met (A110->Y)")
    if condition_2_met:
        conditions_met.append(2)  # 조건 2가 1번 이후 우선순위
        print(f" -> Condition 2 met (E104->R)")
    if condition_3_met:
        conditions_met.append(3)
        print(f" -> Condition 3 met (A108->R)")
    if condition_4_met:
        conditions_met.append(4)
        print(f" -> Condition 4 met (A108->Y)")
    if condition_5_met:
        conditions_met.append(5)
        print(f" -> Condition 5 met (A110->R)")

    return conditions_met, condition_affinities

# CSV 파일을 순회하며 조건을 확인
for filename in os.listdir(residue_scan_dir):
    if filename.endswith("_residue_scan-results.csv"):
        file_path = os.path.join(residue_scan_dir, filename)
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # 첫 번째 줄(헤더)은 건너뜀
            rows = [row for row in reader]  # 나머지 줄 읽기
            structure_name = filename.replace("_residue_scan-results.csv", "")
            conditions_met, condition_affinities = check_conditions(rows, structure_name)

            # 결과 요약을 리스트에 추가
            results_summary.append({
                "Structure": structure_name,
                "Conditions_Met": len(conditions_met),
                "Condition_Details": ",".join(map(str, conditions_met)) if conditions_met else "No conditions met",
                "Condition_1_Affinity": condition_affinities.get(1, "N/A"),
                "Condition_2_Affinity": condition_affinities.get(2, "N/A"),
                "Condition_3_Affinity": condition_affinities.get(3, "N/A"),
                "Condition_4_Affinity": condition_affinities.get(4, "N/A"),
                "Condition_5_Affinity": condition_affinities.get(5, "N/A")
            })

            # 조건을 만족하는 구조를 리스트에 추가 (1번은 필수)
            if 1 in conditions_met and (len(conditions_met) >= 2 and 2 in conditions_met):
                matching_structures.append(structure_name)

# 조건 1을 가장 많이 감소시키는 구조를 기준으로 정렬
condition_1_structures.sort(key=lambda x: x[1])

# 조건을 만족하는 구조를 지정된 디렉토리로 이동
for structure_name in matching_structures:
    source_file = os.path.join(residue_scan_dir, f"{structure_name}_out.maegz")
    if os.path.exists(source_file):
        shutil.copy(source_file, output_dir)

# 결과 요약을 CSV 파일로 저장 (각 조건의 delta Affinity 값을 포함)
with open(results_csv_path, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=["Structure", "Conditions_Met", "Condition_Details", "Condition_1_Affinity", "Condition_2_Affinity", "Condition_3_Affinity", "Condition_4_Affinity", "Condition_5_Affinity"])
    writer.writeheader()
    for summary in results_summary:
        writer.writerow(summary)

# 결과가 없는 경우에도 메시지를 출력
if matching_structures:
    print(f"Finished processing. Found {len(matching_structures)} structures that meet all conditions.")
else:
    print("No structures met all the conditions. Check the results_summary.csv for details.")
