import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import patch


def _fake_docx_module() -> ModuleType:
    module = ModuleType("docx")

    class FakeDocument:
        def __init__(self, *args, **kwargs):
            self.paragraphs = []

    module.Document = FakeDocument
    return module


def _fake_pypdf_module() -> ModuleType:
    module = ModuleType("pypdf")

    class FakePdfReader:
        def __init__(self, *args, **kwargs):
            self.pages = []

    module.PdfReader = FakePdfReader
    return module


def _fake_dotenv_module() -> ModuleType:
    module = ModuleType("dotenv")

    def load_dotenv(*args, **kwargs):
        return True

    module.load_dotenv = load_dotenv
    return module


class DocumentsOcrAndChunksTests(unittest.TestCase):
    def test_normalize_ocr_text_removes_noise(self):
        with patch.dict("sys.modules", {"docx": _fake_docx_module(), "pypdf": _fake_pypdf_module(), "dotenv": _fake_dotenv_module()}):
            from pdm_bot.app.documents import normalize_ocr_text

            raw = "line\x00  one\nHEADER\nHEADER\nHEADER\nHEADER\nсло-\nво"
            normalized = normalize_ocr_text(raw)

            self.assertIn("line one", normalized)
            self.assertIn("слово", normalized)
            self.assertNotIn("HEADER", normalized)

    def test_extract_chunks_smoke_for_txt(self):
        with patch.dict("sys.modules", {"docx": _fake_docx_module(), "pypdf": _fake_pypdf_module(), "dotenv": _fake_dotenv_module()}):
            from pdm_bot.app.documents import extract_chunks

            with tempfile.TemporaryDirectory() as td:
                folder = Path(td) / "pdm"
                folder.mkdir()
                path = folder / "Author - Title (2020).txt"
                path.write_text("абзац " * 300, encoding="utf-8")

                chunks = extract_chunks(path)

            self.assertGreaterEqual(len(chunks), 1)
            first = chunks[0]
            self.assertIn("text", first)
            self.assertEqual(first["doc_type"], "txt")
            self.assertEqual(first["page_start"], None)


if __name__ == "__main__":
    unittest.main()
