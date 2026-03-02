import re

from config.settings import (
    LINKER_KEYWORDS,
    MAX_RELEVANT_PAPERS,
    QUERY_STOPWORDS,
)


def _query_tokens(query):
    tokens = re.findall(r"[a-zA-Z0-9\-\+]+", (query or "").lower())
    cleaned = [t for t in tokens if len(t) >= 3 and t not in QUERY_STOPWORDS]
    return list(dict.fromkeys(cleaned))


def _paper_score(title, abstract, tokens):
    text = f"{title} {abstract}"
    match_count = sum(1 for token in tokens if token in text)
    # Slight title boost.
    title_match_count = sum(1 for token in tokens if token in title)
    return match_count + (0.5 * title_match_count)


def filter_relevant_papers(state):
    query = (state.query or "").strip().lower()
    tokens = _query_tokens(query)

    scored = []

    for paper in state.papers_found:
        title = (paper.get("title") or "").lower()
        abstract = (paper.get("abstract") or "").lower()
        text = f"{title} {abstract}"

        score = _paper_score(title, abstract, tokens)
        has_prompt_signal = score >= 1 if tokens else ("protac" in text or "degrader" in text)

        # If user asks linker-related query, keep stricter chemistry-aware filtering.
        query_is_linker_mode = any(k in query for k in ("linker", "spacer", "peg", "tether"))
        if query_is_linker_mode:
            has_linker_signal = any(keyword in text for keyword in LINKER_KEYWORDS)
            if not has_linker_signal:
                continue

        if has_prompt_signal:
            paper["relevance_score"] = score
            scored.append(paper)

    scored.sort(key=lambda p: p.get("relevance_score", 0), reverse=True)
    relevant = scored[:MAX_RELEVANT_PAPERS]

    state.relevant_papers = relevant

    print("Relevant papers:", len(relevant))
    return state
