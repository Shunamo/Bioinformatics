
    load /home/shunamo/Desktop/Bioinformatics/H5_IL4R/pdb_files/cluster_1_2-out.pdb

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

    png /home/shunamo/Desktop/Bioinformatics/H5_IL4R/ContactedResidues/cluster_1_2-out_contacts.png, dpi=300
    save /home/shunamo/Desktop/Bioinformatics/H5_IL4R/ContactedResidues/cluster_1_2-out_contacts.pdb, contacts
    save /home/shunamo/Desktop/Bioinformatics/H5_IL4R/ContactedResidues/cluster_1_2-out_near_contacts_IL4R.pdb, near_contacts_IL4R
    save /home/shunamo/Desktop/Bioinformatics/H5_IL4R/ContactedResidues/cluster_1_2-out_near_contacts_H5.pdb, near_contacts_H5
    