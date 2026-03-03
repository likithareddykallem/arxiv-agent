import json
import math
from pathlib import Path

from config.settings import MIN_OUTPUT_LINKS, TOTAL_LINK_TARGET
from nodes.dedup_node import dedup_papers
from nodes.query_planner_node import build_round_queries
from nodes.relevance_node import rank_by_relevance
from nodes.result_node import build_link_rows, sort_by_published_date_desc
from nodes.search_node import search_arxiv
from nodes.timeline_node import extract_timeline_range, filter_by_timeline, strip_timeline_from_query
from state.agent_state import AgentState


def run_pipeline(user_query):
    state = AgentState()
    state.query = user_query

    start_date, end_date = extract_timeline_range(user_query)
    planner_query = strip_timeline_from_query(user_query) or user_query
    round_queries = build_round_queries(planner_query)

    if not round_queries:
        round_queries = [{"query": planner_query, "intent": "strict"}]

    queries_count = len(round_queries)
    per_query_total_budget = max(20, math.ceil(TOTAL_LINK_TARGET / queries_count))
    per_source_budget = max(10, math.ceil(per_query_total_budget / 2))

    print("\n=== Pipeline Start ===")
    print(f"Input query: {user_query}")
    print(f"Planner query (timeline removed): {planner_query}")
    if start_date and end_date:
        print(f"Timeline filter: {start_date.isoformat()} -> {end_date.isoformat()}")
    else:
        print("Timeline filter: None")
    print(f"Round count: {queries_count}")
    print(f"Per-source fetch budget per round: {per_source_budget}")
    print("\nGenerated queries:")
    for i, q in enumerate(round_queries, start=1):
        print(f"  {i}. [{q.get('intent', 'unknown')}] {q.get('query', '')}")

    query_trace = []
    all_papers = []

    for round_idx, query_info in enumerate(round_queries, start=1):
        query = query_info["query"]
        query_intent = query_info["intent"]

        print(f"\n--- Crawl Round {round_idx}/{queries_count} ---")

        round_state = AgentState()
        round_state.query = query
        round_state = search_arxiv(round_state, max_results_per_source=per_source_budget)

        before_dedup = len(all_papers)
        all_papers.extend(round_state.papers_found)
        all_papers = dedup_papers(all_papers)
        after_dedup = len(all_papers)

        print(
            f"Round summary: intent={query_intent} | "
            f"found_this_round={len(round_state.papers_found)} | "
            f"unique_total={after_dedup} (added {after_dedup - before_dedup})"
        )

        query_trace.append(
            {
                "round": round_idx,
                "input_query": user_query,
                "planner_query": planner_query,
                "round_query": query,
                "query_intent": query_intent,
                "expanded_search_query": getattr(round_state, "search_query_used", query),
                "per_source_fetch_budget": per_source_budget,
                "papers_found_this_round": len(round_state.papers_found),
                "unique_papers_so_far": len(all_papers),
                "timeline_filter_start": start_date.isoformat() if start_date else None,
                "timeline_filter_end": end_date.isoformat() if end_date else None,
            }
        )

    filtered_by_timeline = filter_by_timeline(all_papers, start_date, end_date)
    minimum_needed = min(MIN_OUTPUT_LINKS, len(filtered_by_timeline))
    ranked, rank_meta = rank_by_relevance(filtered_by_timeline, planner_query, min_results=minimum_needed)
    ranked = sort_by_published_date_desc(ranked)
    ranked = ranked[:TOTAL_LINK_TARGET]

    print("\n--- Post-filter summary ---")
    print(f"Timeline kept: {len(filtered_by_timeline)}")
    print(f"Semantic candidates: {rank_meta.get('semantic_candidates', 0)}")
    print(f"Ranked kept: {len(ranked)}")
    print(f"Fallback added to satisfy minimum links: {rank_meta.get('fallback_added', 0)}")
    print(f"Removed by strict focus/threshold: {rank_meta.get('removed_by_focus_or_threshold', 0)}")

    query_trace.append(
        {
            "stage": "post_aggregation_filtering",
            "papers_after_timeline_filter": len(filtered_by_timeline),
            "papers_after_token_semantic_filter": len(ranked),
            "strict_focus_mode": rank_meta.get("strict_focus_mode", False),
            "semantic_candidates": rank_meta.get("semantic_candidates", 0),
            "removed_by_focus_or_threshold": rank_meta.get("removed_by_focus_or_threshold", 0),
            "fallback_added": rank_meta.get("fallback_added", 0),
            "minimum_output_links_target": MIN_OUTPUT_LINKS,
        }
    )

    state.papers_found = all_papers
    state.relevant_papers = ranked
    state.extracted_data = build_link_rows(ranked)
    state.query_trace = query_trace
    state.scrape_log = state.extracted_data
    _write_scrape_log_json(user_query, query_trace, state.extracted_data)
    _write_result_json(user_query, query_trace, state.extracted_data)
    _print_links_to_console(state.extracted_data)
    print(f"\nFinal output links: {len(state.extracted_data)}")
    print("=== Pipeline End ===\n")
    return state


def _write_scrape_log_json(input_query, query_trace, link_rows):
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "scraped_links_relevance.json"
    payload = {
        "input_query": input_query,
        "query_trace": query_trace,
        "results": link_rows,
    }
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=True)


def _write_result_json(input_query, query_trace, link_rows):
    out_path = Path("result.json")
    payload = {
        "input_query": input_query,
        "total_links": len(link_rows),
        "query_trace": query_trace,
        "links": link_rows,
    }
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=True)


def _print_links_to_console(link_rows):
    print("\nFinal links:")
    if not link_rows:
        print("  No links found.")
        return
    for idx, row in enumerate(link_rows, start=1):
        print(
            f"  {idx}. {row.get('paper', 'Unknown')} | "
            f"{row.get('published_date', 'Not mentioned')} | "
            f"{row.get('url', 'Not mentioned')}"
        )


if __name__ == "__main__":
    try:
        user_query = input("Enter prompt: ").strip()
    except EOFError:
        user_query = ""

    if not user_query:
        print("Empty prompt. Exiting.")
    else:
        run_pipeline(user_query)
