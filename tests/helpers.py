import json
from pathlib import Path


BOOKS = [
    {
        "abbrev": "gn",
        "name": "Gênesis",
        "chapters": [["No princípio criou Deus.", "Haja luz."], ["Assim foram acabados os céus."]],
    },
    {
        "abbrev": "jo",
        "name": "João",
        "chapters": [
            ["No princípio era o Verbo."],
            ["E, ao terceiro dia, fizeram-se umas bodas."],
            ["Jesus respondeu.", "Porque Deus amou o mundo."],
        ],
    },
    {
        "abbrev": "1co",
        "name": "1 Coríntios",
        "chapters": [[f"Versículo {n}." for n in range(1, 14)] for _ in range(13)],
    },
]


def write_bible(path: Path) -> Path:
    path.write_text("\ufeff" + json.dumps(BOOKS, ensure_ascii=False), encoding="utf-8")
    return path
