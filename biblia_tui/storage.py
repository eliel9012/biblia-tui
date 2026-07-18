from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Reference


CONFIG_DIR = Path.home() / ".config" / "biblia"
STATE_FILE = CONFIG_DIR / "state.json"
HISTORY_FILE = CONFIG_DIR / "history.json"


def _read(path: Path, default: Any) -> Any:
    try:
        with path.open(encoding="utf-8") as stream:
            return json.load(stream)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
    temporary.replace(path)


def load_state() -> tuple[Reference, str]:
    state = _read(STATE_FILE, {})
    try:
        ref = Reference(int(state.get("book", 0)), int(state.get("chapter", 0)), int(state.get("verse", 0)))
    except (TypeError, ValueError):
        ref = Reference(0, 0, 0)
    theme = state.get("theme", "dark")
    if theme not in {"dark", "light", "mono"}:
        theme = "dark"
    return ref, theme


def save_state(ref: Reference, theme: str) -> None:
    _write(STATE_FILE, {"book": ref.book, "chapter": ref.chapter, "verse": ref.verse or 0, "theme": theme})


def load_history() -> list[Reference]:
    items = _read(HISTORY_FILE, [])
    history = []
    for item in items:
        try:
            history.append(Reference(int(item["book"]), int(item["chapter"]), item.get("verse")))
        except (KeyError, TypeError, ValueError):
            continue
    return history


def add_history(ref: Reference, maximum: int = 100) -> None:
    history = load_history()
    clean = Reference(ref.book, ref.chapter, ref.verse)
    history = [item for item in history if item != clean]
    history.insert(0, clean)
    payload = [{"book": item.book, "chapter": item.chapter, "verse": item.verse} for item in history[:maximum]]
    _write(HISTORY_FILE, payload)
