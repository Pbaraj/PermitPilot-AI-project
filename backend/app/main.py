from pathlib import Path
from tempfile import NamedTemporaryFile
from io import BytesIO

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.schemas.permit_schema import PermitReviewState
from app.schemas.report_schema import ReportDownloadRequest
from app.services.pdf_service import extract_text_from_pdf
from app.services.pdf_report_service import build_pdf_report
from app.workflows.permit_workflow import run_permit_review_workflow


app = FastAPI(
    title="PermitPilot AI",
    description="Multilingual multi-agent assistant for engineering and permit documents.",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "PermitPilot AI backend is running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
    }


@app.post("/api/review-permit")
async def review_permit(
    file: UploadFile = File(...),
    output_language: str = Form("English"),
    jurisdiction: str = Form("general"),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file was uploaded.",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file.",
        )

    temporary_path = None

    try:
        suffix = Path(file.filename).suffix

        with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(await file.read())
            temporary_path = temp_file.name

        pages = extract_text_from_pdf(temporary_path)

        if not pages or not any(page.text.strip() for page in pages):
            raise HTTPException(
                status_code=422,
                detail=(
                    "No readable text was extracted. "
                    "This may be a scanned PDF. OCR can be added later."
                ),
            )

        state = PermitReviewState(
            filename=file.filename,
            output_language=output_language,
            jurisdiction=jurisdiction,
            pages=pages,
        )

        reviewed_state = run_permit_review_workflow(state)

        return reviewed_state.model_dump()

    finally:
        if temporary_path:
            Path(temporary_path).unlink(missing_ok=True)


@app.post("/api/download-report-pdf")
def download_report_pdf(request: ReportDownloadRequest):
    pdf_bytes = build_pdf_report(request.markdown)

    safe_filename = request.filename or "permit-review-report.pdf"

    if not safe_filename.lower().endswith(".pdf"):
        safe_filename += ".pdf"

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_filename}"'
        },
    )