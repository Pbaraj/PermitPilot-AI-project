from app.schemas.permit_schema import PermitReviewState
from app.services.language_service import detect_language, unique_languages

from app.agents.translation_agent import run_translation_agent
from app.agents.document_reader_agent import run_document_reader_agent
from app.agents.checklist_agent import run_checklist_agent
from app.agents.regulation_match_agent import run_regulation_match_agent
from app.agents.rag_regulation_agent import run_rag_regulation_agent
from app.agents.risk_agent import run_risk_agent
from app.agents.llm_review_agent import run_llm_review_agent
from app.agents.report_writer_agent import run_report_writer_agent
from app.agents.reviewer_agent import run_reviewer_agent
from app.agents.output_translation_agent import run_output_translation_agent


def run_permit_review_workflow(
    state: PermitReviewState
) -> PermitReviewState:
    # 1. Detect original document language
    for page in state.pages:
        page.language = detect_language(page.text)

    state.detected_languages = unique_languages(
        [page.language for page in state.pages]
    )

    # 2. Translate uploaded document internally if needed
    state = run_translation_agent(state)

    # 3. Extract project summary from the document
    state = run_document_reader_agent(state)

    # 4. Check permit completeness using selected jurisdiction checklist
    state = run_checklist_agent(state)

    # 5. Match checklist results with Munich/Bavaria regulation references
    state = run_regulation_match_agent(state)

    # 6. Retrieve relevant Munich/Bavaria regulation context using local RAG
    state = run_rag_regulation_agent(state)

    # 7. Identify missing-document and submission risks
    state = run_risk_agent(state)

    # 8. Add AI/LLM reviewer summary and screening decision
    state = run_llm_review_agent(state)

    # 9. Generate final markdown report
    state = run_report_writer_agent(state)

    # 10. Add reviewer notes
    state = run_reviewer_agent(state)

    # 11. Translate final report into selected output language if needed
    state = run_output_translation_agent(state)

    return state