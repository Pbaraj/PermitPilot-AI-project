from app.schemas.permit_schema import PermitReviewState
from app.services.rag_service import retrieve_regulation_context


def build_rag_queries(state: PermitReviewState) -> list[str]:
    queries = []

    for item in state.checklist_results:
        if item.status == "Missing" or item.evidence_quality in [
            "Mentioned as missing",
            "Not found",
            "Unclear / conditional",
        ]:
            evidence_text = " ".join(item.evidence)

            queries.append(
                f"{item.requirement} {item.status} {item.evidence_quality} {evidence_text}"
            )

    project_summary_query = " ".join(
        [
            state.project_summary.get("project_name", ""),
            state.project_summary.get("project_address", ""),
            state.project_summary.get("building_type", ""),
            state.jurisdiction,
        ]
    )

    if project_summary_query.strip():
        queries.append(project_summary_query)

    if not queries:
        queries.append(f"{state.jurisdiction} building permit application documents")

    return queries


def run_rag_regulation_agent(state: PermitReviewState) -> PermitReviewState:
    queries = build_rag_queries(state)

    rag_context = retrieve_regulation_context(
        jurisdiction=state.jurisdiction,
        queries=queries,
        top_k=6,
    )

    state.project_summary["rag_queries"] = queries[:10]
    state.project_summary["rag_regulation_context"] = rag_context

    return state