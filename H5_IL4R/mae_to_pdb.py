import os
import subprocess

# 입력 및 출력 디렉토리 설정
input_directory = "./prep_files/chain_changed"  # .maegz 파일들이 있는 디렉토리
output_directory = "./pdb_files"  # 변환된 .pdb 파일을 저장할 디렉토리
os.makedirs(output_directory, exist_ok=True)

def convert_maegz_to_pdb(maegz_file):
    """Convert a .maegz file to .pdb using Schrodinger's structconvert"""
    base_name = os.path.splitext(os.path.basename(maegz_file))[0]
    pdb_file = os.path.join(output_directory, f"{base_name}.pdb")
    
    # structconvert 명령어 실행
    structconvert_command = f"$SCHRODINGER/utilities/structconvert -imae {maegz_file} -opdb {pdb_file}"
    
    try:
        subprocess.run(structconvert_command, shell=True, check=True)
        print(f"Converted {maegz_file} to {pdb_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting {maegz_file}: {e}")

# 모든 .maegz 파일 처리
for filename in os.listdir(input_directory):
    if filename.endswith(".maegz"):
        file_path = os.path.join(input_directory, filename)
        print(f"Processing {filename}...")
        convert_maegz_to_pdb(file_path)
