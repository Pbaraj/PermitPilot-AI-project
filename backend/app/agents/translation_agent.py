from app.schemas.permit_schema import PermitReviewState
from app.services.argos_translation_service import translate_text_with_argos


def run_translation_agent(state: PermitReviewState) -> PermitReviewState:
    notes = []

    for page in state.pages:
        if page.language == "en":
            page.normalized_text = page.text
            continue

        translated_text, note = translate_text_with_argos(
            text=page.text,
            source_language=page.language,
            target_language="en",
        )

        page.normalized_text = translated_text
        notes.append(f"Page {page.page_number}: {note}")

    if not notes:
        notes.append("Document was already in English. Internal translation was not required.")

    state.translation_notes = notes
    return state