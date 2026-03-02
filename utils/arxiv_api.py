import requests
import feedparser
from config.settings import MAX_RESULTS

def search_arxiv_api(query):

    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={MAX_RESULTS}"

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

            papers.append({
                "id": entry.id.split("/")[-1],
                "title": entry.title,
                "abstract": entry.summary,
                "pdf_url": pdf_url,
                "content_url": f"https://arxiv.org/abs/{entry.id.split('/')[-1]}",
                "source": "arxiv",
            })

        return papers

    except Exception as e:
        print("arXiv API Error:", e)
        return []
