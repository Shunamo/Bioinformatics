import os
import subprocess
import csv

structure_dir = "/Users/shunamo/Desktop/MolecularDynamics/H5_IL4R/structures/PDB"
output_dir = "ContactedResidues"
os.makedirs(output_dir, exist_ok=True)

structure_files = [f for f in os.listdir(structure_dir) if f.endswith('.pdb')]

# PyMOL 경로
pymol_path = "/Applications/PyMOL.app/Contents/bin/pymol"

# 모든 구조의 레지듀 빈도수 저장용
residue_count_H5 = {}
residue_count_IL4R = {}

for structure_file in structure_files:
    if structure_file.startswith("H5"):
        chain_A = "A"  # H5
        chain_B = "B"  # IL4R
    elif structure_file.startswith("cluster"):
        chain_A = "B"
        chain_B = "A"
    elif structure_file.startswith("reinsilico"):
        chain_A = "C"
        chain_B = "B"
    else:
        continue
    
    pymol_script = f"""
    load {os.path.join(structure_dir, structure_file)}
    
    select contacts, (chain {chain_A} within 4 of chain {chain_B}) or (chain {chain_B} within 4 of chain {chain_A})
    
    color red, chain {chain_A}
    color blue, chain {chain_B}
    
    show surface, chain {chain_A}
    show surface, chain {chain_B}
    
    show sticks, contacts
    color yellow, contacts
    
    png {os.path.join(output_dir, structure_file.replace('.pdb', '_contacts.png'))}, dpi=300
    save {os.path.join(output_dir, structure_file.replace('.pdb', '_contacts.pdb'))}, contacts
    """

    script_filename = os.path.join(output_dir, f"{structure_file.replace('.pdb', '')}_contacts.pml")
    with open(script_filename, 'w') as script_file:
        script_file.write(pymol_script)
    
    subprocess.run([pymol_path, "-cq", script_filename])

    residue_list_H5 = []
    residue_list_IL4R = []
    with open(os.path.join(output_dir, f"{structure_file.replace('.pdb', '')}_contacts.pdb"), 'r') as pdbfile:
        for line in pdbfile:
            if line.startswith("ATOM") or line.startswith("HETATM"):
                resn = line[17:20].strip()
                resi = line[22:26].strip()
                chain = line[21].strip()
                if chain == chain_A:
                    residue_list_H5.append((resn, resi))
                elif chain == chain_B:
                    residue_list_IL4R.append((resn, resi))
        
        # 중복 제거, 내림차순 정렬
        residue_list_H5 = sorted(list(set(residue_list_H5)), key=lambda x: int(x[1]))
        residue_list_IL4R = sorted(list(set(residue_list_IL4R)), key=lambda x: int(x[1]))

        # 빈도수 세기
        for resn, resi in residue_list_H5:
            key = (resn, resi)
            if key in residue_count_H5:
                residue_count_H5[key] += 1
            else:
                residue_count_H5[key] = 1

        for resn, resi in residue_list_IL4R:
            key = (resn, resi)
            if key in residue_count_IL4R:
                residue_count_IL4R[key] += 1
            else:
                residue_count_IL4R[key] = 1
        

        structure_name = os.path.splitext(structure_file)[0]
        with open(os.path.join(output_dir, f"{structure_name}_contacts_residues.csv"), "w", newline="") as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["Residue Name", "Residue ID", "H5", "IL4R"])
            
            for resn, resi in residue_list_H5:
                csvwriter.writerow([resn, resi, "H5", ""])
            csvwriter.writerow([])
            for resn, resi in residue_list_IL4R:
                csvwriter.writerow([resn, resi, "", "IL4R"])

# 전체결과파일
sorted_residue_count_H5 = sorted(residue_count_H5.items(), key=lambda x: x[1], reverse=True)
sorted_residue_count_IL4R = sorted(residue_count_IL4R.items(), key=lambda x: x[1], reverse=True)

with open(os.path.join(output_dir, "all_contacts_residues_count.csv"), "w", newline="") as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(["Residue Name", "Residue ID", "Chain", "Count"])
    
    for residue, count in sorted_residue_count_H5:
        csvwriter.writerow([residue[0], residue[1], "H5", count])
    
    for residue, count in sorted_residue_count_IL4R:
        csvwriter.writerow([residue[0], residue[1], "IL4R", count])
