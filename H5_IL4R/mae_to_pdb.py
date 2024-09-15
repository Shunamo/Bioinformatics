import os
import subprocess

input_directory = "./prep_files/chain_changed" 
output_directory = "./pdb_files" 
os.makedirs(output_directory, exist_ok=True)

def convert_maegz_to_pdb(maegz_file):
    """Convert a .maegz file to .pdb using Schrodinger's structconvert"""
    base_name = os.path.splitext(os.path.basename(maegz_file))[0]
    pdb_file = os.path.join(output_directory, f"{base_name}.pdb")
    
    structconvert_command = f"$SCHRODINGER/utilities/structconvert -imae {maegz_file} -opdb {pdb_file}"
    
    try:
        subprocess.run(structconvert_command, shell=True, check=True)
        print(f"Converted {maegz_file} to {pdb_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting {maegz_file}: {e}")

for filename in os.listdir(input_directory):
    if filename.endswith(".maegz"):
        file_path = os.path.join(input_directory, filename)
        print(f"Processing {filename}...")
        convert_maegz_to_pdb(file_path)
