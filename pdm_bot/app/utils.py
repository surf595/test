import hashlib
import re
from pathlib import Path
from typing import List


def sha1_of_file(path: Path) -> str:
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def split_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not text:
        return []

    chunks, start, length = [], 0, len(text)
    while start < length:
        end = min(start + chunk_size, length)
        chunk = text[start:end]

        if end < length:
            last_break = max(chunk.rfind("\n\n"), chunk.rfind(". "), chunk.rfind("! "), chunk.rfind("? "))
            if last_break > int(chunk_size * 0.55):
                end = start + last_break + 1
                chunk = text[start:end]

        chunk = chunk.strip()
        if chunk:
            chunks.append(chunk)

        if end >= length:
            break
        start = max(end - overlap, start + 1)

    return chunks


def split_message(text: str, limit: int = 4096) -> List[str]:
    if len(text) <= limit:
        return [text]

    parts = []
    start = 0
    while start < len(text):
        end = min(start + limit, len(text))
        part = text[start:end]
        if end < len(text):
            candidate = max(part.rfind("\n\n"), part.rfind("\n"), part.rfind(". "))
            if candidate > int(limit * 0.5):
                end = start + candidate + 1
                part = text[start:end]
        parts.append(part.strip())
        start = end

    return [p for p in parts if p]
