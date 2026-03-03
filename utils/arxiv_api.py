import requests
import feedparser
from config.settings import MAX_RESULTS


def search_arxiv_api(query, max_results=None):
    limit = max_results if isinstance(max_results, int) and max_results > 0 else MAX_RESULTS
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={limit}"

    try:
        response = requests.get(url, timeout=10)
        feed = feedparser.parse(response.text)

        papers = []

        for entry in feed.entries:
            pdf_url = None

            for link in entry.links:
                if link.type == "application/pdf":
                    pdf_url = link.href
                    break

            papers.append(
                {
                    "id": entry.id.split("/")[-1],
                    "title": entry.title,
                    "abstract": entry.summary,
                    "pdf_url": pdf_url,
                    "content_url": f"https://arxiv.org/abs/{entry.id.split('/')[-1]}",
                    "published_date": (getattr(entry, "published", "") or "").split("T")[0] or "Not mentioned",
                    "source": "arxiv",
                }
            )

        return papers

    except Exception as e:
        print("arXiv API Error:", e)
        return []
