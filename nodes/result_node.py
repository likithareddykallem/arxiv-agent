from nodes.timeline_node import parse_paper_date


def sort_by_published_date_desc(papers):
    papers.sort(
        key=lambda p: parse_paper_date(p.get("published_date")) or parse_paper_date("1900-01-01"),
        reverse=True,
    )
    return papers


def build_link_rows(papers):
    rows = []
    for p in papers:
        rows.append(
            {
                "paper": p.get("title", "Unknown"),
                "url": p.get("content_url") or p.get("pdf_url") or "Not mentioned",
                "published_date": p.get("published_date", "Not mentioned"),
            }
        )
    return rows
