import unittest
from unittest.mock import patch

from biblia_tui.clipboard import copy_text
from biblia_tui.themes import next_theme


class ClipboardThemeTests(unittest.TestCase):
    def test_theme_cycle(self):
        self.assertEqual(next_theme("dark"), "light")
        self.assertEqual(next_theme("light"), "mono")
        self.assertEqual(next_theme("mono"), "dark")

    @patch("biblia_tui.clipboard.subprocess.run")
    @patch("biblia_tui.clipboard.shutil.which", side_effect=lambda name: "/usr/bin/wl-copy" if name == "wl-copy" else None)
    def test_clipboard_command(self, _which, run):
        self.assertEqual(copy_text("texto", allow_osc52=False), "wl-copy")
        run.assert_called_once()
        self.assertEqual(run.call_args.kwargs["input"], "texto")

    @patch("biblia_tui.clipboard.shutil.which", return_value=None)
    def test_clipboard_failure_without_fallback(self, _which):
        with self.assertRaises(RuntimeError):
            copy_text("texto", allow_osc52=False)


if __name__ == "__main__":
    unittest.main()
