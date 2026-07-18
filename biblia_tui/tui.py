from __future__ import annotations

import curses
import textwrap
from typing import Callable

from .clipboard import copy_text
from .data import Bible
from .exporter import export_markdown
from .models import Reference, SearchResult
from .references import parse_reference
from .storage import add_history, load_history, save_state
from .themes import THEME_LABELS, apply_theme, next_theme


HELP = [
    ("↑/↓ ou j/k", "versículo anterior/seguinte"),
    ("PgUp/PgDn", "mover uma página"),
    ("←/→ ou h/l", "capítulo anterior/seguinte"),
    ("g", "abrir referência"),
    ("b", "escolher livro e capítulo"),
    ("/", "pesquisar palavra ou frase"),
    ("n / N", "próximo/anterior resultado"),
    ("H", "histórico de referências"),
    ("e", "exportar trecho em Markdown"),
    ("y", "copiar versículo selecionado"),
    ("t", "alternar tema"),
    ("?", "esta ajuda"),
    ("q", "sair"),
]


def safe_addstr(window, y: int, x: int, text: str, attr: int = 0, width: int | None = None) -> None:
    height, max_width = window.getmaxyx()
    if y < 0 or y >= height or x < 0 or x >= max_width:
        return
    allowed = max_width - x - (1 if y == height - 1 else 0)
    if width is not None:
        allowed = min(allowed, width)
    if allowed <= 0:
        return
    try:
        window.addnstr(y, x, text, allowed, attr)
    except curses.error:
        pass


class App:
    def __init__(self, screen, bible: Bible, initial: Reference, theme: str):
        self.screen = screen
        self.bible = bible
        self.ref = bible.clamp(Reference(initial.book, initial.chapter, initial.verse or 0))
        self.theme = theme
        self.colors: dict[str, int] = {}
        self.message = ""
        self.last_results: list[SearchResult] = []
        self.result_index = -1
        self.running = True

    def setup(self) -> None:
        curses.curs_set(0)
        self.screen.keypad(True)
        self.screen.timeout(-1)
        self.colors = apply_theme(self.theme)
        add_history(self.ref)

    def run(self) -> None:
        self.setup()
        while self.running:
            self.draw()
            self.handle_key(self.screen.getch())
        save_state(self.ref, self.theme)

    def draw(self) -> None:
        self.screen.erase()
        height, width = self.screen.getmaxyx()
        if height < 8 or width < 36:
            safe_addstr(self.screen, 0, 0, "Terminal pequeno demais", curses.A_BOLD)
            safe_addstr(self.screen, 2, 0, "Mínimo: 36 colunas × 8 linhas")
            safe_addstr(self.screen, height - 1, 0, "q sair")
            self.screen.refresh()
            return
        self._draw_header(width)
        self._draw_chapter(height, width)
        self._draw_status(height, width)
        self.screen.refresh()

    def _draw_header(self, width: int) -> None:
        title = " Bíblia ACF "
        location = f" {self.bible.book_name(self.ref.book)} {self.ref.chapter + 1} "
        safe_addstr(self.screen, 0, 0, " " * width, self.colors["header"])
        safe_addstr(self.screen, 0, 1, title, self.colors["header"])
        safe_addstr(self.screen, 0, max(1, width - len(location) - 1), location, self.colors["header"])

    def _wrapped_lines(self, width: int) -> list[tuple[int, str, bool]]:
        lines: list[tuple[int, str, bool]] = []
        content_width = max(10, width - 7)
        for index, verse in enumerate(self.bible.verses(self.ref.book, self.ref.chapter)):
            wrapped = textwrap.wrap(verse, content_width, break_long_words=False, break_on_hyphens=False) or [""]
            lines.extend((index, part, part_index == 0) for part_index, part in enumerate(wrapped))
            lines.append((index, "", False))
        return lines

    def _draw_chapter(self, height: int, width: int) -> None:
        lines = self._wrapped_lines(width)
        selected = self.ref.verse or 0
        selected_line = next((i for i, item in enumerate(lines) if item[0] == selected), 0)
        available = height - 2
        start = max(0, selected_line - available // 3)
        if start + available > len(lines):
            start = max(0, len(lines) - available)
        for row, (verse, text, first) in enumerate(lines[start : start + available], start=1):
            attr = self.colors["selected"] if verse == selected else self.colors["normal"]
            prefix = f"{verse + 1:>3}  " if first else "     "
            safe_addstr(self.screen, row, 0, " " * width, attr)
            safe_addstr(self.screen, row, 1, prefix, self.colors["highlight"] if verse == selected else self.colors["muted"])
            safe_addstr(self.screen, row, 6, text, attr)

    def _draw_status(self, height: int, width: int) -> None:
        text = self.message or "←/→ capítulo  g referência  / busca  H histórico  ? ajuda  q sair"
        safe_addstr(self.screen, height - 1, 0, " " * width, self.colors["status"])
        safe_addstr(self.screen, height - 1, 1, text, self.colors["status"], width - 2)
        self.message = ""

    def handle_key(self, key: int) -> None:
        if key in (ord("q"), 27):
            self.running = False
        elif key in (curses.KEY_DOWN, ord("j")):
            self._move_verse(1)
        elif key in (curses.KEY_UP, ord("k")):
            self._move_verse(-1)
        elif key in (curses.KEY_NPAGE,):
            self._move_verse(max(1, self.screen.getmaxyx()[0] // 3))
        elif key in (curses.KEY_PPAGE,):
            self._move_verse(-max(1, self.screen.getmaxyx()[0] // 3))
        elif key in (curses.KEY_RIGHT, ord("l")):
            self.open_reference(self.bible.adjacent_chapter(self.ref.book, self.ref.chapter, 1))
        elif key in (curses.KEY_LEFT, ord("h")):
            self.open_reference(self.bible.adjacent_chapter(self.ref.book, self.ref.chapter, -1))
        elif key == curses.KEY_HOME:
            self.ref = Reference(self.ref.book, self.ref.chapter, 0)
        elif key == curses.KEY_END:
            self.ref = Reference(self.ref.book, self.ref.chapter, len(self._verses()) - 1)
        elif key == ord("g"):
            self.goto_prompt()
        elif key == ord("b"):
            self.choose_book()
        elif key == ord("/"):
            self.search_prompt()
        elif key == ord("n"):
            self.move_result(1)
        elif key == ord("N"):
            self.move_result(-1)
        elif key == ord("H"):
            self.show_history()
        elif key == ord("e"):
            self.export_prompt()
        elif key == ord("y"):
            self.copy_current()
        elif key == ord("t"):
            self.cycle_theme()
        elif key == ord("?"):
            self.show_help()

    def _verses(self) -> list[str]:
        return self.bible.verses(self.ref.book, self.ref.chapter)

    def _move_verse(self, delta: int) -> None:
        verse = min(max((self.ref.verse or 0) + delta, 0), len(self._verses()) - 1)
        self.ref = Reference(self.ref.book, self.ref.chapter, verse)

    def open_reference(self, ref: Reference) -> None:
        selected = ref.verse if ref.verse is not None else 0
        self.ref = self.bible.clamp(Reference(ref.book, ref.chapter, selected))
        add_history(self.ref)

    def prompt(self, label: str, initial: str = "") -> str | None:
        height, width = self.screen.getmaxyx()
        curses.curs_set(1)
        curses.echo()
        self.screen.timeout(-1)
        safe_addstr(self.screen, height - 1, 0, " " * width, self.colors["status"])
        safe_addstr(self.screen, height - 1, 1, label, self.colors["status"])
        safe_addstr(self.screen, height - 1, len(label) + 1, initial, self.colors["status"])
        self.screen.move(height - 1, min(width - 2, len(label) + len(initial) + 1))
        try:
            raw = self.screen.getstr(height - 1, len(label) + 1, max(1, width - len(label) - 3))
            value = raw.decode("utf-8", errors="replace").strip()
            return value or initial or None
        except (curses.error, KeyboardInterrupt):
            return None
        finally:
            curses.noecho()
            curses.curs_set(0)

    def goto_prompt(self) -> None:
        value = self.prompt("Ir para: ", self.bible.label(self.ref))
        if not value:
            return
        try:
            self.open_reference(parse_reference(value, self.bible))
        except ValueError as error:
            self.message = str(error)

    def choose_book(self) -> None:
        items = [book["name"] for book in self.bible.books]
        chosen = self.select_list("Escolha o livro", items, self.ref.book)
        if chosen is None:
            return
        value = self.prompt(f"{items[chosen]} — capítulo: ", "1")
        if value is None:
            return
        try:
            chapter = int(value) - 1
            if not 0 <= chapter < self.bible.chapter_count(chosen):
                raise ValueError
            self.open_reference(Reference(chosen, chapter, 0))
        except ValueError:
            self.message = "Capítulo inválido"

    def search_prompt(self) -> None:
        query = self.prompt("Buscar: ")
        if not query:
            return
        self.message = "Buscando…"
        self.draw()
        results = self.bible.search(query)
        if not results:
            self.message = f"Nenhum resultado para: {query}"
            return
        self.last_results = results
        labels = [f"{self.bible.label(item.reference)}  {item.text}" for item in results]
        chosen = self.select_list(f"Resultados: {query} ({len(results)})", labels, 0)
        if chosen is not None:
            self.result_index = chosen
            self.open_reference(results[chosen].reference)

    def move_result(self, delta: int) -> None:
        if not self.last_results:
            self.message = "Faça uma busca primeiro"
            return
        self.result_index = (self.result_index + delta) % len(self.last_results)
        self.open_reference(self.last_results[self.result_index].reference)
        self.message = f"Resultado {self.result_index + 1}/{len(self.last_results)}"

    def show_history(self) -> None:
        valid = [self.bible.clamp(item) for item in load_history()]
        if not valid:
            self.message = "Histórico vazio"
            return
        chosen = self.select_list("Histórico", [self.bible.label(item) for item in valid], 0)
        if chosen is not None:
            self.open_reference(valid[chosen])

    def export_prompt(self) -> None:
        current = self.bible.label(self.ref)
        value = self.prompt("Exportar referência: ", current)
        if not value:
            return
        try:
            ref = parse_reference(value, self.bible)
            path = export_markdown(self.bible, ref)
            self.message = f"Exportado: {path}"
        except (ValueError, OSError) as error:
            self.message = f"Falha ao exportar: {error}"

    def copy_current(self) -> None:
        ref = Reference(self.ref.book, self.ref.chapter, self.ref.verse or 0)
        text = f"{self.bible.verse_text(ref)} — {self.bible.label(ref)} (ACF)"
        try:
            backend = copy_text(text)
            self.message = f"Versículo copiado ({backend})"
        except RuntimeError as error:
            self.message = str(error)

    def cycle_theme(self) -> None:
        self.theme = next_theme(self.theme)
        self.colors = apply_theme(self.theme)
        self.message = f"Tema: {THEME_LABELS[self.theme]}"

    def show_help(self) -> None:
        items = [f"{key:<15} {description}" for key, description in HELP]
        self.select_list("Ajuda", items, 0, selectable=False)

    def select_list(self, title: str, items: list[str], selected: int = 0, selectable: bool = True) -> int | None:
        if not items:
            return None
        selected = min(max(selected, 0), len(items) - 1)
        while True:
            self.screen.erase()
            height, width = self.screen.getmaxyx()
            safe_addstr(self.screen, 0, 0, " " * width, self.colors["header"])
            safe_addstr(self.screen, 0, 1, f" {title} ", self.colors["header"])
            available = max(1, height - 2)
            start = min(max(0, selected - available // 2), max(0, len(items) - available))
            for row, (index, item) in enumerate(enumerate(items[start : start + available], start=start), start=1):
                attr = self.colors["selected"] if index == selected else self.colors["normal"]
                safe_addstr(self.screen, row, 0, " " * width, attr)
                safe_addstr(self.screen, row, 1, item, attr, width - 2)
            footer = "↑/↓ mover  Enter abrir  Esc voltar" if selectable else "↑/↓ mover  Esc voltar"
            safe_addstr(self.screen, height - 1, 0, " " * width, self.colors["status"])
            safe_addstr(self.screen, height - 1, 1, footer, self.colors["status"])
            self.screen.refresh()
            key = self.screen.getch()
            if key in (27, ord("q")):
                return None
            if key in (curses.KEY_DOWN, ord("j")):
                selected = min(selected + 1, len(items) - 1)
            elif key in (curses.KEY_UP, ord("k")):
                selected = max(selected - 1, 0)
            elif key == curses.KEY_NPAGE:
                selected = min(selected + available, len(items) - 1)
            elif key == curses.KEY_PPAGE:
                selected = max(selected - available, 0)
            elif key in (10, 13, curses.KEY_ENTER) and selectable:
                return selected


def run_tui(bible: Bible, initial: Reference, theme: str) -> None:
    curses.wrapper(lambda screen: App(screen, bible, initial, theme).run())
