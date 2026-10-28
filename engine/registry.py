"""Category list, module discovery and fuzzy search."""

from __future__ import annotations

from typing import Any

from .schema import CATEGORY_IDS, Module

# Explicit imports keep PyInstaller's static analysis happy.
from . import modules  # noqa: F401  (populates Module.__subclasses__)

CATEGORIES: tuple[dict[str, str], ...] = (
    {
        "id": "converters",
        "title": "Converters",
        "subtitle": "Units, bases, sizes and numerals",
        "icon": "converters",
    },
    {
        "id": "math",
        "title": "Math",
        "subtitle": "Expressions, percentages and statistics",
        "icon": "math",
    },
    {
        "id": "text",
        "title": "Text",
        "subtitle": "Case, counts, slugs and patterns",
        "icon": "text",
    },
    {
        "id": "time",
        "title": "Time",
        "subtitle": "Stamps, spans and zones",
        "icon": "time",
    },
    {
        "id": "developer",
        "title": "Developer",
        "subtitle": "JSON, encoding, hashing and IDs",
        "icon": "developer",
    },
    {
        "id": "design",
        "title": "Design",
        "subtitle": "Color, contrast and glass",
        "icon": "design",
    },
)

_CATEGORY_INDEX = {c["id"]: c for c in CATEGORIES}


def _all_subclasses(cls: type) -> list[type]:
    out: list[type] = []
    for sub in cls.__subclasses__():
        out.append(sub)
        out.extend(_all_subclasses(sub))
    return out


def _discover() -> list[type[Module]]:
    found = [c for c in _all_subclasses(Module) if getattr(c, "id", "")]
    ids = [c.id for c in found]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise RuntimeError(f"duplicate module ids: {sorted(dupes)}")
    order = {cid: i for i, cid in enumerate(CATEGORY_IDS)}
    for c in found:
        if c.category not in _CATEGORY_INDEX:
            raise RuntimeError(f"module {c.id!r} has unknown category {c.category!r}")
    found.sort(key=lambda c: (order[c.category], c.title.lower()))
    return found


MODULES: list[type[Module]] = _discover()
MODULE_INDEX: dict[str, type[Module]] = {m.id: m for m in MODULES}


def modules() -> list[type[Module]]:
    return MODULES


def module(module_id: str) -> type[Module] | None:
    return MODULE_INDEX.get(module_id)


def categories() -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    for m in MODULES:
        counts[m.category] = counts.get(m.category, 0) + 1
    return [{**c, "count": counts.get(c["id"], 0)} for c in CATEGORIES]


def modules_in(category_id: str) -> list[dict[str, Any]]:
    return [m.meta() for m in MODULES if m.category == category_id]


def _subsequence_score(needle: str, haystack: str) -> float:
    """Reward compact subsequence matches ('jf' -> 'json formatter')."""
    if not needle:
        return 0.0
    i = 0
    gaps = 0
    last = -1
    for ch in needle:
        idx = haystack.find(ch, i)
        if idx < 0:
            return 0.0
        if last >= 0:
            gaps += idx - last - 1
        last = idx
        i = idx + 1
    length = last + 1
    return 24.0 * (len(needle) / max(1, length)) - gaps * 0.6


def _score(query: str, m: type[Module]) -> float:
    title = m.title.lower()
    keywords = [k.lower() for k in m.keywords]
    category = m.category.lower()
    score = 0.0
    if title == query:
        return 1000.0
    if title.startswith(query):
        score += 200.0
    elif query in title:
        score += 120.0
    for token in query.split():
        if token in title:
            score += 60.0
        if token in category:
            score += 24.0
        for kw in keywords:
            if kw == token:
                score += 40.0
            elif token in kw:
                score += 18.0
    if score == 0.0:
        score = _subsequence_score(query.replace(" ", ""), title.replace(" ", ""))
    if score > 0:
        # Shorter titles with the same evidence rank above long ones.
        score += max(0.0, 12.0 - len(title) * 0.25)
    return score


def search(query: str, limit: int = 20) -> list[dict[str, Any]]:
    q = " ".join((query or "").lower().split())
    if not q:
        return []
    scored = []
    for m in MODULES:
        s = _score(q, m)
        if s > 0:
            scored.append((s, m))
    scored.sort(key=lambda pair: (-pair[0], pair[1].title.lower()))
    out = []
    for _, m in scored[:limit]:
        meta = m.meta()
        meta["categoryTitle"] = _CATEGORY_INDEX[m.category]["title"]
        out.append(meta)
    return out


def schema_for(module_id: str, values: dict[str, Any] | None = None) -> dict[str, Any]:
    m = module(module_id)
    if m is None:
        return {"fields": [], "values": {}}
    values = values or {}
    resolved = m.resolve(values)
    resolved["meta"] = m.meta()
    resolved["categoryTitle"] = _CATEGORY_INDEX[m.category]["title"]
    return resolved


def run(module_id: str, values: dict[str, Any]) -> dict[str, Any]:
    m = module(module_id)
    if m is None:
        return {"outputs": [{"type": "error", "text": f"Unknown module: {module_id}"}], "values": {}}
    resolved = m.resolve(values)
    clean = resolved["values"]
    try:
        outputs = m.run(dict(clean))
    except Exception as exc:  # a tool must never take the app down
        outputs = [{"type": "error", "text": f"{type(exc).__name__}: {exc}"}]
    return {"fields": resolved["fields"], "values": clean, "outputs": outputs}
