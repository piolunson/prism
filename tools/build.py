"""Build the portable Windows folder and zip it.

    .venv/Scripts/python.exe tools/build.py

PyInstaller's PySide6 hook drags in every Qt library the wheel ships
(WebEngine alone is ~195 MB), so after the freeze we drop the modules Prism
never imports and keep the ones QML actually loads.  The pruned bundle is then
checked by running its own ``--self-test`` and ``--smoke`` entry points.
"""

from __future__ import annotations

import fnmatch
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
APP = DIST / "Prism"
ARCHIVE = DIST / "Prism-1.0.0-win64.zip"
PYTHON = Path(sys.executable)

# Qt ships far more than a QML utility needs.  Anything matched here is removed
# from the frozen tree; the smoke test afterwards proves nothing essential went.
DLL_PATTERNS = (
    "Qt6WebEngine*.dll",
    "QtWebEngine*.pyd",
    "Qt6Pdf*.dll",
    "QtPdf*.pyd",
    "Qt6Quick3D*.dll",
    "QtQuick3D*.pyd",
    "Qt6Graphs*.dll",
    "QtGraphs*.pyd",
    "Qt6Multimedia*.dll",
    "QtMultimedia*.pyd",
    "Qt6Charts*.dll",
    "QtCharts*.pyd",
    "Qt6DataVisualization*.dll",
    "Qt6SpatialAudio*.dll",
    "Qt6TextToSpeech*.dll",
    "Qt6Designer*.dll",
    "QtDesigner*.pyd",
    "Qt6Test*.dll",
    "QtTest*.pyd",
    "Qt6Sql*.dll",
    "QtSql*.pyd",
    "Qt6Bluetooth*.dll",
    "Qt6Nfc*.dll",
    "Qt6Positioning*.dll",
    "Qt6Location*.dll",
    "Qt6Sensors*.dll",
    "Qt6SerialPort*.dll",
    "Qt6SerialBus*.dll",
    "Qt6WebSockets*.dll",
    "Qt6WebChannel*.dll",
    "Qt6RemoteObjects*.dll",
    "Qt6Help*.dll",
    "Qt6UiTools*.dll",
    "Qt6Linguist*.dll",
    "Qt6QuickWidgets*.dll",
    "Qt6QmlCompiler*.dll",
    "Qt6QuickTimeline*.dll",
    "Qt6QuickVectorImage*.dll",
    "Qt6Concurrent*.dll",
)

QML_DIRS = (
    "QtQuick3D",
    "QtCharts",
    "QtMultimedia",
    "QtSensors",
    "QtBluetooth",
    "QtNfc",
    "QtPositioning",
    "QtLocation",
    "QtRemoteObjects",
    "QtTest",
    "QtWebEngine",
    "QtQuick/Pdf",
    "QtQuick/Timeline",
)

KEEP_TRANSLATIONS = ("qtbase_en", "qtdeclarative_en")


def run(command: list[str]) -> None:
    print("$", " ".join(command))
    result = subprocess.run(command, cwd=ROOT)
    if result.returncode != 0:
        raise SystemExit(f"failed ({result.returncode}): {command[0]}")


def freeze() -> None:
    run([
        str(PYTHON), "-m", "PyInstaller",
        "--noconfirm", "--clean", "--windowed",
        "--name", "Prism",
        "--icon", str(ROOT / "assets" / "prism.ico"),
        # Absolute sources: the spec lives in build/, so relative paths would
        # resolve against the wrong directory.
        "--add-data", f"{ROOT / 'ui'};ui",
        "--add-data", f"{ROOT / 'assets'};assets",
        "--distpath", str(DIST),
        "--workpath", str(ROOT / "build" / "work"),
        "--specpath", str(ROOT / "build"),
        "prism.py",
    ])


def prune() -> int:
    """Delete unneeded Qt payloads; returns bytes reclaimed."""
    if not APP.exists():
        raise SystemExit(f"missing build output: {APP}")

    removed = 0
    for path in sorted(APP.rglob("*")):
        if not path.is_file():
            continue
        name = path.name
        doomed = any(fnmatch.fnmatch(name, pattern) for pattern in DLL_PATTERNS)
        if not doomed and name.startswith("qt") and name.endswith(".qm"):
            doomed = not name.startswith(KEEP_TRANSLATIONS)
        if doomed:
            removed += path.stat().st_size
            path.unlink()

    qml_root = APP / "_internal" / "PySide6" / "qml"
    for relative in QML_DIRS:
        target = qml_root / relative
        if target.exists():
            removed += sum(p.stat().st_size for p in target.rglob("*") if p.is_file())
            shutil.rmtree(target)

    return removed


def verify() -> None:
    exe = APP / "Prism.exe"
    if not exe.exists():
        raise SystemExit("Prism.exe is missing")

    for args, label in (
        (["--self-test"], "self-test"),
        (["--smoke"], "smoke"),
    ):
        result = subprocess.run([str(exe), *args], cwd=APP, timeout=240)
        if result.returncode != 0:
            raise SystemExit(f"{label} failed in the bundle (exit {result.returncode})")
        print(f"bundle {label}: ok")

    shot = APP / "bundle-check.png"
    for theme in ("light", "dark"):
        result = subprocess.run(
            [str(exe), "--theme", theme, "--view", "home", "--screenshot", str(shot)],
            cwd=APP,
            timeout=240,
        )
        if result.returncode != 0 or not shot.exists() or shot.stat().st_size < 40_000:
            raise SystemExit(f"{theme} screenshot failed in the bundle")
        print(f"bundle screenshot {theme}: {shot.stat().st_size // 1024} KB")
        shot.unlink()


def zip_bundle() -> None:
    if ARCHIVE.exists():
        ARCHIVE.unlink()
    with zipfile.ZipFile(ARCHIVE, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as bundle:
        for path in sorted(APP.rglob("*")):
            if path.is_file():
                bundle.write(path, Path("Prism") / path.relative_to(APP))
    print(f"{ARCHIVE.name}: {ARCHIVE.stat().st_size // (1024 * 1024)} MB")


def size_of(path: Path) -> int:
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


def main() -> int:
    run([str(PYTHON), "tools/make_assets.py"])
    run([str(PYTHON), "tools/make_icon.py"])

    freeze()
    before = size_of(APP)
    freed = prune()
    print(f"pruned {freed / (1024 * 1024):.0f} MB ({before / (1024 * 1024):.0f} -> {size_of(APP) / (1024 * 1024):.0f} MB)")

    verify()
    zip_bundle()
    return 0


if __name__ == "__main__":
    sys.exit(main())
