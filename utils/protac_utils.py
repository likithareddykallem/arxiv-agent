import re

LINKER_KEYWORDS = [
    "linker",
    "peg",
    "spacer",
    "tether",
    "flexible",
    "rigid"
]

TARGET_KEYWORDS = [
    "brd4",
    "crbn",
    "vhl",
    "mdm2",
    "btk"
]

def detect_linker_mentions(text):

    if not text:
        return []

    text_lower = text.lower()

    found = []

    for keyword in LINKER_KEYWORDS:
        if keyword in text_lower:
            found.append(keyword)

    return list(set(found))


def detect_targets(text):

    if not text:
        return []

    text_lower = text.lower()

    targets = []

    for keyword in TARGET_KEYWORDS:
        if keyword in text_lower:
            targets.append(keyword.upper())

    return list(set(targets))