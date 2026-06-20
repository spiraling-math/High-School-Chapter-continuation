from __future__ import annotations

import csv
import hashlib
import html as html_lib
import io
import json
import re
import struct
import sys
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
MANIFEST_CSV = DOCS_DIR / "SOURCE_MANIFEST.csv"
MANIFEST_JSON = DOCS_DIR / "source_manifest.records.json"

EXCLUDED_DIRS = {
    ".git",
    ".agents",
    ".codex",
    "docs",
    "schemas",
    "scripts",
    "apps",
    "core",
    "domains",
    "renderers",
    "exporters",
    "tests",
    "node_modules",
    "__pycache__",
}

ARCHIVE_EXTENSIONS = {".zip"}
TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".json", ".html", ".htm", ".css", ".js", ".ts", ".py", ".xml"}
DOCX_EXTENSIONS = {".docx"}
PDF_EXTENSIONS = {".pdf"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}


@dataclass
class SourceRecord:
    source_id: str
    original_path: str
    filename: str
    file_type: str
    file_size: int
    sha256: str
    extraction_status: str
    rights_status: str
    apparent_owner_or_publisher: str
    course_or_level: str
    subject_domain: str
    strand: str
    chapter_or_unit: str
    document_purpose: str
    presence_of_questions: str
    presence_of_answers: str
    presence_of_worked_solutions: str
    presence_of_diagrams_or_data: str
    language: str
    duplication_status: str = "pending"
    quality_notes: str = "unknown"
    review_notes: str = "unknown"
    source_kind: str = "file"
    container_path: str = ""
    archive_depth: int = 0
    page_count: str = "unknown"
    image_dimensions: str = "unknown"
    text_sample_length: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def normalise_path(value: str) -> str:
    return value.replace("\\", "/").strip("/")


def stable_id(original_path: str) -> str:
    digest = hashlib.sha256(normalise_path(original_path).lower().encode("utf-8")).hexdigest()[:12]
    return f"SRC-{digest.upper()}"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_bytes(path: Path) -> bytes:
    with path.open("rb") as handle:
        return handle.read()


def decode_text(data: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return ""


def strip_html(text: str) -> str:
    text = re.sub(r"<script\b[^>]*>.*?</script>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<style\b[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html_lib.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def extract_docx_text(data: bytes) -> tuple[str, str]:
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            names = archive.namelist()
            text_parts: list[str] = []
            for name in names:
                if name.startswith("word/") and name.endswith(".xml") and (
                    name == "word/document.xml" or "header" in name or "footer" in name
                ):
                    xml = archive.read(name).decode("utf-8", errors="ignore")
                    text_parts.extend(re.findall(r"<w:t[^>]*>(.*?)</w:t>", xml, flags=re.S))
            media_count = sum(1 for name in names if name.startswith("word/media/"))
            text = " ".join(html_lib.unescape(part) for part in text_parts)
            return re.sub(r"\s+", " ", text).strip(), f"DOCX inspected safely; embedded media files: {media_count}"
    except Exception as exc:
        return "", f"DOCX metadata unreadable: {type(exc).__name__}: {exc}"


def extract_pdf_text(data: bytes) -> tuple[str, str, str]:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception:
        return "", "unknown", "PDF header inspected; pypdf unavailable for text extraction"

    try:
        reader = PdfReader(io.BytesIO(data), strict=False)
        if getattr(reader, "is_encrypted", False):
            return "", "unknown", "PDF appears encrypted or protected"
        pages = len(reader.pages)
        parts: list[str] = []
        for page in reader.pages[:2]:
            try:
                parts.append(page.extract_text() or "")
            except Exception:
                parts.append("")
        text = re.sub(r"\s+", " ", " ".join(parts)).strip()
        return text, str(pages), f"PDF inspected safely; text extracted from first {min(pages, 2)} page(s)"
    except Exception as exc:
        return "", "unknown", f"PDF metadata unreadable: {type(exc).__name__}: {exc}"


def png_dimensions(data: bytes) -> str:
    if len(data) >= 24 and data[:8] == b"\x89PNG\r\n\x1a\n":
        width, height = struct.unpack(">II", data[16:24])
        return f"{width} x {height}"
    return "unknown"


def jpeg_dimensions(data: bytes) -> str:
    if len(data) < 4 or data[:2] != b"\xff\xd8":
        return "unknown"
    index = 2
    while index + 9 < len(data):
        if data[index] != 0xFF:
            index += 1
            continue
        marker = data[index + 1]
        index += 2
        if marker in {0xD8, 0xD9}:
            continue
        if index + 2 > len(data):
            break
        length = struct.unpack(">H", data[index : index + 2])[0]
        if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
            if index + 7 <= len(data):
                height, width = struct.unpack(">HH", data[index + 3 : index + 7])
                return f"{width} x {height}"
            break
        index += length
    return "unknown"


def image_dimensions(data: bytes, extension: str) -> str:
    if extension == ".png":
        return png_dimensions(data)
    if extension in {".jpg", ".jpeg"}:
        return jpeg_dimensions(data)
    return "unknown"


def infer_level(path: str, text: str) -> str:
    combined = f"{path} {text[:2000]}".lower()
    checks = [
        ("Preschool and KG", ["preschool", "kindergarten", " kg", "pre-k"]),
        ("Primary school", ["primary", "grade 1", "grade 2", "grade 3", "grade 4", "grade 5"]),
        ("Middle school", ["middle school", "grade 6", "grade 7", "grade 8"]),
        ("High school", ["high school", "grade 9", "grade 10", "grade 11", "grade 12", "advanced school"]),
        ("IBDP Mathematics AA SL", ["ibdp", "aasl", "mathematics: analysis and approaches", "maasl"]),
        ("First-year university", ["university", "undergraduate"]),
    ]
    for label, terms in checks:
        if any(term in combined for term in terms):
            return label
    return "unknown"


DOMAIN_KEYWORDS = [
    ("Early mathematics", ["counting", "subitizing", "recognition", "patterns"]),
    ("Arithmetic", ["arithmetic", "addition", "subtraction", "multiplication", "division"]),
    ("Number", ["number", "integers", "fractions", "decimals", "percentages", "ratio", "surds", "indices"]),
    ("Algebra", ["algebra", "equations", "inequalities", "polynomials", "factor", "expand"]),
    ("Functions", ["functions", "function", "graphs", "domain", "range", "quadratic", "linear", "exponential", "logarithm"]),
    ("Geometry", ["geometry", "angles", "circle", "solid", "construction", "coordinate geometry"]),
    ("Measurement", ["measurement", "area", "volume", "units", "ruler", "perimeter"]),
    ("Trigonometry", ["trig", "trigonometry", "sine", "cosine", "tangent", "radian", "unit circle"]),
    ("Vectors", ["vectors", "vector"]),
    ("Probability", ["probability", "conditional", "random", "binomial", "normal distribution"]),
    ("Statistics", ["statistics", "data", "regression", "correlation", "histogram", "box plot"]),
    ("Calculus", ["calculus", "limits", "differentiation", "derivative", "integration", "integral"]),
    ("Discrete mathematics", ["discrete", "combinatorics", "graph theory", "networks"]),
    ("Decision mathematics", ["decision", "shortest path", "spanning tree", "network flows"]),
    ("Modelling", ["modelling", "modeling", "model"]),
    ("Linear algebra", ["matrix", "matrices", "determinant", "eigen"]),
    ("AI mathematics", ["ai mathematics", "data science", "optimization"]),
]


def infer_domain(path: str, text: str) -> str:
    combined = f"{path} {text[:3000]}".lower()
    hits = [label for label, terms in DOMAIN_KEYWORDS if any(term in combined for term in terms)]
    return "; ".join(dict.fromkeys(hits)) if hits else "unknown"


def infer_chapter_or_unit(path: str, text: str) -> str:
    filename = Path(path.split("::")[-1]).name
    patterns = [
        r"(?:chapter|module|unit)\s*([0-9]{1,2})",
        r"aasl-([0-9]{2})",
        r"bks_MaaSL_([0-9]{2})",
        r"hs-([A-Z][0-9]{1,2})",
    ]
    for pattern in patterns:
        match = re.search(pattern, filename, flags=re.I)
        if match:
            return match.group(0)
    title = re.search(r"<title>(.*?)</title>", text, flags=re.I | re.S)
    if title:
        return re.sub(r"\s+", " ", title.group(1)).strip()[:120]
    return "unknown"


def infer_purpose(path: str, extension: str, text: str) -> str:
    lower = path.lower()
    if lower.endswith(".zip"):
        return "source archive"
    if "project_instructions" in lower:
        return "project instructions"
    if "question engine prompt" in lower:
        return "question engine prompt"
    if "logo" in lower and extension in IMAGE_EXTENSIONS:
        return "brand asset"
    if "teacher notes" in lower or "_tn" in lower:
        return "teacher notes"
    if "worksheet" in lower or "_ws" in lower or "exercise" in lower:
        return "worksheet or exercise"
    if "_ct" in lower or "chapter test" in lower:
        return "chapter test"
    if "assessment" in lower or "capstone" in lower or "100_questions" in lower:
        return "assessment or question collection"
    if "curriculum-map" in lower:
        return "curriculum map"
    if "source-inventory" in lower:
        return "source inventory"
    if extension in {".html", ".htm"} and "spi-math-ibdp-aasl/documents" in lower:
        return "generated curriculum document"
    if extension in IMAGE_EXTENSIONS:
        return "image asset"
    if extension == ".pdf":
        return "PDF source"
    if extension == ".docx":
        return "Word document source"
    if extension in TEXT_EXTENSIONS:
        return "text source"
    return "unknown"


def infer_yes_no(text: str, path: str, terms: list[str]) -> str:
    combined = f"{path} {text[:5000]}".lower()
    return "yes" if any(term in combined for term in terms) else "unknown"


def infer_language(text: str, path: str) -> str:
    combined = f"{path} {text[:5000]}"
    if not combined.strip():
        return "unknown"
    ascii_letters = sum(1 for char in combined if "a" <= char.lower() <= "z")
    arabic_chars = sum(1 for char in combined if "\u0600" <= char <= "\u06ff")
    if arabic_chars > ascii_letters * 0.15:
        return "contains Arabic or mixed language"
    if ascii_letters > 20:
        return "English"
    return "unknown"


def infer_rights(path: str) -> tuple[str, str, str]:
    lower = path.lower()
    if any(term in lower for term in ["spi-math", "spimath", "question engine prompt", "project_instructions"]):
        return "Academy-owned", "SPI-Math", "Rights status inferred from SPI-Math naming; confirm before publication"
    if "teacher notes" in lower or "maasl" in lower or "oxford" in lower or lower.endswith(".pdf"):
        return "Reference only", "Unknown publisher or external source", "Use for coverage and pattern analysis only until license is confirmed"
    if lower.endswith(".zip"):
        return "Rights unknown", "unknown", "Archive requires owner and license review"
    return "Rights unknown", "unknown", "Rights status requires review"


def analyse_data(
    original_path: str,
    data: bytes,
    source_kind: str,
    container_path: str,
    archive_depth: int,
    extraction_status: str,
) -> SourceRecord:
    filename = Path(original_path.split("::")[-1]).name
    extension = Path(filename).suffix.lower()
    file_type = extension[1:].upper() if extension else "unknown"
    text = ""
    quality_notes = "Binary or unsupported format; metadata only"
    page_count = "unknown"
    dimensions = "unknown"

    if extension in TEXT_EXTENSIONS:
        raw = decode_text(data)
        text = strip_html(raw) if extension in {".html", ".htm"} else raw
        quality_notes = "Readable text inspected"
    elif extension in DOCX_EXTENSIONS:
        text, quality_notes = extract_docx_text(data)
    elif extension in PDF_EXTENSIONS:
        text, page_count, quality_notes = extract_pdf_text(data)
    elif extension in IMAGE_EXTENSIONS:
        dimensions = image_dimensions(data, extension)
        quality_notes = f"Image metadata inspected; dimensions: {dimensions}"
    elif extension in ARCHIVE_EXTENSIONS:
        quality_notes = "Archive inspected recursively"

    rights_status, owner, review_notes = infer_rights(original_path)
    has_diagrams = "yes" if extension in IMAGE_EXTENSIONS or re.search(r"\b(svg|diagram|figure|image|table|data set|graph)\b", f"{original_path} {text}", flags=re.I) else "unknown"
    if extension in {".html", ".htm"} and re.search(r"<(svg|img|canvas)\b", decode_text(data), flags=re.I):
        has_diagrams = "yes"

    return SourceRecord(
        source_id=stable_id(original_path),
        original_path=normalise_path(original_path),
        filename=filename,
        file_type=file_type,
        file_size=len(data),
        sha256=sha256_bytes(data),
        extraction_status=extraction_status,
        rights_status=rights_status,
        apparent_owner_or_publisher=owner,
        course_or_level=infer_level(original_path, text),
        subject_domain=infer_domain(original_path, text),
        strand="unknown",
        chapter_or_unit=infer_chapter_or_unit(original_path, text),
        document_purpose=infer_purpose(original_path, extension, text),
        presence_of_questions=infer_yes_no(text, original_path, ["question", "questions", "problem", "exercise", "worksheet", "test"]),
        presence_of_answers=infer_yes_no(text, original_path, ["answer", "answers", "answer key", "mark scheme", "markscheme"]),
        presence_of_worked_solutions=infer_yes_no(text, original_path, ["worked solution", "solution", "solutions", "method marks", "mark scheme"]),
        presence_of_diagrams_or_data=has_diagrams,
        language=infer_language(text, original_path),
        quality_notes=quality_notes,
        review_notes=review_notes,
        source_kind=source_kind,
        container_path=normalise_path(container_path),
        archive_depth=archive_depth,
        page_count=page_count,
        image_dimensions=dimensions,
        text_sample_length=len(text),
        metadata={},
    )


def inspect_archive_bytes(
    archive_path: str,
    data: bytes,
    records: list[SourceRecord],
    depth: int,
    max_depth: int = 4,
) -> None:
    if depth > max_depth:
        return
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            for info in archive.infolist():
                if info.is_dir():
                    continue
                entry_path = f"{archive_path}::{info.filename}"
                if info.flag_bits & 0x1:
                    records.append(
                        SourceRecord(
                            source_id=stable_id(entry_path),
                            original_path=normalise_path(entry_path),
                            filename=Path(info.filename).name,
                            file_type=Path(info.filename).suffix.lower().strip(".").upper() or "unknown",
                            file_size=info.file_size,
                            sha256="unknown",
                            extraction_status="password-protected",
                            rights_status=infer_rights(entry_path)[0],
                            apparent_owner_or_publisher=infer_rights(entry_path)[1],
                            course_or_level=infer_level(entry_path, ""),
                            subject_domain=infer_domain(entry_path, ""),
                            strand="unknown",
                            chapter_or_unit=infer_chapter_or_unit(entry_path, ""),
                            document_purpose=infer_purpose(entry_path, Path(info.filename).suffix.lower(), ""),
                            presence_of_questions="unknown",
                            presence_of_answers="unknown",
                            presence_of_worked_solutions="unknown",
                            presence_of_diagrams_or_data="unknown",
                            language="unknown",
                            source_kind="archive-entry",
                            container_path=archive_path,
                            archive_depth=depth,
                            quality_notes="Encrypted archive entry could not be inspected",
                            review_notes="Requires password or alternate source",
                        )
                    )
                    continue
                try:
                    entry_data = archive.read(info)
                    record = analyse_data(
                        entry_path,
                        entry_data,
                        source_kind="archive-entry",
                        container_path=archive_path,
                        archive_depth=depth,
                        extraction_status="inspected from archive",
                    )
                    records.append(record)
                    entry_extension = Path(info.filename).suffix.lower()
                    if entry_extension in ARCHIVE_EXTENSIONS:
                        inspect_archive_bytes(entry_path, entry_data, records, depth + 1, max_depth=max_depth)
                except Exception as exc:
                    rights_status, owner, review_notes = infer_rights(entry_path)
                    records.append(
                        SourceRecord(
                            source_id=stable_id(entry_path),
                            original_path=normalise_path(entry_path),
                            filename=Path(info.filename).name,
                            file_type=Path(info.filename).suffix.lower().strip(".").upper() or "unknown",
                            file_size=info.file_size,
                            sha256="unknown",
                            extraction_status=f"unreadable archive entry: {type(exc).__name__}: {exc}",
                            rights_status=rights_status,
                            apparent_owner_or_publisher=owner,
                            course_or_level=infer_level(entry_path, ""),
                            subject_domain=infer_domain(entry_path, ""),
                            strand="unknown",
                            chapter_or_unit=infer_chapter_or_unit(entry_path, ""),
                            document_purpose=infer_purpose(entry_path, Path(info.filename).suffix.lower(), ""),
                            presence_of_questions="unknown",
                            presence_of_answers="unknown",
                            presence_of_worked_solutions="unknown",
                            presence_of_diagrams_or_data="unknown",
                            language="unknown",
                            source_kind="archive-entry",
                            container_path=archive_path,
                            archive_depth=depth,
                            quality_notes="Archive entry could not be read",
                            review_notes=review_notes,
                        )
                    )
    except zipfile.BadZipFile as exc:
        source_id = stable_id(archive_path)
        for record in records:
            if record.source_id == source_id:
                record.extraction_status = f"corrupted archive: {type(exc).__name__}: {exc}"
                record.quality_notes = "Archive could not be opened"


def iter_source_files() -> list[Path]:
    paths: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative_parts = path.relative_to(ROOT).parts
        if any(part in EXCLUDED_DIRS for part in relative_parts):
            continue
        paths.append(path)
    return sorted(paths, key=lambda item: rel(item).lower())


def collect_records() -> list[SourceRecord]:
    records: list[SourceRecord] = []
    for path in iter_source_files():
        data = read_bytes(path)
        original_path = rel(path)
        record = analyse_data(
            original_path,
            data,
            source_kind="file",
            container_path="",
            archive_depth=0,
            extraction_status="inspected",
        )
        records.append(record)
        if path.suffix.lower() in ARCHIVE_EXTENSIONS:
            inspect_archive_bytes(original_path, data, records, depth=1)

    by_hash: dict[str, list[SourceRecord]] = defaultdict(list)
    for record in records:
        if record.sha256 != "unknown":
            by_hash[record.sha256].append(record)
    for items in by_hash.values():
        if len(items) == 1:
            items[0].duplication_status = "unique"
        else:
            label = f"duplicate group {items[0].sha256[:12]} ({len(items)} records)"
            for item in items:
                item.duplication_status = label
    return records


FIELDNAMES = [
    "source_id",
    "original_path",
    "filename",
    "file_type",
    "file_size",
    "sha256",
    "extraction_status",
    "rights_status",
    "apparent_owner_or_publisher",
    "course_or_level",
    "subject_domain",
    "strand",
    "chapter_or_unit",
    "document_purpose",
    "presence_of_questions",
    "presence_of_answers",
    "presence_of_worked_solutions",
    "presence_of_diagrams_or_data",
    "language",
    "duplication_status",
    "quality_notes",
    "review_notes",
    "source_kind",
    "container_path",
    "archive_depth",
    "page_count",
    "image_dimensions",
    "text_sample_length",
]


def record_to_dict(record: SourceRecord) -> dict[str, Any]:
    return {field_name: getattr(record, field_name) for field_name in FIELDNAMES}


def write_csv(records: list[SourceRecord]) -> None:
    DOCS_DIR.mkdir(exist_ok=True)
    with MANIFEST_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        for record in records:
            writer.writerow(record_to_dict(record))
    with MANIFEST_JSON.open("w", encoding="utf-8") as handle:
        json.dump([record_to_dict(record) for record in records], handle, indent=2)


def markdown_table(rows: list[list[Any]], headers: list[str]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(value).replace("|", "\\|") for value in row) + " |")
    return "\n".join(lines)


def count_by(records: list[SourceRecord], attribute: str) -> Counter[str]:
    counter: Counter[str] = Counter()
    for record in records:
        value = getattr(record, attribute)
        if value:
            for part in str(value).split("; "):
                counter[part] += 1
    return counter


def top_counts_table(counter: Counter[str], limit: int = 20) -> str:
    return markdown_table([[key, value] for key, value in counter.most_common(limit)], ["Value", "Count"])


def archive_summary(records: list[SourceRecord]) -> list[list[Any]]:
    rows: list[list[Any]] = []
    top_archives = [record for record in records if record.source_kind == "file" and record.file_type == "ZIP"]
    for archive in top_archives:
        children = [record for record in records if record.container_path == archive.original_path]
        child_types = Counter(child.file_type for child in children)
        rows.append(
            [
                archive.original_path,
                archive.file_size,
                len(children),
                ", ".join(f"{key}:{value}" for key, value in child_types.most_common(8)),
                archive.extraction_status,
            ]
        )
    return rows


def inaccessible_records(records: list[SourceRecord]) -> list[SourceRecord]:
    bad_terms = ["unreadable", "password", "corrupted", "metadata unreadable"]
    return [record for record in records if any(term in record.extraction_status.lower() or term in record.quality_notes.lower() for term in bad_terms)]


def duplicate_groups(records: list[SourceRecord]) -> list[list[Any]]:
    groups: dict[str, list[SourceRecord]] = defaultdict(list)
    for record in records:
        if record.sha256 != "unknown":
            groups[record.sha256].append(record)
    rows: list[list[Any]] = []
    for digest, items in groups.items():
        if len(items) > 1:
            rows.append([digest[:12], len(items), "<br>".join(item.original_path for item in items[:6])])
    return rows


def read_curriculum_map_headings() -> list[str]:
    path = ROOT / "spi-math-ibdp-aasl" / "curriculum-map.md"
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="ignore")
    return [line.strip("# ").strip() for line in text.splitlines() if line.startswith("### ")]


def write_doc(path: Path, text: str) -> None:
    path.write_text(text.strip() + "\n", encoding="utf-8")


def generated_file_list() -> str:
    files = [
        "docs/PROJECT_CHARTER.md",
        "docs/SOURCE_MANIFEST.md",
        "docs/SOURCE_MANIFEST.csv",
        "docs/source_manifest.records.json",
        "docs/CONTENT_AUDIT.md",
        "docs/CURRICULUM_COVERAGE.md",
        "docs/QUESTION_PATTERN_CATALOG.md",
        "docs/SOLUTION_STYLE_GUIDE.md",
        "docs/VISUAL_STYLE_AUDIT.md",
        "docs/RISKS_AND_GAPS.md",
        "docs/DECISION_LOG.md",
        "docs/CURRENT_STATE.md",
    ]
    return "\n".join(f"- {item}" for item in files)


def build_docs(records: list[SourceRecord]) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    file_type_counts = count_by(records, "file_type")
    level_counts = count_by(records, "course_or_level")
    domain_counts = count_by(records, "subject_domain")
    purpose_counts = count_by(records, "document_purpose")
    rights_counts = count_by(records, "rights_status")
    bad_records = inaccessible_records(records)
    duplicate_rows = duplicate_groups(records)
    archive_rows = archive_summary(records)
    root_files = [record for record in records if record.source_kind == "file"]
    chapters = read_curriculum_map_headings()
    logo_records = [record for record in records if record.filename.lower() == "spi-math logo.png"]

    write_doc(
        DOCS_DIR / "PROJECT_CHARTER.md",
        f"""
# SPI-Math Question Bank Platform: Project Charter

Generated: {now}

## Objective

Start Phase 0 for the SPI-Math Question Bank Platform by inspecting the uploaded source material, preserving source traceability, and preparing the audit foundation before full application coding begins.

## Source Evidence Used

- `SPI-Math_Project_Instructions.md`
- `Question engine prompt.txt`
- `spi-math logo.png`
- Uploaded ZIP archives and folders under the project root
- Existing `spi-math-ibdp-aasl` curriculum folder and source inventory

## Working Rules Adopted

- Source files are read only.
- Archive contents are inspected recursively without executing scripts, macros, programs, or binaries.
- Generated audit outputs are placed under `docs/`.
- Rights status is conservative. SPI-Math branded internal material is marked `Academy-owned`; external PDFs and publisher-like materials are marked `Reference only`; other archive content remains `Rights unknown` until confirmed.
- English-only product direction from `Question engine prompt.txt` is treated as current project guidance.

## Preliminary Repository Structure

```text
/apps
  /generator-studio
  /question-bank
  /assessment-builder
  /quality-console
  /student-preview
/core
  /curriculum
  /question-schema
  /seeded-random
  /exact-math
  /difficulty
  /misconceptions
  /answer-checking
  /validation
  /bank
  /blueprints
/domains
/renderers
/exporters
/schemas
/tests
/docs
/scripts
```

## Phase 0 Deliverables Created

{generated_file_list()}

## Assumptions

- Broad school-stage ZIP archives are source material, not generated outputs.
- The existing `spi-math-ibdp-aasl` folder is treated as source evidence and prior work, not as the final platform architecture.
- The file named `spi-math logo.png` is the available official logo asset, even though one instruction file mentions `spimath_logo.png`.
- The audit may be refined after deeper document extraction and owner confirmation.

## Blocking Questions

None for Phase 0. Rights confirmation will become blocking before any source-derived content is published or reused beyond analysis.
""",
    )

    write_doc(
        DOCS_DIR / "SOURCE_MANIFEST.md",
        f"""
# Source Manifest

Generated: {now}

The complete row-level manifest is available in `docs/SOURCE_MANIFEST.csv`. A JSON copy is available in `docs/source_manifest.records.json`.

## Accessible Uploaded Files And Archives

{markdown_table([[record.original_path, record.file_type, record.file_size, record.extraction_status] for record in root_files], ["Path", "Type", "Size Bytes", "Status"])}

## Archive Inspection Summary

{markdown_table(archive_rows, ["Archive", "Size Bytes", "Direct Child Files", "Top Child Types", "Status"]) if archive_rows else "No ZIP archives found."}

## Inaccessible Or Partly Unreadable Records

{markdown_table([[record.original_path, record.extraction_status, record.quality_notes] for record in bad_records[:100]], ["Path", "Status", "Notes"]) if bad_records else "No corrupted, password-protected, or unreadable records were detected by the initial audit."}

## File Type Counts

{top_counts_table(file_type_counts)}

## Rights Status Counts

{top_counts_table(rights_counts)}

## Duplicate Hash Groups

{markdown_table(duplicate_rows, ["Hash Prefix", "Count", "Sample Paths"]) if duplicate_rows else "No duplicate file hashes were detected in the initial manifest."}
""",
    )

    write_doc(
        DOCS_DIR / "CONTENT_AUDIT.md",
        f"""
# Content Audit

Generated: {now}

## Initial Inventory Summary

- Total source records, including archive entries: {len(records)}
- Top-level files and folder-contained files: {len(root_files)}
- Top-level ZIP archives: {sum(1 for record in root_files if record.file_type == "ZIP")}
- Records marked as containing questions: {sum(1 for record in records if record.presence_of_questions == "yes")}
- Records marked as containing answers: {sum(1 for record in records if record.presence_of_answers == "yes")}
- Records marked as containing worked solutions: {sum(1 for record in records if record.presence_of_worked_solutions == "yes")}
- Records marked as containing diagrams or data: {sum(1 for record in records if record.presence_of_diagrams_or_data == "yes")}

## Source Hierarchy Detected

- Brand and instruction layer: project instruction Markdown, question engine prompt, and logo image.
- Broad stage archives: preschool and KG, primary school, middle school, high school, and high school worksheets or exercises.
- Focused IBDP AA SL layer: `spi-math-ibdp-aasl` with curriculum map, generated chapter documents, source inventory, QA images, and one tool script that was not executed.
- Teacher notes layer: PDF teacher notes for chapters 1 through 14, with chapter 12 represented by an updated filename.
- Focused DOCX layer: one Module 3 trigonometry document and one Spi-Math Module 2 functions capstone question collection.
- Media check layer: extracted worksheet images and contact sheet.

## Document Purpose Counts

{top_counts_table(purpose_counts)}

## Early Quality Notes

- Archive contents were recursively inventoried and hashed where readable.
- Text extraction was attempted safely for TXT, Markdown, HTML, JSON, CSV, DOCX, and PDF files.
- Source scripts were treated as text only and were not executed.
- Unknown fields are intentionally preserved as `unknown` rather than filled with assumptions.
""",
    )

    write_doc(
        DOCS_DIR / "CURRICULUM_COVERAGE.md",
        f"""
# Curriculum Coverage

Generated: {now}

## Levels And Courses Detected

{top_counts_table(level_counts)}

## Domains Detected

{top_counts_table(domain_counts, limit=30)}

## IBDP AA SL Chapter Map Found

{markdown_table([[chapter] for chapter in chapters], ["Chapter"]) if chapters else "No IBDP chapter map headings were found."}

## Coverage Notes

- Preschool and KG, primary, middle, high school, IBDP AA SL, and first-year university signals are present in the file set.
- High school and IBDP AA SL appear to have the strongest immediately visible structure.
- Primary and preschool coverage exists as archives, but curriculum extraction needs a deeper pass before objectives can be finalized.
- Middle school coverage exists as an archive, but the internal structure needs a deeper pass before generator readiness can be assessed.
- University coverage is currently visible through `university_worksheet_media_check` images and related worksheet media only; objective-level structure is not yet established.

## Objective Taxonomy Status

Objective IDs are not finalized. The next pass should compare source documents before creating stable objective identifiers.
""",
    )

    write_doc(
        DOCS_DIR / "QUESTION_PATTERN_CATALOG.md",
        f"""
# Question Pattern Catalog

Generated: {now}

## Patterns Identified From File Names And Extracted Text

- Worksheet or exercise sets
- Chapter tests
- Multi-question capstone collection
- Generated IBDP chapter documents
- Teacher-note supported exercises
- Diagram or media-supported worksheet material

## Candidate Pattern Families To Confirm

- Direct calculation
- Multi-part constructed response
- Function analysis
- Trigonometric calculation and modelling
- Statistics and probability interpretation
- Graph and diagram interpretation
- Extended assessment-style questions

## Evidence Status

This is an initial catalog. It records likely patterns only where file names or safely extracted text provide a signal. The next audit pass should sample actual question structures from representative documents and connect each pattern to source IDs.
""",
    )

    write_doc(
        DOCS_DIR / "SOLUTION_STYLE_GUIDE.md",
        f"""
# Solution Style Guide

Generated: {now}

## Current Status

The platform requires structured solutions rather than uncontrolled paragraphs. This initial guide records project rules before source-specific solution conventions are fully extracted.

## Required Solution Representation

- Step number
- Mathematical transformation
- Explanation
- Rule or theorem
- Intermediate result
- Units where needed
- Alternative method where valid
- Optional hint
- Mark allocation
- Dependency on earlier steps
- Student-facing and teacher-facing detail levels

## Source Extraction Still Needed

- Accepted equivalent forms
- Rounding conventions
- Mark allocation patterns
- Method mark and accuracy mark style
- Follow-through handling for dependent parts
- Calculator policy by course and level
""",
    )

    logo_note = "No logo record found."
    if logo_records:
        logo = logo_records[0]
        logo_note = f"`{logo.original_path}` inspected. Dimensions: {logo.image_dimensions}. Hash: `{logo.sha256}`."

    write_doc(
        DOCS_DIR / "VISUAL_STYLE_AUDIT.md",
        f"""
# Visual Style Audit

Generated: {now}

## Brand Asset

{logo_note}

## Instruction-Level Visual Rules

- Product name: Spi-Math.
- Tagline: Spiraling Math Into Infinity.
- Visual direction: premium, calm, confident, mathematically beautiful.
- Default interface direction: dark navy surface with controlled cyan, gold, and spectrum accents.
- Typography direction: Fraunces for display, Inter for UI and body, JetBrains Mono for code and seeds, KaTeX for mathematics.
- Logo rule: use the official asset directly, with no redraw, recolor, stretching, or rotation.

## Existing Material Signals

- The `spi-math-ibdp-aasl` HTML documents should be reviewed in the next pass for reusable heading hierarchy, footer treatment, legal identity, and worksheet styling.
- The `university_worksheet_media_check` folder contains extracted images and a contact sheet that should be inspected visually before any diagram style rules are finalized.

## Unknowns

- Final print worksheet layout conventions across all stages.
- Table and answer-space conventions in the school-stage ZIP archives.
- Whether each archive shares one common visual system or several historical systems.
""",
    )

    write_doc(
        DOCS_DIR / "RISKS_AND_GAPS.md",
        f"""
# Risks And Gaps

Generated: {now}

## Rights And Provenance

- Several archives and PDFs have unknown or external rights status. They should guide coverage and pattern analysis only until ownership or license is confirmed.
- Any final generated question bank content must be original unless a source is explicitly authorized.

## Source Completeness

- Some levels are present mainly as archives, so objective-level coverage is not yet complete.
- The prior IBDP inventory states that no separate official IBO syllabus PDF was found in that batch.
- Solutions and mark schemes are not yet confirmed for every level and domain.

## Technical Risks

- Archive and document structures vary across levels, so the extraction pipeline will need adapters rather than one brittle parser.
- Deterministic generation requires exact math, independent validation, and high-volume seed tests before any generator is considered stable.
- Existing generated HTML may be useful as content evidence but should not become the core architecture.

## Immediate Gaps

- Stable curriculum objective identifiers.
- Draft JSON schemas.
- Generator module standard.
- Validation standard.
- First vertical slice recommendation based on source strength.
""",
    )

    write_doc(
        DOCS_DIR / "DECISION_LOG.md",
        f"""
# Decision Log

Generated: {now}

| Date | Decision | Rationale | Status |
| --- | --- | --- | --- |
| {now[:10]} | Start with Phase 0 source audit before full application coding. | Required by `Question engine prompt.txt`; prevents generic platform work disconnected from uploaded curriculum. | Accepted |
| {now[:10]} | Keep source files read only and place generated audit files under `docs/`. | Preserves provenance and prevents accidental overwrites. | Accepted |
| {now[:10]} | Treat SPI-Math branded internal files as Academy-owned for audit purposes, external PDFs as Reference only, and broad archives as Rights unknown until confirmed. | Conservative rights handling is required before content reuse. | Accepted |
| {now[:10]} | Use a modular TypeScript-first repository structure for future implementation. | Matches project architecture instructions and supports standalone offline apps later. | Proposed |
""",
    )

    write_doc(
        DOCS_DIR / "CURRENT_STATE.md",
        f"""
# Current State

Generated: {now}

## Current Phase

Phase 0: Source audit and project foundation.

## Completed Work

- Read project instructions and question engine prompt.
- Inspected available top-level files, folders, and ZIP archive contents.
- Created a hashed source manifest in CSV and JSON form.
- Created initial Phase 0 audit documents.

## Files Created

{generated_file_list()}

## Files Changed

- `scripts/audit_sources.py`

## Decisions Made

- Full application coding is deferred until the source audit and initial architecture package are established.
- Source files remain unmodified.
- Rights status is conservative and must be confirmed before reuse.

## Assumptions

- `spi-math logo.png` is the current official logo asset available in this workspace.
- The existing `spi-math-ibdp-aasl` folder is valid source evidence and prior project work.
- Broad archives require deeper curriculum extraction before objective IDs are finalized.

## Known Problems

- Git is not currently available on PATH in this environment, so no version-control status could be recorded.
- Some source rights are unknown.
- Objective-level curriculum extraction is not complete.

## Failing Tests

No production tests exist yet. The audit script completed if this file was generated.

## Pending Review

- Confirm rights status for the broad stage archives and external-looking PDFs.
- Review the generated source manifest for missing or misclassified sources.
- Decide whether the first vertical slice should begin from the strongest audited source area after deeper sampling.

## Commands

```powershell
& "C:\\Users\\Mohamad Solaiman\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe" scripts\\audit_sources.py
```

## Next Recommended Task

Create the draft schemas and architecture documents, then perform a deeper sampling pass to recommend the first production vertical slice.
""",
    )


def main() -> int:
    records = collect_records()
    write_csv(records)
    build_docs(records)
    print(f"Audit complete. Records: {len(records)}")
    print(f"Wrote {MANIFEST_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
