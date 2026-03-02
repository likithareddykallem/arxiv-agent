from config.settings import MAX_RECRAWL_ROUNDS, MIN_OUTPUT_ROWS, RECRAWL_QUERY_SUFFIXES
from nodes.cleaning_node import clean_papers
from nodes.dedup_node import deduplicate_rows
from nodes.filter_node import filter_relevant_papers
from nodes.llm_extraction_node import llm_extraction_node
from nodes.retrieval_node import retrieve_paper_texts
from nodes.search_node import search_arxiv
from state.agent_state import AgentState


def _paper_key(paper):
    source = str(paper.get("source", "")).strip().lower()
    pid = str(paper.get("id", "")).strip().lower()
    title = str(paper.get("title", "")).strip().lower()
    return source, pid or title


def _build_round_queries(user_query):
    base = (user_query or "").strip()
    queries = []
    for suffix in RECRAWL_QUERY_SUFFIXES:
        q = f"{base} {suffix}".strip() if suffix else base
        if q and q not in queries:
            queries.append(q)
    return queries[:MAX_RECRAWL_ROUNDS]


def run_pipeline(user_query):
    state = AgentState()
    state.query = user_query

    seen_papers = set()
    aggregated_rows = []
    round_queries = _build_round_queries(user_query)

    for round_idx, query in enumerate(round_queries, start=1):
        round_state = AgentState()
        round_state.query = query

        round_state = search_arxiv(round_state)
        round_state = filter_relevant_papers(round_state)

        # Recrawl mode: process only new papers from this round.
        new_relevant = []
        for paper in round_state.relevant_papers:
            key = _paper_key(paper)
            if key in seen_papers:
                continue
            seen_papers.add(key)
            new_relevant.append(paper)
        round_state.relevant_papers = new_relevant

        print(f"Recrawl round {round_idx}: new relevant papers {len(new_relevant)}")

        if not round_state.relevant_papers:
            continue

        round_state = retrieve_paper_texts(round_state)
        round_state = clean_papers(round_state)
        round_state = llm_extraction_node(round_state)
        round_state = deduplicate_rows(round_state)

        aggregated_rows.extend(round_state.extracted_data)

        state.papers_found.extend(round_state.papers_found)
        state.relevant_papers.extend(round_state.relevant_papers)
        state.target_fields = round_state.target_fields or state.target_fields

        state.extracted_data = aggregated_rows
        state = deduplicate_rows(state)
        aggregated_rows = state.extracted_data

        print(f"Recrawl round {round_idx}: extracted rows total {len(aggregated_rows)}")

        if len(aggregated_rows) >= MIN_OUTPUT_ROWS:
            break

    # Final guard: if still below minimum, keep whatever high-precision rows were found.
    state.extracted_data = aggregated_rows
    return state
