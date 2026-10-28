"""The single seam between QML and Python."""

from __future__ import annotations

import json
from typing import Any

from PySide6.QtCore import Property, QObject, Qt, Signal, Slot
from PySide6.QtGui import QFontDatabase, QGuiApplication

from engine import registry

from .paths import VERSION
from .settings import Settings
from .win_effects import animations_enabled, glass_supported

UI_FONT_CANDIDATES = (
    "Segoe UI Variable Text",
    "Segoe UI Variable",
    "Segoe UI",
    "Inter",
    "SF Pro Text",
)
DISPLAY_FONT_CANDIDATES = (
    "Segoe UI Variable Display",
    "Segoe UI Variable Text",
    "Segoe UI Semibold",
    "Segoe UI",
    "Inter",
)
MONO_FONT_CANDIDATES = (
    "Cascadia Mono",
    "Cascadia Code",
    "JetBrains Mono",
    "Consolas",
    "SF Mono",
    "Menlo",
    "DejaVu Sans Mono",
)


def _pick(candidates: tuple[str, ...], fallback: str) -> str:
    try:
        families = set(QFontDatabase.families())
    except Exception:
        return fallback
    lowered = {f.lower(): f for f in families}
    for name in candidates:
        if name in families:
            return name
        if name.lower() in lowered:
            return lowered[name.lower()]
    return fallback


class Bridge(QObject):
    themeChanged = Signal()
    prefsChanged = Signal()
    listsChanged = Signal()

    def __init__(self, settings: Settings, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._settings = settings
        self._initial_view: dict[str, Any] = {
            "view": "home",
            "categoryId": "",
            "moduleId": "",
            "overlay": "none",
        }
        self._preview_theme: str | None = None
        self._theme_mode = str(settings.get("theme", "system"))
        if self._theme_mode not in ("system", "light", "dark"):
            self._theme_mode = "system"
        self._motion_mode = str(settings.get("motion", "system"))
        if self._motion_mode not in ("system", "full", "reduced"):
            self._motion_mode = "system"
        self._hints = QGuiApplication.styleHints()
        self._hints.colorSchemeChanged.connect(self._on_color_scheme)
        self._ui_font = _pick(UI_FONT_CANDIDATES, QGuiApplication.font().family())
        self._display_font = _pick(DISPLAY_FONT_CANDIDATES, self._ui_font)
        self._mono_font = _pick(MONO_FONT_CANDIDATES, "Consolas")

    # -- appearance --------------------------------------------------------- #

    def _on_color_scheme(self, *_args: Any) -> None:
        if self._theme_mode == "system":
            self.themeChanged.emit()

    def _system_dark(self) -> bool:
        try:
            return self._hints.colorScheme() == Qt.ColorScheme.Dark
        except Exception:
            return False

    @Property(str, notify=themeChanged)
    def themeMode(self) -> str:
        return self._theme_mode

    @Property(bool, notify=themeChanged)
    def dark(self) -> bool:
        if self._preview_theme:
            return self._preview_theme == "dark"
        return self._system_dark() if self._theme_mode == "system" else self._theme_mode == "dark"

    def set_preview_theme(self, mode: str | None) -> None:
        """Used by ``--theme`` so screenshots never touch saved preferences."""
        self._preview_theme = mode if mode in ("light", "dark") else None
        self.themeChanged.emit()

    def set_initial_view(self, view: dict[str, Any]) -> None:
        self._initial_view = dict(view)

    @Property("QVariantMap", constant=True)
    def initialView(self) -> dict[str, Any]:
        return self._initial_view

    @Slot(str)
    def setThemeMode(self, mode: str) -> None:
        if mode not in ("system", "light", "dark"):
            return
        self._theme_mode = mode
        self._settings.set("theme", mode)
        self.themeChanged.emit()

    # -- motion ------------------------------------------------------------- #

    @Property(str, notify=prefsChanged)
    def motionMode(self) -> str:
        return self._motion_mode

    @Property(bool, notify=prefsChanged)
    def reducedMotion(self) -> bool:
        if self._motion_mode == "reduced":
            return True
        if self._motion_mode == "full":
            return False
        return not animations_enabled()

    @Property(bool, notify=prefsChanged)
    def systemAnimations(self) -> bool:
        return animations_enabled()

    @Slot(str)
    def setMotionMode(self, mode: str) -> None:
        if mode not in ("system", "full", "reduced"):
            return
        self._motion_mode = mode
        self._settings.set("motion", mode)
        self.prefsChanged.emit()

    # -- desktop glass ------------------------------------------------------ #

    @Property(bool, constant=True)
    def glassSupported(self) -> bool:
        return glass_supported()

    @Property(bool, notify=prefsChanged)
    def desktopGlass(self) -> bool:
        return bool(self._settings.get("desktopGlass", False)) and self.glassSupported

    @Slot(bool)
    def setDesktopGlass(self, enabled: bool) -> None:
        self._settings.set("desktopGlass", bool(enabled) and self.glassSupported)
        self.prefsChanged.emit()

    # -- fonts and meta ----------------------------------------------------- #

    @Property(str, constant=True)
    def uiFont(self) -> str:
        return self._ui_font

    @Property(str, constant=True)
    def displayFont(self) -> str:
        return self._display_font

    @Property(str, constant=True)
    def monoFont(self) -> str:
        return self._mono_font

    @Property(str, constant=True)
    def version(self) -> str:
        return VERSION

    @Property(int, constant=True)
    def moduleCount(self) -> int:
        return len(registry.modules())

    # -- engine ------------------------------------------------------------- #

    @Slot(result="QVariantList")
    def categories(self) -> list[dict[str, Any]]:
        return registry.categories()

    @Slot(str, result="QVariantList")
    def modulesIn(self, category_id: str) -> list[dict[str, Any]]:
        return registry.modules_in(category_id)

    @Slot(result="QVariantList")
    def allModules(self) -> list[dict[str, Any]]:
        return [m.meta() for m in registry.modules()]

    @Slot(str, result="QVariantMap")
    def moduleSchema(self, module_id: str) -> dict[str, Any]:
        return registry.schema_for(module_id)

    @Slot(str, str, result="QVariantMap")
    def runModule(self, module_id: str, values_json: str) -> dict[str, Any]:
        try:
            values = json.loads(values_json) if values_json else {}
        except json.JSONDecodeError:
            values = {}
        if not isinstance(values, dict):
            values = {}
        return registry.run(module_id, values)

    @Slot(str, int, result="QVariantList")
    def search(self, query: str, limit: int = 18) -> list[dict[str, Any]]:
        return registry.search(query, limit)

    # -- recents and favorites ---------------------------------------------- #

    def _metas(self, ids: list[str]) -> list[dict[str, Any]]:
        out = []
        for module_id in ids:
            m = registry.module(module_id)
            if m is not None:
                meta = m.meta()
                meta["categoryTitle"] = next(
                    (c["title"] for c in registry.CATEGORIES if c["id"] == m.category), m.category
                )
                out.append(meta)
        return out

    @Property("QVariantList", notify=listsChanged)
    def recentModules(self) -> list[dict[str, Any]]:
        return self._metas(self._settings.recents())

    @Property("QVariantList", notify=listsChanged)
    def favoriteModules(self) -> list[dict[str, Any]]:
        return self._metas(self._settings.favorites())

    @Slot(str)
    def pushRecent(self, module_id: str) -> None:
        if registry.module(module_id) is None:
            return
        self._settings.push_recent(module_id)
        self.listsChanged.emit()

    @Slot(str, result=bool)
    def toggleFavorite(self, module_id: str) -> bool:
        if registry.module(module_id) is None:
            return False
        state = self._settings.toggle_favorite(module_id)
        self.listsChanged.emit()
        return state

    @Slot(str, result=bool)
    def isFavorite(self, module_id: str) -> bool:
        return module_id in self._settings.favorites()

    @Slot(str)
    def copy(self, text: str) -> None:
        QGuiApplication.clipboard().setText(text)

    @Slot()
    def clearRecents(self) -> None:
        self._settings.set("recents", "[]")
        self.listsChanged.emit()
