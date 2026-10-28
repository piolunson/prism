"""Developer: JSON, Base64, hashing and identifiers."""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import uuid
from typing import Any

from ..schema import Field, Module, error, kv, listout, note, opts, text, value


class JsonFormatter(Module):
    id = "json"
    category = "developer"
    title = "JSON Formatter"
    subtitle = "Validate, pretty-print, minify"
    icon = "braces"
    keywords = ("json", "format", "pretty", "minify", "validate", "lint", "beautify", "parse")
    fields = (
        Field("body", "textarea", "JSON", default="", placeholder='{"hello": "world", "n": 42}', rows=8, mono=True),
        Field(
            "indent",
            "select",
            "Indent",
            default="2",
            options=opts(("2", "2 spaces"), ("4", "4 spaces"), ("tab", "Tab"), ("0", "Minified")),
        ),
        Field("sort", "toggle", "Sort keys", default=False),
    )

    @classmethod
    def run(cls, v: dict[str, Any]) -> list[dict[str, Any]]:
        raw = str(v["body"])
        if not raw.strip():
            return [note("Paste JSON to format or validate it.")]
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            line = raw.splitlines()[exc.lineno - 1] if exc.lineno - 1 < len(raw.splitlines()) else ""
            pointer = " " * max(0, exc.colno - 1) + "^"
            return [
                error(f"Invalid JSON — {exc.msg} (line {exc.lineno}, column {exc.colno})"),
                text("Where", f"{line}\n{pointer}", mono=True),
            ]
        indent: int | str = 0
        if v["indent"] == "tab":
            indent = "\t"
        elif v["indent"] != "0":
            indent = int(v["indent"])
        formatted = json.dumps(parsed, indent=indent or None, sort_keys=v["sort"], ensure_ascii=False)
        if v["indent"] == "0":
            formatted = json.dumps(parsed, separators=(",", ":"), sort_keys=v["sort"], ensure_ascii=False)
        stats = _shape(parsed)
        return [
            text("Formatted", formatted, mono=True),
            kv(
                "About",
                [
                    ("Status", "valid"),
                    ("Type", stats["type"]),
                    ("Keys / items", f"{stats['count']:,}"),
                    ("Depth", stats["depth"]),
                    ("Size", f"{len(formatted.encode('utf-8')):,} bytes"),
                ],
            ),
            listout("Key paths", stats["paths"][:24]) if stats["paths"] else note("No nested keys."),
        ]


def _shape(value: Any, depth: int = 1, path: str = "$") -> dict[str, Any]:
    paths: list[str] = []
    max_depth = depth
    count = 0
    if isinstance(value, dict):
        kind = "object"
        count = len(value)
        for key, child in value.items():
            child_path = f"{path}.{key}"
            paths.append(child_path)
            if isinstance(child, (dict, list)):
                sub = _shape(child, depth + 1, child_path)
                paths.extend(sub["paths"])
                max_depth = max(max_depth, sub["depth"])
    elif isinstance(value, list):
        kind = "array"
        count = len(value)
        for index, child in enumerate(value[:20]):
            child_path = f"{path}[{index}]"
            if isinstance(child, (dict, list)):
                sub = _shape(child, depth + 1, child_path)
                paths.extend(sub["paths"])
                max_depth = max(max_depth, sub["depth"])
    else:
        kind = type(value).__name__
    return {"type": kind, "count": count, "depth": max_depth, "paths": paths}


class Base64Tool(Module):
    id = "base64"
    category = "developer"
    title = "Base64"
    subtitle = "Encode and decode, URL-safe too"
    icon = "shuffle"
    keywords = ("base64", "encode", "decode", "btoa", "atob", "url safe", "mime")
    fields = (
        Field("body", "textarea", "Input", default="", placeholder="Hello, world", rows=6, mono=True),
        Field(
            "mode",
            "select",
            "Direction",
            default="encode",
            options=opts(("encode", "Encode"), ("decode", "Decode")),
        ),
        Field("urlsafe", "toggle", "URL-safe alphabet", default=False),
    )

    @classmethod
    def run(cls, v: dict[str, Any]) -> list[dict[str, Any]]:
        raw = str(v["body"])
        if not raw.strip():
            return [note("Type text to encode, or Base64 to decode.")]
        urlsafe = bool(v["urlsafe"])
        if v["mode"] == "encode":
            data = raw.encode("utf-8")
            encoded = base64.urlsafe_b64encode(data) if urlsafe else base64.b64encode(data)
            out = encoded.decode("ascii")
            return [
                text("Base64", out, mono=True),
                kv(
                    "Details",
                    [
                        ("Input", f"{len(data):,} bytes"),
                        ("Output", f"{len(out):,} chars"),
                        ("Overhead", f"{(len(out) / max(1, len(data)) - 1) * 100:+.0f}%"),
                    ],
                ),
            ]
        cleaned = "".join(raw.split())
        try:
            if urlsafe:
                decoded = base64.urlsafe_b64decode(cleaned + "=" * (-len(cleaned) % 4))
            else:
                decoded = base64.b64decode(cleaned + "=" * (-len(cleaned) % 4), validate=True)
        except (binascii.Error, ValueError) as exc:
            return [error(f"Not valid Base64: {exc}")]
        try:
            decoded_text = decoded.decode("utf-8")
            printable = True
        except UnicodeDecodeError:
            decoded_text = decoded.decode("latin-1")
            printable = False
        return [
            text("Decoded", decoded_text, mono=True),
            kv(
                "Details",
                [
                    ("Bytes", f"{len(decoded):,}"),
                    ("Looked like", "UTF-8 text" if printable else "binary (shown as latin-1)"),
                    ("Hex", decoded[:24].hex() + ("…" if len(decoded) > 24 else "")),
                ],
            ),
        ]


class HashTool(Module):
    id = "hash"
    category = "developer"
    title = "Hash"
    subtitle = "Five digests at once"
    icon = "fingerprint"
    keywords = ("hash", "md5", "sha1", "sha256", "sha512", "blake2", "checksum", "digest", "integrity")
    fields = (
        Field("body", "textarea", "Input", default="", placeholder="Text to hash…", rows=6, mono=True),
        Field("upper", "toggle", "Uppercase", default=False),
    )

    @classmethod
    def run(cls, v: dict[str, Any]) -> list[dict[str, Any]]:
        raw = str(v["body"])
        if not raw:
            return [note("Type or paste text to hash it.")]
        data = raw.encode("utf-8")
        digests = [
            ("MD5", hashlib.md5(data).hexdigest()),
            ("SHA-1", hashlib.sha1(data).hexdigest()),
            ("SHA-256", hashlib.sha256(data).hexdigest()),
            ("SHA-512", hashlib.sha512(data).hexdigest()),
            ("BLAKE2b", hashlib.blake2b(data).hexdigest()),
        ]
        if v["upper"]:
            digests = [(name, value.upper()) for name, value in digests]
        return [
            kv("Digests", digests),
            kv(
                "Details",
                [
                    ("Bytes hashed", f"{len(data):,}"),
                    ("Encoding", "UTF-8"),
                    ("Characters", f"{len(raw):,}"),
                ],
            ),
            note("MD5 and SHA-1 are fine for checksums, not for security."),
        ]


class UuidTool(Module):
    id = "uuid"
    category = "developer"
    title = "UUID"
    subtitle = "Fresh identifiers, in bulk"
    icon = "tag"
    keywords = ("uuid", "guid", "id", "identifier", "generate", "random", "v4")
    fields = (
        Field("count", "slider", "How many", default=3, min=1, max=12, step=1),
        Field(
            "version",
            "select",
            "Version",
            default="4",
            options=opts(("4", "v4 — random"), ("1", "v1 — time based")),
        ),
        Field("upper", "toggle", "Uppercase", default=False),
        Field("braces", "toggle", "Wrap in braces", default=False),
    )

    @classmethod
    def run(cls, v: dict[str, Any]) -> list[dict[str, Any]]:
        count = int(v["count"])
        values = []
        for _ in range(count):
            value_str = str(uuid.uuid4() if v["version"] == "4" else uuid.uuid1())
            if v["upper"]:
                value_str = value_str.upper()
            if v["braces"]:
                value_str = "{" + value_str + "}"
            values.append(value_str)
        outputs: list[dict[str, Any]] = [
            listout(f"{count} UUID{'s' if count != 1 else ''}", values),
            kv("Details", [("Version", f"v{v['version']}"), ("Count", count), ("Length", len(values[0]))]),
        ]
        if count > 1:
            outputs.append(value("First", values[0]))
        return outputs
