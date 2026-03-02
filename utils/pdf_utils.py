import fitz
import requests
import os
import tempfile

def extract_pdf_text_from_url(pdf_url):

    if not pdf_url:
        return None

    temp_path = None

    try:
        response = requests.get(pdf_url, timeout=20)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(response.content)
            temp_path = temp_file.name

        doc = fitz.open(temp_path)

        text = ""
        for page in doc:
            text += page.get_text()

        doc.close()
        return text

    except Exception:
        return None
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
