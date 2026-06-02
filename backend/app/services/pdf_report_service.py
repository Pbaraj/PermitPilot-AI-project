from io import BytesIO
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


def clean_text(text: str) -> str:
    replacements = {
        "→": "->",
        "—": "-",
        "–": "-",
        "✅": "",
        "❌": "",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def markdown_inline_to_html(text: str) -> str:
    text = clean_text(text)
    text = escape(text)

    # Convert simple markdown bold: **text**
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)

    return text


def is_markdown_table_line(line: str) -> bool:
    return line.strip().startswith("|") and line.strip().endswith("|")


def is_table_separator(line: str) -> bool:
    cleaned = line.strip().replace("|", "").replace("-", "").replace(":", "").strip()
    return cleaned == ""


def split_table_row(line: str) -> list[str]:
    line = line.strip()

    if line.startswith("|"):
        line = line[1:]

    if line.endswith("|"):
        line = line[:-1]

    return [cell.strip() for cell in line.split("|")]


def get_column_widths(column_count: int):
    usable_width = A4[0] - 4 * cm

    if column_count == 6:
        return [
            3.3 * cm,  # Requirement
            1.7 * cm,  # Status
            1.4 * cm,  # Required
            2.4 * cm,  # Evidence Quality
            1.4 * cm,  # Pages
            usable_width - (3.3 + 1.7 + 1.4 + 2.4 + 1.4) * cm,  # Evidence
        ]

    if column_count == 5:
        return [
            3.5 * cm,
            1.7 * cm,
            3.0 * cm,
            6.0 * cm,
            usable_width - (3.5 + 1.7 + 3.0 + 6.0) * cm,
        ]

    if column_count == 4:
        return [
            4.2 * cm,
            1.8 * cm,
            3.2 * cm,
            usable_width - (4.2 + 1.8 + 3.2) * cm,
        ]

    return [usable_width / column_count] * column_count


def build_report_table(table_lines: list[str], styles):
    rows = []

    for line in table_lines:
        if is_table_separator(line):
            continue

        cells = split_table_row(line)

        if not cells:
            continue

        paragraph_cells = [
            Paragraph(
                markdown_inline_to_html(cell),
                styles["TableHeader"] if not rows else styles["TableCell"],
            )
            for cell in cells
        ]

        rows.append(paragraph_cells)

    if not rows:
        return Spacer(1, 0.2 * cm)

    column_count = len(rows[0])
    col_widths = get_column_widths(column_count)

    table = Table(
        rows,
        colWidths=col_widths,
        repeatRows=1,
        hAlign="LEFT",
    )

    table_style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EEF8")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ]
    )

    table.setStyle(table_style)

    return table


def add_page_header_footer(canvas, doc):
    canvas.saveState()

    width, height = A4

    canvas.setFont("Helvetica-Bold", 9)
    canvas.setFillColor(colors.HexColor("#0F172A"))
    canvas.drawString(2 * cm, height - 1.2 * cm, "PermitPilot AI - Permit Document Review Report")

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.drawRightString(width - 2 * cm, 1.2 * cm, f"Page {doc.page}")

    canvas.restoreState()


def build_pdf_report(markdown_text: str) -> bytes:
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=1.8 * cm,
    )

    base_styles = getSampleStyleSheet()

    styles = {
        "Title": ParagraphStyle(
            "CustomTitle",
            parent=base_styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#0F172A"),
            spaceAfter=18,
        ),
        "Heading1": ParagraphStyle(
            "CustomHeading1",
            parent=base_styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=18,
            textColor=colors.HexColor("#0F172A"),
            spaceBefore=14,
            spaceAfter=8,
        ),
        "Heading2": ParagraphStyle(
            "CustomHeading2",
            parent=base_styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#1E3A8A"),
            spaceBefore=12,
            spaceAfter=7,
        ),
        "Body": ParagraphStyle(
            "CustomBody",
            parent=base_styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#334155"),
            spaceAfter=6,
        ),
        "Bullet": ParagraphStyle(
            "CustomBullet",
            parent=base_styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            leftIndent=12,
            firstLineIndent=-8,
            textColor=colors.HexColor("#334155"),
            spaceAfter=5,
        ),
        "SmallNote": ParagraphStyle(
            "CustomSmallNote",
            parent=base_styles["BodyText"],
            fontName="Helvetica-Oblique",
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#475569"),
            spaceBefore=6,
            spaceAfter=8,
        ),
        "TableHeader": ParagraphStyle(
            "CustomTableHeader",
            parent=base_styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.2,
            leading=9,
            textColor=colors.HexColor("#0F172A"),
        ),
        "TableCell": ParagraphStyle(
            "CustomTableCell",
            parent=base_styles["BodyText"],
            fontName="Helvetica",
            fontSize=6.8,
            leading=8.6,
            textColor=colors.HexColor("#334155"),
        ),
    }

    story = []

    lines = markdown_text.splitlines()
    index = 0

    while index < len(lines):
        raw_line = lines[index]
        line = raw_line.strip()

        if not line:
            story.append(Spacer(1, 0.18 * cm))
            index += 1
            continue

        if is_markdown_table_line(line):
            table_lines = []

            while index < len(lines) and is_markdown_table_line(lines[index].strip()):
                table_lines.append(lines[index].strip())
                index += 1

            story.append(build_report_table(table_lines, styles))
            story.append(Spacer(1, 0.35 * cm))
            continue

        if line.startswith("# "):
            title = line.replace("# ", "", 1).strip()
            story.append(Paragraph(markdown_inline_to_html(title), styles["Title"]))

        elif line.startswith("## "):
            heading = line.replace("## ", "", 1).strip()
            story.append(Paragraph(markdown_inline_to_html(heading), styles["Heading1"]))

        elif line.startswith("### "):
            heading = line.replace("### ", "", 1).strip()
            story.append(Paragraph(markdown_inline_to_html(heading), styles["Heading2"]))

        elif line.startswith("- "):
            bullet_text = line.replace("- ", "", 1).strip()
            story.append(
                Paragraph(
                    f"• {markdown_inline_to_html(bullet_text)}",
                    styles["Bullet"],
                )
            )

        elif re.match(r"^\d+\.\s+", line):
            story.append(Paragraph(markdown_inline_to_html(line), styles["Bullet"]))

        elif "preliminary AI screening" in line.lower() or "not legal advice" in line.lower():
            story.append(Paragraph(markdown_inline_to_html(line), styles["SmallNote"]))

        else:
            story.append(Paragraph(markdown_inline_to_html(line), styles["Body"]))

        index += 1

    document.build(
        story,
        onFirstPage=add_page_header_footer,
        onLaterPages=add_page_header_footer,
    )

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes