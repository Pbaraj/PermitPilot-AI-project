from typing import Any

from pydantic import BaseModel, Field


class ExtractedPage(BaseModel):
    page_number: int
    text: str
    language: str = "unknown"
    normalized_text: str = ""


class ChecklistResult(BaseModel):
    id: str
    requirement: str
    status: str
    required: bool = True
    evidence_quality: str = "Not found"
    evidence: list[str] = Field(default_factory=list)
    page_references: list[int] = Field(default_factory=list)


class RiskItem(BaseModel):
    title: str
    severity: str
    explanation: str
    recommendation: str


class PermitReviewState(BaseModel):
    filename: str
    output_language: str = "English"
    jurisdiction: str = "general"

    pages: list[ExtractedPage] = Field(default_factory=list)
    detected_languages: list[str] = Field(default_factory=list)
    translation_notes: list[str] = Field(default_factory=list)

    project_summary: dict[str, Any] = Field(default_factory=dict)
    checklist_results: list[ChecklistResult] = Field(default_factory=list)
    risks: list[RiskItem] = Field(default_factory=list)

    readiness_score: int = 0
    final_report_markdown: str = ""
    reviewer_notes: list[str] = Field(default_factory=list)