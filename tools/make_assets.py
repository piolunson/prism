"""Generate every static graphic Prism ships.

The icons are 24×24 stroke drawings tinted at runtime, so they are written once
here with a fixed ink colour and colourised by QML's MultiEffect.  Run with::

    .venv/Scripts/python.exe tools/make_assets.py
"""

from __future__ import annotations

import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ICONS = ROOT / "assets" / "icons"
GRAPHICS = ROOT / "assets" / "graphics"

INK = "#14161A"
PAPER = "#F4F1EA"

STROKE_ICONS: dict[str, str] = {
    # categories -------------------------------------------------------------
    "converters": '<path d="M4 8h13l-3.5-3.5"/><path d="M20 16H7l3.5 3.5"/>',
    "math": '<path d="M17.5 5.5H6.5l6 6.5-6 6.5h11"/>',
    "text": '<path d="M4 6h16M4 12h11M4 18h13"/>',
    "time": '<circle cx="12" cy="12" r="8.2"/><path d="M12 7.2V12l3.4 2"/>',
    "developer": '<path d="M9 7.5L4.5 12 9 16.5"/><path d="M15 7.5L19.5 12 15 16.5"/><path d="M13.4 5l-2.8 14"/>',
    "design": '<path d="M12 3.2l2.5 6.3 6.3 2.5-6.3 2.5L12 20.8l-2.5-6.3L3.2 12l6.3-2.5z"/>',
    # converters -------------------------------------------------------------
    "ruler": '<rect x="3" y="9" width="18" height="6" rx="1.6"/><path d="M7.5 9v3M11 9v3M14.5 9v3M18 9v3"/>',
    "hash": '<path d="M9.4 3.2L7.4 20.8M16.6 3.2l-2 17.6M4.2 9h16.6M3.2 15h16.6"/>',
    "drive": '<rect x="3" y="4.6" width="18" height="6.2" rx="2"/><rect x="3" y="13.2" width="18" height="6.2" rx="2"/><path d="M7 7.7h.01M7 16.3h.01"/>',
    "column": '<path d="M7 4.5h3.2v15H7zM13.8 4.5H17v15h-3.2z"/><path d="M4 20.5h16"/>',
    # math -------------------------------------------------------------------
    "calculator": '<rect x="4.6" y="3" width="14.8" height="18" rx="3"/><path d="M8 7.4h8"/><path d="M8.4 12h.01M12 12h.01M15.6 12h.01M8.4 16.2h.01M12 16.2h.01M15.6 16.2h.01"/>',
    "percent": '<path d="M18.4 5.6L5.6 18.4"/><circle cx="7.4" cy="7.4" r="2.3"/><circle cx="16.6" cy="16.6" r="2.3"/>',
    "bars": '<path d="M6 20V11.5M12 20V5.5M18 20v-5.8"/><path d="M3.6 20h16.8"/>',
    "parabola": '<path d="M3.2 19.4C7 4.6 17 4.6 20.8 19.4"/><path d="M12 4v16"/>',
    # text -------------------------------------------------------------------
    "type": '<path d="M5 19.2L12 4.8l7 14.4"/><path d="M8.4 14.2h7.2"/>',
    "chart": '<path d="M4 4.5v15h16"/><path d="M7 15.2l4-4.4 3.2 2.6 5-6"/>',
    "link": '<path d="M10.6 13.4l2.8-2.8"/><path d="M9.1 11l-1.9 1.9a3.6 3.6 0 005.1 5.1l1.9-1.9"/><path d="M14.9 13l1.9-1.9a3.6 3.6 0 00-5.1-5.1L9.8 7.9"/>',
    "pattern": '<path d="M8 4.2H4.8v15.6H8M16 4.2h3.2v15.6H16"/><path d="M10.6 10.4h2.8M10.6 13.6h2.8"/>',
    # time -------------------------------------------------------------------
    "clock": '<circle cx="12" cy="12" r="8.2"/><path d="M12 7.2V12l3.4 2"/>',
    "calendar": '<rect x="3.2" y="5.2" width="17.6" height="15.6" rx="3"/><path d="M3.2 10h17.6M8.4 3.2v4M15.6 3.2v4"/>',
    "globe": '<circle cx="12" cy="12" r="8.6"/><path d="M3.4 12h17.2"/><path d="M12 3.4c3.1 3.6 3.1 13.6 0 17.2M12 3.4c-3.1 3.6-3.1 13.6 0 17.2"/>',
    "hourglass": '<path d="M6.4 3.2h11.2M6.4 20.8h11.2"/><path d="M8.2 3.2v2.9c0 2.6 3.8 4.1 3.8 5.9s-3.8 3.3-3.8 5.9v2.9"/><path d="M15.8 3.2v2.9c0 2.6-3.8 4.1-3.8 5.9s3.8 3.3 3.8 5.9v2.9"/>',
    # developer --------------------------------------------------------------
    "braces": '<path d="M9.4 3.8C7.4 3.8 7 5.6 7 6.8v2.4c0 1.6-.9 2.2-2.2 2.8 1.3.6 2.2 1.2 2.2 2.8v2.4c0 1.2.4 3 2.4 3"/><path d="M14.6 3.8c2 0 2.4 1.8 2.4 3v2.4c0 1.6.9 2.2 2.2 2.8-1.3.6-2.2 1.2-2.2 2.8v2.4c0 1.2-.4 3-2.4 3"/>',
    "shuffle": '<path d="M3.6 7.4h4.2l8 9.2h4.4"/><path d="M3.6 16.6h4.2l2.6-3"/><path d="M17.4 4.6l3 2.8-3 2.8M17.4 13.8l3 2.8-3 2.8"/>',
    "fingerprint": '<path d="M12 4.6c-4.1 0-7.4 3.3-7.4 7.4v2.4"/><path d="M12 8.2c-2.1 0-3.8 1.7-3.8 3.8v5"/><path d="M12 11.6c-.5 0-.9.4-.9.9v6.9"/><path d="M15.8 12a3.8 3.8 0 00-3.8-3.8"/><path d="M19.4 13.4v1.4c0 1-.2 1.9-.6 2.8"/>',
    "tag": '<path d="M11.4 3.4H5.4a2 2 0 00-2 2v6a2 2 0 00.6 1.4l7 7a2 2 0 002.8 0l6-6a2 2 0 000-2.8l-7-7a2 2 0 00-1.4-.6z"/><path d="M7.6 7.6h.01"/>',
    # design -----------------------------------------------------------------
    "droplet": '<path d="M12 3.2s6 6.5 6 10.2a6 6 0 11-12 0C6 9.7 12 3.2 12 3.2z"/>',
    "contrast": '<circle cx="12" cy="12" r="8.6"/><path d="M12 3.4v17.2a8.6 8.6 0 000-17.2z" fill="currentColor" stroke="none"/>',
    "palette": '<path d="M12 3.2a8.8 8.8 0 000 17.6c1.7 0 2.1-1 1.4-1.9-.8-1 .1-2.3 1.4-2.3h1.7a4.3 4.3 0 004.3-4.3c0-5-4.2-9.1-8.8-9.1z"/><circle cx="8.2" cy="9.4" r="1.1" fill="currentColor" stroke="none"/><circle cx="12" cy="7.4" r="1.1" fill="currentColor" stroke="none"/><circle cx="15.8" cy="9.8" r="1.1" fill="currentColor" stroke="none"/>',
    "layers": '<path d="M12 3.2l8.6 4.9-8.6 4.9L3.4 8.1 12 3.2z"/><path d="M3.4 13.2l8.6 4.9 8.6-4.9"/>',
    # interface --------------------------------------------------------------
    "search": '<circle cx="11" cy="11" r="6.4"/><path d="M15.8 15.8l4.2 4.2"/>',
    "star": '<path d="M12 3.6l2.6 5.5 6 .9-4.3 4.2 1 6-5.3-2.9-5.3 2.9 1-6L3.4 10l6-.9z"/>',
    "star-filled": '<path d="M12 3.6l2.6 5.5 6 .9-4.3 4.2 1 6-5.3-2.9-5.3 2.9 1-6L3.4 10l6-.9z" fill="currentColor"/>',
    "sun": '<circle cx="12" cy="12" r="4.1"/><path d="M12 2.6v2.2M12 19.2v2.2M2.6 12h2.2M19.2 12h2.2M5.3 5.3l1.6 1.6M17.1 17.1l1.6 1.6M18.7 5.3l-1.6 1.6M6.9 17.1l-1.6 1.6"/>',
    "moon": '<path d="M20.2 14.6A8.6 8.6 0 019.4 3.8a8.6 8.6 0 1010.8 10.8z"/>',
    "gear": '<circle cx="12" cy="12" r="3.2"/><path d="M12 2.6v2.6M12 18.8v2.6M2.6 12h2.6M18.8 12h2.6M5.3 5.3l1.9 1.9M16.8 16.8l1.9 1.9M18.7 5.3l-1.9 1.9M7.2 16.8l-1.9 1.9"/>',
    "close": '<path d="M6.2 6.2l11.6 11.6M17.8 6.2L6.2 17.8"/>',
    "minimize": '<path d="M5 12h14"/>',
    "maximize": '<rect x="5" y="5" width="14" height="14" rx="2.2"/>',
    "restore": '<rect x="4" y="7.4" width="12.2" height="12.2" rx="2"/><path d="M8 7.4V5.2h12.2v12.2h-2.2"/>',
    "chevron-right": '<path d="M9.4 5l7 7-7 7"/>',
    "chevron-left": '<path d="M14.6 5l-7 7 7 7"/>',
    "chevron-down": '<path d="M5 9.4l7 7 7-7"/>',
    "arrow-left": '<path d="M20 12H4.4M10 6l-6 6 6 6"/>',
    "home": '<path d="M3.8 11.2L12 4l8.2 7.2"/><path d="M6.2 10v9.4h11.6V10"/>',
    "bolt": '<path d="M13.2 2.6L4.6 13.8h5.6l-1 7.6 8.6-11.2h-5.6z"/>',
    "copy": '<rect x="9" y="9" width="11.4" height="11.4" rx="2.4"/><path d="M15 5.6H6.4a2 2 0 00-2 2v8.6"/>',
    "check": '<path d="M4.4 12.4l4.8 4.8L19.6 6.8"/>',
    "spark": '<path d="M12 3.4l1.7 5.9 5.9 1.7-5.9 1.7L12 18.6l-1.7-5.9-5.9-1.7 5.9-1.7z"/>',
    "history": '<path d="M3.6 12a8.4 8.4 0 108.4-8.4c-3 0-5.6 1.5-7.1 3.8"/><path d="M3.2 4.6v4.2h4.2"/><path d="M12 7.8V12l3.4 2"/>',
    "info": '<circle cx="12" cy="12" r="8.6"/><path d="M12 10.8v5.6M12 7.6h.01"/>',
    "filter": '<path d="M3.6 5.6h16.8l-6.4 7.4v6.2l-4-2v-4.2z"/>',
}

FILLED = {"star-filled", "contrast"}

ICON_TEMPLATE = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" '
    'fill="none" stroke="{ink}" stroke-width="1.7" stroke-linecap="round" '
    'stroke-linejoin="round">\n  {body}\n</svg>\n'
)


def write_icons() -> None:
    ICONS.mkdir(parents=True, exist_ok=True)
    for name, body in STROKE_ICONS.items():
        body = body.replace("currentColor", INK)
        (ICONS / f"{name}.svg").write_text(
            ICON_TEMPLATE.format(ink=INK, body=body), encoding="utf-8"
        )


LOGO = """<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256" fill="none">
  <defs>
    <linearGradient id="sheen" x1="88" y1="88" x2="216" y2="216" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity="0.62"/>
      <stop offset="0.62" stop-color="#FFFFFF" stop-opacity="0.06"/>
      <stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="front"><rect x="88" y="88" width="128" height="128" rx="34"/></clipPath>
  </defs>
  <rect x="40" y="40" width="128" height="128" rx="34" fill="{ink}"/>
  <rect x="88" y="88" width="128" height="128" rx="34" fill="{ink}" fill-opacity="0.14"
        stroke="{ink}" stroke-opacity="0.92" stroke-width="6"/>
  <g clip-path="url(#front)">
    <path d="M88 156L216 118" stroke="{ink}" stroke-opacity="0.9" stroke-width="6" stroke-linecap="round"/>
    <path d="M88 186L216 152" stroke="{ink}" stroke-opacity="0.34" stroke-width="6" stroke-linecap="round"/>
    <rect x="88" y="88" width="128" height="128" fill="url(#sheen)"/>
  </g>
</svg>
"""

MARK = """<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none">
  <rect x="6" y="6" width="34" height="34" rx="10" fill="{ink}"/>
  <rect x="24" y="24" width="34" height="34" rx="10" fill="{ink}" fill-opacity="0.12"
        stroke="{ink}" stroke-width="2.6"/>
  <path d="M24 42L58 33" stroke="{ink}" stroke-width="2.6" stroke-linecap="round"/>
</svg>
"""


def write_logo() -> None:
    (ROOT / "assets" / "logo.svg").write_text(LOGO.format(ink=INK), encoding="utf-8")
    (ROOT / "assets" / "logo-dark.svg").write_text(LOGO.format(ink=PAPER), encoding="utf-8")
    (ROOT / "assets" / "mark.svg").write_text(MARK.format(ink=INK), encoding="utf-8")
    (ROOT / "assets" / "mark-dark.svg").write_text(MARK.format(ink=PAPER), encoding="utf-8")


WALLPAPER_LIGHT = """<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1000" viewBox="0 0 1600 1000">
  <defs>
    <radialGradient id="warm" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#F6C9A4" stop-opacity="0.95"/>
      <stop offset="0.55" stop-color="#F6C9A4" stop-opacity="0.42"/>
      <stop offset="1" stop-color="#F6C9A4" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="cool" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#A9C4EE" stop-opacity="0.92"/>
      <stop offset="0.55" stop-color="#A9C4EE" stop-opacity="0.38"/>
      <stop offset="1" stop-color="#A9C4EE" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="mint" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#B7DECB" stop-opacity="0.9"/>
      <stop offset="0.6" stop-color="#B7DECB" stop-opacity="0.3"/>
      <stop offset="1" stop-color="#B7DECB" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="lilac" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#D8C6EE" stop-opacity="0.85"/>
      <stop offset="0.6" stop-color="#D8C6EE" stop-opacity="0.28"/>
      <stop offset="1" stop-color="#D8C6EE" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="base" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#F7F3EC"/>
      <stop offset="0.55" stop-color="#F1EDE6"/>
      <stop offset="1" stop-color="#E9E6E1"/>
    </linearGradient>
  </defs>
  <rect width="1600" height="1000" fill="url(#base)"/>
  <ellipse cx="230" cy="180" rx="560" ry="430" fill="url(#warm)"/>
  <ellipse cx="1430" cy="140" rx="520" ry="400" fill="url(#cool)"/>
  <ellipse cx="1300" cy="880" rx="560" ry="420" fill="url(#mint)"/>
  <ellipse cx="180" cy="930" rx="520" ry="380" fill="url(#lilac)"/>
  <ellipse cx="800" cy="480" rx="640" ry="330" fill="url(#warm)" opacity="0.35"/>
</svg>
"""

WALLPAPER_DARK = """<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1000" viewBox="0 0 1600 1000">
  <defs>
    <radialGradient id="indigo" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#38428F" stop-opacity="0.85"/>
      <stop offset="0.55" stop-color="#38428F" stop-opacity="0.34"/>
      <stop offset="1" stop-color="#38428F" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="teal" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#1C6F73" stop-opacity="0.8"/>
      <stop offset="0.55" stop-color="#1C6F73" stop-opacity="0.3"/>
      <stop offset="1" stop-color="#1C6F73" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="plum" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#5E2450" stop-opacity="0.75"/>
      <stop offset="0.55" stop-color="#5E2450" stop-opacity="0.26"/>
      <stop offset="1" stop-color="#5E2450" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="amber" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#8A5A2B" stop-opacity="0.6"/>
      <stop offset="0.6" stop-color="#8A5A2B" stop-opacity="0.18"/>
      <stop offset="1" stop-color="#8A5A2B" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="base" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#08090C"/>
      <stop offset="0.5" stop-color="#0C0E13"/>
      <stop offset="1" stop-color="#101218"/>
    </linearGradient>
  </defs>
  <rect width="1600" height="1000" fill="url(#base)"/>
  <ellipse cx="240" cy="200" rx="600" ry="450" fill="url(#indigo)"/>
  <ellipse cx="1400" cy="180" rx="520" ry="420" fill="url(#teal)"/>
  <ellipse cx="1280" cy="900" rx="600" ry="440" fill="url(#plum)"/>
  <ellipse cx="200" cy="940" rx="520" ry="380" fill="url(#amber)"/>
</svg>
"""


def write_wallpapers() -> None:
    GRAPHICS.mkdir(parents=True, exist_ok=True)
    (GRAPHICS / "wallpaper-light.svg").write_text(WALLPAPER_LIGHT, encoding="utf-8")
    (GRAPHICS / "wallpaper-dark.svg").write_text(WALLPAPER_DARK, encoding="utf-8")


def write_noise() -> None:
    """A tiny alpha-noise tile: the grain that keeps glass from looking plasticky."""
    from PySide6.QtGui import QColor, QImage

    rng = random.Random(7)
    size = 128
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    for y in range(size):
        for x in range(size):
            value = rng.randint(0, 255)
            alpha = rng.randint(6, 22)
            image.setPixelColor(x, y, QColor(value, value, value, alpha))
    image.save(str(GRAPHICS / "noise.png"), "PNG")


def main() -> None:
    write_icons()
    write_logo()
    write_wallpapers()
    write_noise()
    print(f"icons: {len(STROKE_ICONS)}")
    print(f"assets written to {ROOT / 'assets'}")


if __name__ == "__main__":
    main()
