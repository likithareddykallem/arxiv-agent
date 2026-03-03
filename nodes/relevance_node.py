import re

from config.settings import (
    MAX_SEMANTIC_CANDIDATES,
    MIN_COMBINED_RELEVANCE,
    SEMANTIC_RERANK_ENABLED,
    STRICT_FOCUS_HIGH_SCORE,
)
from utils.llm_utils import semantic_relevance_score


def query_tokens(text):
    tokens = re.findall(r"[a-zA-Z0-9\-\+]+", (text or "").lower())
    stop = {"papers", "paper", "from", "to", "between", "about", "need", "only", "urls", "url", "links", "link"}
    return [t for t in tokens if len(t) >= 3 and t not in stop and not re.fullmatch(r"(19|20)\d{2}", t)]


def token_match_score(query, title, abstract):
    tokens = query_tokens(query)
    if not tokens:
        return 0.0, 0, 0.0
    title_l = (title or "").lower()
    abstract_l = (abstract or "").lower()
    text = f"{title_l} {abstract_l}"
    hits = sum(1 for t in tokens if t in text)
    title_hits = sum(1 for t in tokens if t in title_l)
    coverage = hits / len(tokens)
    score = hits + (0.5 * title_hits)
    return score, hits, coverage


def rank_by_relevance(papers, user_query, min_results=0):
    if not papers:
        return [], {
            "strict_focus_mode": False,
            "semantic_candidates": 0,
            "removed_by_focus_or_threshold": 0,
            "fallback_added": 0,
        }

    token_scored = []
    for p in papers:
        t_score, hits, coverage = token_match_score(user_query, p.get("title", ""), p.get("abstract", ""))
        if hits == 0 and coverage == 0:
            continue
        cp = dict(p)
        cp["token_score"] = t_score
        cp["relevance_hits"] = hits
        cp["relevance_coverage"] = round(coverage, 3)
        token_scored.append(cp)

    if not token_scored:
        token_scored = [dict(p) for p in papers]
        for p in token_scored:
            p["token_score"] = 0.0
            p["relevance_hits"] = 0
            p["relevance_coverage"] = 0.0

    token_scored.sort(key=lambda p: p.get("token_score", 0), reverse=True)
    candidates = token_scored[:MAX_SEMANTIC_CANDIDATES]
    max_token = max([p.get("token_score", 0) for p in candidates], default=1.0) or 1.0

    ranked = []
    scored_all = []
    strict_focus_mode = len(query_tokens(user_query)) >= 2

    for p in candidates:
        normalized_token = p.get("token_score", 0) / max_token
        sem = {"score": 0.0, "primary_focus": False, "reason": "semantic rerank disabled"}
        if SEMANTIC_RERANK_ENABLED:
            sem = semantic_relevance_score(user_query, p.get("title", ""), p.get("abstract", ""))
        combined = (0.55 * normalized_token) + (0.45 * sem.get("score", 0.0))

        p["token_score_normalized"] = round(normalized_token, 4)
        p["semantic_score"] = sem.get("score", 0.0)
        p["semantic_primary_focus"] = sem.get("primary_focus", False)
        p["semantic_reason"] = sem.get("reason", "")
        p["relevance_score"] = round(combined, 4)

        passes_threshold = combined >= MIN_COMBINED_RELEVANCE
        passes_focus = True if not strict_focus_mode else (p["semantic_primary_focus"] or combined >= STRICT_FOCUS_HIGH_SCORE)

        if passes_threshold and passes_focus:
            ranked.append(p)
        scored_all.append(p)

    ranked.sort(key=lambda p: p.get("relevance_score", 0), reverse=True)

    fallback_added = 0
    if min_results > 0 and len(ranked) < min_results:
        ranked_ids = {r.get("id") for r in ranked}
        scored_all.sort(key=lambda p: p.get("relevance_score", 0), reverse=True)
        for p in scored_all:
            if len(ranked) >= min_results:
                break
            if p.get("id") in ranked_ids:
                continue
            ranked.append(p)
            ranked_ids.add(p.get("id"))
            fallback_added += 1

    ranked.sort(key=lambda p: p.get("relevance_score", 0), reverse=True)
    total_candidates = len(candidates)
    removed_by_focus = total_candidates - len(ranked)
    return ranked, {
        "strict_focus_mode": strict_focus_mode,
        "semantic_candidates": total_candidates,
        "removed_by_focus_or_threshold": max(0, removed_by_focus),
        "fallback_added": fallback_added,
    }
