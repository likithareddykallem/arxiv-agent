def paper_key(paper):
    source = str(paper.get("source", "")).strip().lower()
    pid = str(paper.get("id", "")).strip().lower()
    title = str(paper.get("title", "")).strip().lower()
    return source, pid or title


def dedup_papers(papers):
    seen = set()
    out = []
    for p in papers:
        key = paper_key(p)
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
    return out
