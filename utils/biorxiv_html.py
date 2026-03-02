import requests
from bs4 import BeautifulSoup

def fetch_biorxiv_html(url):

    try:
        if not url:
            return None

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

        return soup.get_text(separator=" ")

    except Exception:
        return None
