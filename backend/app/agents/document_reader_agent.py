import re

from app.schemas.permit_schema import PermitReviewState


def find_value(patterns: list[str], text: str) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)

        if match:
            return match.group(1).strip()

    return None


def run_document_reader_agent(state: PermitReviewState) -> PermitReviewState:
    full_text = "\n".join(
    page.normalized_text if page.normalized_text else page.text
    for page in state.pages
)

    project_name = find_value(
        [
            r"project name\s*:\s*(.+)",
            r"project title\s*:\s*(.+)",
            r"bauvorhaben\s*:\s*(.+)",
            r"projektname\s*:\s*(.+)",
        ],
        full_text,
    )

    project_address = find_value(
        [
            r"project address\s*:\s*(.+)",
            r"site address\s*:\s*(.+)",
            r"address\s*:\s*(.+)",
            r"adresse\s*:\s*(.+)",
            r"standort\s*:\s*(.+)",
        ],
        full_text,
    )

    applicant = find_value(
        [
            r"applicant\s*:\s*(.+)",
            r"client\s*:\s*(.+)",
            r"owner\s*:\s*(.+)",
            r"bauherr\s*:\s*(.+)",
            r"antragsteller\s*:\s*(.+)",
        ],
        full_text,
    )

    building_type = find_value(
        [
            r"building type\s*:\s*(.+)",
            r"building use\s*:\s*(.+)",
            r"nutzung\s*:\s*(.+)",
            r"gebäudetyp\s*:\s*(.+)",
        ],
        full_text,
    )

    state.project_summary = {
        "project_name": project_name or "Not clearly identified",
        "project_address": project_address or "Not clearly identified",
        "applicant": applicant or "Not clearly identified",
        "building_type": building_type or "Not clearly identified",
        "pages_reviewed": len(state.pages),
        "detected_languages": state.detected_languages,
    }

    return state