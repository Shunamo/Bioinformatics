import os
import subprocess
import csv

def run_pymol_script(structure_file, pymol_path, script_filename):
    pymol_script = f"""
    load {os.path.join(structure_dir, structure_file)}

    # Direct contacts
    select contacts, (chain A within 4 of chain B) or (chain B within 4 of chain A)

    # Near contacts, excluding direct contacts
    select near_contacts_IL4R, byres (chain A within 6 of contacts) and not byres contacts
    select near_contacts_H5, byres (chain B within 6 of contacts) and not byres contacts

    # Visualization and saving
    color red, chain A
    color blue, chain B
    show sticks, contacts
    show sticks, near_contacts_IL4R
    show sticks, near_contacts_H5

    png {os.path.join(output_dir, structure_file.replace('.pdb', '_contacts.png'))}, dpi=300
    save {os.path.join(output_dir, structure_file.replace('.pdb', '_contacts.pdb'))}, contacts
    save {os.path.join(output_dir, structure_file.replace('.pdb', '_near_contacts_IL4R.pdb'))}, near_contacts_IL4R
    save {os.path.join(output_dir, structure_file.replace('.pdb', '_near_contacts_H5.pdb'))}, near_contacts_H5
    """
    with open(script_filename, 'w') as script_file:
        script_file.write(pymol_script)
    subprocess.run([pymol_path, "-cq", script_filename], check=True)

def extract_residue_data(file_path, chain_ids):
    residue_lists = {chain: [] for chain in chain_ids}
    with open(file_path, 'r') as pdbfile:
        for line in pdbfile:
            if line.startswith("ATOM") or line.startswith("HETATM"):
                resn = line[17:20].strip()
                resi = line[22:26].strip()
                chain = line[21].strip()
                if chain in chain_ids:
                    residue_lists[chain].append((resn, resi))
    for chain in chain_ids:
        residue_lists[chain] = sorted(list(set(residue_lists[chain])), key=lambda x: int(x[1]))
    return residue_lists

structure_dir = "/home/shunamo/Desktop/Bioinformatics/H5_IL4R/pdb_files"
output_dir = "/home/shunamo/Desktop/Bioinformatics/H5_IL4R/ContactedResidues"
os.makedirs(output_dir, exist_ok=True)

structure_files = [f for f in os.listdir(structure_dir) if f.endswith('.pdb')]
pymol_path = "/home/shunamo/Desktop/pymol/bin/pymol"
residue_count = {'H5': {'Direct': {}, 'Near': {}}, 'IL4R': {'Direct': {}, 'Near': {}}}

for structure_file in structure_files:
    script_filename = os.path.join(output_dir, f"{structure_file.replace('.pdb', '')}_contacts.pml")
    run_pymol_script(structure_file, pymol_path, script_filename)

    contacts_path = os.path.join(output_dir, structure_file.replace('.pdb', '_contacts.pdb'))
    near_contacts_IL4R_path = os.path.join(output_dir, structure_file.replace('.pdb', '_near_contacts_IL4R.pdb'))
    near_contacts_H5_path = os.path.join(output_dir, structure_file.replace('.pdb', '_near_contacts_H5.pdb'))

    contacts_residue_lists = extract_residue_data(contacts_path, ['A', 'B'])
    near_residue_lists_IL4R = extract_residue_data(near_contacts_IL4R_path, ['A'])
    near_residue_lists_H5 = extract_residue_data(near_contacts_H5_path, ['B'])

    for resn, resi in contacts_residue_lists['A']:
        residue_count['IL4R']['Direct'][(resn, resi)] = residue_count['IL4R']['Direct'].get((resn, resi), 0) + 1
    for resn, resi in contacts_residue_lists['B']:
        residue_count['H5']['Direct'][(resn, resi)] = residue_count['H5']['Direct'].get((resn, resi), 0) + 1
    for resn, resi in near_residue_lists_IL4R['A']:
        residue_count['IL4R']['Near'][(resn, resi)] = residue_count['IL4R']['Near'].get((resn, resi), 0) + 1
    for resn, resi in near_residue_lists_H5['B']:
        residue_count['H5']['Near'][(resn, resi)] = residue_count['H5']['Near'].get((resn, resi), 0) + 1

with open(os.path.join(output_dir, "all_contacts_residues_count.csv"), "w", newline="") as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(["Residue Name", "Residue ID", "Chain", "Contact Type", "Count"])
    for chain in residue_count:
        for contact_type in residue_count[chain]:
            for (resn, resi), count in sorted(residue_count[chain][contact_type].items(), key=lambda x: x[1], reverse=True):
                csvwriter.writerow([resn, resi, chain, contact_type, count])
