from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock

from biblia_tui.data import Bible
from biblia_tui.models import Reference
from biblia_tui.tui import App
from tests.helpers import write_bible


class NavigationFlowTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.bible = Bible(write_bible(Path(self.temp.name) / "acf.json"))
        self.app = App(None, self.bible, Reference(0, 0, 0), "dark")

    def tearDown(self):
        self.temp.cleanup()

    def test_library_flows_book_chapter_verse(self):
        self.app.select_list = Mock(side_effect=[1, 2, 1])
        self.app.open_reference = Mock()
        self.app.browse_bible()
        self.app.open_reference.assert_called_once_with(Reference(1, 2, 1))
        titles = [call.args[0] for call in self.app.select_list.call_args_list]
        self.assertIn("Biblioteca", titles[0])
        self.assertIn("João", titles[1])
        self.assertIn("João 3", titles[2])

    def test_chapter_cancel_returns_to_book_list(self):
        self.app.select_list = Mock(side_effect=[1, None, None])
        self.app.browse_bible()
        self.assertEqual(self.app.select_list.call_count, 3)


if __name__ == "__main__":
    unittest.main()
