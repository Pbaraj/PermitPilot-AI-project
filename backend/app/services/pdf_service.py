from pathlib import Path
import fitz

from app.schemas.permit_schema import ExtractedPage
from app.services.text_normalizer import normalize_text


def extract_text_from_pdf(file_path: str | Path) -> list[ExtractedPage]:
    pages: list[ExtractedPage] = []

    document = fitz.open(file_path)

    for index, page in enumerate(document, start=1):
        text = page.get_text("text") or ""
        text = normalize_text(text)

        pages.append(
            ExtractedPage(
                page_number=index,
                text=text.strip()
            )
        )

    document.close()
    return pages