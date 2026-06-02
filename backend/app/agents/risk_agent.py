from app.schemas.permit_schema import PermitReviewState, RiskItem


def run_risk_agent(state: PermitReviewState) -> PermitReviewState:
    risks: list[RiskItem] = []

    high_priority_items = {
        "fire_safety",
        "structural_report",
        "energy_certificate",
        "drainage_plan",
        "signatures"
    }

    missing_required_items = [
        item for item in state.checklist_results
        if item.required and item.status == "Missing"
    ]

    for item in missing_required_items:
        severity = "High" if item.id in high_priority_items else "Medium"

        risks.append(
            RiskItem(
                title=f"Missing: {item.requirement}",
                severity=severity,
                explanation=(
                    f"The uploaded document does not clearly contain "
                    f"'{item.requirement}'."
                ),
                recommendation=(
                    f"Add or clearly label the section for "
                    f"'{item.requirement}' before submission."
                )
            )
        )

    found_required_items = [
        item for item in state.checklist_results
        if item.required and item.status == "Found"
    ]

    total_required = len(found_required_items) + len(missing_required_items)

    if total_required == 0:
        state.readiness_score = 0
    else:
        state.readiness_score = round(
            len(found_required_items) / total_required * 100
        )

    state.risks = risks
    return state