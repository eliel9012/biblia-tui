from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from biblia_tui.data import Bible
from biblia_tui.exporter import export_markdown, markdown_for
from biblia_tui.models import Reference
from tests.helpers import write_bible


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.bible = Bible(write_bible(self.root / "acf.json"))

    def tearDown(self):
        self.temp.cleanup()

    def test_range_to_markdown(self):
        text = markdown_for(self.bible, Reference(0, 0, 0, 1))
        self.assertIn("# Gênesis 1:1-2", text)
        self.assertIn("> **1.** No princípio", text)
        self.assertIn("> **2.** Haja luz", text)

    def test_whole_chapter(self):
        text = markdown_for(self.bible, Reference(0, 0))
        self.assertEqual(text.count("> **"), 2)

    def test_writes_destination(self):
        destination = self.root / "trecho.md"
        result = export_markdown(self.bible, Reference(1, 2, 1), destination)
        self.assertEqual(result, destination)
        self.assertIn("João 3:2", destination.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
