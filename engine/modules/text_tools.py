"""Text: case conversion, statistics, slugs and regex work."""

from __future__ import annotations

import re
import unicodedata
from typing import Any

from ..schema import Field, Module, error, kv, listout, note, opts, text, value


def split_words(value: str) -> list[str]:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value)
    return [w for w in re.split(r"[^0-9A-Za-z\u00c0-\u024f]+", value) if w]


class CaseConverter(Module):
    id = "case"
    category = "text"
    title = "Case & Format"
    subtitle = "Ten cases, one paste"
    icon = "type"
    keywords = ("case", "upper", "lower", "title", "camel", "snake", "kebab", "pascal", "constant", "sentence", "format")
    fields = (
        Field("body", "textarea", "Text", default="", placeholder="Paste anything…", rows=5),
        Field(
            "mode",
            "select",
            "Convert to",
            default="snake",
            options=opts(
                ("lower", "lowercase"),
                ("upper", "UPPERCASE"),
                ("title", "Title Case"),
                ("sentence", "Sentence case"),
                ("camel", "camelCase"),
                ("pascal", "PascalCase"),
                ("snake", "snake_case"),
                ("kebab", "kebab-case"),
                ("constant", "CONSTANT_CASE"),
                ("toggle", "tOGGLE cASE"),
            ),
        ),
    )

    @classmethod
    def run(cls, v: dict[str, Any]) -> list[dict[str, Any]]:
        body = str(v["body"])
        if not body.strip():
            return [note("Paste text to convert it.")]
        mode = v["mode"]
        words = split_words(body)
        if mode == "lower":
            out = body.lower()
        elif mode == "upper":
            out = body.upper()
        elif mode == "title":
            out = " ".join(w[:1].upper() + w[1:].lower() for w in words)
        elif mode == "sentence":
            out = re.sub(r"(^|[.!?]\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), body.lower())
        elif mode == "camel":
            out = (words[0].lower() if words else "") + "".join(w.capitalize() for w in words[1:])
        elif mode == "pascal":
            out = "".join(w.capitalize() for w in words)
        elif mode == "snake":
            out = "_".join(w.lower() for w in words)
        elif mode == "kebab":
            out = "-".join(w.lower() for w in words)
        elif mode == "constant":
            out = "_".join(w.upper() for w in words)
        else:
            out = "".join(c.lower() if c.isupper() else c.upper() for c in body)
        return [text("Result", out, mono=False), kv("Dimensions", [("Words", len(words)), ("Characters", len(out))])]


class TextStats(Module):
    id = "textstats"
    category = "text"
    title = "Text Stats"
    subtitle = "Counts, length and reading time"
    icon = "chart"
    keywords = ("word count", "characters", "reading time", "sentences", "paragraphs", "count", "length")
    fields = (
        Field("body", "textarea", "Text", default="", placeholder="Paste text…", rows=6),
    )

    @classmethod
    def run(cls, v: dict[str, Any]) -> list[dict[str, Any]]:
        body = str(v["body"])
        if not body.strip():
            return [note("Paste text to measure it.")]
        words = re.findall(r"[^\s]+", body)
        sentences = [s for s in re.split(r"[.!?]+(?:\s|$)", body) if s.strip()]
        paragraphs = [p for p in re.split(r"\n\s*\n", body.strip()) if p.strip()]
        lines = body.splitlines()
        letters = sum(1 for c in body if c.isalpha())
        avg = (sum(len(w) for w in words) / len(words)) if words else 0.0
        read_min = len(words) / 220.0
        speak_min = len(words) / 140.0

        def as_time(minutes: float) -> str:
            if minutes < 1:
                return f"{max(1, round(minutes * 60))} sec"
            return f"{minutes:.1f} min"

        counts: dict[str, int] = {}
        for w in re.findall(r"[a-z0-9']+", body.lower()):
            if len(w) > 2:
                counts[w] = counts.get(w, 0) + 1
        top = sorted(counts.items(), key=lambda kvp: (-kvp[1], kvp[0]))[:6]
        return [
            kv(
                "Counts",
                [
                    ("Characters", f"{len(body):,}"),
                    ("Without spaces", f"{len(re.sub(r'\\s', '', body)):,}"),
                    ("Letters", f"{letters:,}"),
                    ("Words", f"{len(words):,}"),
                    ("Sentences", f"{len(sentences):,}"),
                    ("Paragraphs", f"{len(paragraphs):,}"),
                    ("Lines", f"{len(lines):,}"),
                ],
            ),
            kv(
                "Reading",
                [
                    ("Reading time", as_time(read_min)),
                    ("Speaking time", as_time(speak_min)),
                    ("Avg word", f"{avg:.2f} chars"),
                    ("Longest word", max(words, key=len) if words else "—"),
                ],
            ),
            listout("Most frequent", [f"{w} ×{n}" for w, n in top]) if top else note("No repeated words yet."),
        ]


class Slugify(Module):
    id = "slug"
    category = "text"
    title = "Slug & Clean"
    subtitle = "URL and filename-safe text"
    icon = "link"
    keywords = ("slug", "url", "filename", "clean", "normalize", "ascii", "permalink", "safe")
    fields = (
        Field("body", "textarea", "Text", default="", placeholder="Héllo, Wörld — a title!", rows=4),
        Field(
            "separator",
            "select",
            "Separator",
            default="-",
            options=opts(("-", "Hyphen ( - )"), ("_", "Underscore ( _ )"), (".", "Dot ( . )")),
        ),
        Field("ascii", "toggle", "Fold to ASCII", default=True),
        Field("lower", "toggle", "Lowercase", default=True),
    )

    @classmethod
    def run(cls, v: dict[str, Any]) -> list[dict[str, Any]]:
        raw = str(v["body"])
        if not raw.strip():
            return [note("Paste text to make a slug.")]
        body = raw
        if v["ascii"]:
            body = unicodedata.normalize("NFKD", body)
            body = body.encode("ascii", "ignore").decode("ascii")
        else:
            body = unicodedata.normalize("NFC", body)
        if v["lower"]:
            body = body.lower()
        sep = v["separator"]
        slug = re.sub(r"[^0-9A-Za-z\u00c0-\u024f]+", sep, body).strip(sep)
        slug = re.sub(re.escape(sep) + "{2,}", sep, slug)
        filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "", slug).strip(". ")
        if not slug:
            return [error("Nothing slug-worthy survived — try text with letters or numbers.")]
        return [
            value("Slug", slug),
            kv(
                "Variants",
                [
                    ("Filename", filename or "—"),
                    ("Length", f"{len(slug)} chars"),
                    ("Words", str(len([p for p in slug.split(sep) if p]))),
                ],
            ),
            value("Sample URL", f"https://example.com/{slug}", mono=True),
        ]


class RegexTool(Module):
    id = "regex"
    category = "text"
    title = "Regex Find & Replace"
    subtitle = "Test patterns, see every match"
    icon = "pattern"
    keywords = ("regex", "regexp", "pattern", "match", "replace", "substitute", "find", "grep")
    fields = (
        Field("body", "textarea", "Text", default="", placeholder="The quick brown fox…", rows=5),
        Field("pattern", "text", "Pattern", default=r"\b(\w+)\s+fox\b", placeholder=r"\b\w+@\w+\.\w+\b", mono=True),
        Field("replacement", "text", "Replace with", default="cat", placeholder=r"\1 — groups work", mono=True),
        Field("ignore_case", "toggle", "Ignore case", default=True),
        Field("multiline", "toggle", "Multiline (^ $ per line)", default=False),
        Field("dotall", "toggle", "Dot matches newlines", default=False),
    )

    @classmethod
    def run(cls, v: dict[str, Any]) -> list[dict[str, Any]]:
        body = str(v["body"])
        pattern = str(v["pattern"])
        if not pattern:
            return [note("Enter a pattern to test.")]
        flags = 0
        if v["ignore_case"]:
            flags |= re.IGNORECASE
        if v["multiline"]:
            flags |= re.MULTILINE
        if v["dotall"]:
            flags |= re.DOTALL
        try:
            rx = re.compile(pattern, flags)
        except re.error as exc:
            return [error(f"Pattern error: {exc}")]
        matches = list(rx.finditer(body))
        replaced = rx.sub(str(v["replacement"]), body)
        detail = kv("Matches", [("Found", str(len(matches))), ("Pattern", pattern), ("Flags", _flags(v))])
        if matches:
            rows = []
            for m in matches[:40]:
                snippet = m.group(0)
                if len(snippet) > 60:
                    snippet = snippet[:57] + "…"
                rows.append(f"{m.start()}–{m.end()}  {snippet!r}")
            if len(matches) > 40:
                rows.append(f"… {len(matches) - 40} more")
            return [text("Replaced", replaced, mono=True), detail, listout("Every match", rows)]
        return [text("Replaced", replaced, mono=True), detail, note("No matches — the text is unchanged.")]


def _flags(v: dict[str, Any]) -> str:
    active = [name for name in ("ignore_case", "multiline", "dotall") if v[name]]
    return ", ".join(active) if active else "none"
