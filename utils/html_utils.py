import requests
from bs4 import BeautifulSoup

def fetch_arxiv_html_text(paper_id):

    url = f"https://arxiv.org/abs/{paper_id}"

    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "lxml")

        return soup.get_text(separator=" ")

    except:
        return None