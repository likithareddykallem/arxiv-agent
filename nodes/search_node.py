from concurrent.futures import ThreadPoolExecutor

from utils.arxiv_api import search_arxiv_api
from utils.biorxiv_api import search_biorxiv


def _build_search_query(user_query):
    query = (user_query or "").strip()
    lowered = query.lower()
    extras = []

    # Controlled synonym expansion only when relevant.
    if "protac" in lowered and "degrader" not in lowered:
        extras.append("degrader")
    if any(k in lowered for k in ("linker", "spacer", "peg", "tether")):
        for term in ("linker", "spacer", "peg"):
            if term not in lowered:
                extras.append(term)

    if extras:
        return f"{query} {' '.join(extras)}"
    return query


def search_arxiv(state):
    search_query = _build_search_query(state.query)

    with ThreadPoolExecutor(max_workers=2) as executor:
        arxiv_future = executor.submit(search_arxiv_api, search_query)
        biorxiv_future = executor.submit(search_biorxiv, search_query)
        arxiv_papers = arxiv_future.result()
        biorxiv_papers = biorxiv_future.result()

    state.papers_found = arxiv_papers + biorxiv_papers

    print(f"arXiv papers: {len(arxiv_papers)}")
    print(f"bioRxiv papers: {len(biorxiv_papers)}")

    return state
