from utils.protac_utils import detect_linker_mentions, detect_targets

def extract_knowledge_node(state):

    extracted = []

    for paper in state.relevant_papers:

        text = paper.get("full_text")

        linkers = detect_linker_mentions(text)
        targets = detect_targets(text)

        extracted.append({
            "paper": paper["title"],
            "linker_signals": ", ".join(linkers) if linkers else "None",
            "targets": ", ".join(targets) if targets else "None"
        })

    state.extracted_data = extracted

    print("Knowledge rows:", len(extracted))

    return state