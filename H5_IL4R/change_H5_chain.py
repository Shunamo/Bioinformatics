import os
import gzip
import shutil

# 경로 설정
pdb_directory = "/home/shkim/H5_IL4R/H5_IL4R_structure/renumbered_pdb"
output_directory = "/home/shkim/H5_IL4R/haddock_H5_IL4R/prep_files/chain_changed"

# 결과를 저장할 디렉토리 생성
os.makedirs(output_directory, exist_ok=True)

def change_chain_in_pdb(pdb_file, old_chain, new_chain):
    """PDB 파일에서 특정 체인을 새로운 체인으로 변경"""
    with open(pdb_file, 'r') as file:
        lines = file.readlines()

    new_lines = []
    for line in lines:
        if line.startswith('ATOM') or line.startswith('HETATM'):
            if line[21] == old_chain:
                new_line = line[:21] + new_chain + line[22:]
                new_lines.append(new_line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    with open(pdb_file, 'w') as file:
        file.writelines(new_lines)

def decompress_maegz(maegz_file):
    """maegz 파일을 해제하여 PDB 파일 추출"""
    pdb_file = maegz_file[:-6] + ".pdb"
    with gzip.open(maegz_file, 'rb') as f_in:
        with open(pdb_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    return pdb_file

def compress_pdb(pdb_file):
    """PDB 파일을 maegz 파일로 압축"""
    maegz_file = pdb_file[:-4] + "-modified.maegz"
    with open(pdb_file, 'rb') as f_in:
        with gzip.open(maegz_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    return maegz_file

# 파일을 처리
for filename in os.listdir(pdb_directory):
    if filename.endswith(".maegz"):
        maegz_file_path = os.path.join(pdb_directory, filename)
        
        # maegz 파일 해제하여 PDB 파일 추출
        pdb_file = decompress_maegz(maegz_file_path)

        # 체인 A와 B를 교환 (체인 A를 X로 임시 변경, B를 A로, X를 B로)
        change_chain_in_pdb(pdb_file, 'A', 'X')  # 임시 체인 X로 변경
        change_chain_in_pdb(pdb_file, 'B', 'A')  # B를 A로 변경
        change_chain_in_pdb(pdb_file, 'X', 'B')  # 임시 체인 X를 B로 변경

        # PDB 파일을 다시 maegz 파일로 압축
        new_maegz_file = compress_pdb(pdb_file)
        
        # 수정된 maegz 파일을 출력 디렉토리에 저장
        shutil.move(new_maegz_file, os.path.join(output_directory, os.path.basename(new_maegz_file)))

        # 원본 PDB 파일 삭제
        os.remove(pdb_file)

print("체인 A와 B의 교환 및 파일 압축이 완료되었습니다.")
