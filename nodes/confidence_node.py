def compute_confidence(state):

    scores = []

    for row in state.extracted_data:

        score = 0.0
        if row.get("smiles"):
            score += 0.4

        scores.append(score)

    state.confidence_scores = scores
    return state