import subprocess
import os
import time

# 상위 50개 구조의 디렉토리 (구조 파일이 있는 디렉토리)
top_50_directory = "./mmgbsa_results/existing_structures"

# residue scanning 결과가 저장될 디렉토리
residue_scan_results_dir = "./"  # 결과 파일이 저장될 디렉토리

# Schrodinger에서 사용할 체인 정보
H5_chain = 'B'

# Residue Scanning에 사용할 변이 리스트
mutations = """
B:104 ARG
B:108 ARG
B:108 TYR
B:110 ARG
B:110 TYR
"""

# Schrodinger CPU 개수
num_cores = 40

# 결과를 저장할 디렉토리 생성
os.makedirs(residue_scan_results_dir, exist_ok=True)

def perform_residue_scanning(maegz_file, result_csv_path):
    """Residue Scanning을 수행하는 함수"""
    maegz_base = os.path.splitext(os.path.basename(maegz_file))[0]
    
    # 변이 파일 생성
    mutation_file_name = os.path.join(residue_scan_results_dir, f"{maegz_base}_mutations.txt")
    with open(mutation_file_name, 'w') as mut_file:
        mut_file.write(mutations)
    
    # Residue Scanning 스크립트 작성
    script_content = f"""#!/bin/bash
$SCHRODINGER/run residue_scanning_backend.py -fast -jobname {maegz_base}_residue_scan -res_file {mutation_file_name} -refine_mut prime_residue -calc hydropathy,rotatable,vdw_surf_comp,sasa_polar,sasa_nonpolar,sasa_total -dist 0.00 {maegz_file} -receptor_asl 'NOT (chain.n {H5_chain})' -add_res_scan_wam -HOST localhost:{num_cores} -TMPLAUNCHDIR
"""
    # 스크립트 파일명 설정
    script_filename = os.path.join(residue_scan_results_dir, f"residue_scanning_{maegz_base}.sh")
    
    with open(script_filename, 'w') as sh_file:
        sh_file.write(script_content)
    subprocess.run(["chmod", "+x", script_filename])
    
    try:
        process = subprocess.run([script_filename], check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        print(f"Successfully processed {maegz_file}")
        print(process.stdout.decode())
        
        # 결과 CSV 파일 확인 (파일 생성까지 기다리기)
        print(f"Checking for result CSV in: {result_csv_path}")
        for _ in range(60):
            if os.path.exists(result_csv_path):
                print(f"Result CSV found: {result_csv_path}")
                break
            time.sleep(1)
        
        if not os.path.exists(result_csv_path):
            print(f"Error: {maegz_file} residue scanning likely failed. CSV not found at {result_csv_path}.")
            return False
        
        # maegz 파일 삭제 (성공 시)
        print(f"Removing processed maegz file: {maegz_file}")
        os.remove(maegz_file)
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error processing {maegz_file}: {e.stderr.decode()}")
        return False
    finally:
        # 작업 완료 후 스크립트 파일 및 변이 파일 삭제
        print(f"Cleaning up: {script_filename}, {mutation_file_name}")
        os.remove(script_filename)
        os.remove(mutation_file_name)

# CSV 파일이 없는 구조 목록을 확인
remaining_files = [f for f in os.listdir(top_50_directory) if f.endswith(".maegz")]
failed_files = []

print("Checking for missing CSV files...")

for filename in remaining_files:
    maegz_base = os.path.splitext(filename)[0]
    result_csv = f"{maegz_base}_residue_scan-results.csv"
    result_csv_path = os.path.join(residue_scan_results_dir, result_csv)

    # CSV 파일이 없는 경우에만 리스트에 추가
    if not os.path.exists(result_csv_path):
        print(f"Missing CSV for structure: {filename}")
        failed_files.append(filename)
    else:
        print(f"CSV already exists for structure: {filename}, skipping residue scanning.")

# 실패한 파일에 대해서만 Residue Scanning 수행
while failed_files:
    print(f"Remaining structures to process: {len(failed_files)}")
    print(f"Structures left to process: {failed_files}")
    
    filename = failed_files.pop(0)
    maegz_file_path = os.path.join(top_50_directory, filename)
    result_csv_path = os.path.join(residue_scan_results_dir, f"{os.path.splitext(filename)[0]}_residue_scan-results.csv")
    
    # Residue Scanning 수행
    success = perform_residue_scanning(maegz_file_path, result_csv_path)
    if not success:
        print(f"Retrying Residue Scanning for {filename}")
        failed_files.append(filename)  # 실패한 경우 다시 리스트에 추가
    
    # 모든 파일에 대해 Residue Scanning이 성공하면 루프 종료
    if not failed_files:
        print("All residue scanning operations completed successfully.")
    else:
        print("Some residue scanning operations failed. Retrying...")
        time.sleep(60)  # 실패한 경우 60초 대기 후 다시 시도
