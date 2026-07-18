from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from biblia_tui.data import Bible, normalize
from biblia_tui.models import Reference
from tests.helpers import write_bible


class BibleTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.bible = Bible(write_bible(Path(self.temp.name) / "acf.json"))

    def tearDown(self):
        self.temp.cleanup()

    def test_reads_bom_and_structure(self):
        self.assertEqual(len(self.bible.books), 3)
        self.assertEqual(self.bible.book_name(0), "Gênesis")
        self.assertEqual(self.bible.chapter_count(1), 3)

    def test_normalize_removes_case_and_accents(self):
        self.assertEqual(normalize("GÊNESIS"), "genesis")

    def test_search_ignores_case_and_accents(self):
        results = self.bible.search("PRINCIPIO")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].reference, Reference(0, 0, 0))

    def test_adjacent_chapter_crosses_book(self):
        self.assertEqual(self.bible.adjacent_chapter(0, 1, 1), Reference(1, 0, 0))
        self.assertEqual(self.bible.adjacent_chapter(1, 0, -1), Reference(0, 1, 0))

    def test_search_limit(self):
        self.assertEqual(len(self.bible.search("versículo", limit=5)), 5)


if __name__ == "__main__":
    unittest.main()
