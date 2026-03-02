from utils.smiles_utils import detect_smiles

def detect_smiles_node(state):

    for paper in state.relevant_papers:

        smiles_list = detect_smiles(paper.get("full_text"))

        for smi in smiles_list:
            state.extracted_data.append({
                "paper": paper["title"],
                "source": paper["pdf_url"],
                "smiles": smi
            })

    return state