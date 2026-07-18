from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from biblia_tui.data import Bible
from biblia_tui.models import Reference
from biblia_tui.references import parse_reference
from tests.helpers import write_bible


class ReferenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.bible = Bible(write_bible(Path(self.temp.name) / "acf.json"))

    def tearDown(self):
        self.temp.cleanup()

    def test_full_name_and_abbreviation(self):
        self.assertEqual(parse_reference("João 3:2", self.bible), Reference(1, 2, 1))
        self.assertEqual(parse_reference("jo 3:2", self.bible), Reference(1, 2, 1))

    def test_numbered_book_and_range(self):
        self.assertEqual(parse_reference("1 Coríntios 13:1-3", self.bible), Reference(2, 12, 0, 2))

    def test_case_and_accents(self):
        self.assertEqual(parse_reference("GENESIS 1:1", self.bible), Reference(0, 0, 0))

    def test_invalid_values(self):
        for value in ("Nada", "Livro 1", "João 99", "João 3:99", "João 3:2-1"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_reference(value, self.bible)


if __name__ == "__main__":
    unittest.main()
