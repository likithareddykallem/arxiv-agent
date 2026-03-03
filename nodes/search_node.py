from concurrent.futures import ThreadPoolExecutor

from utils.arxiv_api import search_arxiv_api
from utils.biorxiv_api import search_biorxiv


def search_arxiv(state, max_results_per_source=None):
    search_query = (state.query or "").strip()
    state.search_query_used = search_query

    with ThreadPoolExecutor(max_workers=2) as executor:
        arxiv_future = executor.submit(search_arxiv_api, search_query, max_results=max_results_per_source)
        biorxiv_future = executor.submit(search_biorxiv, search_query, max_results=max_results_per_source)
        arxiv_papers = arxiv_future.result()
        biorxiv_papers = biorxiv_future.result()

    state.papers_found = arxiv_papers + biorxiv_papers

    print(f"Search query: {search_query}")
    print(f"arXiv papers: {len(arxiv_papers)}")
    print(f"bioRxiv papers: {len(biorxiv_papers)}")

    return state
