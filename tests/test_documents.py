import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import patch


def _fake_docx_module() -> ModuleType:
    m = ModuleType("docx")

    class FakeDocument:
        def __init__(self, *args, **kwargs):
            self.paragraphs = []

    m.Document = FakeDocument
    return m


def _fake_pypdf_module() -> ModuleType:
    m = ModuleType("pypdf")

    class FakePdfReader:
        def __init__(self, *args, **kwargs):
            self.pages = []

    m.PdfReader = FakePdfReader
    return m


def _fake_dotenv_module() -> ModuleType:
    m = ModuleType("dotenv")

    def load_dotenv(*args, **kwargs):
        return True

    m.load_dotenv = load_dotenv
    return m


class MetadataTests(unittest.TestCase):
    def test_extract_basic_metadata_from_named_file(self):
        with patch.dict(
            "sys.modules",
            {"docx": _fake_docx_module(), "pypdf": _fake_pypdf_module(), "dotenv": _fake_dotenv_module()},
        ):
            from pdm_bot.app.documents import extract_basic_metadata

            with tempfile.TemporaryDirectory() as td:
                folder = Path(td) / "PDM"
                folder.mkdir()
                path = folder / "Freud - Intro (1910).txt"
                path.write_text("x", encoding="utf-8")

                meta = extract_basic_metadata(path)

                self.assertEqual(meta["author"], "Freud")
                self.assertEqual(meta["title"], "Intro")
                self.assertEqual(meta["year"], "1910")
                self.assertEqual(meta["corpus"], "pdm")


if __name__ == "__main__":
    unittest.main()
