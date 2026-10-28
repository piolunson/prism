"""Converters: units, number bases, data sizes, roman numerals."""

from __future__ import annotations

from typing import Any

from ..schema import Field, Module, error, fmt_number, kv, listout, note, opts, value

LENGTH = {
    "m": ("Meter", 1.0),
    "km": ("Kilometer", 1000.0),
    "cm": ("Centimeter", 0.01),
    "mm": ("Millimeter", 0.001),
    "um": ("Micrometer", 1e-6),
    "nm": ("Nanometer", 1e-9),
    "in": ("Inch", 0.0254),
    "ft": ("Foot", 0.3048),
    "yd": ("Yard", 0.9144),
    "mi": ("Mile", 1609.344),
    "nmi": ("Nautical mile", 1852.0),
}

MASS = {
    "kg": ("Kilogram", 1.0),
    "g": ("Gram", 0.001),
    "mg": ("Milligram", 1e-6),
    "t": ("Metric ton", 1000.0),
    "lb": ("Pound", 0.45359237),
    "oz": ("Ounce", 0.028349523125),
    "st": ("Stone", 6.35029318),
}

AREA = {
    "m2": ("Square meter", 1.0),
    "km2": ("Square kilometer", 1e6),
    "cm2": ("Square centimeter", 1e-4),
    "ha": ("Hectare", 10000.0),
    "acre": ("Acre", 4046.8564224),
    "ft2": ("Square foot", 0.09290304),
    "in2": ("Square inch", 0.00064516),
    "mi2": ("Square mile", 2589988.110336),
}

VOLUME = {
    "l": ("Liter", 1.0),
    "ml": ("Milliliter", 0.001),
    "m3": ("Cubic meter", 1000.0),
    "cm3": ("Cubic centimeter", 0.001),
    "ft3": ("Cubic foot", 28.316846592),
    "gal": ("US gallon", 3.785411784),
    "qt": ("US quart", 0.946352946),
    "pt": ("US pint", 0.473176473),
    "cup": ("US cup", 0.2365882365),
    "floz": ("US fluid ounce", 0.0295735295625),
    "tbsp": ("Tablespoon", 0.01478676478125),
    "tsp": ("Teaspoon", 0.00492892159375),
}

SPEED = {
    "ms": ("Meters / second", 1.0),
    "kmh": ("Kilometers / hour", 1.0 / 3.6),
    "mph": ("Miles / hour", 0.44704),
    "kn": ("Knot", 1852.0 / 3600.0),
    "fts": ("Feet / second", 0.3048),
}

TEMPERATURE = ("c", "f", "k")

DIMENSIONS: dict[str, tuple[str, dict[str, tuple[str, float]]]] = {
    "length": ("Length", LENGTH),
    "mass": ("Mass", MASS),
    "temperature": ("Temperature", {}),
    "area": ("Area", AREA),
    "volume": ("Volume", VOLUME),
    "speed": ("Speed", SPEED),
}


def _temp_options() -> tuple[dict[str, str], ...]:
    return opts(("c", "Celsius (°C)"), ("f", "Fahrenheit (°F)"), ("k", "Kelvin (K)"))


def _to_celsius(v: float, unit: str) -> float:
    if unit == "f":
        return (v - 32.0) * 5.0 / 9.0
    if unit == "k":
        return v - 273.15
    return v


def _from_celsius(c: float, unit: str) -> float:
    if unit == "f":
        return c * 9.0 / 5.0 + 32.0
    if unit == "k":
        return c + 273.15
    return c


class UnitConverter(Module):
    id = "unit"
    category = "converters"
    title = "Unit Converter"
    subtitle = "Length, mass, temperature, area, volume, speed"
    icon = "ruler"
    keywords = (
        "unit",
        "convert",
        "length",
        "distance",
        "mass",
        "weight",
        "temperature",
        "celsius",
        "fahrenheit",
        "kelvin",
        "area",
        "volume",
        "speed",
        "mph",
        "kmh",
        "inch",
        "cm",
        "feet",
        "meters",
        "kg",
        "lb",
        "ounce",
        "gallon",
        "liter",
    )
    fields = (
        Field(
            "dim",
            "select",
            "Dimension",
            default="length",
            options=tuple(
                {"value": key, "label": label} for key, (label, _) in DIMENSIONS.items()
            ),
        ),
        Field("amount", "number", "Value", default=1.0, step=1.0),
        Field("from", "select", "From", default="m", dynamic=True),
        Field("to", "select", "To", default="ft", dynamic=True),
    )

    @classmethod
    def options_for(cls, key: str, values: dict[str, Any]) -> tuple[dict[str, str], ...] | None:
        if key not in ("from", "to"):
            return None
        dim = values.get("dim", "length")
        if dim == "temperature":
            return _temp_options()
        table = DIMENSIONS.get(dim, DIMENSIONS["length"])[1]
        return tuple({"value": u, "label": label} for u, (label, _) in table.items())

    @classmethod
    def coerce(cls, values: dict[str, Any]) -> dict[str, Any]:
        clean = super().coerce(values)
        # Keep from/to inside the chosen dimension with sensible defaults.
        dim = clean.get("dim", "length")
        if dim == "temperature":
            pairs = {"from": "c", "to": "f"}
        elif dim == "length":
            pairs = {"from": "m", "to": "ft"}
        elif dim == "mass":
            pairs = {"from": "kg", "to": "lb"}
        elif dim == "area":
            pairs = {"from": "m2", "to": "ft2"}
        elif dim == "volume":
            pairs = {"from": "l", "to": "gal"}
        else:
            pairs = {"from": "kmh", "to": "mph"}
        options = {o["value"] for o in (cls.options_for("from", clean) or ())}
        for key, fallback in pairs.items():
            if clean.get(key) not in options:
                clean[key] = fallback if fallback in options else next(iter(options))
        return clean

    @classmethod
    def run(cls, v: dict[str, Any]) -> list[dict[str, Any]]:
        dim = v["dim"]
        amount = float(v["amount"])
        src, dst = v["from"], v["to"]
        if dim == "temperature":
            result = _from_celsius(_to_celsius(amount, src), dst)
            labels = {"c": "°C", "f": "°F", "k": "K"}
            return [
                value("Result", f"{fmt_number(result)} {labels[dst]}"),
                kv(
                    "Both sides",
                    [
                        ("Input", f"{fmt_number(amount)} {labels[src]}"),
                        ("Output", f"{fmt_number(result)} {labels[dst]}"),
                    ],
                ),
            ]
        table = DIMENSIONS[dim][1]
        src_factor = table[src][1]
        dst_factor = table[dst][1]
        result = amount * src_factor / dst_factor
        return [
            value("Result", f"{fmt_number(result)} {dst}"),
            kv(
                "Conversion",
                [
                    ("From", f"{fmt_number(amount)} {src}"),
                    ("To", f"{fmt_number(result)} {dst}"),
                    ("Rate", f"1 {src} = {fmt_number(src_factor / dst_factor, 8)} {dst}"),
                ],
            ),
            listout(
                f"All {DIMENSIONS[dim][0].lower()} units",
                [
                    f"{fmt_number(amount * src_factor / factor)}  {unit}"
                    for unit, (_, factor) in table.items()
                    if unit != src
                ],
            ),
        ]


class NumberBase(Module):
    id = "base"
    category = "converters"
    title = "Number Base"
    subtitle = "Binary, octal, decimal and hex in one view"
    icon = "hash"
    keywords = ("binary", "hex", "octal", "decimal", "base", "radix", "bits", "0x", "0b", "bitwise")
    fields = (
        Field(
            "input",
            "text",
            "Value",
            default="255",
            placeholder="42, 0b1010, 0o52, 0xFF",
            hint="Prefix with 0b, 0o or 0x to pin the base",
            mono=True,
        ),
        Field(
            "base",
            "select",
            "Input base",
            default="auto",
            options=opts(
                ("auto", "Detect"), ("2", "Binary (2)"), ("8", "Octal (8)"),
                ("10", "Decimal (10)"), ("16", "Hex (16)"),
            ),
        ),
    )

    @classmethod
    def run(cls, v: dict[str, Any]) -> list[dict[str, Any]]:
        raw = str(v["input"]).strip().replace("_", "").replace(" ", "")
        if not raw:
            return [note("Type a number to see it in every base.")]
        base = v["base"]
        sign = -1 if raw.startswith("-") else 1
        body = raw.lstrip("+-")
        try:
            if base == "auto":
                lowered = body.lower()
                if lowered.startswith("0x"):
                    n, detected = int(body[2:], 16), "hex"
                elif lowered.startswith("0b"):
                    n, detected = int(body[2:], 2), "binary"
                elif lowered.startswith("0o"):
                    n, detected = int(body[2:], 8), "octal"
                else:
                    n, detected = int(body, 10), "decimal"
            else:
                n = int(body, int(base))
                detected = {"2": "binary", "8": "octal", "10": "decimal", "16": "hex"}[base]
            n *= sign
        except ValueError:
            return [error(f"“{v['input']}” is not a valid integer in {base if base != 'auto' else 'this'} base.")]
        if abs(n) > 2**128:
            return [error("That number is too large to convert (limit 2¹²⁸).")]
        bits = format(n, "016b") if n >= 0 else "—"
        return [
            value("Decimal", f"{n:,}"),
            kv(
                "Every base",
                [
                    ("Binary", f"0b{format(n, 'b')}"),
                    ("Octal", f"0o{format(n, 'o')}"),
                    ("Decimal", str(n)),
                    ("Hex", f"0x{format(n, 'X')}"),
                    ("Detected", detected),
                ],
            ),
            kv(
                "Bit view",
                [("16-bit", bits), ("Set bits", str(bin(abs(n)).count("1"))), ("Bytes", str((abs(n).bit_length() + 7) // 8))],
            ),
        ]


DATA_UNITS = {
    "b": ("Byte", 1.0),
    "kb": ("Kilobyte (1000)", 1000.0),
    "kib": ("Kibibyte (1024)", 1024.0),
    "mb": ("Megabyte (1000²)", 1e6),
    "mib": ("Mebibyte (1024²)", 1024.0**2),
    "gb": ("Gigabyte (1000³)", 1e9),
    "gib": ("Gibibyte (1024³)", 1024.0**3),
    "tb": ("Terabyte (1000⁴)", 1e12),
    "tib": ("Tebibyte (1024⁴)", 1024.0**4),
}


class DataSize(Module):
    id = "data"
    category = "converters"
    title = "Data Size"
    subtitle = "Bytes, SI and binary prefixes"
    icon = "drive"
    keywords = ("bytes", "kb", "mb", "gb", "tb", "kib", "mib", "storage", "file size", "bits")
    fields = (
        Field("amount", "number", "Value", default=1.0, min=0.0, step=1.0),
        Field(
            "from",
            "select",
            "From",
            default="mb",
            options=tuple({"value": u, "label": l} for u, (l, _) in DATA_UNITS.items()),
        ),
        Field(
            "to",
            "select",
            "To",
            default="mib",
            options=tuple({"value": u, "label": l} for u, (l, _) in DATA_UNITS.items()),
        ),
    )

    @classmethod
    def run(cls, v: dict[str, Any]) -> list[dict[str, Any]]:
        amount = float(v["amount"])
        raw = amount * DATA_UNITS[v["from"]][1]
        result = raw / DATA_UNITS[v["to"]][1]
        return [
            value("Result", f"{fmt_number(result)} {v['to'].upper()}"),
            kv(
                "Raw size",
                [
                    ("Bytes", fmt_number(raw)),
                    ("Bits", fmt_number(raw * 8, 8)),
                    ("Difference", f"{((DATA_UNITS[v['to']][1] / DATA_UNITS[v['from']][1]) - 1) * 100:+,.4g}%"),
                ],
            ),
            listout(
                "In every unit",
                [
                    f"{fmt_number(raw / factor)}  {u.upper()}"
                    for u, (_, factor) in DATA_UNITS.items()
                ],
            ),
        ]


ROMAN_MAP = (
    (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
    (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
    (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
)
ROMAN_VALUES = {s: n for n, s in ROMAN_MAP}


def to_roman(n: int) -> str:
    out = []
    for num, sym in ROMAN_MAP:
        while n >= num:
            out.append(sym)
            n -= num
    return "".join(out)


def from_roman(s: str) -> int:
    total = 0
    i = 0
    upper = s.upper()
    while i < len(upper):
        two = upper[i : i + 2]
        if two in ROMAN_VALUES and len(two) == 2:
            total += ROMAN_VALUES[two]
            i += 2
            continue
        one = upper[i]
        if one not in ROMAN_VALUES:
            raise ValueError(one)
        total += ROMAN_VALUES[one]
        i += 1
    return total


class RomanNumerals(Module):
    id = "roman"
    category = "converters"
    title = "Roman Numerals"
    subtitle = "Both directions, validated"
    icon = "column"
    keywords = ("roman", "numeral", "latin", "mmxxv", "iv", "xl", "convert")
    fields = (
        Field(
            "input",
            "text",
            "Number or numeral",
            default="2026",
            placeholder="1984 or MCMLXXXIV",
            mono=True,
        ),
    )

    @classmethod
    def run(cls, v: dict[str, Any]) -> list[dict[str, Any]]:
        raw = str(v["input"]).strip()
        if not raw:
            return [note("Type a number (1–3999) or a numeral like MCMLXXXIV.")]
        if raw.lstrip("-").isdigit():
            n = int(raw)
            if not 0 < n < 4000:
                return [error("Roman numerals cover 1 – 3999.")]
            roman = to_roman(n)
            return [
                value("Numeral", roman),
                kv("Details", [("Value", n), ("Length", f"{len(roman)} symbols"), ("Reversed", roman[::-1])]),
            ]
        try:
            n = from_roman(raw)
        except ValueError as exc:
            return [error(f"“{exc}” is not a Roman numeral symbol.")]
        canonical = to_roman(n) if 0 < n < 4000 else None
        if canonical is None:
            return [error("That numeral is out of range (1 – 3999).")]
        outputs = [
            value("Value", n),
            kv("Details", [("Numeral", canonical), ("Canonical", "yes" if canonical == raw.upper() else "no, normalised")]),
        ]
        if canonical != raw.upper():
            outputs.append(note(f"Normalised to {canonical}."))
        return outputs
