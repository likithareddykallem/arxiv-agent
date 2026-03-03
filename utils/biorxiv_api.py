import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin

from config.settings import MAX_RESULTS


def _parse_biorxiv_date(node):
    date_tag = node.select_one("span.highwire-cite-metadata-date")
    date_text = date_tag.get_text(" ", strip=True) if date_tag else node.get_text(" ", strip=True)
    date_text = re.sub(r"^\s*posted\s*", "", date_text, flags=re.IGNORECASE).strip()

    for fmt in ("%B %d, %Y", "%b %d, %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_text, fmt).date().isoformat()
        except Exception:
            continue

    year_match = re.search(r"\b(19|20)\d{2}\b", date_text)
    if year_match:
        return f"{year_match.group(0)}-01-01"
    return "Not mentioned"


def search_biorxiv(query, max_results=None):
    limit = max_results if isinstance(max_results, int) and max_results > 0 else MAX_RESULTS
    encoded_query = quote_plus(query)
    url = (
        "https://www.biorxiv.org/search/"
        f"{encoded_query}%20numresults%3A{limit}%20sort%3Arelevance-rank"
    )

    try:
        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                )
            },
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        papers = []
        result_nodes = soup.select("div.highwire-article-citation")

        for node in result_nodes:
            title_tag = node.select_one("span.highwire-cite-title a")
            if not title_tag:
                continue

            content_url = urljoin("https://www.biorxiv.org", title_tag.get("href", ""))
            paper_id = content_url.split("/content/")[-1] if "/content/" in content_url else content_url
            snippet_tag = node.select_one("div.highwire-cite-snippet")
            snippet = snippet_tag.get_text(" ", strip=True) if snippet_tag else ""
            published_date = _parse_biorxiv_date(node)

            papers.append(
                {
                    "id": paper_id,
                    "title": title_tag.get_text(" ", strip=True),
                    "abstract": snippet or title_tag.get_text(" ", strip=True),
                    "pdf_url": f"{content_url}.full.pdf",
                    "content_url": content_url,
                    "published_date": published_date,
                    "source": "biorxiv",
                }
            )

        return papers

    except Exception as e:
        print("bioRxiv Error:", e)
        return []
