from utils.pubchem_api import fetch_smiles_from_pubchem

MAX_COMPOUNDS = 50

def fetch_smiles_node(state):

    limited_compounds = state.compounds_found[:MAX_COMPOUNDS]

    success = 0

    for compound in limited_compounds:

        smiles = fetch_smiles_from_pubchem(compound)

        if smiles:
            success += 1
            state.extracted_data.append({
                "compound": compound,
                "smiles": smiles
            })
        else:
            print(f"PubChem NOT FOUND → {compound}")

    print(f"SMILES retrieved: {success}")

    return state