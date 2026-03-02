from utils.text_utils import clean_text

def clean_papers(state):

    for paper in state.relevant_papers:
        paper["full_text"] = clean_text(paper.get("full_text"))

    return state