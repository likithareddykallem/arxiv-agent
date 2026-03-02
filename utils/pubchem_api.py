import requests

def fetch_smiles_from_pubchem(compound_name):

    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{compound_name}/property/CanonicalSMILES/JSON"

    try:
        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            return None

        data = response.json()

        smiles = data["PropertyTable"]["Properties"][0]["CanonicalSMILES"]

        return smiles

    except:
        return None