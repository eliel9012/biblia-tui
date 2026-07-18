from __future__ import annotations

import json
import os
from pathlib import Path
import unicodedata

from .models import Reference, SearchResult


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.casefold())
    return "".join(char for char in value if not unicodedata.combining(char))


def data_candidates() -> list[Path]:
    paths: list[Path] = []
    if configured := os.environ.get("BIBLIA_DATA"):
        paths.append(Path(configured).expanduser())
    paths.extend(
        [
            Path(__file__).resolve().parents[1] / "data" / "acf.json",
            Path.home() / ".local" / "share" / "biblia-tui" / "acf.json",
            Path.home() / "acf.json",
        ]
    )
    return paths


def find_data_file() -> Path:
    for path in data_candidates():
        if path.is_file():
            return path
    checked = "\n  ".join(str(path) for path in data_candidates())
    raise FileNotFoundError(
        "Texto bíblico não encontrado. Execute scripts/download_data.py ou defina "
        f"BIBLIA_DATA.\nLocais verificados:\n  {checked}"
    )


class Bible:
    def __init__(self, path: Path | None = None):
        self.path = path or find_data_file()
        with self.path.open(encoding="utf-8-sig") as stream:
            self.books: list[dict] = json.load(stream)
        self._validate()
        self.aliases = self._make_aliases()

    def _validate(self) -> None:
        if not isinstance(self.books, list) or not self.books:
            raise ValueError("Base bíblica vazia ou inválida")
        for book in self.books:
            if not {"name", "abbrev", "chapters"} <= book.keys():
                raise ValueError("Livro com estrutura inválida")

    def _make_aliases(self) -> dict[str, int]:
        aliases: dict[str, int] = {}
        for index, book in enumerate(self.books):
            name = normalize(book["name"])
            abbrev = normalize(book["abbrev"])
            variants = {name, abbrev, name.replace(" ", ""), abbrev.replace(" ", "")}
            first = name.split()[0]
            if not first.isdigit() and sum(b["name"].split()[0] == book["name"].split()[0] for b in self.books) == 1:
                variants.add(first)
            for variant in variants:
                aliases[variant] = index
        common = {
            "gen": "gn", "genesis": "gn", "ex": "ex", "exodo": "ex",
            "sl": "sl", "salmo": "sl", "salmos": "sl", "pv": "pv",
            "mt": "mt", "mc": "mc", "lc": "lc", "joao": "jo",
            "rom": "rm", "apoc": "ap", "apocalipse": "ap",
        }
        by_abbrev = {normalize(b["abbrev"]): i for i, b in enumerate(self.books)}
        for alias, abbrev in common.items():
            if abbrev in by_abbrev:
                aliases[alias] = by_abbrev[abbrev]
        return aliases

    def book_name(self, index: int) -> str:
        return self.books[index]["name"]

    def chapter_count(self, book: int) -> int:
        return len(self.books[book]["chapters"])

    def verses(self, book: int, chapter: int) -> list[str]:
        return self.books[book]["chapters"][chapter]

    def verse_text(self, ref: Reference) -> str:
        if ref.verse is None:
            raise ValueError("Referência não possui versículo")
        return self.verses(ref.book, ref.chapter)[ref.verse]

    def label(self, ref: Reference, include_end: bool = True) -> str:
        label = f"{self.book_name(ref.book)} {ref.chapter + 1}"
        if ref.verse is not None:
            label += f":{ref.verse + 1}"
            if include_end and ref.end_verse is not None and ref.end_verse != ref.verse:
                label += f"-{ref.end_verse + 1}"
        return label

    def clamp(self, ref: Reference) -> Reference:
        book = min(max(ref.book, 0), len(self.books) - 1)
        chapter = min(max(ref.chapter, 0), self.chapter_count(book) - 1)
        verses = self.verses(book, chapter)
        verse = None if ref.verse is None else min(max(ref.verse, 0), len(verses) - 1)
        end = None if ref.end_verse is None else min(max(ref.end_verse, verse or 0), len(verses) - 1)
        return Reference(book, chapter, verse, end)

    def adjacent_chapter(self, book: int, chapter: int, delta: int) -> Reference:
        chapter += delta
        if chapter < 0 and book > 0:
            book -= 1
            chapter = self.chapter_count(book) - 1
        elif chapter >= self.chapter_count(book) and book < len(self.books) - 1:
            book += 1
            chapter = 0
        return self.clamp(Reference(book, chapter, 0))

    def search(self, query: str, limit: int = 200) -> list[SearchResult]:
        needle = normalize(query).strip()
        if not needle:
            return []
        results: list[SearchResult] = []
        for book_index, book in enumerate(self.books):
            for chapter_index, chapter in enumerate(book["chapters"]):
                for verse_index, text in enumerate(chapter):
                    if needle in normalize(text):
                        results.append(SearchResult(Reference(book_index, chapter_index, verse_index), text))
                        if len(results) >= limit:
                            return results
        return results
