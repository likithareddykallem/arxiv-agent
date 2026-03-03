import re
from datetime import date, datetime


def extract_timeline_range(user_query):
    text = (user_query or "").lower()

    m = re.search(r"\b((19|20)\d{2})\s*(?:-|to|and)\s*((19|20)\d{2})\b", text)
    if m:
        y1, y2 = int(m.group(1)), int(m.group(3))
        return date(min(y1, y2), 1, 1), date(max(y1, y2), 12, 31)

    m = re.search(r"\b((19|20)\d{2})\b", text)
    if m:
        y = int(m.group(1))
        return date(y, 1, 1), date(y, 12, 31)

    return None, None


def strip_timeline_from_query(user_query):
    text = (user_query or "").strip()
    if not text:
        return ""

    text = re.sub(
        r"\b(?:between\s+)?((19|20)\d{2})\s*(?:-|to|and)\s*((19|20)\d{2})\b",
        " ",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"\b(19|20)\d{2}\b", " ", text)
    text = re.sub(r"\b(from|between|to|and|during|in)\b", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip(" ,.-")
    return text


def parse_paper_date(raw_date):
    raw = str(raw_date or "").strip()
    if not raw or raw.lower() == "not mentioned":
        return None

    try:
        return datetime.fromisoformat(raw).date()
    except Exception:
        pass

    for fmt in ("%B %d, %Y", "%b %d, %Y", "%Y-%m-%d", "%Y"):
        try:
            parsed = datetime.strptime(raw, fmt).date()
            if fmt == "%Y":
                return date(parsed.year, 1, 1)
            return parsed
        except Exception:
            continue

    y = re.search(r"\b(19|20)\d{2}\b", raw)
    if y:
        return date(int(y.group(0)), 1, 1)
    return None


def filter_by_timeline(papers, start_date, end_date):
    if not start_date or not end_date:
        return papers

    filtered = []
    for p in papers:
        pdate = parse_paper_date(p.get("published_date"))
        if pdate and start_date <= pdate <= end_date:
            filtered.append(p)
    return filtered
