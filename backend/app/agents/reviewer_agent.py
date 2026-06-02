from app.schemas.permit_schema import PermitReviewState


def run_reviewer_agent(state: PermitReviewState) -> PermitReviewState:
    notes = []

    if not state.pages:
        notes.append("No readable text was extracted from the document.")

    missing_count = len(
        [
            item for item in state.checklist_results
            if item.required and item.status == "Missing"
        ]
    )

    if missing_count == 0:
        notes.append(
            "All required MVP checklist items were found. "
            "Jurisdiction-specific human verification is still recommended."
        )
    elif missing_count <= 3:
        notes.append(
            "Some required items are missing. Human review is recommended."
        )
    else:
        notes.append(
            "Many required items are missing. Human review is strongly recommended."
        )

    state.reviewer_notes = notes
    return state