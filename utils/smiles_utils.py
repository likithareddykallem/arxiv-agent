import re
from utils.rdkit_utils import validate_smiles

SMILES_REGEX = r"\b[A-Za-z0-9@+\-\[\]\(\)=#$\\/]{10,}\b"

def detect_smiles(text):

    if not text:
        return []

    candidates = re.findall(SMILES_REGEX, text)

    valid_smiles = []

    for cand in candidates:

        # Reject obvious noise
        if len(cand) > 200:
            continue

        if validate_smiles(cand):
            valid_smiles.append(cand)

    return valid_smiles