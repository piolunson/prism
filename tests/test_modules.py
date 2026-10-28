from __future__ import annotations

import re

import pytest

from engine import run, schema_for


def blob(result: dict) -> str:
    """Everything the module said, flattened — handy for substring checks."""
    parts = []
    for block in result["outputs"]:
        parts.append(str(block.get("label", "")))
        parts.append(str(block.get("text", "")))
        parts.append(str(block.get("caption", "")))
        for pair in block.get("pairs", []) or []:
            parts.extend([pair["k"], pair["v"]])
        parts.extend(block.get("items", []) or [])
        parts.extend(block.get("colors", []) or [])
    return "\n".join(parts)


def kinds(result: dict) -> list[str]:
    return [b["type"] for b in result["outputs"]]


# --------------------------------------------------------------------------- #
# Converters
# --------------------------------------------------------------------------- #


def test_unit_length_conversion():
    out = run("unit", {"dim": "length", "amount": 1, "from": "m", "to": "ft"})
    assert "3.28" in blob(out)
    assert kinds(out)[0] == "value"


def test_unit_temperature_is_affine():
    out = run("unit", {"dim": "temperature", "amount": 100, "from": "c", "to": "f"})
    assert "212" in blob(out)
    out = run("unit", {"dim": "temperature", "amount": 0, "from": "c", "to": "k"})
    assert "273.15" in blob(out)


def test_unit_lists_every_unit():
    out = run("unit", {"dim": "mass", "amount": 1, "from": "kg", "to": "g"})
    assert "1,000" in blob(out)
    assert len(out["outputs"][-1]["items"]) == 6


def test_number_base_detects_prefixes():
    assert "0xFF" in blob(run("base", {"input": "255", "base": "auto"}))
    assert "10" in blob(run("base", {"input": "0b1010", "base": "auto"}))
    assert "255" in blob(run("base", {"input": "FF", "base": "16"}))


def test_number_base_rejects_junk():
    out = run("base", {"input": "hello", "base": "10"})
    assert kinds(out) == ["error"]


def test_number_base_handles_negatives_and_limits():
    assert "-255" in blob(run("base", {"input": "-255", "base": "10"}))
    assert kinds(run("base", {"input": "9" * 30, "base": "10"})) == ["value", "kv", "kv"]
    assert kinds(run("base", {"input": "9" * 80, "base": "10"})) == ["error"]


def test_data_size_si_vs_binary():
    out = run("data", {"amount": 1, "from": "mb", "to": "mib"})
    assert "0.953" in blob(out)


def test_roman_both_directions():
    assert "MCMLXXXIV" in blob(run("roman", {"input": "1984"}))
    assert "1984" in blob(run("roman", {"input": "mcmlxxxiv"}))
    assert kinds(run("roman", {"input": "4000"})) == ["error"]
    assert kinds(run("roman", {"input": "IQ"})) == ["error"]


# --------------------------------------------------------------------------- #
# Math
# --------------------------------------------------------------------------- #


def test_calculator_arithmetic():
    assert "1,024" in blob(run("calc", {"expr": "2^10", "angle": "deg"}))
    assert "14" in blob(run("calc", {"expr": "2 * (3 + 4)", "angle": "deg"}))


def test_calculator_degrees_and_functions():
    assert "1" in blob(run("calc", {"expr": "sin(90)", "angle": "deg"}))
    assert "0.5" in blob(run("calc", {"expr": "cos(60)", "angle": "deg"}))
    assert "3" in blob(run("calc", {"expr": "sqrt(9)", "angle": "deg"}))


@pytest.mark.parametrize(
    "expression",
    ["1/0", "__import__('os').system('echo hi')", "lambda: 1", "open('x')", "9" * 400],
)
def test_calculator_is_safe(expression):
    out = run("calc", {"expr": expression, "angle": "deg"})
    assert kinds(out)[0] in ("error", "value")
    if kinds(out)[0] == "value":
        pytest.fail("unsafe expression was evaluated")


def test_calculator_empty_is_a_note():
    assert kinds(run("calc", {"expr": ""})) == ["note"]


def test_percentage_modes():
    assert "12" in blob(run("percent", {"mode": "of", "a": 15, "b": 80}))
    assert "25" in blob(run("percent", {"mode": "is", "a": 20, "b": 80}))
    out = run("percent", {"mode": "change", "a": 50, "b": 75})
    assert "+50" in blob(out)
    assert "180" in blob(run("percent", {"mode": "apply", "a": 200, "b": 10, "direction": "down"}))


def test_percentage_change_from_zero_is_an_error():
    assert kinds(run("percent", {"mode": "change", "a": 0, "b": 5})) == ["error"]


def test_statistics_summary():
    out = run("stats", {"numbers": "1, 2, 3, 4, 5"})
    text = blob(out)
    assert "Mean" in text and "3" in text
    assert "Median" in text
    assert "Range" in text


def test_statistics_needs_numbers():
    assert kinds(run("stats", {"numbers": "no digits here"})) == ["note"]


def test_quadratic_roots():
    out = run("quadratic", {"a": 1, "b": -3, "c": 2})
    text = blob(out)
    assert "1" in text and "2" in text
    assert "two real roots" in text


def test_quadratic_complex_and_linear():
    assert "i" in blob(run("quadratic", {"a": 1, "b": 0, "c": 1}))
    assert "linear" in blob(run("quadratic", {"a": 0, "b": 2, "c": -4}))


# --------------------------------------------------------------------------- #
# Text
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "mode,expected",
    [
        ("snake", "hello_world"),
        ("kebab", "hello-world"),
        ("camel", "helloWorld"),
        ("pascal", "HelloWorld"),
        ("constant", "HELLO_WORLD"),
        ("upper", "HELLO WORLD"),
        ("lower", "hello world"),
        ("title", "Hello World"),
    ],
)
def test_case_conversion(mode, expected):
    assert expected in blob(run("case", {"body": "hello world", "mode": mode}))


def test_text_stats_counts():
    out = run("textstats", {"body": "One two three. Four five!"})
    text = blob(out)
    assert "Words" in text and "5" in text
    assert "Sentences" in text and "2" in text


def test_slug_folds_accents():
    out = run("slug", {"body": "Héllo, Wörld — a title!", "separator": "-", "ascii": True, "lower": True})
    assert "hello-world-a-title" in blob(out)


def test_slug_can_fail_gracefully():
    assert kinds(run("slug", {"body": "!!! ???"})) == ["error"]


def test_regex_replacement_and_matches():
    out = run(
        "regex",
        {
            "body": "The quick brown fox jumps",
            "pattern": r"\b(\w+)\s+fox\b",
            "replacement": "cat",
            "ignore_case": True,
            "multiline": False,
            "dotall": False,
        },
    )
    text = blob(out)
    assert "The quick cat" in text
    assert "Found" in text


def test_regex_bad_pattern_is_an_error():
    out = run("regex", {"body": "x", "pattern": "(", "replacement": ""})
    assert kinds(out)[0] == "error"


# --------------------------------------------------------------------------- #
# Time
# --------------------------------------------------------------------------- #


def test_epoch_zero_is_the_unix_epoch():
    out = run("timestamp", {"input": "0", "unit": "auto"})
    assert "1970-01-01T00:00:00Z" in blob(out)


def test_timestamp_accepts_iso_and_relative():
    assert "2026-01-01T00:00:00Z" in blob(run("timestamp", {"input": "2026-01-01T00:00:00Z", "unit": "auto"}))
    assert kinds(run("timestamp", {"input": "next tuesday", "unit": "auto"}))[0] == "error"


def test_timestamp_milliseconds():
    out = run("timestamp", {"input": "1735689600000", "unit": "auto"})
    assert "2025-01-01" in blob(out)


def test_date_difference():
    out = run("datediff", {"start": "2026-01-01", "end": "2026-01-31", "inclusive": False})
    assert "30" in blob(out)
    out = run("datediff", {"start": "2026-01-31", "end": "2026-01-01", "inclusive": False})
    assert "swapped" in blob(out)


def test_date_difference_bad_date():
    assert kinds(run("datediff", {"start": "someday", "end": "2026-01-01"}))[0] == "error"


def test_timezone_conversion():
    out = run(
        "timezone",
        {
            "when": "2026-01-01T00:00:00",
            "from_zone": "UTC",
            "to_zone": "Asia/Tokyo",
        },
    )
    assert "09:00" in blob(out)


def test_countdown_duration_parts():
    out = run("countdown", {"mode": "duration", "duration": "1h 30m", "target": "+1d"})
    assert "5,400" in blob(out)


def test_countdown_until_future_date():
    out = run("countdown", {"mode": "until", "target": "+7d", "duration": ""})
    assert kinds(out)[0] == "value"
    assert "in " in out["outputs"][0]["text"]


# --------------------------------------------------------------------------- #
# Developer
# --------------------------------------------------------------------------- #


def test_json_formats_and_sorts():
    out = run("json", {"body": '{"b": 2, "a": 1}', "indent": "2", "sort": True})
    formatted = out["outputs"][0]["text"]
    assert formatted.index('"a"') < formatted.index('"b"')
    assert '"a": 1' in formatted


def test_json_invalid_reports_position():
    out = run("json", {"body": '{"a": }', "indent": "2", "sort": False})
    assert kinds(out)[0] == "error"
    assert "line" in out["outputs"][0]["text"]


def test_base64_roundtrip():
    encoded = run("base64", {"body": "Hello", "mode": "encode", "urlsafe": False})
    assert "SGVsbG8=" in blob(encoded)
    decoded = run("base64", {"body": "SGVsbG8=", "mode": "decode", "urlsafe": False})
    assert "Hello" in blob(decoded)


def test_base64_rejects_junk():
    assert kinds(run("base64", {"body": "!!!not base64!!!", "mode": "decode", "urlsafe": False}))[0] == "error"


def test_hash_known_digests():
    text = blob(run("hash", {"body": "abc", "upper": False}))
    assert "900150983cd24fb0d6963f7d28e17f72" in text
    assert "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad" in text


def test_uuid_count_and_shape():
    out = run("uuid", {"count": 4, "version": "4", "upper": False, "braces": False})
    items = out["outputs"][0]["items"]
    assert len(items) == 4
    assert all(re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}", u) for u in items)


def test_uuid_uppercase_and_braces():
    out = run("uuid", {"count": 1, "version": "4", "upper": True, "braces": True})
    item = out["outputs"][0]["items"][0]
    assert item.startswith("{") and item.endswith("}") and item.upper() == item


# --------------------------------------------------------------------------- #
# Design
# --------------------------------------------------------------------------- #


def test_color_conversion():
    text = blob(run("color", {"color": "#3A6DF0"}))
    assert "#3A6DF0" in text
    assert "rgb(58, 109, 240)" in text


def test_color_accepts_rgb_input_and_rejects_junk():
    assert "rgb(58, 109, 240)" in blob(run("color", {"color": "rgb(58, 109, 240)"}))
    assert kinds(run("color", {"color": "cornflower"})) == ["error"]


def test_contrast_black_on_white_is_max():
    out = run("contrast", {"foreground": "#000000", "background": "#FFFFFF"})
    assert "21.00:1" in blob(out)
    assert "pass" in blob(out)


def test_contrast_low_pair_fails():
    out = run("contrast", {"foreground": "#BBBBBB", "background": "#FFFFFF"})
    assert "fail" in blob(out)


def test_palette_harmony_sizes():
    out = run("palette", {"color": "#C2553F", "harmony": "analogous"})
    assert len(out["outputs"][0]["colors"]) == 3
    out = run("palette", {"color": "#C2553F", "harmony": "mono"})
    assert len(out["outputs"][0]["colors"]) == 5


def test_glass_tuner_emits_css():
    out = run("glass", {"theme": "light", "blur": 28, "tint": 18, "radius": 20, "shadow": 28})
    css = out["outputs"][0]["text"]
    assert "blur(28px)" in css
    assert "border-radius: 20px" in css
    assert "rgba(255, 255, 255, 0.18)" in css


def test_every_module_resolves_its_own_defaults():
    from engine import MODULES

    for m in MODULES:
        resolved = schema_for(m.id)
        for field in resolved["fields"]:
            if field["type"] == "select":
                assert field["options"], f"{m.id}.{field['key']} has no options"
