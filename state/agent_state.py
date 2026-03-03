from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class AgentState:
    query: str = ""
    papers_found: List[Dict] = field(default_factory=list)
    relevant_papers: List[Dict] = field(default_factory=list)
    extracted_data: List[Dict] = field(default_factory=list)
    scrape_log: List[Dict] = field(default_factory=list)
    query_trace: List[Dict] = field(default_factory=list)
