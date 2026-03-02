import ast
import json
import os
import re

import ollama


MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
_RESOLVED_MODEL = None
_LAST_LLM_ERROR = None


FIELD_GROUPS = {
    "protac": ["target_protein", "e3_ligase", "warhead"],
    "linker": ["linker_type", "linker_length", "functional_groups", "linker_attachment_site"],
    "assay": ["assay_type", "degradation_dc50", "degradation_dmax", "cell_line"],
    "chemistry": ["smiles", "scaffold", "substituents"],
}


def infer_target_fields(query):
    q = (query or "").lower()
    fields = []

    if "protac" in q or "degrader" in q:
        fields.extend(FIELD_GROUPS["protac"])
    if any(k in q for k in ("linker", "spacer", "peg", "tether")):
        fields.extend(FIELD_GROUPS["linker"])
    if any(k in q for k in ("dc50", "dmax", "assay", "activity", "potency", "cell")):
        fields.extend(FIELD_GROUPS["assay"])
    if any(k in q for k in ("smiles", "chem", "scaffold", "substituent", "compound")):
        fields.extend(FIELD_GROUPS["chemistry"])

    if not fields:
        fields = ["main_entities", "methods", "key_findings"]

    # Keep order, remove duplicates.
    dedup = []
    seen = set()
    for field in fields:
        if field not in seen:
            seen.add(field)
            dedup.append(field)

    # Always include evidence context.
    dedup.append("context")
    return dedup


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
            print(f"LLM Model fallback: '{preferred}' not found, using '{candidate}'.")
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


def normalize_result(raw_result, target_fields):
    if not isinstance(raw_result, dict):
        return None

    normalized = {}
    for field in target_fields:
        value = raw_result.get(field, "Not mentioned")
        if isinstance(value, (list, tuple, set)):
            value = ", ".join(str(v).strip() for v in value if str(v).strip())
        value = str(value).strip() if value is not None else "Not mentioned"
        normalized[field] = value if value else "Not mentioned"

    return normalized


def has_meaningful_fields(row):
    if not row:
        return False
    for key, value in row.items():
        if key == "context":
            continue
        if str(value).strip().lower() != "not mentioned":
            return True
    return False


def extract_structured_info(text_chunk, query, target_fields):
    fields_json = ",\n  ".join(f"\"{field}\": \"...\"" for field in target_fields)
    prompt = f"""
You are a strict scientific information extraction engine.

TASK:
- Extract only information explicitly present in the text and relevant to query: "{query}".
- Return exactly these fields as JSON keys:
{", ".join(target_fields)}
- If a field is not explicitly present, return "Not mentioned".
- Do not infer or hallucinate.

Return JSON only:
{{
  {fields_json}
}}

Text:
{text_chunk}
"""

    try:
        model_name = _resolve_model_name()
        response = ollama.chat(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.get("message", {}).get("content", "")
        parsed = parse_llm_json(content)
        return normalize_result(parsed, target_fields)
    except Exception as e:
        global _LAST_LLM_ERROR
        err_msg = str(e)
        if err_msg != _LAST_LLM_ERROR:
            print("LLM Error:", e)
            _LAST_LLM_ERROR = err_msg
        return None
