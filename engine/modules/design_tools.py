"""Design: color conversion, contrast, palettes and glass specs."""

from __future__ import annotations

import colorsys
import re
from typing import Any

from ..schema import Field, Module, error, kv, listout, note, opts, swatches, text, value

HEX_RE = re.compile(r"^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
RGB_RE = re.compile(r"rgba?\(\s*(\d{1,3})\s*[, ]\s*(\d{1,3})\s*[, ]\s*(\d{1,3})", re.I)
HSL_RE = re.compile(r"hsla?\(\s*(\d{1,3})(?:deg)?\s*[, ]\s*(\d{1,3})%\s*[, ]\s*(\d{1,3})%", re.I)


def parse_color(raw: str) -> tuple[int, int, int] | None:
    s = (raw or "").strip()
    m = HEX_RE.match(s)
    if m:
        body = m.group(1)
        if len(body) == 3:
            body = "".join(c * 2 for c in body)
        if len(body) == 8:
            body = body[:6]
        return int(body[0:2], 16), int(body[2:4], 16), int(body[4:6], 16)
    m = RGB_RE.match(s)
    if m:
        return tuple(max(0, min(255, int(x))) for x in m.groups())  # type: ignore[return-value]
    m = HSL_RE.match(s)
    if m:
        r, g, b = colorsys.hls_to_rgb(int(m.group(1)) / 360.0, int(m.group(3)) / 100.0, int(m.group(2)) / 100.0)
        return round(r * 255), round(g * 255), round(b * 255)
    return None


def to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def to_hsl(rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    r, g, b = (c / 255.0 for c in rgb)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return round(h * 360) % 360, round(s * 100), round(l * 100)


def luminance(rgb: tuple[int, int, int]) -> float:
    def channel(c: int) -> float:
        x = c / 255.0
        return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    la, lb = luminance(a), luminance(b)
    lighter, darker = max(la, lb), min(la, lb)
    return (lighter + 0.05) / (darker + 0.05)


class ColorConverter(Module):
    id = "color"
    category = "design"
    title = "Color Converter"
    subtitle = "HEX, RGB and HSL in sync"
    icon = "droplet"
    keywords = ("color", "colour", "hex", "rgb", "hsl", "convert", "picker", "swatch", "tint")
    fields = (
        Field("color", "color", "Color", default="#3A6DF0", hint="HEX, rgb() or hsl() all accepted"),
    )

    @classmethod
    def run(cls, v: dict[str, Any]) -> list[dict[str, Any]]:
        rgb = parse_color(str(v["color"]))
        if rgb is None:
            return [error(f"“{v['color']}” is not a color. Try #3A6DF0 or rgb(58,109,240).")]
        hex_color = to_hex(rgb)
        h, s, l = to_hsl(rgb)
        return [
            swatches("Preview", [hex_color]),
            kv(
                "Formats",
                [
                    ("HEX", hex_color),
                    ("HEX (lower)", hex_color.lower()),
                    ("RGB", f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"),
                    ("HSL", f"hsl({h}, {s}%, {l}%)"),
                ],
            ),
            kv(
                "Channels",
                [
                    ("Red", rgb[0]),
                    ("Green", rgb[1]),
                    ("Blue", rgb[2]),
                    ("Luminance", f"{luminance(rgb):.3f}"),
                ],
            ),
            listout(
                "Tints & shades",
                [to_hex(hsl_to_rgb(h, s, pct)) for pct in (90, 75, 60, 40, 25, 12)],
            ),
        ]


def hsl_to_rgb(h: int, s: int, l: int) -> tuple[int, int, int]:
    r, g, b = colorsys.hls_to_rgb(h / 360.0, l / 100.0, s / 100.0)
    return round(r * 255), round(g * 255), round(b * 255)


class ContrastChecker(Module):
    id = "contrast"
    category = "design"
    title = "Contrast Checker"
    subtitle = "WCAG AA and AAA, honestly"
    icon = "contrast"
    keywords = ("contrast", "wcag", "accessibility", "a11y", "ratio", "readability", "aa", "aaa", "luminance")
    fields = (
        Field("foreground", "color", "Text", default="#111111"),
        Field("background", "color", "Background", default="#F4F1EA"),
    )

    @classmethod
    def run(cls, v: dict[str, Any]) -> list[dict[str, Any]]:
        fg = parse_color(str(v["foreground"]))
        bg = parse_color(str(v["background"]))
        if fg is None or bg is None:
            return [error("Both fields need a color like #111111.")]
        ratio = contrast_ratio(fg, bg)
        aa = ratio >= 4.5
        aal = ratio >= 3.0
        aaa = ratio >= 7.0
        aaal = ratio >= 4.5

        def badge(ok: bool) -> str:
            return "pass" if ok else "fail"

        return [
            value("Ratio", f"{ratio:.2f}:1"),
            swatches("Pair", [to_hex(fg), to_hex(bg)], caption="text · background"),
            kv(
                "WCAG",
                [
                    ("AA normal", badge(aa)),
                    ("AA large", badge(aal)),
                    ("AAA normal", badge(aaa)),
                    ("AAA large", badge(aaal)),
                ],
            ),
            {"type": "meter", "label": "Headroom", "ratio": min(1.0, ratio / 21.0), "caption": f"{ratio:.2f} of 21"},
            note(
                "Comfortable for long reading."
                if ratio >= 7
                else "Fine for headings and UI labels."
                if ratio >= 4.5
                else "Only large text — consider darkening."
                if ratio >= 3
                else "Below every threshold; pick a stronger pair."
            ),
        ]


class PaletteBuilder(Module):
    id = "palette"
    category = "design"
    title = "Palette Builder"
    subtitle = "One color, five moves"
    icon = "palette"
    keywords = ("palette", "harmony", "complementary", "analogous", "triadic", "tetradic", "scheme", "colors")
    fields = (
        Field("color", "color", "Base", default="#C2553F"),
        Field(
            "harmony",
            "select",
            "Harmony",
            default="analogous",
            options=opts(
                ("analogous", "Analogous"),
                ("complementary", "Complementary"),
                ("split", "Split complementary"),
                ("triadic", "Triadic"),
                ("tetradic", "Tetradic"),
                ("mono", "Monochrome ramp"),
            ),
        ),
    )

    @classmethod
    def run(cls, v: dict[str, Any]) -> list[dict[str, Any]]:
        rgb = parse_color(str(v["color"]))
        if rgb is None:
            return [error("Base needs a color like #C2553F.")]
        h, s, l = to_hsl(rgb)
        harmony = v["harmony"]
        colors: list[str] = []
        if harmony == "mono":
            colors = [to_hex(hsl_to_rgb(h, s, pct)) for pct in (16, 32, 50, 68, 84)]
        else:
            offsets = {
                "analogous": (-30, 0, 30),
                "complementary": (0, 180),
                "split": (0, 150, 210),
                "triadic": (0, 120, 240),
                "tetradic": (0, 90, 180, 270),
            }[harmony]
            for offset in offsets:
                colors.append(to_hex(hsl_to_rgb((h + offset) % 360, s, l)))
        return [
            swatches(harmony.replace("_", " ").capitalize(), colors, caption=" · ".join(colors)),
            listout("Hex values", colors),
            kv(
                "Base",
                [
                    ("HEX", to_hex(rgb)),
                    ("Hue", f"{h}°"),
                    ("Saturation", f"{s}%"),
                    ("Lightness", f"{l}%"),
                    ("Spread", f"{len(colors)} colors"),
                ],
            ),
        ]


class GlassTuner(Module):
    id = "glass"
    category = "design"
    title = "Glass Tuner"
    subtitle = "Blur, tint and shadow — copy the CSS"
    icon = "layers"
    keywords = ("glass", "glassmorphism", "blur", "backdrop", "frosted", "translucent", "css", "shadow", "material")
    fields = (
        Field(
            "theme",
            "select",
            "Theme",
            default="light",
            options=opts(("light", "Light"), ("dark", "Dark")),
        ),
        Field("blur", "slider", "Blur", default=28, min=0, max=64, step=1),
        Field("tint", "slider", "Tint opacity %", default=18, min=0, max=60, step=1),
        Field("radius", "slider", "Corner radius", default=20, min=0, max=40, step=1),
        Field("shadow", "slider", "Shadow", default=28, min=0, max=80, step=1),
    )

    @classmethod
    def run(cls, v: dict[str, Any]) -> list[dict[str, Any]]:
        dark = v["theme"] == "dark"
        blur = int(v["blur"])
        tint = int(v["tint"]) / 100.0
        radius = int(v["radius"])
        shadow = int(v["shadow"])
        tint_rgb = "255, 255, 255" if not dark else "12, 12, 14"
        edge = "rgba(255, 255, 255, 0.55)" if not dark else "rgba(255, 255, 255, 0.14)"
        shade = "rgba(15, 18, 24, 0.16)" if not dark else "rgba(0, 0, 0, 0.5)"
        css = (
            f"background: rgba({tint_rgb}, {tint:.2f});\n"
            f"backdrop-filter: blur({blur}px) saturate(180%);\n"
            f"-webkit-backdrop-filter: blur({blur}px) saturate(180%);\n"
            f"border: 1px solid {edge};\n"
            f"border-radius: {radius}px;\n"
            f"box-shadow: 0 {shadow}px {shadow * 2}px {shade};"
        )
        qml = (
            f"MultiEffect {{\n"
            f"    blurEnabled: true; blur: {blur / 64:.2f}\n"
            f"    maskEnabled: true; radius: {radius}\n"
            f"}}\n"
            f"Rectangle {{ color: \"rgba({tint_rgb}, {tint:.2f})\"; radius: {radius} }}"
        )
        return [
            text("CSS", css, mono=True),
            kv(
                "Readout",
                [
                    ("Blur", f"{blur} px"),
                    ("Tint", f"{tint * 100:.0f}%"),
                    ("Radius", f"{radius} px"),
                    ("Shadow", f"0 {shadow}px {shadow * 2}px"),
                ],
            ),
            text("QML equivalent", qml, mono=True),
            note("Push blur up on large surfaces and down on small chips — weight follows size."),
        ]
