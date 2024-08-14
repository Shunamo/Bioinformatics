import subprocess
import os
import gzip
import shutil

pdb_directory = "/home/shkim/H5_IL4R/haddock_H5_IL4R/H5_IL4R_5/4_emref"
output_directory = "/home/shkim/H5_IL4R/haddock_H5_IL4R/prep_files/H5_IL4R_5"

# 결과를 저장할 디렉토리 생성 (이미 존재하는 경우 에러 방지)
os.makedirs(output_directory, exist_ok=True)

def decompress_gz(file_path):
    """GZ 파일을 압축 해제하는 함수"""
    decompressed_file = file_path[:-3]  # .gz를 제거한 파일 이름
    with gzip.open(file_path, 'rb') as f_in:
        with open(decompressed_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    return decompressed_file

def perform_prep(pdb_file):
    """Prep 작업을 수행하는 함수"""
    pdb_base = os.path.splitext(os.path.basename(pdb_file))[0]
    
    script_content = f"""#!/bin/bash
$SCHRODINGER/utilities/prepwizard {pdb_file} {output_directory}/{pdb_base}-out.maegz -fillsidechains -disulfides -assign_all_residues -rehtreat -max_states 1 -epik_pH 7.4 -epik_pHt 2.0 -antibody_cdr_scheme Kabat -samplewater -propka_pH 7.4 -f S-OPLS -rmsd 0.3 -watdist 5.0 -JOBNAME {output_directory}/{pdb_base}_prep -HOST localhost:40
"""
    script_filename = f"prep_script_{pdb_base}.sh"
    
    with open(script_filename, 'w') as sh_file:
        sh_file.write(script_content)
    
    subprocess.run(["chmod", "+x", script_filename])
    
    try:
        process = subprocess.run([f"./{script_filename}"], check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        print(f"Successfully processed {pdb_file}")
        print(process.stdout.decode())
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error processing {pdb_file}: {e.stderr.decode()}")
        return False
    finally:
        if os.path.exists(script_filename):
            os.remove(script_filename)

# 실패한 작업을 걸러내기
failed_files = []
for filename in os.listdir(pdb_directory):
    if filename.endswith(".pdb.gz") or filename.endswith(".pdb"):
        pdb_base = os.path.splitext(os.path.basename(filename))[0]
        result_maegz_path = os.path.join(output_directory, f"{pdb_base}-out.maegz")
        
        if not os.path.exists(result_maegz_path):
            failed_files.append(filename)

# 실패한 파일들에 대해서만 prep 작업 수행
for filename in failed_files:
    pdb_file_path = os.path.join(pdb_directory, filename)
    if filename.endswith(".pdb.gz"):
        pdb_file_path = decompress_gz(pdb_file_path)
    success = perform_prep(pdb_file_path)
