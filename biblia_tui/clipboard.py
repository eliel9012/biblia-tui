from __future__ import annotations

import base64
import os
import shutil
import subprocess
import sys


COMMANDS = (
    ("wl-copy", ["wl-copy"]),
    ("xclip", ["xclip", "-selection", "clipboard"]),
    ("xsel", ["xsel", "--clipboard", "--input"]),
    ("pbcopy", ["pbcopy"]),
    ("termux-clipboard-set", ["termux-clipboard-set"]),
)


def copy_text(text: str, allow_osc52: bool = True) -> str:
    for name, command in COMMANDS:
        if shutil.which(name):
            try:
                subprocess.run(command, input=text, text=True, check=True, timeout=5)
                return name
            except (subprocess.SubprocessError, OSError):
                continue
    if allow_osc52 and sys.stdout.isatty() and os.environ.get("TERM", "") != "dumb":
        encoded = base64.b64encode(text.encode()).decode()
        sys.stdout.write(f"\033]52;c;{encoded}\a")
        sys.stdout.flush()
        return "OSC 52"
    raise RuntimeError("Nenhuma ferramenta de área de transferência disponível")
