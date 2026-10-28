"""Build ``assets/prism.ico`` from ``assets/app-icon.svg``.

Qt can write a single-image ICO, but Windows picks the best size from the
multi-image container — so we assemble one ourselves with PNG payloads (valid
since Vista) at every size Explorer, the taskbar and Alt-Tab ask for.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

from PySide6.QtCore import QBuffer, QRectF, Qt
from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "assets" / "app-icon.svg"
TARGET = ROOT / "assets" / "prism.ico"
SIZES = (16, 24, 32, 48, 64, 128, 256)


def render(renderer: QSvgRenderer, side: int) -> bytes:
    image = QImage(side, side, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
    renderer.render(painter, QRectF(0, 0, side, side))
    painter.end()

    buffer = QBuffer()
    buffer.open(QBuffer.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    buffer.close()
    return bytes(buffer.data())


def build() -> Path:
    renderer = QSvgRenderer(str(SOURCE))
    if not renderer.isValid():
        raise SystemExit(f"cannot read {SOURCE}")

    payloads = [(side, render(renderer, side)) for side in SIZES]

    header = struct.pack("<HHH", 0, 1, len(payloads))
    offset = len(header) + 16 * len(payloads)
    entries, blobs = [], []
    for side, data in payloads:
        entries.append(
            struct.pack(
                "<BBBBHHII",
                0 if side >= 256 else side,
                0 if side >= 256 else side,
                0,
                0,
                1,
                32,
                len(data),
                offset,
            )
        )
        blobs.append(data)
        offset += len(data)

    TARGET.write_bytes(header + b"".join(entries) + b"".join(blobs))
    return TARGET


def main() -> int:
    app = QGuiApplication.instance() or QGuiApplication([])  # noqa: F841 - QPainter needs it
    target = build()
    print(f"{target} {target.stat().st_size // 1024} KB ({len(SIZES)} sizes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
