from __future__ import annotations

import pytest

from engine import registry


def test_every_category_has_four_modules():
    cats = registry.categories()
    assert [c["id"] for c in cats] == [
        "converters",
        "math",
        "text",
        "time",
        "developer",
        "design",
    ]
    assert all(c["count"] == 4 for c in cats)
    assert len(registry.modules()) == 24


def test_ids_are_unique_and_known():
    ids = [m.id for m in registry.modules()]
    assert len(ids) == len(set(ids))
    for module_id in ids:
        assert registry.module(module_id) is not None


def test_every_module_is_complete():
    for m in registry.modules():
        assert m.title and m.subtitle and m.icon
        assert m.category in {c["id"] for c in registry.CATEGORIES}
        assert m.fields, f"{m.id} has no fields"
        assert len({f.key for f in m.fields}) == len(m.fields), f"{m.id} has duplicate keys"
        meta = m.meta()
        assert meta["search"]


def test_schema_for_returns_fields_and_values():
    resolved = registry.schema_for("unit")
    assert resolved["meta"]["id"] == "unit"
    keys = [f["key"] for f in resolved["fields"]]
    assert keys == ["dim", "amount", "from", "to"]
    assert resolved["values"]["from"] == "m"
    assert all(f["visible"] for f in resolved["fields"])


def test_dynamic_options_follow_the_dimension():
    resolved = registry.schema_for("unit", {"dim": "mass"})
    by_key = {f["key"]: f for f in resolved["fields"]}
    values = {o["value"] for o in by_key["from"]["options"]}
    assert "kg" in values and "m" not in values
    assert resolved["values"]["from"] == "kg"


def test_switching_dimensions_never_leaves_an_invalid_unit():
    resolved = registry.run("unit", {"dim": "volume", "from": "m", "to": "ft"})
    values = resolved["values"]
    assert values["from"] != "m" and values["to"] != "ft"
    assert resolved["outputs"][0]["type"] in ("value", "error")


def test_search_finds_titles_and_keywords():
    assert registry.search("json")[0]["id"] == "json"
    assert registry.search("sha256")[0]["id"] == "hash"
    assert registry.search("percentage")[0]["id"] == "percent"
    assert registry.search("uuid")[0]["id"] == "uuid"
    assert registry.search("timezone")[0]["id"] == "timezone"
    assert registry.search("glass")[0]["id"] == "glass"
    assert registry.search("binary")[0]["id"] == "base"
    assert registry.search("") == []


def test_search_is_ordered_and_limited():
    results = registry.search("convert", limit=5)
    assert 0 < len(results) <= 5
    assert all("categoryTitle" in r for r in results)


def test_search_survives_garbage():
    assert registry.search("!!!)(") == []


def test_run_unknown_module_is_graceful():
    out = registry.run("nope", {})
    assert out["outputs"][0]["type"] == "error"


def test_run_wraps_crashes():
    out = registry.run("json", {"body": "{\"a\": 1}"})
    assert out["outputs"][0]["type"] == "text"


@pytest.mark.parametrize("module_id", [m.id for m in registry.modules()])
def test_run_with_junk_values_never_raises(module_id):
    junk = {"a": "abc", "b": None, "value": "$$$", "body": "\\x00", "n": [1, 2]}
    out = registry.run(module_id, junk)
    assert isinstance(out["outputs"], list) and out["outputs"]
    assert all("type" in block for block in out["outputs"])
