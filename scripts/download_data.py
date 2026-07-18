#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys
from urllib.request import urlopen


URL = "https://raw.githubusercontent.com/thiagobodruk/biblia/master/json/acf.json"
DESTINATION = Path(__file__).resolve().parents[1] / "data" / "acf.json"


def main() -> int:
    destination = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else DESTINATION
    print(f"Baixando {URL}")
    with urlopen(URL, timeout=30) as response:
        payload = response.read()
    books = json.loads(payload.decode("utf-8-sig"))
    if len(books) != 66 or any(not {"name", "abbrev", "chapters"} <= book.keys() for book in books):
        raise ValueError("Arquivo recebido não possui estrutura bíblica esperada")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".tmp")
    temporary.write_bytes(payload)
    temporary.replace(destination)
    chapters = sum(len(book["chapters"]) for book in books)
    verses = sum(len(chapter) for book in books for chapter in book["chapters"])
    print(f"Pronto: {destination} ({len(books)} livros, {chapters} capítulos, {verses} versículos)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
