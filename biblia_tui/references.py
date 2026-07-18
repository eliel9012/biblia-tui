from __future__ import annotations

import re

from .data import Bible, normalize
from .models import Reference


REFERENCE_RE = re.compile(
    r"^\s*(?P<book>.+?)\s+(?P<chapter>\d+)(?:\s*:\s*(?P<verse>\d+)(?:\s*-\s*(?P<end>\d+))?)?\s*$"
)


def parse_reference(value: str, bible: Bible) -> Reference:
    match = REFERENCE_RE.match(value)
    if not match:
        raise ValueError("Use formato como João 3:16 ou 1 Coríntios 13")
    book_key = normalize(match.group("book")).replace(".", "").strip()
    book_key_compact = book_key.replace(" ", "")
    book = bible.aliases.get(book_key, bible.aliases.get(book_key_compact))
    if book is None:
        matches = {index for alias, index in bible.aliases.items() if alias.startswith(book_key)}
        if len(matches) == 1:
            book = matches.pop()
        else:
            raise ValueError(f"Livro não encontrado: {match.group('book')}")
    chapter = int(match.group("chapter")) - 1
    if not 0 <= chapter < bible.chapter_count(book):
        raise ValueError(f"Capítulo inválido para {bible.book_name(book)}")
    verse = int(match.group("verse")) - 1 if match.group("verse") else None
    end = int(match.group("end")) - 1 if match.group("end") else None
    verse_count = len(bible.verses(book, chapter))
    if verse is not None and not 0 <= verse < verse_count:
        raise ValueError("Versículo inicial inválido")
    if end is not None and (verse is None or end < verse or end >= verse_count):
        raise ValueError("Fim do trecho inválido")
    return Reference(book, chapter, verse, end)
