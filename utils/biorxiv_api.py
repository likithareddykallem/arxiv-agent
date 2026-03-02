import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin

from config.settings import MAX_RESULTS

def search_biorxiv(query):
    encoded_query = quote_plus(query)
    url = (
        "https://www.biorxiv.org/search/"
        f"{encoded_query}%20numresults%3A{MAX_RESULTS}%20sort%3Arelevance-rank"
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

            papers.append({
                "id": paper_id,
                "title": title_tag.get_text(" ", strip=True),
                "abstract": snippet or title_tag.get_text(" ", strip=True),
                "pdf_url": f"{content_url}.full.pdf",
                "content_url": content_url,
                "source": "biorxiv",
            })

        return papers

    except Exception as e:
        print("bioRxiv Error:", e)
        return []
