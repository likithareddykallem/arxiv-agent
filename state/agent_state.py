from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class AgentState:
    query: str = ""
    papers_found: List[Dict] = field(default_factory=list)
    relevant_papers: List[Dict] = field(default_factory=list)
    extracted_data: List[Dict] = field(default_factory=list)
    target_fields: List[str] = field(default_factory=list)
    compounds_found: List[str] = field(default_factory=list)
    confidence_scores: List[float] = field(default_factory=list)
    iteration: int = 0
