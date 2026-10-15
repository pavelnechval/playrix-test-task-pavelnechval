"""Read an API key at runtime without ever printing, logging or storing it.

Looks in the process environment first, then (on Windows) in the user
environment in the registry, so a variable created after the terminal or app
started still works, then in the repository's .env file, which prepare.py
writes and git ignores (W028).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


def read_key(names: tuple[str, ...]) -> str | None:
    for name in names:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    if sys.platform == "win32":
        import winreg

        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as env:
                for name in names:
                    try:
                        value = str(winreg.QueryValueEx(env, name)[0]).strip()
                    except FileNotFoundError:
                        continue
                    if value:
                        return value
        except OSError:
            pass
    if ENV_FILE.exists():  # NAME=value lines; "export " and quotes are allowed
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            name, sep, value = line.strip().removeprefix("export ").partition("=")
            value = value.strip().strip('"').strip("'")
            if sep and name.strip() in names and value:
                return value
    return None
