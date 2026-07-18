from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class Reference:
    book: int
    chapter: int
    verse: int | None = None
    end_verse: int | None = None


@dataclass(frozen=True)
class SearchResult:
    reference: Reference
    text: str
