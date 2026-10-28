"""Declarative schema shared by every tool in Prism.

A module declares typed *fields* and returns typed *output blocks*.  The QML
layer renders both generically, so adding a tool never means writing new UI.
"""

from __future__ import annotations

from dataclasses import dataclass, field as dc_field
from typing import Any, ClassVar, Iterable


# --------------------------------------------------------------------------- #
# Fields
# --------------------------------------------------------------------------- #

FIELD_TYPES = (
    "number",
    "text",
    "textarea",
    "select",
    "toggle",
    "slider",
    "color",
)


@dataclass(frozen=True)
class Field:
    """One input control.

    ``visible_when`` is either ``None`` or ``{"key": <field>, "in": [values]}`` /
    ``{"key": <field>, "not": <value>}``.  The registry resolves it, so QML only
    ever sees a boolean ``visible``.
    """

    key: str
    type: str
    label: str
    default: Any = ""
    hint: str = ""
    placeholder: str = ""
    options: tuple[dict[str, Any], ...] = ()
    min: float | None = None
    max: float | None = None
    step: float | None = None
    rows: int = 3
    mono: bool = False
    dynamic: bool = False  # options come from Module.options_for()
    visible_when: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.type not in FIELD_TYPES:
            raise ValueError(f"unknown field type {self.type!r} on {self.key!r}")
        if not self.key:
            raise ValueError("field key must be non-empty")
        if self.type == "select" and not self.options and not self.dynamic:
            raise ValueError(f"select field {self.key!r} needs options or dynamic=True")
        if self.type in ("number", "slider") and self.default in ("", None):
            raise ValueError(f"numeric field {self.key!r} needs a default")

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "type": self.type,
            "label": self.label,
            "default": self.default,
            "hint": self.hint,
            "placeholder": self.placeholder,
            "options": [dict(o) for o in self.options],
            "min": self.min,
            "max": self.max,
            "step": self.step,
            "rows": self.rows,
            "mono": self.mono,
        }


@dataclass(frozen=True)
class Option:
    """Convenience builder for select options."""

    value: str
    label: str

    def to_dict(self) -> dict[str, str]:
        return {"value": self.value, "label": self.label}


def opts(*pairs: tuple[str, str]) -> tuple[dict[str, str], ...]:
    """``opts(("c", "Celsius"), ("f", "Fahrenheit"))`` -> tuple of option dicts."""
    return tuple({"value": v, "label": l} for v, l in pairs)


def simple_opts(values: Iterable[str]) -> tuple[dict[str, str], ...]:
    return tuple({"value": v, "label": v} for v in values)


# --------------------------------------------------------------------------- #
# Output blocks
# --------------------------------------------------------------------------- #

OUTPUT_TYPES = ("value", "kv", "list", "text", "note", "error", "swatches", "meter")


def value(label: str, text: Any, *, mono: bool = True, hint: str = "") -> dict[str, Any]:
    return {"type": "value", "label": label, "text": _fmt(text), "mono": mono, "hint": hint}


def kv(label: str, pairs: Iterable[tuple[str, Any]], *, mono: bool = True) -> dict[str, Any]:
    return {
        "type": "kv",
        "label": label,
        "pairs": [{"k": k, "v": _fmt(v)} for k, v in pairs],
        "mono": mono,
    }


def listout(label: str, items: Iterable[Any], *, mono: bool = True) -> dict[str, Any]:
    return {"type": "list", "label": label, "items": [_fmt(i) for i in items], "mono": mono}


def text(label: str, body: Any, *, mono: bool = True) -> dict[str, Any]:
    return {"type": "text", "label": label, "text": _fmt(body) if not isinstance(body, str) else body, "mono": mono}


def note(message: str) -> dict[str, Any]:
    return {"type": "note", "text": message}


def error(message: str) -> dict[str, Any]:
    return {"type": "error", "text": message}


def swatches(label: str, colors: Iterable[str], *, caption: str = "") -> dict[str, Any]:
    return {
        "type": "swatches",
        "label": label,
        "colors": [c for c in colors],
        "caption": caption,
    }


def meter(label: str, ratio: float, caption: str = "") -> dict[str, Any]:
    return {"type": "meter", "label": label, "ratio": max(0.0, min(1.0, ratio)), "caption": caption}


def fmt_number(value: float, sig: int = 6) -> str:
    """Readable numbers: commas for normal magnitudes, science only at extremes."""
    if value != value:
        return "—"
    if value in (float("inf"), float("-inf")):
        return "∞" if value > 0 else "−∞"
    if value == 0:
        return "0"
    magnitude = abs(value)
    if magnitude >= 1e12 or magnitude < 1e-4:
        return f"{value:.4e}"
    import math as _math

    decimals = sig - 1 - int(_math.floor(_math.log10(magnitude)))
    decimals = max(0, min(10, decimals))
    text = f"{value:,.{decimals}f}"
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def _fmt(v: Any) -> str:
    if isinstance(v, float):
        if v != v:  # NaN
            return "—"
        if v == int(v) and abs(v) < 1e15:
            return str(int(v))
        return f"{v:.10g}"
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v)


# --------------------------------------------------------------------------- #
# Module
# --------------------------------------------------------------------------- #

CATEGORY_IDS = ("converters", "math", "text", "time", "developer", "design")


class Module:
    """Base class for a tool.  Subclasses set class attributes and implement run()."""

    id: ClassVar[str] = ""
    category: ClassVar[str] = ""
    title: ClassVar[str] = ""
    subtitle: ClassVar[str] = ""
    icon: ClassVar[str] = "spark"
    keywords: ClassVar[tuple[str, ...]] = ()
    view: ClassVar[str] = "form"  # "form" | "calculator"
    fields: ClassVar[tuple[Field, ...]] = ()

    # -- metadata ----------------------------------------------------------- #

    @classmethod
    def meta(cls) -> dict[str, Any]:
        return {
            "id": cls.id,
            "category": cls.category,
            "title": cls.title,
            "subtitle": cls.subtitle,
            "icon": cls.icon,
            "keywords": list(cls.keywords),
            "view": cls.view,
            "search": " ".join(
                [cls.title.lower(), cls.category.lower(), cls.subtitle.lower(), *cls.keywords]
            ).lower(),
        }

    @classmethod
    def defaults(cls) -> dict[str, Any]:
        return {f.key: f.default for f in cls.fields}

    # -- behaviour ---------------------------------------------------------- #

    @classmethod
    def options_for(cls, key: str, values: dict[str, Any]) -> tuple[dict[str, str], ...] | None:
        """Dynamic options for a select field.  ``None`` means "use the declared ones"."""
        return None

    @classmethod
    def visible_for(cls, field: Field, values: dict[str, Any]) -> bool:
        cond = field.visible_when
        if not cond:
            return True
        current = values.get(cond.get("key", ""), None)
        if "in" in cond:
            return current in cond["in"]
        if "not" in cond:
            return current != cond["not"]
        if "equals" in cond:
            return current == cond["equals"]
        return True

    @classmethod
    def coerce(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Validate and repair incoming values so run() can trust them."""
        out: dict[str, Any] = {}
        for f in cls.fields:
            raw = values.get(f.key, f.default)
            if f.type == "number":
                try:
                    num = float(raw)
                    if num != num or num in (float("inf"), float("-inf")):
                        num = float(f.default)
                except (TypeError, ValueError):
                    num = float(f.default)
                if f.min is not None:
                    num = max(float(f.min), num)
                if f.max is not None:
                    num = min(float(f.max), num)
                out[f.key] = int(num) if num == int(num) and abs(num) < 1e15 else num
            elif f.type == "slider":
                try:
                    num = float(raw)
                except (TypeError, ValueError):
                    num = float(f.default)
                lo = float(f.min) if f.min is not None else 0.0
                hi = float(f.max) if f.max is not None else 100.0
                num = max(lo, min(hi, num))
                out[f.key] = int(num) if num == int(num) else round(num, 2)
            elif f.type == "toggle":
                out[f.key] = bool(raw) and raw not in ("false", "0", 0)
            elif f.type == "select":
                options = cls.options_for(f.key, out) or f.options
                allowed = [o["value"] for o in options]
                out[f.key] = raw if raw in allowed else (allowed[0] if allowed else raw)
            else:
                out[f.key] = "" if raw is None else str(raw)
        return out

    @classmethod
    def resolve(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Coerce values, then hand QML the field metadata it needs this frame."""
        clean = cls.coerce(values)
        fields = []
        for f in cls.fields:
            d = f.to_dict()
            dynamic = cls.options_for(f.key, clean)
            if dynamic is not None:
                d["options"] = [dict(o) for o in dynamic]
            d["visible"] = cls.visible_for(f, clean)
            fields.append(d)
        return {"fields": fields, "values": clean}

    @classmethod
    def run(cls, values: dict[str, Any]) -> list[dict[str, Any]]:
        raise NotImplementedError

    @classmethod
    def empty(cls) -> bool:
        """True when nothing meaningful has been typed yet."""
        return all(not str(v).strip() for v in cls.coerce({}).values() if isinstance(v, str))
