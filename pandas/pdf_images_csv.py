
import os
import json
import logging
from pathlib import Path
from io import BytesIO

import fitz
import pdfplumber
import pandas as pd
import pytesseract

from PIL import Image, ImageOps
from openpyxl import load_workbook


# ==========================================================
# 1. CONFIGURATION
# ==========================================================

INPUT_DIR = Path("input_documents")
OUTPUT_DIR = Path("output")
IMAGE_DIR = OUTPUT_DIR / "extracted_images"

INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
IMAGE_DIR.mkdir(exist_ok=True)

SUPPORTED_EXTENSIONS = {
    ".pdf", ".csv", ".xlsx", ".xls",
    ".txt", ".png", ".jpg", ".jpeg", ".tiff"
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger(__name__)


# ==========================================================
# 2. COMMON DATA STRUCTURE
# ==========================================================

def create_record(
    text,
    source,
    content_type,
    page_number=None,
    bbox=None,
    sequence=None,
    sheet_name=None,
    extra_metadata=None
):
    """
    Creates a standardized content record for every file type.

    Preserves source, page, coordinates, content type,
    reading sequence and other extraction metadata.
    """

    metadata = {
        "source": str(source),
        "content_type": content_type,
        "page_number": page_number,
        "bbox": list(bbox) if bbox else None,
        "sequence": sequence,
        "sheet_name": sheet_name
    }

    if extra_metadata:
        metadata.update(extra_metadata)

    return {
        "text": str(text).strip(),
        "metadata": metadata
    }


# ==========================================================
# 3. IMAGE OCR
# ==========================================================

def extract_image_text(image):
    """
    Extracts readable text from an image using Tesseract OCR.

    Performs basic grayscale and contrast preprocessing.
    Returns extracted text.
    """

    try:
        if not isinstance(image, Image.Image):
            image = Image.open(image)

        image = ImageOps.exif_transpose(image)
        image = image.convert("RGB")
        image = ImageOps.grayscale(image)
        image = ImageOps.autocontrast(image)

        return pytesseract.image_to_string(
            image,
            config="--psm 3"
        ).strip()

    except Exception:
        logger.exception("Image OCR failed")
        return ""


# ==========================================================
# 4. GEOMETRY HELPERS
# ==========================================================

def calculate_overlap(box_a, box_b):
    """
    Calculates intersection area between two bounding boxes.

    Used to identify text blocks that overlap extracted
    table regions, preventing duplicate table content.
    """

    x0 = max(box_a[0], box_b[0])
    y0 = max(box_a[1], box_b[1])
    x1 = min(box_a[2], box_b[2])
    y1 = min(box_a[3], box_b[3])

    if x1 <= x0 or y1 <= y0:
        return 0.0

    return (x1 - x0) * (y1 - y0)


def get_reading_order(elements):
    """
    Sorts page elements approximately in reading order.

    Uses vertical position first and horizontal position
    second. This is suitable for simple single-column PDFs.

    Complex multi-column layouts require layout detection.
    """

    return sorted(
        elements,
        key=lambda item: (
            round(item["bbox"][1], 1),
            item["bbox"][0]
        )
    )


# ==========================================================
# 5. PDF TEXT EXTRACTION
# ==========================================================

def extract_pdf_text_blocks(page):
    """
    Extracts individual text blocks from a PDF page.

    Preserves each block's bounding box so that its position
    can be reconstructed later.
    """

    elements = []

    page_data = page.get_text("dict")

    for block in page_data["blocks"]:

        if block["type"] != 0:
            continue

        lines = []

        for line in block.get("lines", []):

            line_text = "".join(
                span["text"]
                for span in line.get("spans", [])
            )

            if line_text.strip():
                lines.append(line_text)

        text = "\n".join(lines).strip()

        if not text:
            continue

        elements.append({
            "type": "text",
            "text": text,
            "bbox": tuple(block["bbox"])
        })

    return elements


# ==========================================================
# 6. PDF TABLE EXTRACTION
# ==========================================================

def extract_pdf_tables(plumber_page):
    """
    Extracts tables from a PDF page using pdfplumber.

    Preserves table bounding boxes and converts tables
    into Markdown for downstream RAG processing.
    """

    elements = []

    for table_index, table in enumerate(
        plumber_page.find_tables()
    ):

        rows = table.extract()

        if not rows:
            continue

        df = pd.DataFrame(rows)

        df = df.dropna(how="all")
        df = df.dropna(axis=1, how="all")

        if df.empty:
            continue

        # First row is treated as column headers.
        headers = [
            str(value).strip()
            if value is not None
            else f"column_{i}"
            for i, value in enumerate(df.iloc[0])
        ]

        # Handle duplicate column names.
        seen = {}
        unique_headers = []

        for header in headers:
            count = seen.get(header, 0)
            seen[header] = count + 1

            unique_headers.append(
                header if count == 0
                else f"{header}_{count + 1}"
            )

        df.columns = unique_headers
        df = df.iloc[1:].reset_index(drop=True)

        # Preserve table structure as Markdown.
        table_text = df.to_markdown(index=False)

        elements.append({
            "type": "table",
            "text": table_text,
            "bbox": tuple(table.bbox),
            "table_number": table_index + 1
        })

    return elements


# ==========================================================
# 7. PDF IMAGE EXTRACTION
# ==========================================================

def extract_pdf_images(page, page_number, source):
    """
    Extracts images using PyMuPDF's positioned image blocks.

    Preserves image coordinates, saves image files,
    and extracts text inside images using OCR.

    Important: Image OCR extracts text, not a visual
    description of charts, diagrams or photographs.
    """

    elements = []

    image_blocks = [
        block
        for block in page.get_text("dict")["blocks"]
        if block["type"] == 1
    ]

    for image_index, block in enumerate(image_blocks):

        try:
            image_bytes = block.get("image")

            if not image_bytes:
                continue

            image = Image.open(
                BytesIO(image_bytes)
            )

            image_path = (
                IMAGE_DIR /
                f"{Path(source).stem}_page_{page_number}"
                f"_image_{image_index + 1}.png"
            )

            image.convert("RGB").save(image_path)

            # OCR text inside the image.
            image_text = extract_image_text(image)

            elements.append({
                "type": "image",
                "text": image_text,
                "bbox": tuple(block["bbox"]),
                "image_path": str(image_path),
                "image_number": image_index + 1
            })

        except Exception:
            logger.exception(
                "PDF image extraction failed: %s",
                source
            )

    return elements


# ==========================================================
# 8. PDF PAGE PROCESSING
# ==========================================================

def extract_pdf_page(page, plumber_page, page_number, source):
    """
    Extracts all content from one PDF page.

    Combines text, tables and images, removes text blocks
    substantially overlapping table regions, and sorts
    elements according to their original page positions.

    Uses full-page OCR as a fallback when the page has
    little extractable text.
    """

    elements = []

    # Extract individual text blocks.
    text_elements = extract_pdf_text_blocks(page)

    # Extract positioned tables.
    table_elements = extract_pdf_tables(plumber_page)

    # Extract positioned images and their OCR.
    image_elements = extract_pdf_images(
        page,
        page_number,
        source
    )

    table_boxes = [
        element["bbox"]
        for element in table_elements
    ]

    # Remove text blocks that are mostly inside a table.
    # This avoids indexing the same table twice.
    for text_element in text_elements:

        text_area = (
            (text_element["bbox"][2] - text_element["bbox"][0])
            *
            (text_element["bbox"][3] - text_element["bbox"][1])
        )

        if text_area <= 0:
            continue

        overlaps_table = any(
            calculate_overlap(
                text_element["bbox"],
                table_box
            ) / text_area > 0.5
            for table_box in table_boxes
        )

        if not overlaps_table:
            elements.append(text_element)

    elements.extend(table_elements)
    elements.extend(image_elements)

    # OCR entire page only when normal extraction
    # produces almost no text, tables or image OCR.
    total_text = " ".join(
        element["text"] for element in elements
    ).strip()

    if len(total_text) < 30:

        try:
            pix = page.get_pixmap(
                matrix=fitz.Matrix(2, 2),
                alpha=False
            )

            page_image = Image.open(
                BytesIO(pix.tobytes("png"))
            )

            ocr_text = extract_image_text(page_image)

            if ocr_text:
                elements.append({
                    "type": "page_ocr",
                    "text": ocr_text,
                    "bbox": (0, 0, page.rect.width, page.rect.height)
                })

        except Exception:
            logger.exception(
                "Full page OCR failed: %s page %s",
                source,
                page_number
            )

    # Approximate reading order.
    elements = get_reading_order(elements)

    # Convert all elements into common records.
    records = []

    for sequence, element in enumerate(elements, start=1):

        content_type = element["type"]

        text = element["text"]

        # Even images without OCR text are retained as
        # records with their image path and coordinates.
        if content_type == "image" and not text:
            text = "[Image with no OCR-detected text]"

        records.append(
            create_record(
                text=text,
                source=source,
                content_type=f"pdf_{content_type}",
                page_number=page_number,
                bbox=element["bbox"],
                sequence=sequence,
                extra_metadata={
                    key: value
                    for key, value in element.items()
                    if key not in {"type", "text", "bbox"}
                }
            )
        )

    return records


# ==========================================================
# 9. COMPLETE PDF EXTRACTION
# ==========================================================

def extract_pdf(file_path):
    """
    Processes all PDF pages.

    Uses PyMuPDF for text and image positions and pdfplumber
    for table extraction and table coordinates.
    """

    records = []

    try:

        with fitz.open(file_path) as pdf_doc:

            with pdfplumber.open(file_path) as plumber_pdf:

                for index, page in enumerate(pdf_doc):

                    page_number = index + 1

                    logger.info(
                        "PDF %s page %s",
                        file_path.name,
                        page_number
                    )

                    plumber_page = plumber_pdf.pages[index]

                    page_records = extract_pdf_page(
                        page,
                        plumber_page,
                        page_number,
                        file_path.name
                    )

                    records.extend(page_records)

    except Exception:
        logger.exception(
            "PDF processing failed: %s",
            file_path.name
        )

    return records


# ==========================================================
# 10. CSV EXTRACTION
# ==========================================================

def extract_csv(file_path):
    """
    Extracts CSV headers and rows.

    Converts the complete dataset into structured Markdown.
    """

    records = []

    try:

        df = pd.read_csv(
            file_path,
            encoding="utf-8-sig",
            sep=None,
            engine="python",
            on_bad_lines="warn"
        )

        df = df.fillna("")

        text = "CSV DATA:\n" + df.to_markdown(index=False)

        records.append(
            create_record(
                text,
                file_path.name,
                "csv_table",
                extra_metadata={
                    "row_count": len(df),
                    "column_names": list(df.columns)
                }
            )
        )

    except Exception:
        logger.exception(
            "CSV processing failed: %s",
            file_path.name
        )

    return records


# ==========================================================
# 11. EXCEL EXTRACTION
# ==========================================================

def extract_excel(file_path):
    """
    Extracts all Excel sheets and their tabular data.

    Also extracts embedded images and performs OCR on them.
    Preserves sheet names, row information and image positions.
    """

    records = []

    try:

        excel_file = pd.ExcelFile(file_path)

        for sheet_name in excel_file.sheet_names:

            df = pd.read_excel(
                excel_file,
                sheet_name=sheet_name
            )

            if not df.empty:

                df = df.fillna("")

                records.append(
                    create_record(
                        "EXCEL SHEET: " + sheet_name +
                        "\n" + df.to_markdown(index=False),
                        file_path.name,
                        "excel_table",
                        sheet_name=sheet_name,
                        extra_metadata={
                            "row_count": len(df),
                            "column_names": list(df.columns)
                        }
                    )
                )

        # Extract embedded Excel images using openpyxl.
        # _images and _data are internal openpyxl APIs.
        # Pin/test openpyxl versions if using this in production.
        if file_path.suffix.lower() == ".xlsx":

            workbook = load_workbook(
                file_path,
                data_only=True
            )

            for sheet in workbook.worksheets:

                for index, excel_image in enumerate(
                    getattr(sheet, "_images", []),
                    start=1
                ):

                    try:

                        image = Image.open(
                            BytesIO(excel_image._data())
                        )

                        image_path = (
                            IMAGE_DIR /
                            f"{file_path.stem}_{sheet.title}"
                            f"_image_{index}.png"
                        )

                        image.convert("RGB").save(image_path)

                        image_text = extract_image_text(image)

                        anchor = excel_image.anchor

                        # Excel anchors are cell-based, not PDF
                        # page coordinates.
                        anchor_cell = None

                        if hasattr(anchor, "_from"):
                            anchor_cell = (
                                f"{anchor._from.col + 1},"
                                f"{anchor._from.row + 1}"
                            )

                        records.append(
                            create_record(
                                image_text or
                                "[Image with no OCR-detected text]",
                                file_path.name,
                                "excel_image",
                                sheet_name=sheet.title,
                                sequence=index,
                                extra_metadata={
                                    "image_path": str(image_path),
                                    "anchor_cell": anchor_cell
                                }
                            )
                        )

                    except Exception:
                        logger.exception(
                            "Excel image extraction failed"
                        )

    except Exception:
        logger.exception(
            "Excel processing failed: %s",
            file_path.name
        )

    return records


# ==========================================================
# 12. TEXT EXTRACTION
# ==========================================================

def extract_txt(file_path):
    """
    Reads plain text files and creates a common record.
    """

    try:

        text = file_path.read_text(
            encoding="utf-8",
            errors="replace"
        )

        if text.strip():

            return [
                create_record(
                    text,
                    file_path.name,
                    "text"
                )
            ]

    except Exception:
        logger.exception(
            "Text extraction failed: %s",
            file_path.name
        )

    return []


# ==========================================================
# 13. IMAGE FILE EXTRACTION
# ==========================================================

def extract_image(file_path):
    """
    Extracts OCR text from standalone image files.
    Preserves the image file path in metadata.
    """

    text = extract_image_text(file_path)

    return [
        create_record(
            text or "[Image with no OCR-detected text]",
            file_path.name,
            "image_ocr",
            extra_metadata={
                "image_path": str(file_path)
            }
        )
    ]


# ==========================================================
# 14. DOCUMENT TYPE ROUTER
# ==========================================================

def process_document(file_path):
    """
    Detects the input extension and invokes the correct
    extraction function.
    """

    extension = file_path.suffix.lower()

    logger.info("Processing document: %s", file_path)

    if extension == ".pdf":
        return extract_pdf(file_path)

    if extension == ".csv":
        return extract_csv(file_path)

    if extension in [".xlsx", ".xls"]:
        return extract_excel(file_path)

    if extension == ".txt":
        return extract_txt(file_path)

    if extension in [".png", ".jpg", ".jpeg", ".tiff"]:
        return extract_image(file_path)

    return []


# ==========================================================
# 15. PROCESS ALL DOCUMENTS
# ==========================================================

def process_all_documents(input_dir):
    """
    Recursively processes all supported documents inside
    the input directory and combines extracted records.
    """

    all_records = []

    for file_path in Path(input_dir).rglob("*"):

        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        records = process_document(file_path)

        all_records.extend(records)

    return all_records


# ==========================================================
# 16. POSITION-AWARE MARKDOWN EXPORT
# ==========================================================

def save_markdown(records, output_path):
    """
    Exports extracted records into readable Markdown.

    Preserves original document sequence, page numbers,
    content types and image references.
    """

    with open(output_path, "w", encoding="utf-8") as file:

        for record in records:

            metadata = record["metadata"]

            file.write(
                f"\n\n## {metadata['source']}\n"
            )

            if metadata.get("page_number"):
                file.write(
                    f"\nPage: {metadata['page_number']}\n"
                )

            if metadata.get("sheet_name"):
                file.write(
                    f"\nSheet: {metadata['sheet_name']}\n"
                )

            file.write(
                f"\nType: {metadata['content_type']}\n"
            )

            if metadata.get("bbox"):
                file.write(
                    f"\nPosition: {metadata['bbox']}\n"
                )

            file.write(
                f"\nSequence: {metadata.get('sequence')}\n"
            )

            file.write("\n")

            # Image reference is retained even when OCR
            # cannot detect any text.
            image_path = metadata.get("image_path")

            if image_path:
                file.write(
                    f"\n[IMAGE REFERENCE: {image_path}]\n"
                )

            file.write(record["text"])

            file.write("\n\n---\n")


# ==========================================================
# 17. JSONL EXPORT
# ==========================================================

def save_jsonl(records, output_path):
    """
    Exports each extracted content element as one JSON line.

    Suitable for downstream chunking, indexing and storage.
    """

    with open(output_path, "w", encoding="utf-8") as file:

        for record in records:

            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                    default=str
                ) + "\n"
            )

def create_dummy_files():
    """
    Generates sample documents covering supported formats
    so the extraction pipeline can be tested end to end.
    """

    INPUT_DIR.mkdir(exist_ok=True)

    # TXT
    (INPUT_DIR / "employee.txt").write_text(
        "Employee: Rahul\nDepartment: Engineering\n"
        "Experience: 4 years\nSkills: Python, RAG, ML",
        encoding="utf-8"
    )

    # CSV
    pd.DataFrame({
        "Product": ["Laptop", "Mobile", "Tablet"],
        "Price": [50000, 20000, 15000],
        "Quantity": [5, 10, 8]
    }).to_csv(INPUT_DIR / "products.csv", index=False)

    # Excel
    with pd.ExcelWriter(
        INPUT_DIR / "sales.xlsx",
        engine="openpyxl"
    ) as writer:

        pd.DataFrame({
            "Month": ["Jan", "Feb", "Mar"],
            "Revenue": [100000, 150000, 200000]
        }).to_excel(
            writer, sheet_name="Revenue", index=False
        )

        pd.DataFrame({
            "Employee": ["Rahul", "Priya"],
            "Department": ["IT", "HR"]
        }).to_excel(
            writer, sheet_name="Employees", index=False
        )

    # Image containing OCR-readable text
    from PIL import ImageDraw

    image = Image.new("RGB", (700, 200), "white")
    draw = ImageDraw.Draw(image)

    draw.text((30, 30), "INVOICE", fill="black")
    draw.text((30, 80), "Customer: Rahul", fill="black")
    draw.text((30, 130), "Amount: 25000", fill="black")

    image_path = INPUT_DIR / "invoice.png"
    image.save(image_path)

    # PDF containing text, table and embedded image
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table,
        TableStyle, Image as PDFImage
    )
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from reportlab.lib.units import inch

    styles = getSampleStyleSheet()

    elements = [
        Paragraph("Company Sales Report", styles["Title"]),
        Spacer(1, 20),
        Paragraph(
            "This report contains product sales details.",
            styles["BodyText"]
        ),
        Spacer(1, 20)
    ]

    table = Table([
        ["Product", "Price", "Quantity"],
        ["Laptop", "50000", "5"],
        ["Mobile", "20000", "10"],
        ["Tablet", "15000", "8"]
    ])

    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey)
    ]))

    elements.extend([
        table,
        Spacer(1, 30),
        Paragraph("Invoice Image", styles["Heading2"]),
        PDFImage(str(image_path), width=4*inch, height=1.2*inch)
    ])

    SimpleDocTemplate(
        str(INPUT_DIR / "report.pdf")
    ).build(elements)

create_dummy_files()

extracted_records = process_all_documents(INPUT_DIR)

save_markdown(
    extracted_records,
    OUTPUT_DIR / "extracted_content.md"
)

save_jsonl(
    extracted_records,
    OUTPUT_DIR / "extracted_content.jsonl"
)
# ==========================================================
# 18. MAIN EXECUTION
# ==========================================================

if __name__ == "__main__":

    extracted_records = process_all_documents(INPUT_DIR)

    save_markdown(
        extracted_records,
        OUTPUT_DIR / "extracted_content.md"
    )

    save_jsonl(
        extracted_records,
        OUTPUT_DIR / "extracted_content.jsonl"
    )

    logger.info(
        "Extraction completed. Total records: %s",
        len(extracted_records)
    )
