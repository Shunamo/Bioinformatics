import subprocess
import time
import os
import csv

pdb_directory = "/home/shkim/H5_IL4R/haddock_H5_IL4R/prep_files/new/H5_IL4R_1"
output_directory = "/home/shkim/H5_IL4R/haddock_H5_IL4R/mmgbsa_results/new/H5_IL4R_1"
# top_50_directory = "/home/shkim/H5_IL4R/haddock_H5_IL4R/rf2_1/rf2_1_TOP50"  # 주석 처리
il4r_chain = 'A'
num_cores = 20  

os.makedirs(output_directory, exist_ok=True)
# os.makedirs(top_50_directory, exist_ok=True)  

results = [] 

def perform_mmgbsa(maegz_file):
    """MM-GBSA 계산을 수행하는 함수"""
    maegz_base = os.path.splitext(os.path.basename(maegz_file))[0]
    
    os.chdir(output_directory)
    
    script_content = f"""#!/bin/bash
$SCHRODINGER/prime_mmgbsa {maegz_file} -csv_output=yes -ligand="chain. {il4r_chain}" -jobname={maegz_base}_prime_mmgbsa -job_type=ENERGY -HOST localhost:{num_cores}
"""
    script_filename = f"mmgbsa_script_{maegz_base}.sh"
    
    with open(script_filename, 'w') as sh_file:
        sh_file.write(script_content)
    
    subprocess.run(["chmod", "+x", script_filename])
    
    max_retries = 10  
    retry_delay = 600  
    
    for attempt in range(max_retries):
        try:
            process = subprocess.run([f"./{script_filename}"], check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            print(f"Successfully processed {maegz_file}")
            print(process.stdout.decode())
            
            result_csv = f"{maegz_base}_prime_mmgbsa-out.csv"
            result_csv_path = os.path.join(output_directory, result_csv)
            if os.path.exists(result_csv_path):
                with open(result_csv_path, 'r') as f:
                    lines = f.readlines()
                    for line in lines[1:]:
                        parts = line.strip().split(',')
                        binding_energy = float(parts[-1])
                        results.append((maegz_file, binding_energy))
                return True
            
            # 로그 파일만 존재할 경우 실패
            error_log = f"{maegz_base}_prime_mmgbsa.err.log"
            if os.path.exists(error_log):
                print(f"Error log found for {maegz_file}. This job may have failed.")
                return False
            
        except subprocess.CalledProcessError as e:
            error_message = e.stderr.decode()
            print(f"Error processing {maegz_file}: {error_message}")
            if "Could not checkout licenses" in error_message:
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay // 60} minutes... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                else:
                    print("Max retries reached. Skipping this job.")
                    return False
            else:
                return False
    
    os.chdir("..")
    return False

# 상위 50개 결과 찾기 기능
# def find_top_results(num_results):
#     """MM-GBSA 결과 파일에서 상위 N개를 찾고, 해당 maegz 파일을 복사"""
#     # Binding energy로 정렬하고 상위 N개 선택
#     results.sort(key=lambda x: x[1])
#     top_results = results[:num_results]
    
#     # 상위 N개 maegz 파일을 H5_IL4R_1_TOP50 디렉토리로 복사하고 결과도 저장
#     with open(os.path.join(top_50_directory, f"top_{num_results}_results.csv"), 'w') as f_out:
#         f_out.write("Maegz_File,Binding_Energy\n")
#         for result in top_results:
#             maegz_file = result[0]
#             binding_energy = result[1]
#             maegz_file_name = os.path.basename(maegz_file)
#             subprocess.run(["cp", maegz_file, top_50_directory])
#             f_out.write(f"{maegz_file_name},{binding_energy}\n")

failed_files = []
for f in os.listdir(pdb_directory):
    if f.endswith(".maegz"):
        base_name = os.path.splitext(f)[0]
        result_csv = os.path.join(output_directory, f"{base_name}_prime_mmgbsa-out.csv")
        if not os.path.exists(result_csv):
            failed_files.append(f)

while failed_files:
    filename = failed_files.pop(0)
    maegz_file_path = os.path.join(pdb_directory, filename)
    
    success = perform_mmgbsa(maegz_file_path)
    if not success:
        failed_files.append(filename)

with open(os.path.join(output_directory, "all_results.csv"), 'w', newline='') as f_out:
    writer = csv.writer(f_out)
    writer.writerow(["Maegz_File", "Binding_Energy"])
    writer.writerows(results)

#상위 결과 복사 기능
# num_top_results = int(input("상위 몇 개의 결과를 저장하시겠습니까? "))
# find_top_results(num_top_results)
