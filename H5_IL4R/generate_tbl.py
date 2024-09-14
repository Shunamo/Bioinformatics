import os

def generate_cdr3_tbl_files(output_dir, h5_chain='B', il4r_chain='A', active_residues_range=(100, 115), il4r_active_residues=None):
    """
    H5의 100번부터 115번까지 각각 하나씩 active로 설정하고, IL4R는 passive로 설정하는
    여러 .tbl 파일을 생성합니다. IL4R의 active residues도 선택할 수 있습니다.
    
    Args:
    - output_dir (str): 생성된 tbl 파일을 저장할 디렉토리.
    - h5_chain (str): H5의 체인 (기본값: 'B').
    - il4r_chain (str): IL4R의 체인 (기본값: 'A').
    - active_residues_range (tuple): H5의 active residue 범위 (기본값: (100, 115)).
    - il4r_active_residues (list): IL4R의 active residues (기본값: None -> passive로만 설정).
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # IL4R의 passive residues 설정 (상호작용하는 residue들)
    il4r_passive_residues = [69, 127, 41, 67, 71, 70, 39, 43, 42, 125, 72, 126, 68, 131, 66, 124, 130, 13, 182, 129, 40, 123, 44, 74, 154, 14, 91, 182, 128, 181, 73, 93, 15]

    if il4r_active_residues:
        il4r_passive_residues = [res for res in il4r_passive_residues if res not in il4r_active_residues]
        il4r_active_string = " or ".join([f"(resid {res} and segid {il4r_chain})" for res in il4r_active_residues])
    else:
        il4r_active_string = ""
    
    il4r_passive_string = " or ".join([f"(resid {res} and segid {il4r_chain})" for res in il4r_passive_residues])
    
    for active_resid in range(active_residues_range[0], active_residues_range[1] + 1):
        # Active residue 설정 (H5)
        active_residue_string = f"(resid {active_resid} and segid {h5_chain})"
        
        # Passive residues 설정 (active residue 제외)
        passive_residues = [res for res in range(active_residues_range[0], active_residues_range[1] + 1) if res != active_resid]
        passive_residue_string = " or ".join([f"(resid {res} and segid {h5_chain})" for res in passive_residues])
        
        # tbl 파일 내용 구성
        tbl_content = f"""
! H5 active residue (resid {active_resid})
assign
(
    {active_residue_string}
)
(
    {il4r_passive_string}
{f" or {il4r_active_string}" if il4r_active_string else ""}
) 2.0 2.0 0.0

! H5 passive residues (resid {active_residues_range[0]}-{active_residues_range[1]}, excluding {active_resid})
assign
(
    {passive_residue_string}
)
(
    {il4r_passive_string}
{f" or {il4r_active_string}" if il4r_active_string else ""}
) 2.0 2.0 0.0
"""
        
        # tbl 파일 이름 및 경로 설정
        tbl_filename = f"restraint_{active_resid}.tbl"
        tbl_file_path = os.path.join(output_dir, tbl_filename)
        
        # tbl 파일 저장
        with open(tbl_file_path, 'w') as tbl_file:
            tbl_file.write(tbl_content)
        
        print(f"Generated {tbl_filename}")

# 예시 실행: tbl 파일을 생성하여 지정된 디렉토리에 저장
generate_cdr3_tbl_files(
    output_dir="./generated_cdr3_tbl_files",
    il4r_active_residues=[69, 127]  # 예시로 IL4R의 69번과 127번을 active로 설정
)
