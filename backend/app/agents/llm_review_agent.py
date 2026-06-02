from app.schemas.permit_schema import PermitReviewState
from app.services.llm_service import call_llm_json


def create_fallback_llm_review(state: PermitReviewState) -> dict:
    missing_required = [
        item.requirement
        for item in state.checklist_results
        if item.required and item.status == "Missing"
    ]

    high_risks = [
        risk.title
        for risk in state.risks
        if risk.severity.lower() == "high"
    ]

    rag_context = state.project_summary.get("rag_regulation_context", [])

    if len(missing_required) == 0:
        decision = "Ready for detailed manual review."
        summary = (
            "The uploaded document appears to contain the main required items "
            "based on the selected checklist. A qualified reviewer should still "
            "verify legal, technical, and project-specific requirements."
        )

    elif len(high_risks) > 0 or len(missing_required) >= 5:
        decision = (
            "Incomplete submission — correction required before full permit review."
        )

        if rag_context:
            summary = (
                "The application contains some basic project information, but several "
                "important Munich-relevant documents are missing or unclear. Retrieved "
                "Munich/Bavaria regulation context also indicates that these documents "
                "are relevant for completeness screening. The document should be corrected "
                "before it is treated as ready for detailed review."
            )
        else:
            summary = (
                "The application contains some basic project information, but several "
                "important Munich-relevant documents are missing or unclear. The document "
                "should be corrected before it is treated as ready for detailed review."
            )

    else:
        decision = "Partially complete — manual review recommended."

        if rag_context:
            summary = (
                "The application contains several required items, but some documents are "
                "missing or unclear. Retrieved Munich/Bavaria regulation context supports "
                "manual verification of the missing or conditional requirements."
            )
        else:
            summary = (
                "The application contains several required items, but some documents are "
                "missing or unclear. A human reviewer should check the missing items before "
                "the submission proceeds further."
            )

    priority_actions = missing_required[:5]

    if not priority_actions:
        priority_actions = [
            "Verify that all documents are formally complete and correctly signed.",
            "Check project-specific Munich/LBK requirements.",
            "Confirm that drawings and technical proofs are consistent.",
        ]

    return {
        "ai_screening_decision": decision,
        "ai_reviewer_summary": summary,
        "priority_actions": priority_actions,
        "llm_used": False,
        "llm_provider": "fallback",
        "llm_model": "rule-based reviewer",
    }


def normalize_priority_actions(value, fallback_actions: list[str]) -> list[str]:
    if isinstance(value, list):
        cleaned_actions = [
            str(action).strip()
            for action in value
            if str(action).strip() and str(action).strip().lower() != "none"
        ]

        if cleaned_actions:
            return cleaned_actions

    if isinstance(value, str) and value.strip() and value.strip().lower() != "none":
        return [value.strip()]

    return fallback_actions


def valid_text_or_fallback(value, fallback_value: str) -> str:
    if isinstance(value, str) and value.strip() and value.strip().lower() != "none":
        return value.strip()

    return fallback_value


def run_llm_review_agent(state: PermitReviewState) -> PermitReviewState:
    missing_required = [
        {
            "id": item.id,
            "requirement": item.requirement,
            "status": item.status,
            "evidence_quality": item.evidence_quality,
            "evidence": item.evidence,
            "pages": item.page_references,
        }
        for item in state.checklist_results
        if item.required and item.status == "Missing"
    ]

    found_items = [
        {
            "id": item.id,
            "requirement": item.requirement,
            "status": item.status,
            "evidence_quality": item.evidence_quality,
            "evidence": item.evidence,
            "pages": item.page_references,
        }
        for item in state.checklist_results
        if item.status == "Found"
    ]

    regulation_matches = state.project_summary.get("regulation_matches", [])

    rag_regulation_context = state.project_summary.get(
        "rag_regulation_context",
        [],
    )

    risk_items = [
        {
            "title": risk.title,
            "severity": risk.severity,
            "explanation": risk.explanation,
            "recommendation": risk.recommendation,
        }
        for risk in state.risks
    ]

    system_prompt = """
You are a careful AI permit-screening assistant for Munich building permit documents.

You do not approve or reject permits.
You only provide a preliminary document completeness review.

Return ONLY valid JSON.
Do not return markdown.
Do not return null values.

Required JSON structure:
{
  "ai_screening_decision": "short decision string",
  "ai_reviewer_summary": "concise reviewer summary string",
  "priority_actions": ["action 1", "action 2", "action 3"],
  "llm_used": true
}

Rules:
- Never say the permit is approved.
- Never say the permit is rejected as a legal decision.
- Never give legal advice.
- Emphasize that final verification remains with the responsible authority or qualified reviewer.
- Use the retrieved regulation context to explain why missing documents may matter, but do not treat retrieved text as legal advice.
- Be practical and concise.
- Prioritize missing high-risk items such as fire safety, energy/GEG documentation, drainage, building drawings, site plan, signatures, and application form.
- If information is uncertain, still return a useful preliminary screening decision instead of null.
"""

    user_payload = {
        "filename": state.filename,
        "jurisdiction": state.jurisdiction,
        "detected_languages": state.detected_languages,
        "project_summary": {
            "project_name": state.project_summary.get("project_name"),
            "project_address": state.project_summary.get("project_address"),
            "applicant": state.project_summary.get("applicant"),
            "building_type": state.project_summary.get("building_type"),
        },
        "readiness_score": state.readiness_score,
        "missing_required_items": missing_required,
        "found_items": found_items,
        "regulation_matches": regulation_matches,
        "rag_regulation_context": rag_regulation_context,
        "risks": risk_items,
    }

    llm_result = call_llm_json(
        system_prompt=system_prompt,
        user_payload=user_payload,
    )

    fallback = create_fallback_llm_review(state)

    if not llm_result or "llm_error" in llm_result:
        state.project_summary["ai_screening_decision"] = fallback[
            "ai_screening_decision"
        ]
        state.project_summary["ai_reviewer_summary"] = fallback[
            "ai_reviewer_summary"
        ]
        state.project_summary["priority_actions"] = fallback["priority_actions"]

        state.project_summary["llm_used"] = False
        state.project_summary["llm_provider"] = "fallback"
        state.project_summary["llm_model"] = "rule-based reviewer"

        if llm_result and "llm_error" in llm_result:
            state.project_summary["llm_error"] = llm_result["llm_error"]

        return state

    llm_decision = llm_result.get("ai_screening_decision")
    llm_summary = llm_result.get("ai_reviewer_summary")
    llm_priority_actions = llm_result.get("priority_actions")

    state.project_summary["ai_screening_decision"] = valid_text_or_fallback(
        llm_decision,
        fallback["ai_screening_decision"],
    )

    state.project_summary["ai_reviewer_summary"] = valid_text_or_fallback(
        llm_summary,
        fallback["ai_reviewer_summary"],
    )

    state.project_summary["priority_actions"] = normalize_priority_actions(
        llm_priority_actions,
        fallback["priority_actions"],
    )

    state.project_summary["llm_used"] = True
    state.project_summary["llm_provider"] = llm_result.get(
        "llm_provider",
        "unknown",
    )
    state.project_summary["llm_model"] = llm_result.get(
        "llm_model",
        "unknown",
    )

    if (
        not isinstance(llm_decision, str)
        or not isinstance(llm_summary, str)
        or not llm_decision
        or not llm_summary
    ):
        state.project_summary["llm_warning"] = (
            "The LLM provider responded, but one or more review fields were empty. "
            "Fallback text was used for missing fields."
        )

    return state