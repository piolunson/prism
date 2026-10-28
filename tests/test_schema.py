from __future__ import annotations

import pytest

from engine.schema import (
    Field,
    Module,
    error,
    kv,
    listout,
    meter,
    note,
    opts,
    swatches,
    text,
    value,
)


def test_field_rejects_unknown_type():
    with pytest.raises(ValueError):
        Field("x", "wizard", "X")


def test_select_requires_options_or_dynamic():
    with pytest.raises(ValueError):
        Field("x", "select", "X")
    Field("x", "select", "X", dynamic=True)  # allowed
    Field("x", "select", "X", options=opts(("a", "A")))


def test_number_field_requires_a_default():
    with pytest.raises(ValueError):
        Field("x", "number", "X", default="")


class Demo(Module):
    id = "demo"
    category = "math"
    title = "Demo"
    fields = (
        Field("n", "number", "N", default=5, min=0, max=10),
        Field("mode", "select", "Mode", default="a", options=opts(("a", "A"), ("b", "B"))),
        Field("flag", "toggle", "Flag", default=False),
        Field("body", "text", "Body", default=""),
    )

    @classmethod
    def run(cls, values):
        return [value("N", values["n"])]


def test_coerce_clamps_and_repairs():
    clean = Demo.coerce({"n": "99", "mode": "zzz", "flag": "true", "body": 12})
    assert clean["n"] == 10
    assert clean["mode"] == "a"
    assert clean["flag"] is True
    assert clean["body"] == "12"


def test_coerce_survives_garbage_numbers():
    clean = Demo.coerce({"n": "not a number", "flag": None})
    assert clean["n"] == 5
    assert clean["flag"] is False


def test_resolve_reports_visibility():
    resolved = Demo.resolve({"n": 3})
    assert [f["key"] for f in resolved["fields"]] == ["n", "mode", "flag", "body"]
    assert all(f["visible"] for f in resolved["fields"])
    assert resolved["values"]["n"] == 3


def test_visible_when_rules():
    field = Field("b", "text", "B", visible_when={"key": "mode", "not": ""})
    assert Demo.visible_for(field, {"mode": "a"}) is True
    field2 = Field("b", "text", "B", visible_when={"key": "mode", "in": ["x"]})
    assert Demo.visible_for(field2, {"mode": "a"}) is False


def test_meta_search_blob_is_lowercase():
    meta = Demo.meta()
    assert meta["id"] == "demo"
    assert meta["search"] == meta["search"].lower()


def test_output_helpers_shape():
    assert value("A", 3)["text"] == "3"
    assert value("A", 3.5)["text"] == "3.5"
    assert value("A", 0.1 + 0.2)["text"].startswith("0.3")
    assert kv("K", [("a", 1)])["pairs"][0] == {"k": "a", "v": "1"}
    assert listout("L", [1, 2])["items"] == ["1", "2"]
    assert text("T", "body")["text"] == "body"
    assert note("hi")["type"] == "note"
    assert error("bad")["type"] == "error"
    assert swatches("S", ["#fff"])["colors"] == ["#fff"]
    assert meter("M", 5.0)["ratio"] == 1.0
    assert meter("M", -2)["ratio"] == 0.0
