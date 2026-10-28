"""Tinted SVG icons for QML.

Qt's ``MultiEffect.colorization`` silently no-ops on some rendering backends,
which left every glyph in its raw asset colour (invisible in dark mode).  We
rasterise and tint the SVGs ourselves instead: the result is identical under
the offscreen rasteriser, on the GPU, and inside a PyInstaller bundle.

QML asks for ``image://prism-icon/<name>/<rrggbb>/<pixels>`` and always gets a
ready-to-draw bitmap, cached per colour and size.
"""

from __future__ import annotations

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QImage, QPainter
from PySide6.QtQuick import QQuickImageProvider
from PySide6.QtSvg import QSvgRenderer

from .paths import resource

MAX_PIXELS = 256
CACHE_LIMIT = 512


class IconProvider(QQuickImageProvider):
    """Renders a monochrome SVG glyph in an arbitrary colour."""

    def __init__(self) -> None:
        super().__init__(QQuickImageProvider.ImageType.Image)
        self._cache: dict[tuple[str, str, int], QImage] = {}

    def requestImage(self, image_id: str, size: QSize, requested: QSize) -> QImage:  # noqa: N802 - Qt API
        name, colour, pixels = self._parse(image_id)
        side = max(8, min(MAX_PIXELS, pixels or requested.width() or 32))
        key = (name, colour, side)
        cached = self._cache.get(key)
        if cached is not None:
            size.setWidth(cached.width())
            size.setHeight(cached.height())
            return cached

        image = self._render(name, colour, side)
        if len(self._cache) > CACHE_LIMIT:
            self._cache.clear()
        self._cache[key] = image
        size.setWidth(image.width())
        size.setHeight(image.height())
        return image

    @staticmethod
    def _parse(image_id: str) -> tuple[str, str, int]:
        parts = image_id.split("/")
        name = parts[0] or "spark"
        colour = parts[1] if len(parts) > 1 and parts[1] else "14161a"
        try:
            pixels = int(parts[2]) if len(parts) > 2 else 0
        except ValueError:
            pixels = 0
        return name, colour, pixels

    @staticmethod
    def _render(name: str, colour: str, side: int) -> QImage:
        painter = None
        image = QImage(side, side, QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)
        renderer = QSvgRenderer(resource("assets", "icons", f"{name}.svg"))
        if renderer.isValid():
            painter = QPainter(image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            renderer.render(painter, QRectF(0, 0, side, side))
            # Recolour every painted pixel, keeping the glyph's alpha.
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
            painter.fillRect(image.rect(), QColor(f"#{colour}"))
            painter.end()
        image.setDevicePixelRatio(2.0)
        return image
