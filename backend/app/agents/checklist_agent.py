import json
import re
from pathlib import Path

from app.schemas.permit_schema import PermitReviewState, ChecklistResult


CHECKLIST_DIR = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "checklists"
)


CHECKLIST_FILE_BY_JURISDICTION = {
    "general": "general_permit_checklist.json",
    "germany": "munich_lbk_checklist.json",
    "munich": "munich_lbk_checklist.json",
    "bavaria": "munich_lbk_checklist.json",
}


NEGATIVE_PHRASES = [
    # English
    "missing",
    "is missing",
    "are missing",
    "not attached",
    "not enclosed",
    "not included",
    "not provided",
    "not available",
    "not submitted",
    "not present",
    "not added",
    "not appended",
    "not yet attached",
    "not yet provided",
    "not yet submitted",
    "no evidence",
    "no document",
    "without",

    # German
    "fehlt",
    "fehlen",
    "nicht beigefügt",
    "nicht beigelegt",
    "nicht enthalten",
    "nicht vorhanden",
    "nicht eingereicht",
    "nicht vorgelegt",
    "nicht angehängt",
    "nicht angefügt",
    "sind nicht beigefügt",
    "ist nicht beigefügt",
    "liegt nicht vor",
    "liegen nicht vor",
]


def load_checklist(jurisdiction: str) -> list[dict]:
    jurisdiction_key = (jurisdiction or "general").lower()

    checklist_file = CHECKLIST_FILE_BY_JURISDICTION.get(
        jurisdiction_key,
        "general_permit_checklist.json",
    )

    checklist_path = CHECKLIST_DIR / checklist_file

    if not checklist_path.exists():
        fallback_path = CHECKLIST_DIR / "general_permit_checklist.json"
        return json.loads(fallback_path.read_text(encoding="utf-8"))

    return json.loads(checklist_path.read_text(encoding="utf-8"))


def clean_sentence(text: str) -> str:
    return " ".join(text.replace("\n", " ").split())


def split_into_sentences(text: str) -> list[str]:
    text = text.replace("\r", "\n")
    parts = re.split(r"(?<=[.!?])\s+|\n\s*\n+", text)

    sentences = []

    for part in parts:
        cleaned = clean_sentence(part)

        if cleaned:
            sentences.append(cleaned)

    return sentences


def is_negative_sentence(sentence: str) -> bool:
    sentence_lower = sentence.lower()

    return any(
        phrase in sentence_lower
        for phrase in NEGATIVE_PHRASES
    )


def find_keyword_evidence(
    keyword: str,
    pages: list[tuple[int, str]],
    max_hits: int = 3,
) -> tuple[list[str], list[int], list[str], list[int]]:
    positive_evidence = []
    positive_pages = []

    negative_evidence = []
    negative_pages = []

    keyword_lower = keyword.lower()

    for page_number, page_text in pages:
        sentences = split_into_sentences(page_text)

        for sentence in sentences:
            sentence_lower = sentence.lower()

            if keyword_lower in sentence_lower:
                if is_negative_sentence(sentence):
                    negative_evidence.append(sentence)
                    negative_pages.append(page_number)
                else:
                    positive_evidence.append(sentence)
                    positive_pages.append(page_number)

            if len(positive_evidence) + len(negative_evidence) >= max_hits:
                break

        if len(positive_evidence) + len(negative_evidence) >= max_hits:
            break

    return (
        positive_evidence,
        sorted(set(positive_pages)),
        negative_evidence,
        sorted(set(negative_pages)),
    )


def remove_duplicates(items: list[str]) -> list[str]:
    unique_items = []

    for item in items:
        if item not in unique_items:
            unique_items.append(item)

    return unique_items


def run_checklist_agent(state: PermitReviewState) -> PermitReviewState:
    checklist = load_checklist(state.jurisdiction)

    pages = []

    for page in state.pages:
        combined_text = ""

        if page.normalized_text:
            combined_text += page.normalized_text

        combined_text += "\n\n--- Original text ---\n\n"
        combined_text += page.text

        pages.append((page.page_number, combined_text))

    results: list[ChecklistResult] = []

    for item in checklist:
        all_positive_evidence = []
        all_positive_pages = []

        all_negative_evidence = []
        all_negative_pages = []

        keywords = item.get("keywords", [])
        required = item.get("required", True)

        for keyword in keywords:
            (
                positive_evidence,
                positive_pages,
                negative_evidence,
                negative_pages,
            ) = find_keyword_evidence(keyword, pages)

            all_positive_evidence.extend(positive_evidence)
            all_positive_pages.extend(positive_pages)

            all_negative_evidence.extend(negative_evidence)
            all_negative_pages.extend(negative_pages)

        unique_positive_evidence = remove_duplicates(all_positive_evidence)
        unique_negative_evidence = remove_duplicates(all_negative_evidence)

        positive_page_references = sorted(set(all_positive_pages))
        negative_page_references = sorted(set(all_negative_pages))

        if unique_negative_evidence:
            status = "Missing"
            evidence_quality = "Mentioned as missing"
            evidence = unique_negative_evidence[:3]
            page_references = negative_page_references[:5]

        elif unique_positive_evidence:
            status = "Found"
            evidence_quality = "Found with evidence"
            evidence = unique_positive_evidence[:3]
            page_references = positive_page_references[:5]

        else:
            status = "Missing" if required else "Unclear"

            if required:
                evidence_quality = "Not found"
            else:
                evidence_quality = "Unclear / conditional"

            evidence = []
            page_references = []

        results.append(
            ChecklistResult(
                id=item.get("id", "unknown"),
                requirement=item.get("requirement", "Unknown requirement"),
                required=required,
                status=status,
                evidence_quality=evidence_quality,
                evidence=evidence,
                page_references=page_references,
            )
        )

    state.checklist_results = results
    return state