import re

from config.settings import LINKER_TYPE_PATTERNS


def _find_linker_types(text):
    lowered = (text or "").lower()
    found = []
    for linker_type, patterns in LINKER_TYPE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, lowered):
                found.append(linker_type)
                break
    return sorted(set(found))


def _extract_evidence(text, linker_types):
    if not text or not linker_types:
        return "Not mentioned"

    sentences = re.split(r"(?<=[.!?])\s+", text)
    cues = [lt.lower() for lt in linker_types]
    for sentence in sentences:
        s = sentence.strip()
        if not s:
            continue
        s_low = s.lower()
        if "linker" in s_low and any(cue in s_low for cue in cues):
            return s[:400]
    for sentence in sentences:
        s = sentence.strip()
        if not s:
            continue
        s_low = s.lower()
        if any(cue in s_low for cue in cues):
            return s[:400]
    return "Not mentioned"


def llm_extraction_node(state):
    extracted_data = []

    for paper in state.relevant_papers:
        text = " ".join(
            [
                str(paper.get("title") or ""),
                str(paper.get("abstract") or ""),
                str(paper.get("full_text") or ""),
            ]
        )

        if "protac" not in text.lower() and "degrader" not in text.lower():
            continue

        linker_types = _find_linker_types(text)
        if not linker_types:
            continue

        url = paper.get("content_url") or paper.get("pdf_url") or "Not mentioned"
        extracted_data.append(
            {
                "paper": paper.get("title", "Unknown"),
                "source": paper.get("source", "unknown"),
                "url": url,
                "linker_types": ", ".join(linker_types),
                "evidence": _extract_evidence(text, linker_types),
            }
        )

    state.extracted_data = extracted_data
    return state
