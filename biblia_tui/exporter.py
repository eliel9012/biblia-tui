from __future__ import annotations

from pathlib import Path
import re

from .data import Bible, normalize
from .models import Reference


def markdown_for(bible: Bible, ref: Reference) -> str:
    verses = bible.verses(ref.book, ref.chapter)
    start = ref.verse if ref.verse is not None else 0
    end = ref.end_verse if ref.end_verse is not None else (start if ref.verse is not None else len(verses) - 1)
    selected = verses[start : end + 1]
    exact = Reference(ref.book, ref.chapter, start, end)
    lines = [f"# {bible.label(exact)}", ""]
    lines.extend(f"> **{number}.** {text}" for number, text in enumerate(selected, start=start + 1))
    lines.extend(["", "— *Almeida Corrigida Fiel (ACF)*", ""])
    return "\n".join(lines)


def default_export_path(bible: Bible, ref: Reference) -> Path:
    label = normalize(bible.label(ref)).replace(":", "-")
    slug = re.sub(r"[^a-z0-9]+", "-", label).strip("-")
    return Path.home() / "Bíblia" / f"{slug}.md"


def export_markdown(bible: Bible, ref: Reference, path: Path | None = None) -> Path:
    destination = (path or default_export_path(bible, ref)).expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(markdown_for(bible, ref), encoding="utf-8")
    return destination
