from config.settings import MAX_RECRAWL_ROUNDS
from utils.llm_utils import generate_search_queries_with_intents


def build_round_queries(user_query, max_rounds=MAX_RECRAWL_ROUNDS):
    base_query = (user_query or "").strip()
    if not base_query:
        return []

    planned = generate_search_queries_with_intents(base_query, max_queries_per_intent=max_rounds)
    broad = planned.get("broad_queries", [])
    strict = planned.get("strict_queries", [])

    merged = []
    max_len = max(len(broad), len(strict))
    for i in range(max_len):
        if i < len(strict):
            merged.append({"query": strict[i], "intent": "strict"})
        if i < len(broad):
            merged.append({"query": broad[i], "intent": "broad"})

    out = []
    seen = set()
    for item in merged:
        q = item["query"].strip()
        key = q.lower()
        if not q or key in seen:
            continue
        seen.add(key)
        out.append(item)

    if not out:
        out = [{"query": base_query, "intent": "strict"}]
    return out
