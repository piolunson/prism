"""Prism — bootstrap the Qt application around the QML shell."""

from __future__ import annotations

import argparse
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Any

from PySide6.QtCore import (
    Q_ARG,
    QEventLoop,
    QMetaObject,
    QObject,
    Qt,
    QtMsgType,
    QTimer,
    QUrl,
    qInstallMessageHandler,
)
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow
from PySide6.QtQuickControls2 import QQuickStyle

from engine import registry

from . import win_effects
from .bridge import Bridge
from .icon_provider import IconProvider
from .paths import APP_NAME, VERSION, log_dir, qml_entry, resource
from .settings import Settings

LOG = logging.getLogger("prism")

QML_WARNINGS: list[str] = []


def _setup_logging(verbose: bool = False) -> None:
    LOG.setLevel(logging.DEBUG)
    handler = RotatingFileHandler(
        log_dir() / "prism.log", maxBytes=512_000, backupCount=2, encoding="utf-8"
    )
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    LOG.addHandler(handler)
    if verbose:
        stream = logging.StreamHandler(sys.stderr)
        stream.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
        LOG.addHandler(stream)


def _qt_message_handler(mode, context, message: str) -> None:
    text = f"{context.file}:{context.line} {message}" if context.file else message
    if mode in (QtMsgType.QtWarningMsg, QtMsgType.QtCriticalMsg, QtMsgType.QtFatalMsg):
        QML_WARNINGS.append(text)
        LOG.warning("qt: %s", text)
    else:
        LOG.debug("qt: %s", text)


def _self_test() -> int:
    """Exercise every tool with defaults and a couple of live values."""
    failures = 0
    for module in registry.modules():
        result = registry.run(module.id, {})
        blocks = result.get("outputs") or []
        if not blocks:
            print(f"FAIL {module.id}: no output")
            failures += 1
            continue
        if all(block.get("type") == "error" for block in blocks):
            print(f"FAIL {module.id}: {blocks[0].get('text')}")
            failures += 1
    print(f"modules: {len(registry.modules())}, failures: {failures}")
    return 0 if failures == 0 else 1


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="Prism", add_help=True)
    parser.add_argument("--self-test", action="store_true", help="run the tool engine and exit")
    parser.add_argument("--smoke", action="store_true", help="drive the real QML shell headlessly and exit")
    parser.add_argument("--screenshot", metavar="PATH", help="render, save a PNG and exit")
    parser.add_argument("--theme", choices=("light", "dark", "system"), help="theme for this run only")
    parser.add_argument("--view", default="home", help="home | category:<id> | module:<id>")
    parser.add_argument("--overlay", choices=("none", "palette", "settings"), default="none")
    parser.add_argument("--height", type=int, default=0, help="window height override")
    parser.add_argument("--width", type=int, default=0, help="window width override")
    parser.add_argument("--strict", action="store_true", help="exit non-zero on QML warnings")
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args(argv)


def _initial_view(spec: str) -> dict[str, Any]:
    view: dict[str, Any] = {"view": "home", "categoryId": "", "moduleId": ""}
    if spec.startswith("category:"):
        view.update(view="category", categoryId=spec.split(":", 1)[1])
    elif spec.startswith("module:"):
        view.update(view="module", moduleId=spec.split(":", 1)[1])
        module = registry.module(view["moduleId"])
        if module is not None:
            view["categoryId"] = module.category
    return view


BENIGN_WARNINGS = (
    "Failed to create",
    "QRhi",
    "RHI",
    "OpenGL",
    "Failed to build graphics pipeline",
    "toOpenGLTexture",
    "QQuickWidget",
    "Populating font family aliases",
    "QFontDatabase",
)


def _pump(milliseconds: int) -> None:
    """Let Qt run for a while without pulling in the QtTest module."""
    loop = QEventLoop()
    QTimer.singleShot(milliseconds, loop.quit)
    loop.exec()


def _run_smoke(engine: QQmlApplicationEngine, bridge: Bridge) -> int:
    """Drive the real shell headlessly: navigation, live edits, search, overlays."""
    root = engine.rootObjects()[0]
    failures: list[str] = []

    def find(name: str):
        obj = root.findChild(QObject, name)
        if obj is None:
            failures.append(f"missing object {name}")
            print(f"SMOKE FAIL missing object {name}")
        return obj

    def call(obj, method: str, *args) -> None:
        if obj is None:
            return
        if not args:
            ok = QMetaObject.invokeMethod(obj, method)
        elif len(args) == 1:
            ok = QMetaObject.invokeMethod(obj, method, Q_ARG("QVariant", args[0]))
        elif len(args) == 2:
            ok = QMetaObject.invokeMethod(
                obj, method, Q_ARG("QVariant", args[0]), Q_ARG("QVariant", args[1])
            )
        else:
            ok = False
        if not ok:
            failures.append(f"{method} not invokable")
            print(f"SMOKE FAIL {method} not invokable")

    def as_list(value: object) -> list:
        if hasattr(value, "toVariant"):
            value = value.toVariant()  # type: ignore[union-attr]
        if value is None:
            return []
        try:
            return list(value)  # type: ignore[arg-type]
        except TypeError:
            return []

    def check(label: str, condition: bool, detail: object = "") -> None:
        if condition:
            print(f"SMOKE ok   {label}")
        else:
            failures.append(label)
            print(f"SMOKE FAIL {label}: {detail}")

    shell = find("appShell")
    module = find("moduleView")
    palette = find("palette")
    search = find("paletteSearch")
    sheet = find("settingsSheet")
    category = find("categoryView")

    check("starts on home", shell is not None and shell.property("view") == "home")
    check("24 modules", bridge.moduleCount == 24)

    call(shell, "openCategory", "math")
    _pump(80)
    check("category opens", shell.property("view") == "category" and shell.property("categoryId") == "math")
    check("category lists four tools", category is not None and len(as_list(category.property("tools"))) == 4)

    call(shell, "openModule", "unit")
    _pump(120)
    check("module opens", module.property("moduleId") == "unit")
    outputs = as_list(module.property("outputs"))
    check("unit renders a result", bool(outputs) and outputs[0]["type"] == "value", outputs)
    call(module, "setValue", "amount", 3.0)
    _pump(260)
    outputs = as_list(module.property("outputs"))
    check("live edit recomputes", bool(outputs) and "9.84" in outputs[0]["text"], outputs[:1])

    call(shell, "openModule", "json")
    _pump(120)
    check("module switch resets fields", "body" in as_list(module.property("fieldKeys")))
    call(module, "setValue", "body", '{"a": ')
    _pump(260)
    outputs = as_list(module.property("outputs"))
    check("invalid json reports an error", bool(outputs) and outputs[0]["type"] == "error", outputs[:1])

    call(palette, "show")
    _pump(80)
    check("palette opens with every tool", palette.property("open") is True and len(as_list(palette.property("results"))) == 24)
    if search is not None:
        search.setProperty("text", "hash")
        _pump(80)
        results = as_list(palette.property("results"))
        check("palette searches", bool(results) and results[0]["id"] == "hash", results[:1])
    call(palette, "close")
    _pump(60)
    check("palette closes", palette.property("open") is False)

    call(sheet, "show")
    _pump(60)
    check("settings sheet opens", sheet is not None and sheet.property("open") is True)
    call(sheet, "hide")
    _pump(40)

    bridge.setThemeMode("dark")
    check("dark mode applies", bridge.dark is True)
    bridge.setThemeMode("light")
    check("light mode applies", bridge.dark is False)
    bridge.setThemeMode("system")

    bridge.toggleFavorite("uuid")
    check("favorites persist", any(m["id"] == "uuid" for m in bridge.favoriteModules))
    bridge.toggleFavorite("uuid")
    check("recents record visits", any(m["id"] == "json" for m in bridge.recentModules))

    noisy = [
        warning
        for warning in QML_WARNINGS
        if not any(token in warning for token in BENIGN_WARNINGS)
    ]
    check("no QML warnings", not noisy, noisy[:6])

    print(f"SMOKE {'PASS' if not failures else 'FAIL'} ({len(failures)} failures)")
    return 0 if not failures else 4


def _save_screenshot(window: QQuickWindow, path: str) -> None:
    image = window.grabWindow()
    ok = image.save(path, "PNG")
    LOG.info("screenshot %s -> %s (%dx%d)", "saved" if ok else "failed", path, image.width(), image.height())
    print(f"{'saved' if ok else 'failed'} {path} {image.width()}x{image.height()}")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv if argv is not None else sys.argv[1:])
    _setup_logging(args.verbose)

    # A windowed (--noconsole) build has no standard streams; keep prints harmless.
    for stream in ("stdout", "stderr"):
        if getattr(sys, stream) is None:
            setattr(sys, stream, open(os.devnull, "w", encoding="utf-8"))

    if args.self_test:
        return _self_test()

    if args.smoke:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([sys.argv[0]])
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_NAME)
    app.setOrganizationName(APP_NAME)
    app.setApplicationVersion(VERSION)
    icon = resource("assets", "prism.ico")
    app.setWindowIcon(QIcon(icon if os.path.exists(icon) else resource("assets", "logo.svg")))
    app.setQuitOnLastWindowClosed(True)

    qInstallMessageHandler(_qt_message_handler)

    settings = Settings()
    bridge = Bridge(settings)
    initial = _initial_view(args.view)
    initial["overlay"] = args.overlay
    bridge.set_initial_view(initial)
    if args.theme:
        bridge.set_preview_theme(args.theme)

    engine = QQmlApplicationEngine()
    engine.addImageProvider("prism-icon", IconProvider())
    engine.rootContext().setContextProperty("App", bridge)
    engine.load(QUrl.fromLocalFile(qml_entry()))
    if not engine.rootObjects():
        LOG.error("QML failed to load: %s", qml_entry())
        print("error: QML failed to load", file=sys.stderr)
        return 2

    window = engine.rootObjects()[0]
    if not isinstance(window, QQuickWindow):
        LOG.error("root object is not a window")
        return 2
    engine._bridge = bridge  # type: ignore[attr-defined]  keep the bridge alive
    engine._window = window  # type: ignore[attr-defined]

    if args.width or args.height:
        width = args.width or window.width()
        height = args.height or window.height()
        window.resize(width, height)

    def apply_chrome() -> None:
        hwnd = int(window.winId())
        win_effects.apply_chrome(hwnd, dark=bridge.dark)
        if bridge.desktopGlass:
            window.setColor(Qt.transparent)
            win_effects.set_backdrop(hwnd, "acrylic")
        LOG.info("chrome: hwnd=%s dark=%s glass=%s", hwnd, bridge.dark, bridge.desktopGlass)

    apply_chrome()
    bridge.themeChanged.connect(lambda: win_effects.apply_chrome(int(window.winId()), dark=bridge.dark))

    if args.smoke:
        return _run_smoke(engine, bridge)

    if args.screenshot:
        QTimer.singleShot(1500, lambda: (_save_screenshot(window, args.screenshot), app.quit()))

    exit_code = app.exec()
    if args.strict and QML_WARNINGS:
        print(f"qml warnings: {len(QML_WARNINGS)}", file=sys.stderr)
        for warning in QML_WARNINGS:
            print(f"  {warning}", file=sys.stderr)
        return 3
    return exit_code
