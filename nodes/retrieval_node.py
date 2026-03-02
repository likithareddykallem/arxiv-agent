from concurrent.futures import ThreadPoolExecutor

from utils.biorxiv_html import fetch_biorxiv_html
from utils.html_utils import fetch_arxiv_html_text
from utils.pdf_utils import extract_pdf_text_from_url
from utils.text_utils import is_text_sufficient


def _retrieve_one(paper):
    source = paper.get("source", "arxiv")

    if source == "biorxiv":
        html_text = fetch_biorxiv_html(paper.get("content_url", ""))
        if is_text_sufficient(html_text):
            paper["full_text"] = html_text
            return paper
        pdf_url = paper.get("pdf_url")
        paper["full_text"] = extract_pdf_text_from_url(pdf_url) if pdf_url else None
    else:
        # arXiv /abs pages often lack sufficient full-body chemistry detail; prefer PDF first.
        pdf_url = paper.get("pdf_url")
        pdf_text = extract_pdf_text_from_url(pdf_url) if pdf_url else None
        if is_text_sufficient(pdf_text):
            paper["full_text"] = pdf_text
            return paper
        html_text = fetch_arxiv_html_text(paper["id"])
        paper["full_text"] = html_text if is_text_sufficient(html_text) else pdf_text

    return paper


def retrieve_paper_texts(state):
    if not state.relevant_papers:
        return state

    with ThreadPoolExecutor(max_workers=4) as executor:
        state.relevant_papers = list(executor.map(_retrieve_one, state.relevant_papers))

    return state
