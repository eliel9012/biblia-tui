from __future__ import annotations

import curses


THEMES = ("dark", "light", "mono")
THEME_LABELS = {"dark": "escuro", "light": "claro", "mono": "monocromático"}


def next_theme(theme: str) -> str:
    return THEMES[(THEMES.index(theme) + 1) % len(THEMES)]


def apply_theme(theme: str) -> dict[str, int]:
    curses.start_color()
    try:
        curses.use_default_colors()
    except curses.error:
        pass
    if theme == "mono" or not curses.has_colors():
        return {
            "normal": curses.A_NORMAL,
            "header": curses.A_REVERSE | curses.A_BOLD,
            "selected": curses.A_REVERSE,
            "muted": curses.A_DIM,
            "status": curses.A_REVERSE,
            "highlight": curses.A_BOLD,
        }
    if theme == "light":
        pairs = {
            1: (curses.COLOR_BLACK, curses.COLOR_WHITE),
            2: (curses.COLOR_BLUE, curses.COLOR_WHITE),
            3: (curses.COLOR_WHITE, curses.COLOR_BLUE),
            4: (curses.COLOR_YELLOW, curses.COLOR_BLUE),
        }
    else:
        pairs = {
            1: (curses.COLOR_WHITE, curses.COLOR_BLACK),
            2: (curses.COLOR_CYAN, curses.COLOR_BLACK),
            3: (curses.COLOR_BLACK, curses.COLOR_CYAN),
            4: (curses.COLOR_YELLOW, curses.COLOR_BLACK),
        }
    for pair, colors in pairs.items():
        curses.init_pair(pair, *colors)
    return {
        "normal": curses.color_pair(1),
        "header": curses.color_pair(3) | curses.A_BOLD,
        "selected": curses.color_pair(2) | curses.A_REVERSE,
        "muted": curses.color_pair(2) | curses.A_DIM,
        "status": curses.color_pair(3),
        "highlight": curses.color_pair(4) | curses.A_BOLD,
    }
