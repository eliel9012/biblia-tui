from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from biblia_tui.models import Reference
from biblia_tui import storage


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        root = Path(self.temp.name)
        self.state_patch = patch.object(storage, "STATE_FILE", root / "state.json")
        self.history_patch = patch.object(storage, "HISTORY_FILE", root / "history.json")
        self.state_patch.start()
        self.history_patch.start()

    def tearDown(self):
        self.history_patch.stop()
        self.state_patch.stop()
        self.temp.cleanup()

    def test_state_round_trip(self):
        storage.save_state(Reference(1, 2, 1), "light")
        self.assertEqual(storage.load_state(), (Reference(1, 2, 1), "light"))

    def test_history_newest_first_and_unique(self):
        first = Reference(0, 0, 0)
        second = Reference(1, 2, 1)
        storage.add_history(first)
        storage.add_history(second)
        storage.add_history(first)
        self.assertEqual(storage.load_history(), [first, second])


if __name__ == "__main__":
    unittest.main()
