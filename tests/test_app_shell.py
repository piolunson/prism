"""Exercise the real application as a process.

Embedding a live ``QQmlApplicationEngine`` inside pytest fights shiboken's
object lifetime rules (the engine outlives the python objects it owns and the
interpreter dies at teardown).  Instead we drive the shipped entry point the
same way a user does: ``python prism.py --smoke`` boots Qt offscreen, walks the
whole QML tree, edits fields, opens overlays and fails loudly on any warning.
"""

from __future__ import annotations

import os
import struct
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PRISM = ROOT / "prism.py"

ENV = {
    **os.environ,
    "QT_QPA_PLATFORM": "offscreen",
    "QT_LOGGING_RULES": "qt.qpa.*=false",
    "PYTHONIOENCODING": "utf-8",
}


def run(*args: str, timeout: int = 180) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        [sys.executable, str(PRISM), *args],
        cwd=ROOT,
        env=ENV,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return proc


def test_engine_defaults_are_clean():
    proc = run("--self-test")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "failures: 0" in proc.stdout


def test_shell_smoke_passes():
    proc = run("--smoke", timeout=240)
    output = proc.stdout + proc.stderr
    assert proc.returncode == 0, output
    assert "SMOKE PASS" in output, output
    assert "SMOKE FAIL" not in output, output
    # The assertions we care about most, spelled out so a regression names itself.
    for label in (
        "starts on home",
        "24 modules",
        "category opens",
        "module opens",
        "live edit recomputes",
        "module switch resets fields",
        "palette searches",
        "settings sheet opens",
        "dark mode applies",
        "light mode applies",
        "no QML warnings",
    ):
        assert f"SMOKE ok   {label}" in output, f"{label} did not pass:\n{output}"


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_screenshot_renders(theme: str, tmp_path: Path):
    target = tmp_path / f"{theme}.png"
    proc = run("--theme", theme, "--view", "module:unit", "--screenshot", str(target))
    assert proc.returncode == 0, proc.stderr
    assert target.exists(), proc.stdout + proc.stderr

    data = target.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    width, height = struct.unpack(">II", data[16:24])
    assert width >= 900 and height >= 600
    # A blank window compresses to almost nothing; this catches a white screen.
    assert len(data) > 40_000, f"{theme} screenshot looks empty ({len(data)} bytes)"
