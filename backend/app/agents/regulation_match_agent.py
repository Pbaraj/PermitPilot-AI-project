import json
from pathlib import Path

from app.schemas.permit_schema import PermitReviewState


REGULATION_DIR = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "regulations"
)


RULE_FILE_BY_JURISDICTION = {
    "munich": "munich_lbk_rules.json",
    "germany": "munich_lbk_rules.json",
    "bavaria": "munich_lbk_rules.json",
}


def load_regulation_rules(jurisdiction: str) -> list[dict]:
    jurisdiction_key = (jurisdiction or "general").lower()

    rule_file = RULE_FILE_BY_JURISDICTION.get(jurisdiction_key)

    if not rule_file:
        return []

    rule_path = REGULATION_DIR / rule_file

    if not rule_path.exists():
        return []

    return json.loads(rule_path.read_text(encoding="utf-8"))


def create_status_comment(checklist_status: str, rule: dict) -> str:
    requirement_title = rule.get("title", "This requirement")

    if checklist_status == "Found":
        return (
            f"{requirement_title} was detected in the uploaded document. "
            "The item should still be checked by a qualified reviewer for completeness and formal correctness."
        )

    if checklist_status == "Missing":
        return (
            f"{requirement_title} was not clearly found or was mentioned as missing. "
            "This may create a permit-submission risk and should be added or clearly labelled."
        )

    return (
        f"{requirement_title} could not be clearly verified. "
        "Human review is recommended."
    )


def run_regulation_match_agent(state: PermitReviewState) -> PermitReviewState:
    rules = load_regulation_rules(state.jurisdiction)

    if not rules:
        state.project_summary["regulation_matches"] = []
        return state

    rules_by_requirement_id = {
        rule["requirement_id"]: rule
        for rule in rules
        if "requirement_id" in rule
    }

    regulation_matches = []

    for checklist_item in state.checklist_results:
        rule = rules_by_requirement_id.get(checklist_item.id)

        if not rule:
            continue

        regulation_matches.append(
            {
                "requirement_id": checklist_item.id,
                "requirement": checklist_item.requirement,
                "status": checklist_item.status,
                "required": checklist_item.required,
                "evidence_pages": checklist_item.page_references,
                "jurisdiction": rule.get("jurisdiction", "Munich / Bavaria"),
                "reference": rule.get("reference", "Reference not specified"),
                "rule_summary": rule.get("rule_summary", ""),
                "severity": rule.get("severity", "Medium"),
                "comment": create_status_comment(
                    checklist_status=checklist_item.status,
                    rule=rule,
                ),
            }
        )

    state.project_summary["regulation_matches"] = regulation_matches

    return state