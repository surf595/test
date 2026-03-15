import unittest

from pdm_bot.app.utils import split_text


class SplitTextTests(unittest.TestCase):
    def test_split_text_returns_empty_for_blank(self):
        self.assertEqual(split_text("   ", 100, 10), [])

    def test_split_text_splits_and_preserves_overlap_progress(self):
        text = "A" * 120 + "\n\n" + "B" * 120 + ". " + "C" * 120
        chunks = split_text(text, chunk_size=140, overlap=20)
        self.assertGreaterEqual(len(chunks), 2)
        self.assertTrue(all(chunks))


if __name__ == "__main__":
    unittest.main()
