from utils.compound_utils import detect_compound_names

def detect_compounds_node(state):

    compounds = []

    for paper in state.relevant_papers:

        detected = detect_compound_names(paper.get("full_text"))
        compounds.extend(detected)

    state.compounds_found = list(set(compounds))

    print("Compounds detected:", len(state.compounds_found))

    return state