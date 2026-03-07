import re
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

from docx import Document as DocxDocument
from pypdf import PdfReader

from .config import CHUNK_OVERLAP, CHUNK_SIZE
from .utils import split_text


def normalize_ocr_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    lines = [ln.strip() for ln in text.splitlines()]
    if lines:
        freq = {}
        for ln in lines:
            if 5 <= len(ln) <= 100:
                freq[ln] = freq.get(ln, 0) + 1
        garbage = {k for k, v in freq.items() if v >= 4}
        lines = [ln for ln in lines if ln not in garbage]
    return "\n".join(lines).strip()


def extract_basic_metadata(path: Path) -> Dict:
    name = path.stem
    metadata = {
        "author": "",
        "title": name,
        "year": "",
        "language": "ru" if re.search(r"[А-Яа-яЁё]", name) else "en",
        "doc_type": path.suffix.lower().lstrip("."),
        "section": path.parent.name,
        "chapter": "",
        "tags": [],
        "corpus": path.parent.name.lower(),
    }

    m = re.match(r"(?P<author>.+?)\s+-\s+(?P<title>.+?)(?:\s+\((?P<year>\d{4})\))?$", name)
    if m:
        metadata["author"] = m.group("author") or ""
        metadata["title"] = m.group("title") or name
        metadata["year"] = m.group("year") or ""
    return metadata


def read_txt(path: Path) -> str:
    return normalize_ocr_text(path.read_text(encoding="utf-8", errors="ignore"))


def read_docx(path: Path) -> str:
    doc = DocxDocument(str(path))
    return normalize_ocr_text("\n".join(p.text for p in doc.paragraphs))


def read_pdf_pages(path: Path) -> List[Tuple[int, str]]:
    pages: List[Tuple[int, str]] = []
    try:
        reader = PdfReader(str(path))
        for i, page in enumerate(reader.pages, start=1):
            try:
                txt = normalize_ocr_text(page.extract_text() or "")
                pages.append((i, txt))
            except Exception:
                pages.append((i, ""))
    except Exception:
        pages = []

    if any(t.strip() for _, t in pages):
        return pages

    try:
        result = subprocess.run(["pdftotext", str(path), "-"], capture_output=True, text=True, check=True)
        text = normalize_ocr_text(result.stdout or "")
        if text:
            return [(1, text)]
    except Exception:
        return []

    return []


def extract_chunks(path: Path) -> List[Dict]:
    suffix = path.suffix.lower()
    meta = extract_basic_metadata(path)

    if suffix in {".txt", ".md"}:
        text = read_txt(path)
        return [
            {
                "text": chunk,
                "page_start": None,
                "page_end": None,
                **meta,
            }
            for chunk in split_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
        ]

    if suffix == ".docx":
        text = read_docx(path)
        return [
            {
                "text": chunk,
                "page_start": None,
                "page_end": None,
                **meta,
            }
            for chunk in split_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
        ]

    if suffix == ".pdf":
        rows: List[Dict] = []
        for page_no, page_text in read_pdf_pages(path):
            if not page_text.strip():
                continue
            for chunk in split_text(page_text, CHUNK_SIZE, CHUNK_OVERLAP):
                rows.append(
                    {
                        "text": chunk,
                        "page_start": page_no,
                        "page_end": page_no,
                        **meta,
                    }
                )
        return rows

    raise ValueError(f"Неподдерживаемый формат: {suffix}")
