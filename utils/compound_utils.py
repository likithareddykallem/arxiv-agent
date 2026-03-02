import re

COMPOUND_REGEX = r"\b[A-Z][A-Za-z0-9\-]{2,}\b"

# Common scientific noise words
NOISE_WORDS = {
    "Introduction", "Methods", "Results", "Discussion",
    "Figure", "Table", "Protein", "Cell", "Analysis",
    "Model", "Data", "Study", "Author", "University",
    "PROTAC"
}

def detect_compound_names(text):

    if not text:
        return []

    candidates = re.findall(COMPOUND_REGEX, text)

    filtered = []

    for cand in candidates:

        if cand in NOISE_WORDS:
            continue

        # Reject obvious non-chemical words
        if len(cand) < 4:
            continue

        filtered.append(cand)

    return list(set(filtered))