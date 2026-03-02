MAX_RESULTS = 12
TEXT_MIN_LENGTH = 2000
MAX_RELEVANT_PAPERS = 8
MAX_CHUNKS_PER_PAPER = 3
STOP_AFTER_FIRST_EXTRACTION_PER_PAPER = True
ALLOW_MINIMUM_FALLBACK = False

LINKER_KEYWORDS = [
    "linker",
    "peg",
    "polyethylene glycol",
    "alkyl chain",
    "spacer",
    "flexible linker",
    "rigid linker",
    "ethylene glycol",
    "triazole",
    "amide linker",
    "ether linker",
]

LINKER_TYPE_PATTERNS = {
    "PEG": [
        r"\bpeg\b",
        r"polyethylene glycol",
        r"ethylene glycol",
    ],
    "Alkyl": [
        r"\balkyl\b",
        r"alkyl chain",
        r"methylene",
    ],
    "Aromatic": [
        r"\baromatic\b",
        r"\bphenyl\b",
        r"\bbenzyl\b",
    ],
    "Triazole": [
        r"triazole",
    ],
    "Piperazine": [
        r"piperazine",
    ],
    "Amide": [
        r"\bamide\b",
    ],
    "Ether": [
        r"\bether\b",
    ],
    "Rigid": [
        r"\brigid\b",
    ],
    "Flexible": [
        r"\bflexible\b",
    ],
}

NON_EXPERIMENTAL_TITLE_KEYWORDS = [
    "review",
    "machine learning",
    "deep learning",
    "reinforcement learning",
    "in silico",
    "graph-based",
    "generative model",
    "structure prediction",
    "point cloud",
]

QUERY_STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "for",
    "with",
    "without",
    "of",
    "in",
    "on",
    "to",
    "from",
    "by",
    "using",
    "via",
    "based",
    "analysis",
    "study",
    "paper",
}

MIN_OUTPUT_ROWS = 5
MAX_RECRAWL_ROUNDS = 4
RECRAWL_QUERY_SUFFIXES = [
    "",
    "experimental synthesis",
    "medicinal chemistry",
    "structure activity relationship",
]

CONFIDENCE_WEIGHTS = {
    "smiles": 0.4,
    "linker_type": 0.3,
    "length": 0.3
}
