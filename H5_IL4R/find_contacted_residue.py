load docked_structure.pdb

color blue, chain A
color red, chain B

#맞닿은 레지듀 찾기
select contacts, (chain A within 4 of chain B) or (chain B within 4 of chain A)
show sticks, contacts
color yellow, contacts


iterate contacts, print(resn, resi, chain)
png contacts.png, dpi=300


save IL4R_contacts.pdb, contacts
