# console_demo.py - Aligns OpenTUI packages/core/src/examples/console-demo.ts
# Interactive console: log level buttons (LOG/INFO/WARN/ERROR/DEBUG), output area, status line.

from __future__ import annotations

import time
from typing import Any

from pytui.components.box import Box

_main_container: Any = None
_title_text: Any = None
_instructions_text: Any = None
_status_text: Any = None
_log_scrollbox: Any = None
_log_text: Any = None
_log_lines: list[str] = []
_button_counters: dict[str, int] = {"log": 0, "info": 0, "warn": 0, "error": 0, "debug": 0}


class ConsoleButton(Box):
    """Box that acts as a button: on_mouse down appends a log line and updates status."""

    def __init__(self, ctx: Any, options: dict | None = None) -> None:
        super().__init__(ctx, options or {})
        self._log_type = options.get("log_type", "log") if options else "log"
        self._label = options.get("title", self._log_type.upper()) if options else self._log_type.upper()

    def on_mouse(self, event: dict) -> None:
        if event.get("type") != "down":
            return
        global _button_counters, _log_lines, _status_text, _log_text
        _button_counters[self._log_type] = _button_counters.get(self._log_type, 0) + 1
        count = _button_counters[self._log_type]
        ts = time.strftime("%H:%M:%S", time.localtime())
        line = f"[{ts}] {self._log_type.upper()} #{count} triggered"
        _log_lines.append(line)
        if _log_text is not None:
            _log_text.set_content("\n".join(_log_lines[-50:]))
        if _status_text is not None:
            _status_text.set_content(f"Last: {self._log_type.upper()} #{count} at {ts}")


def run(renderer: Any) -> None:
    global _main_container, _title_text, _instructions_text, _status_text
    global _log_scrollbox, _log_text, _log_lines, _button_counters
    from pytui.components.text import Text
    from pytui.components.scrollbox import Scrollbox

    _log_lines.clear()
    _button_counters = {"log": 0, "info": 0, "warn": 0, "error": 0, "debug": 0}

    renderer.use_mouse = True  # enable hit_test + on_mouse for button clicks
    renderer.set_background_color("#1a1b26")

    _main_container = Box(
        renderer.context,
        {
            "id": "console_demo_main",
            "flex_direction": "column",
            "flex_grow": 1,
            "max_height": "100%",
            "max_width": "100%",
            "backgroundColor": "#1a1b26",
        },
    )
    renderer.root.add(_main_container)

    _title_text = Text(
        renderer.context,
        {
            "id": "console_demo_title",
            "content": "Console Demo",
            "width": "100%",
            "height": 1,
            "fg": "#7aa2f7",
        },
    )
    _main_container.add(_title_text)

    _instructions_text = Text(
        renderer.context,
        {
            "id": "console_demo_instructions",
            "content": "Click a level (or focus + Enter): LOG INFO WARN ERROR DEBUG · Ctrl+C exit",
            "width": "100%",
            "height": 1,
            "fg": "#565f89",
        },
    )
    _main_container.add(_instructions_text)

    buttons_row = Box(
        renderer.context,
        {
            "id": "console_buttons_row",
            "flex_direction": "row",
            "width": "100%",
            "height": 3,
        },
    )
    _main_container.add(buttons_row)

    btn_opts = [
        ("log", "LOG", "#9ece6a"),
        ("info", "INFO", "#7dcfff"),
        ("warn", "WARN", "#e0af68"),
        ("error", "ERROR", "#f7768e"),
        ("debug", "DEBUG", "#bb9af7"),
    ]
    for log_type, label, color in btn_opts:
        btn = ConsoleButton(
            renderer.context,
            {
                "id": f"btn_{log_type}",
                "log_type": log_type,
                "title": label,
                "width": 12,
                "height": 3,
                "border": True,
                "backgroundColor": color,
                "borderColor": "#565f89",
            },
        )
        t = Text(renderer.context, {"content": label, "fg": "#1a1b26", "width": 12, "height": 1})
        btn.add(t)
        buttons_row.add(btn)

    log_container = Box(
        renderer.context,
        {
            "id": "console_log_container",
            "flex_grow": 1,
            "border": True,
            "padding": 1,
            "backgroundColor": "#24283b",
        },
    )
    _main_container.add(log_container)

    _log_scrollbox = Scrollbox(
        renderer.context,
        {"id": "console_log_scroll", "width": "100%", "height": "100%", "backgroundColor": "#1f2335"},
    )
    log_container.add(_log_scrollbox)

    _log_text = Text(
        renderer.context,
        {"id": "console_log_text", "content": "(click a level to log)", "fg": "#a9b1d6", "width": "100%", "height": 20},
    )
    _log_scrollbox.add(_log_text)

    _status_text = Text(
        renderer.context,
        {
            "id": "console_demo_status",
            "content": "Ready",
            "width": "100%",
            "height": 1,
            "fg": "#565f89",
        },
    )
    _main_container.add(_status_text)


def destroy(renderer: Any) -> None:
    global _main_container, _title_text, _instructions_text, _status_text, _log_scrollbox, _log_text
    if _main_container and renderer.root:
        try:
            renderer.root.remove(_main_container.id)
        except Exception:
            pass
    _main_container = None
    _title_text = None
    _instructions_text = None
    _status_text = None
    _log_scrollbox = None
    _log_text = None
