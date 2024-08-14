import os
import shutil
import csv
#상위 50개 구조 select하는 스크립트
# MMGBSA 결과가 저장된 디렉토리
mmgbsa_results_directory = "./haddock_H5_IL4R/mmgbsa_results/H5_IL4R_2"
# 구조 파일이 저장된 디렉토리
structure_files_directory = "./haddock_H5_IL4R/prep_files/H5_IL4R_2"
# 선택된 상위 50개 구조를 저장할 디렉토리
top_50_directory = "./haddock_H5_IL4R/H5_IL4R_2_TOP50"
# 결과 CSV 파일을 저장할 디렉토리
output_directory = "./haddock_H5_IL4R/mmgbsa_results/H5_IL4R_2"

# 디렉토리 생성 (이미 존재하는 경우 무시)
os.makedirs(top_50_directory, exist_ok=True)
os.makedirs(output_directory, exist_ok=True)

# 전체 결과를 저장할 리스트
all_results = []

# 디렉토리에서 모든 MMGBSA 결과 CSV 파일을 읽음
for filename in os.listdir(mmgbsa_results_directory):
    if filename.endswith("-out.csv"):
        file_path = os.path.join(mmgbsa_results_directory, filename)
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # 첫 번째 행(헤더)을 건너뜀
            for row in reader:
                binding_affinity = float(row[-1])  # 바인딩 affinity 값은 마지막 열에 위치
                all_results.append((filename, binding_affinity))

# 바인딩 affinity 값으로 정렬 (작은 값이 먼저 오도록)
all_results.sort(key=lambda x: x[1])

# 상위 50개의 결과를 선택
top_50_results = all_results[:50]

# 상위 50개의 구조 파일을 다른 폴더로 복사
for result in top_50_results:
    filename = result[0].replace("-out_prime_mmgbsa-out.csv", "-out.maegz")
    source_file = os.path.join(structure_files_directory, filename)
    destination_file = os.path.join(top_50_directory, filename)
    if os.path.exists(source_file):
        shutil.copy(source_file, destination_file)
        print(f"Successfully copied {source_file} to {destination_file}")
    else:
        print(f"File not found: {source_file}")
# 전체 결과를 포함하는 CSV 파일 생성
with open(os.path.join(output_directory, "all_results.csv"), 'w', newline='') as f_all:
    writer = csv.writer(f_all)
    writer.writerow(["Filename", "Binding_Affinity"])
    writer.writerows(all_results)

# 상위 50개 결과를 포함하는 CSV 파일 생성
with open(os.path.join(output_directory, "top_50_results.csv"), 'w', newline='') as f_top:
    writer = csv.writer(f_top)
    writer.writerow(["Filename", "Binding_Affinity"])
    writer.writerows(top_50_results)

print("작업이 완료되었습니다.")
