"""Preferences, recents and favorites, stored with QSettings."""

from __future__ import annotations

import json
from typing import Any

from PySide6.QtCore import QSettings

from .paths import APP_NAME

MAX_RECENTS = 8


class Settings:
    def __init__(self, store: QSettings | None = None) -> None:
        self._s = store or QSettings(APP_NAME, APP_NAME)

    # -- primitives --------------------------------------------------------- #

    def get(self, key: str, default: Any) -> Any:
        value = self._s.value(key, default)
        if isinstance(default, bool):
            if isinstance(value, str):
                return value.lower() in ("1", "true", "yes")
            return bool(value)
        if isinstance(default, int):
            try:
                return int(value)
            except (TypeError, ValueError):
                return default
        return value if value is not None else default

    def set(self, key: str, value: Any) -> None:
        self._s.setValue(key, value)
        self._s.sync()

    # -- composites --------------------------------------------------------- #

    def _json_list(self, key: str) -> list[str]:
        raw = self._s.value(key, "[]")
        try:
            data = json.loads(raw) if isinstance(raw, str) else list(raw)
        except (json.JSONDecodeError, TypeError):
            return []
        return [str(item) for item in data if isinstance(item, (str, int))]

    def recents(self) -> list[str]:
        return self._json_list("recents")

    def push_recent(self, module_id: str) -> list[str]:
        items = [m for m in self.recents() if m != module_id]
        items.insert(0, module_id)
        items = items[:MAX_RECENTS]
        self.set("recents", json.dumps(items))
        return items

    def favorites(self) -> list[str]:
        return self._json_list("favorites")

    def toggle_favorite(self, module_id: str) -> bool:
        items = self.favorites()
        if module_id in items:
            items.remove(module_id)
            self.set("favorites", json.dumps(items))
            return False
        items.insert(0, module_id)
        self.set("favorites", json.dumps(items))
        return True
