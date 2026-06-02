from app.schemas.permit_schema import PermitReviewState


def safe_table_cell(value) -> str:
    """
    Keeps markdown tables stable by removing line breaks and pipe characters.
    """
    if value is None:
        return "-"

    text = str(value).strip()

    if not text:
        return "-"

    text = text.replace("|", "/")
    text = text.replace("\n", " ")
    text = " ".join(text.split())

    return text


def safe_text(value) -> str:
    """
    Cleans text for normal report paragraphs.
    """
    if value is None:
        return "-"

    text = str(value).strip()

    if not text:
        return "-"

    text = text.replace("\n", " ")
    text = " ".join(text.split())

    return text


def format_reviewer_mode(
    llm_used: bool,
    llm_provider: str,
) -> str:
    provider = (llm_provider or "").lower()

    if not llm_used:
        return "Fallback rule-based AI reviewer"

    if provider == "openrouter":
        return "OpenRouter LLM reviewer"

    if provider == "ollama":
        return "Local Ollama LLM reviewer"

    if provider == "openai":
        return "OpenAI LLM reviewer"

    if provider == "huggingface":
        return "Hugging Face LLM reviewer"

    return "LLM reviewer"


def create_checklist_table(state: PermitReviewState) -> str:
    lines = [
        "| Requirement | Status | Required | Evidence Quality | Evidence pages | Evidence |",
        "|---|---|---|---|---|---|",
    ]

    for item in state.checklist_results:
        required = "Yes" if item.required else "No"

        pages = ", ".join(str(p) for p in item.page_references)
        if not pages:
            pages = "-"

        evidence_quality = getattr(item, "evidence_quality", "Not found")
        evidence = " / ".join(item.evidence) if item.evidence else "-"

        lines.append(
            "| "
            f"{safe_table_cell(item.requirement)} | "
            f"{safe_table_cell(item.status)} | "
            f"{safe_table_cell(required)} | "
            f"{safe_table_cell(evidence_quality)} | "
            f"{safe_table_cell(pages)} | "
            f"{safe_table_cell(evidence)} |"
        )

    return "\n".join(lines)


def create_rag_context_section(state: PermitReviewState) -> str:
    """
    Creates a readable RAG section.

    A numbered card-style format is used instead of a wide markdown table,
    because it exports much better to PDF.
    """
    rag_context = state.project_summary.get("rag_regulation_context", [])

    if not rag_context:
        return (
            "No retrieved regulation context available. "
            "This section is available when Munich/Bavaria RAG retrieval is enabled."
        )

    lines = []

    for index, chunk in enumerate(rag_context, start=1):
        title = safe_text(chunk.get("title", "Unknown title"))
        source = safe_text(chunk.get("source", "Unknown source"))
        score = safe_text(chunk.get("score", "-"))
        matched_query = safe_text(chunk.get("matched_query", "-"))
        context_text = safe_text(chunk.get("text", ""))

        lines.append(f"### {index}. {title}")
        lines.append("")
        lines.append(f"- **Source:** {source}")
        lines.append(f"- **Relevance score:** {score}")
        lines.append(f"- **Matched query:** {matched_query}")
        lines.append(f"- **Retrieved context:** {context_text}")
        lines.append("")

    lines.append(
        "These retrieved snippets are used as supporting context for AI-assisted "
        "screening. They do not replace the official legal text or human review."
    )

    return "\n".join(lines).strip()


def create_risk_section(state: PermitReviewState) -> str:
    if not state.risks:
        return "No major risks were detected based on the selected checklist."

    lines = []

    for risk in state.risks:
        lines.append(
            f"- **{risk.severity} — {risk.title}**: "
            f"{risk.explanation} "
            f"Recommendation: {risk.recommendation}"
        )

    return "\n".join(lines)


def create_regulation_matching_section(state: PermitReviewState) -> str:
    regulation_matches = state.project_summary.get("regulation_matches", [])

    if not regulation_matches:
        return (
            "No Munich/Bavaria regulation references were matched. "
            "This section is only available for Munich, Bavaria, or Germany jurisdiction mode."
        )

    lines = [
        "| Requirement | Status | Reference | Regulation note |",
        "|---|---|---|---|",
    ]

    for match in regulation_matches:
        requirement = match.get("requirement", "Unknown requirement")
        status = match.get("status", "Unknown")
        reference = match.get("reference", "Reference not specified")
        rule_summary = match.get("rule_summary", "")

        lines.append(
            "| "
            f"{safe_table_cell(requirement)} | "
            f"{safe_table_cell(status)} | "
            f"{safe_table_cell(reference)} | "
            f"{safe_table_cell(rule_summary)} |"
        )

    return "\n".join(lines)


def create_regulation_risk_notes(state: PermitReviewState) -> str:
    regulation_matches = state.project_summary.get("regulation_matches", [])

    if not regulation_matches:
        return "No regulation-specific risk notes available."

    lines = []

    for match in regulation_matches:
        status = match.get("status", "")
        severity = match.get("severity", "Medium")
        requirement = match.get("requirement", "Unknown requirement")
        comment = match.get("comment", "")

        if status == "Missing":
            lines.append(f"- **{severity} — {requirement}**: {comment}")

    if not lines:
        return (
            "No missing Munich/Bavaria regulation-matched items were detected. "
            "Human verification is still recommended."
        )

    return "\n".join(lines)


def create_ai_screening_section(state: PermitReviewState) -> str:
    decision = state.project_summary.get(
        "ai_screening_decision",
        "AI screening decision not available.",
    )

    summary = state.project_summary.get(
        "ai_reviewer_summary",
        "AI reviewer summary not available.",
    )

    priority_actions = state.project_summary.get("priority_actions", [])

    llm_used = state.project_summary.get("llm_used", False)
    llm_provider = state.project_summary.get("llm_provider", "fallback")
    llm_model = state.project_summary.get("llm_model", "rule-based reviewer")
    llm_error = state.project_summary.get("llm_error")

    reviewer_mode = format_reviewer_mode(
        llm_used=llm_used,
        llm_provider=llm_provider,
    )

    rag_context = state.project_summary.get("rag_regulation_context", [])

    rag_note = (
        "Munich/Bavaria RAG context was retrieved and provided to the reviewer."
        if rag_context
        else "No RAG regulation context was available for this review."
    )

    lines = [
        f"- **AI screening decision:** {decision}",
        f"- **AI reviewer mode:** {reviewer_mode}",
        f"- **LLM provider:** {llm_provider}",
        f"- **LLM model:** {llm_model}",
        f"- **RAG context:** {rag_note}",
    ]

    if llm_error:
        lines.append(f"- **LLM error / fallback reason:** {safe_text(llm_error)}")

    lines.extend(
        [
            "",
            f"**AI reviewer summary:** {summary}",
            "",
            "**Priority actions:**",
        ]
    )

    if priority_actions:
        for index, action in enumerate(priority_actions, start=1):
            lines.append(f"{index}. {action}")
    else:
        lines.append("1. No priority actions were generated.")

    lines.append("")
    lines.append(
        "This is a preliminary AI screening result. Final verification and "
        "permit decisions must remain with the responsible human authority or qualified reviewer."
    )

    return "\n".join(lines)


def run_report_writer_agent(state: PermitReviewState) -> PermitReviewState:
    languages = ", ".join(state.detected_languages)

    translation_notes = "; ".join(state.translation_notes)

    if not translation_notes:
        translation_notes = "Translation not required or no translation notes available."

    project_name = state.project_summary.get(
        "project_name", "Not clearly identified"
    )
    project_address = state.project_summary.get(
        "project_address", "Not clearly identified"
    )
    applicant = state.project_summary.get(
        "applicant", "Not clearly identified"
    )
    building_type = state.project_summary.get(
        "building_type", "Not clearly identified"
    )

    report = f"""
# Permit Document Review Report

## 1. Document Overview

- **File name:** {state.filename}
- **Detected language(s):** {languages}
- **Translation notes:** {translation_notes}
- **Selected jurisdiction:** {state.jurisdiction}
- **Requested report language:** {state.output_language}
- **Pages reviewed:** {len(state.pages)}

## 2. Project Summary

- **Project name:** {project_name}
- **Project address:** {project_address}
- **Applicant / Client:** {applicant}
- **Building type / Use:** {building_type}

## 3. AI Screening Decision

{create_ai_screening_section(state)}

## 4. Permit Readiness Score

**{state.readiness_score}%**

This score is based on the selected checklist. It is a preliminary completeness indicator, not legal approval.

## 5. Checklist Completeness

{create_checklist_table(state)}

## 6. Munich/Bavaria Regulation Matching

{create_regulation_matching_section(state)}

## 7. Retrieved Munich Regulation Context

{create_rag_context_section(state)}

## 8. Regulation-Based Risk Notes

{create_regulation_risk_notes(state)}

## 9. General Risk Analysis

{create_risk_section(state)}

## 10. Recommended Next Steps

1. Add all missing required documents.
2. Clearly label Munich/Bavaria-relevant documents such as Antragsformular, Amtlicher Lageplan, Bauzeichnungen, Baubeschreibung, Brandschutznachweis, Standsicherheitsnachweis, GEG/Energie documentation, Entwässerungsplan, and Unterschriften.
3. Check whether conditional documents such as Baumbestandserklärung, Stellplatznachweis, Vollmacht, or additional LBK documents are required for the specific project.
4. Ask a qualified architect, engineer, or Munich Lokalbaukommission reviewer to verify project-specific requirements.
5. Treat this AI output as a screening aid only, not as an approval or legal decision.

## 11. Disclaimer

This report is generated by an AI-assisted document review system. It is not legal advice and does not replace review by a qualified engineer, architect, lawyer, or permitting authority.
""".strip()

    state.final_report_markdown = report
    return state