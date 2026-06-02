from pydantic import BaseModel


class ReportDownloadRequest(BaseModel):
    filename: str = "permit-review-report.pdf"
    markdown: str