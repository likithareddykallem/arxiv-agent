import re

def clean_text(text):

    if not text:
        return text

    text = re.sub(r"\s+", " ", text)
    return text.strip()


def is_text_sufficient(text, min_length=2000):

    return text and len(text) > min_length