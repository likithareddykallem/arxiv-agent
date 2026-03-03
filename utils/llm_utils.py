import ast
import json
import os
import re

import ollama


MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
_RESOLVED_MODEL = None
_SEMANTIC_CACHE = {}


def _resolve_model_name():
    global _RESOLVED_MODEL
    if _RESOLVED_MODEL:
        return _RESOLVED_MODEL

    preferred = MODEL_NAME
    fallbacks = ["llama3.2:3b", "llama3.2", "llama3", "mistral", "qwen2.5:3b"]

    try:
        listing = ollama.list()
        models = listing.get("models", []) if isinstance(listing, dict) else []
        installed = {m.get("model") for m in models if isinstance(m, dict) and m.get("model")}
    except Exception:
        installed = set()

    if preferred in installed:
        _RESOLVED_MODEL = preferred
        return _RESOLVED_MODEL

    for candidate in fallbacks:
        if candidate in installed:
            _RESOLVED_MODEL = candidate
            return _RESOLVED_MODEL

    _RESOLVED_MODEL = preferred
    return _RESOLVED_MODEL


def parse_llm_json(content):
    if not content:
        return None

    candidates = []
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", content, flags=re.IGNORECASE)
    if fence_match:
        candidates.append(fence_match.group(1).strip())

    obj_match = re.search(r"\{[\s\S]*?\}", content)
    if obj_match:
        candidates.append(obj_match.group(0).strip())

    candidates.append(content.strip())

    for candidate in candidates:
        if not candidate:
            continue
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            try:
                parsed = ast.literal_eval(candidate)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                continue
    return None


def generate_search_queries_with_intents(query, max_queries_per_intent=6):
    base = (query or "").strip()
    if not base:
        return {"broad_queries": [], "strict_queries": []}

    prompt = f"""
You are a scientific literature search planner.

User query:
"{base}"

Generate two sets of search queries for arXiv/bioRxiv:
1) broad_queries: maximize recall with synonyms and neighboring terms.
2) strict_queries: maximize precision and stay tightly on intent.

Rules:
- Each query should be short (4 to 14 words).
- Do not include numbering or explanations.
- Do not include timeline constraints, explicit years, year ranges, or date words in the queries (timeline is handled in a separate step).
- Return JSON only:
{{
  "broad_queries": ["..."],
  "strict_queries": ["..."]
}}
"""
    try:
        model_name = _resolve_model_name()
        response = ollama.chat(model=model_name, messages=[{"role": "user", "content": prompt}])
        parsed = parse_llm_json(response.get("message", {}).get("content", ""))
        if isinstance(parsed, dict):
            broad = parsed.get("broad_queries")
            strict = parsed.get("strict_queries")

            def _clean(items):
                if not isinstance(items, list):
                    return []
                out = []
                seen = set()
                for it in items:
                    q = str(it).strip()
                    if not q:
                        continue
                    # Strip accidental timeline fragments from generated queries.
                    q = re.sub(r"\b(?:between\s+)?(19|20)\d{2}\s*(?:-|to|and)\s*(19|20)\d{2}\b", " ", q, flags=re.IGNORECASE)
                    q = re.sub(r"\b(19|20)\d{2}\b", " ", q)
                    q = re.sub(r"\b(from|between|to|during|in)\b", " ", q, flags=re.IGNORECASE)
                    q = re.sub(r"\s+", " ", q).strip(" ,.-")
                    if not q:
                        continue
                    key = q.lower()
                    if key in seen:
                        continue
                    seen.add(key)
                    out.append(q)
                return out[:max_queries_per_intent]

            broad_clean = _clean(broad)
            strict_clean = _clean(strict)
            if base.lower() not in {q.lower() for q in broad_clean + strict_clean}:
                strict_clean.insert(0, base)
            return {"broad_queries": broad_clean, "strict_queries": strict_clean}
    except Exception:
        pass

    fallback = [base, f"{base} review", f"{base} analysis"]
    return {"broad_queries": fallback[:max_queries_per_intent], "strict_queries": [base]}


def semantic_relevance_score(query, title, abstract):
    key = (str(query).strip().lower(), str(title).strip().lower(), str(abstract).strip().lower())
    if key in _SEMANTIC_CACHE:
        return _SEMANTIC_CACHE[key]

    prompt = f"""
You are a strict scientific relevance scorer.

User query:
"{query}"

Paper:
Title: "{title}"
Abstract: "{abstract}"

Return JSON only:
{{
  "score": 0.0,
  "primary_focus": false,
  "reason": "short reason"
}}
"""
    try:
        model_name = _resolve_model_name()
        response = ollama.chat(model=model_name, messages=[{"role": "user", "content": prompt}])
        parsed = parse_llm_json(response.get("message", {}).get("content", ""))
        if isinstance(parsed, dict):
            try:
                score = float(parsed.get("score", 0.0))
            except Exception:
                score = 0.0
            result = {
                "score": max(0.0, min(1.0, round(score, 4))),
                "primary_focus": bool(parsed.get("primary_focus", False)),
                "reason": str(parsed.get("reason", "")).strip()[:160],
            }
            _SEMANTIC_CACHE[key] = result
            return result
    except Exception:
        pass

    result = {"score": 0.0, "primary_focus": False, "reason": "semantic scorer unavailable"}
    _SEMANTIC_CACHE[key] = result
    return result
