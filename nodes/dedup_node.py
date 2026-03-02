def _norm(value):
    return str(value or "").strip()


def _merge_csv_values(a, b):
    left = [x.strip() for x in _norm(a).split(",") if x.strip() and x.strip().lower() != "not mentioned"]
    right = [x.strip() for x in _norm(b).split(",") if x.strip() and x.strip().lower() != "not mentioned"]
    merged = []
    seen = set()
    for item in left + right:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            merged.append(item)
    return ", ".join(merged) if merged else "Not mentioned"


def deduplicate_rows(state):
    merged_by_key = {}

    for row in state.extracted_data:
        paper = _norm(row.get("paper")) or "Unknown"
        url = _norm(row.get("url")) or "Not mentioned"
        key = (paper.lower(), url.lower())

        if key not in merged_by_key:
            merged_by_key[key] = dict(row)
            merged_by_key[key]["paper"] = paper
            merged_by_key[key]["url"] = url
            continue

        existing = merged_by_key[key]
        existing["linker_types"] = _merge_csv_values(existing.get("linker_types"), row.get("linker_types"))
        if _norm(existing.get("evidence")).lower() in ("", "not mentioned"):
            existing["evidence"] = _norm(row.get("evidence")) or "Not mentioned"

    state.extracted_data = list(merged_by_key.values())
    return state
