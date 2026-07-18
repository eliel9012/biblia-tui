from __future__ import annotations

import argparse
from pathlib import Path
import sys

from . import __version__
from .data import Bible
from .exporter import export_markdown
from .references import parse_reference
from .storage import load_state
from .tui import run_tui


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(prog="biblia", description="A Bíblia em tela cheia no terminal")
    command.add_argument("reference", nargs="?", help='referência inicial, por exemplo "João 3:16"')
    command.add_argument("--data", type=Path, help="caminho alternativo para acf.json")
    command.add_argument("--export", dest="export_reference", help="exportar referência para Markdown sem abrir a TUI")
    command.add_argument("--output", type=Path, help="arquivo de saída para --export")
    command.add_argument("--version", action="version", version=f"Bíblia TUI {__version__}")
    return command


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        bible = Bible(args.data)
        saved, theme = load_state()
        if args.export_reference:
            ref = parse_reference(args.export_reference, bible)
            path = export_markdown(bible, ref, args.output)
            print(path)
            return 0
        initial = parse_reference(args.reference, bible) if args.reference else saved
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            print("biblia: interface requer terminal interativo", file=sys.stderr)
            return 2
        run_tui(bible, initial, theme, start_in_library=args.reference is None)
        return 0
    except (FileNotFoundError, ValueError, OSError) as error:
        print(f"biblia: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
