from pdbfixer import PDBFixer
from openmm.app import PDBFile, Modeller
fixer = PDBFixer('1ce1-processed.pdb')

# 물 분자, POP chain 제거 Modeller 생성
modeller = Modeller(fixer.topology, fixer.positions)

# 물 분자, POP cahin 제거
residues_to_delete = [residue for residue in modeller.topology.residues() if residue.name in ['HOH', 'POP']]
modeller.delete(residues_to_delete)

with open('1ce1-processed-fixed.pdb', 'w') as f:
    PDBFile.writeFile(modeller.topology, modeller.positions, f)
