from app.schemas.permit_schema import PermitReviewState
from app.services.argos_translation_service import translate_text_with_argos


def run_output_translation_agent(state: PermitReviewState) -> PermitReviewState:
    if state.output_language.lower() == "english":
        return state

    translated_report, note = translate_text_with_argos(
        text=state.final_report_markdown,
        source_language="en",
        target_language=state.output_language,
    )

    state.final_report_markdown = translated_report
    state.reviewer_notes.append(f"Output report translation: {note}")

    return state