"""Filesystem locations, in development and inside a PyInstaller bundle."""

from __future__ import annotations

import os
import sys
from pathlib import Path

APP_NAME = "Prism"
VERSION = "1.0.0"


def base_dir() -> Path:
    """The folder that holds ``app/``, ``ui/`` and ``assets/``."""
    frozen = getattr(sys, "_MEIPASS", None)
    if frozen:
        return Path(frozen)
    return Path(__file__).resolve().parent.parent


def resource(*parts: str) -> str:
    return str(base_dir().joinpath(*parts))


def qml_entry() -> str:
    return resource("ui", "qml", "Main.qml")


def data_dir() -> Path:
    root = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
    path = (Path(root) if root else Path.home() / ".local" / "share") / APP_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def log_dir() -> Path:
    path = data_dir() / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path
