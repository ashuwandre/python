"""
Document ingestion pipeline:
1. Scan an input folder recursively.
2. Calculate SHA-256 hashes and skip already-processed/duplicate files.
3. Extract text from PDF, DOCX, XLSX, XLS, CSV, TXT and Markdown.
4. Extract embedded images from PDF, DOCX and XLSX where supported.
5. OCR images with Tesseract; optionally improve/extract image text with GPT vision.
6. Append image-derived text to the extracted document text.
7. Save a Markdown file next to each source document.
8. Run Microsoft Presidio PII detection and mask the Markdown text.
9. Save a masked Markdown file next to the source.
10. Persist processing state in SQLite so unchanged documents are not reprocessed.

Notes:
- PDF/DOCX/XLSX embedded-image extraction is supported.
- Legacy .doc and .xls are supported for text extraction where dependencies permit,
  but embedded-image extraction from these legacy formats is not guaranteed.
- Excel cell images are extracted from XLSX drawing relationships by openpyxl when
  available; images pasted as floating objects may require workbook-specific testing.
- GPT vision is optional. Set OPENAI_API_KEY and ENABLE_GPT_VISION=1 to enable it.
- Tesseract must be installed as a system application, not just a Python package.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import logging
import mimetypes
import os
import re
import sqlite3
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

# ----------------------------- Configuration -----------------------------

SUPPORTED_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".xlsx", ".xls", ".csv", ".txt", ".md", ".markdown"
}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}
DEFAULT_OUTPUT_SUFFIX = ".md"
DB_FILENAME = ".document_ingestion_state.sqlite3"
LOG_FILENAME = "document_ingestion.log"

LOG = logging.getLogger("document_ingestion")
GENERATED_MARKER = "<!-- generated_by_document_ingestion -->"


@dataclass
class Settings:
    input_dir: Path
    state_db: Path
    recursive: bool = True
    enable_gpt_vision: bool = False
    vision_model: str = "gpt-4o-mini"
    ocr_language: str = "eng"
    ocr_dpi: int = 220
    max_image_mb: int = 15
    pii_entities: Optional[list[str]] = None
    pii_score_threshold: float = 0.35
    overwrite_markdown: bool = False
    include_source_metadata: bool = True


# ----------------------------- Hash / state ------------------------------

def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Calculate a streaming SHA-256 hash without loading the whole file."""
    digest = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


class StateStore:
    """SQLite state store for idempotency and duplicate detection."""

    def __init__(self, db_path: Path):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(db_path), timeout=30)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS processed_documents (
                source_path TEXT PRIMARY KEY,
                sha256 TEXT NOT NULL,
                status TEXT NOT NULL,
                markdown_path TEXT,
                masked_markdown_path TEXT,
                processed_at TEXT NOT NULL,
                error TEXT
            )
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_processed_sha
            ON processed_documents(sha256)
        """)
        self.conn.commit()

    def is_unchanged(self, path: Path, file_hash: str) -> bool:
        row = self.conn.execute(
            "SELECT sha256, status FROM processed_documents WHERE source_path=?",
            (str(path.resolve()),)
        ).fetchone()
        return bool(row and row[0] == file_hash and row[1] == "completed")

    def find_duplicate(self, file_hash: str, current_path: Path) -> Optional[str]:
        row = self.conn.execute(
            """SELECT source_path FROM processed_documents
               WHERE sha256=? AND status='completed' AND source_path<>?
               LIMIT 1""",
            (file_hash, str(current_path.resolve()))
        ).fetchone()
        return row[0] if row else None

    def mark(self, path: Path, file_hash: str, status: str,
             markdown_path: Optional[Path] = None,
             masked_path: Optional[Path] = None,
             error: Optional[str] = None) -> None:
        self.conn.execute("""
            INSERT INTO processed_documents
            (source_path, sha256, status, markdown_path,
             masked_markdown_path, processed_at, error)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(source_path) DO UPDATE SET
                sha256=excluded.sha256,
                status=excluded.status,
                markdown_path=excluded.markdown_path,
                masked_markdown_path=excluded.masked_markdown_path,
                processed_at=excluded.processed_at,
                error=excluded.error
        """, (
            str(path.resolve()), file_hash, status,
            str(markdown_path) if markdown_path else None,
            str(masked_path) if masked_path else None,
            datetime.now(timezone.utc).isoformat(),
            error
        ))
        self.conn.commit()

    def close(self):
        self.conn.close()


# ----------------------------- Text helpers ------------------------------

def safe_read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="replace")


def clean_text(text: str) -> str:
    text = text.replace("\x00", "")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip()


def table_to_markdown(headers: list[str], rows: Iterable[Iterable[object]]) -> str:
    def cell(v):
        if v is None:
            return ""
        return str(v).replace("|", r"\|").replace("\n", " ").strip()

    header = "| " + " | ".join(cell(x) for x in headers) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    body = [
        "| " + " | ".join(cell(x) for x in row) + " |"
        for row in rows
    ]
    return "\n".join([header, sep, *body])


# ----------------------------- File extraction ---------------------------

def extract_pdf(path: Path, settings: Settings) -> tuple[str, list[tuple[str, bytes]]]:
    import fitz  # PyMuPDF

    doc = fitz.open(path)
    text_parts = []
    images: list[tuple[str, bytes]] = []
    for page_num, page in enumerate(doc, start=1):
        page_text = page.get_text("text")
        if page_text.strip():
            text_parts.append(f"\n## Page {page_num}\n\n{page_text}")

        # Extract embedded images. Duplicate xrefs are deduplicated per document.
        seen_xrefs = set()
        for image_index, image_info in enumerate(page.get_images(full=True), start=1):
            xref = image_info[0]
            if xref in seen_xrefs:
                continue
            seen_xrefs.add(xref)
            try:
                image_data = doc.extract_image(xref)
                images.append((f"pdf_page_{page_num}_image_{image_index}.{image_data.get('ext', 'png')}",
                               image_data["image"]))
            except Exception as exc:
                LOG.warning("Could not extract PDF image xref %s from %s: %s", xref, path, exc)

    doc.close()
    return clean_text("\n".join(text_parts)), images


def extract_docx(path: Path) -> tuple[str, list[tuple[str, bytes]]]:
    from docx import Document

    document = Document(path)
    parts = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            parts.append(paragraph.text)

    for table_index, table in enumerate(document.tables, start=1):
        rows = [[cell.text for cell in row.cells] for row in table.rows]
        if rows:
            parts.append(f"\n### Table {table_index}\n\n")
            parts.append(table_to_markdown(rows[0], rows[1:]))

    images = []
    # python-docx exposes embedded images through related image parts.
    image_count = 0
    for rel in document.part.rels.values():
        if "image" in rel.reltype:
            image_count += 1
            try:
                part = rel.target_part
                content_type = getattr(part, "content_type", "image/png")
                ext = mimetypes.guess_extension(content_type) or ".png"
                images.append((f"docx_image_{image_count}{ext}", part.blob))
            except Exception as exc:
                LOG.warning("Could not extract DOCX image: %s", exc)

    return clean_text("\n\n".join(parts)), images


def extract_xlsx(path: Path) -> tuple[str, list[tuple[str, bytes]]]:
    from openpyxl import load_workbook

    workbook = load_workbook(path, data_only=True, read_only=False)
    parts = []
    images = []
    image_count = 0

    for sheet in workbook.worksheets:
        parts.append(f"\n## Sheet: {sheet.title}\n")
        rows = []
        for row in sheet.iter_rows(values_only=True):
            values = list(row)
            if any(value is not None for value in values):
                rows.append(values)

        if rows:
            max_cols = max(len(row) for row in rows)
            normalized = [row + [None] * (max_cols - len(row)) for row in rows]
            headers = [
                str(v) if v is not None else f"Column_{i+1}"
                for i, v in enumerate(normalized[0])
            ]
            parts.append(table_to_markdown(headers, normalized[1:]))

        # openpyxl supports images attached to worksheet drawings in XLSX.
        for image in getattr(sheet, "_images", []):
            image_count += 1
            try:
                raw = image._data()
                ext = getattr(image, "format", None) or "png"
                images.append((f"xlsx_{sheet.title}_image_{image_count}.{ext}", raw))
            except Exception as exc:
                LOG.warning("Could not extract XLSX image: %s", exc)

    workbook.close()
    return clean_text("\n\n".join(parts)), images


def extract_xls(path: Path) -> tuple[str, list[tuple[str, bytes]]]:
    import xlrd

    workbook = xlrd.open_workbook(path)
    parts = []
    for sheet in workbook.sheets():
        parts.append(f"\n## Sheet: {sheet.name}\n")
        rows = [
            [sheet.cell_value(r, c) for c in range(sheet.ncols)]
            for r in range(sheet.nrows)
        ]
        if rows:
            headers = [
                str(v) if v != "" else f"Column_{i+1}"
                for i, v in enumerate(rows[0])
            ]
            parts.append(table_to_markdown(headers, rows[1:]))
    # xlrd 2.x does not support extracting images from .xls.
    return clean_text("\n\n".join(parts)), []


def extract_csv(path: Path) -> tuple[str, list[tuple[str, bytes]]]:
    import pandas as pd

    df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding_errors="replace")
    return table_to_markdown(list(df.columns), df.values.tolist()), []


def extract_document(path: Path, settings: Settings) -> tuple[str, list[tuple[str, bytes]]]:
    ext = path.suffix.lower()

    if ext == ".pdf":
        return extract_pdf(path, settings)
    if ext == ".docx":
        return extract_docx(path)
    if ext == ".xlsx":
        return extract_xlsx(path)
    if ext == ".xls":
        return extract_xls(path)
    if ext == ".csv":
        return extract_csv(path)
    if ext in {".txt", ".md", ".markdown"}:
        return safe_read_text(path), []

    if ext == ".doc":
        # Legacy .doc requires antiword or LibreOffice conversion.
        import subprocess
        result = subprocess.run(
            ["antiword", str(path)],
            capture_output=True, text=True, check=True, timeout=120
        )
        return clean_text(result.stdout), []

    raise ValueError(f"Unsupported file extension: {ext}")


# ----------------------------- OCR / Vision -------------------------------

def ocr_with_tesseract(image_bytes: bytes, language: str = "eng") -> str:
    from PIL import Image
    import pytesseract

    image = Image.open(io.BytesIO(image_bytes))
    return clean_text(pytesseract.image_to_string(image, lang=language))


def describe_image_with_gpt(image_bytes: bytes, model: str) -> str:
    """Extract readable text and describe relevant visual content with GPT vision."""
    import base64
    from openai import OpenAI

    client = OpenAI()
    encoded = base64.b64encode(image_bytes).decode("utf-8")

    # Detect the actual image MIME type instead of assuming PNG.
    from PIL import Image
    with Image.open(io.BytesIO(image_bytes)) as img:
        image_format = (img.format or "PNG").lower()
    mime_type = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
                 "webp": "image/webp", "tiff": "image/tiff", "bmp": "image/bmp"}.get(
                     image_format, "image/png"
                 )
    response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract all readable text from this image accurately. "
                    "Preserve headings, labels, table values and sequence. "
                    "If it contains a chart, diagram or screenshot, also describe "
                    "the relevant information needed to understand it. "
                    "Do not guess unreadable text; mark it as [unreadable]."
                )
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract the text and explain relevant visual content."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{encoded}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ]
    )
    return clean_text(response.choices[0].message.content or "")


def process_images(images: list[tuple[str, bytes]], settings: Settings) -> list[str]:
    results = []

    for image_name, image_bytes in images:
        if len(image_bytes) > settings.max_image_mb * 1024 * 1024:
            LOG.warning("Skipping oversized image %s", image_name)
            continue

        image_parts = [f"### Image: {image_name}"]

        # OCR is the local baseline.
        try:
            ocr_text = ocr_with_tesseract(
                image_bytes,
                language=settings.ocr_language
            )
            if ocr_text:
                image_parts.append("#### OCR text\n" + ocr_text)
        except Exception as exc:
            LOG.warning("Tesseract OCR failed for %s: %s", image_name, exc)

        # GPT Vision is optional and can be more useful for diagrams/screenshots.
        if settings.enable_gpt_vision:
            try:
                vision_text = describe_image_with_gpt(
                    image_bytes,
                    settings.vision_model
                )
                if vision_text:
                    image_parts.append("#### GPT Vision extraction\n" + vision_text)
            except Exception as exc:
                LOG.exception("GPT vision failed for %s: %s", image_name, exc)

        if len(image_parts) > 1:
            results.append("\n\n".join(image_parts))

    return results


# ----------------------------- Presidio PII masking -----------------------

def build_presidio_analyzer():
    from presidio_analyzer import AnalyzerEngine
    from presidio_analyzer.nlp_engine import NlpEngineProvider

    # Default Presidio NLP engine uses spaCy. Install en_core_web_lg or
    # another compatible model as described in the README/documentation.
    provider = NlpEngineProvider(
        nlp_configuration={
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": "en_core_web_lg"}]
        }
    )
    nlp_engine = provider.create_engine()
    return AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])


def mask_pii(text: str, analyzer, score_threshold: float = 0.35,
             entities: Optional[list[str]] = None) -> str:
    from presidio_anonymizer import AnonymizerEngine
    from presidio_anonymizer.entities import OperatorConfig

    anonymizer = AnonymizerEngine()

    results = analyzer.analyze(
        text=text,
        language="en",
        entities=entities,
        score_threshold=score_threshold
    )

    operators = {
        "DEFAULT": OperatorConfig("replace", {"new_value": "<PII>"}),
        "PERSON": OperatorConfig("replace", {"new_value": "<PERSON>"}),
        "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<EMAIL>"}),
        "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "<PHONE>"}),
        "CREDIT_CARD": OperatorConfig("replace", {"new_value": "<CREDIT_CARD>"}),
        "US_SSN": OperatorConfig("replace", {"new_value": "<SSN>"}),
        "LOCATION": OperatorConfig("replace", {"new_value": "<LOCATION>"}),
        "IP_ADDRESS": OperatorConfig("replace", {"new_value": "<IP_ADDRESS>"}),
    }

    anonymized = anonymizer.anonymize(
        text=text,
        analyzer_results=results,
        operators=operators
    )
    return anonymized.text


class PIIMaskingService:
    """Small service wrapper around Presidio analysis and anonymization."""

    def __init__(self, score_threshold: float = 0.35,
                 entities: Optional[list[str]] = None):
        self.analyzer = build_presidio_analyzer()
        self.score_threshold = score_threshold
        self.entities = entities

    def mask(self, text: str) -> str:
        return mask_pii(
            text=text,
            analyzer=self.analyzer,
            score_threshold=self.score_threshold,
            entities=self.entities
        )


# ----------------------------- Markdown output ----------------------------

def markdown_paths(source: Path) -> tuple[Path, Path]:
    # Avoid overwriting a Markdown source document with its own extracted output.
    output_stem = source.stem + ".extracted" if source.suffix.lower() in {".md", ".markdown"} else source.stem
    raw_md = source.with_name(output_stem + ".md")
    masked_md = source.with_name(output_stem + ".masked.md")
    return raw_md, masked_md


def build_markdown(source: Path, text: str, settings: Settings) -> str:
    if settings.include_source_metadata:
        metadata = (
            f"{GENERATED_MARKER}\n"
            f"<!-- source_file: {source.name} -->\n"
            f"<!-- source_path: {source.resolve()} -->\n"
            f"<!-- processed_at_utc: {datetime.now(timezone.utc).isoformat()} -->\n\n"
        )
    else:
        metadata = ""

    return metadata + f"# {source.name}\n\n" + clean_text(text) + "\n"


# ----------------------------- Pipeline ----------------------------------

def iter_files(input_dir: Path, recursive: bool = True) -> Iterable[Path]:
    iterator = input_dir.rglob("*") if recursive else input_dir.glob("*")
    for path in iterator:
        if not path.is_file():
            continue
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        # Do not re-ingest generated Markdown outputs or the state database.
        if path.name.endswith(".masked.md"):
            continue
        if path.name == DB_FILENAME:
            continue
        # Ignore Markdown files generated by this pipeline on later scans.
        if path.suffix.lower() in {".md", ".markdown"}:
            try:
                with path.open("r", encoding="utf-8", errors="ignore") as f:
                    if GENERATED_MARKER in f.read(512):
                        continue
            except OSError:
                pass
        yield path


def process_one(path: Path, settings: Settings, state: StateStore, analyzer) -> str:
    file_hash = sha256_file(path)

    # Skip unchanged files already processed successfully.
    if state.is_unchanged(path, file_hash):
        LOG.info("SKIP unchanged: %s", path)
        return "skipped_unchanged"

    # Detect identical content at a different path.
    duplicate_of = state.find_duplicate(file_hash, path)
    if duplicate_of:
        LOG.info("SKIP duplicate: %s (same content as %s)", path, duplicate_of)
        state.mark(path, file_hash, "duplicate", error=f"Duplicate of {duplicate_of}")
        return "duplicate"

    raw_md, masked_md = markdown_paths(path)

    try:
        LOG.info("Processing: %s", path)

        text, images = extract_document(path, settings)
        image_texts = process_images(images, settings)

        combined_text = "\n\n".join(
            part for part in [text, *image_texts] if part.strip()
        )

        if not combined_text.strip():
            combined_text = "[No text could be extracted from this document.]"

        markdown = build_markdown(path, combined_text, settings)

        if settings.overwrite_markdown or not raw_md.exists():
            raw_md.write_text(markdown, encoding="utf-8")

        # PII masking is performed on the extracted Markdown content.
        masked_text = mask_pii(
            markdown,
            analyzer=analyzer,
            score_threshold=settings.pii_score_threshold,
            entities=settings.pii_entities
        )

        if settings.overwrite_markdown or not masked_md.exists():
            masked_md.write_text(masked_text, encoding="utf-8")

        state.mark(
            path,
            file_hash,
            "completed",
            markdown_path=raw_md,
            masked_path=masked_md
        )

        LOG.info("Completed: %s", path)
        return "completed"

    except Exception as exc:
        LOG.exception("Failed to process %s", path)
        state.mark(path, file_hash, "failed", error=str(exc))
        return "failed"


def main():
    parser = argparse.ArgumentParser(
        description="Hash-aware document extraction, OCR, vision and PII masking pipeline."
    )
    parser.add_argument("--input-dir", required=True, help="Folder containing source documents.")
    parser.add_argument("--recursive", action="store_true", help="Scan subfolders recursively.")
    parser.add_argument("--enable-gpt-vision", action="store_true", help="Enable GPT vision extraction.")
    parser.add_argument("--vision-model", default="gpt-4o-mini")
    parser.add_argument("--overwrite-markdown", action="store_true")
    parser.add_argument("--ocr-language", default="eng")
    parser.add_argument("--state-db", default=None)

    args = parser.parse_args()

    input_dir = Path(args.input_dir).expanduser().resolve()
    if not input_dir.exists() or not input_dir.is_dir():
        raise SystemExit(f"Input directory does not exist or is not a directory: {input_dir}")

    settings = Settings(
        input_dir=input_dir,
        state_db=Path(args.state_db).resolve() if args.state_db else input_dir / DB_FILENAME,
        recursive=args.recursive,
        enable_gpt_vision=args.enable_gpt_vision,
        vision_model=args.vision_model,
        ocr_language=args.ocr_language,
        overwrite_markdown=args.overwrite_markdown
    )

    log_path = input_dir / LOG_FILENAME
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )

    pii_service = PIIMaskingService(
        score_threshold=settings.pii_score_threshold,
        entities=settings.pii_entities
    )
    analyzer = pii_service.analyzer
    state = StateStore(settings.state_db)

    summary = {
        "completed": 0,
        "skipped_unchanged": 0,
        "duplicate": 0,
        "failed": 0
    }

    try:
        for path in iter_files(input_dir, recursive=settings.recursive):
            # Avoid processing generated markdown as a second source if it is
            # in the same input folder and not an original source file.
            if path.suffix.lower() in {".md", ".markdown"}:
                if path.name.endswith(".masked.md"):
                    continue
            status = process_one(path, settings, state, analyzer)
            summary[status] = summary.get(status, 0) + 1
    finally:
        state.close()

    print("\nPROCESSING SUMMARY")
    print(json.dumps(summary, indent=2))
    print(f"Log file: {log_path}")


if __name__ == "__main__":
    main()
