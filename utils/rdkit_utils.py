from rdkit import Chem

def validate_smiles(smiles):

    mol = Chem.MolFromSmiles(smiles)
    return mol is not None


def canonicalise_smiles(smiles):

    mol = Chem.MolFromSmiles(smiles)
    if mol:
        return Chem.MolToSmiles(mol)

    return smiles