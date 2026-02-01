# key_input_demo.py - Key input debug: press any key combinations and see parsed output.
# Aligns with OpenTUI keypress-debug-demo / keypress-debug-demo.ts.

from __future__ import annotations

from typing import Any

_output_lines: list[str] = []
_output_display: Any = None
_parent_container: Any = None
_MAX_LINES = 24


def _repr_char(c: Any) -> str:
    if c is None or c == "":
        return "(none)"
    s = str(c)
    if s == "\t":
        return "\\t"
    if s == "\n":
        return "\\n"
    if s == "\r":
        return "\\r"
    if s == "\x1b":
        return "\\x1b"
    if len(s) == 1 and ord(s) < 32:
        return repr(s)
    return repr(s)


def _format_key_event(key: Any) -> str:
    """Format a key event (dict or KeyEvent) as a single line."""
    name = key.get("name") if hasattr(key, "get") else getattr(key, "name", "")
    char = key.get("char") if hasattr(key, "get") else getattr(key, "char", None)
    seq = key.get("sequence") if hasattr(key, "get") else getattr(key, "sequence", "")
    ctrl = key.get("ctrl") if hasattr(key, "get") else getattr(key, "ctrl", False)
    shift = key.get("shift") if hasattr(key, "get") else getattr(key, "shift", False)
    meta = key.get("meta") if hasattr(key, "get") else getattr(key, "meta", False)
    option = key.get("option") if hasattr(key, "get") else getattr(key, "option", False)
    source = key.get("source") if hasattr(key, "get") else getattr(key, "source", "")
    event_type = key.get("eventType") if hasattr(key, "get") else getattr(key, "event_type", "press")

    char_str = _repr_char(char)
    seq_repr = repr(seq) if seq else "(none)"
    mods = []
    if ctrl:
        mods.append("Ctrl")
    if shift:
        mods.append("Shift")
    if meta or option:
        mods.append("Meta/Alt")
    mod_str = "+".join(mods) if mods else "-"
    return f"name={name!r} char={char_str} sequence={seq_repr} mods={mod_str} type={event_type} source={source!r}"


def _on_keypress(key: Any) -> None:
    global _output_lines, _output_display
    line = _format_key_event(key)
    _output_lines.append(line)
    if len(_output_lines) > _MAX_LINES:
        _output_lines.pop(0)
    if _output_display:
        _output_display.set_content("\n".join(_output_lines))
        _output_display.request_render()


def run(renderer: Any) -> None:
    global _output_lines, _output_display, _parent_container

    from pytui.components.box import Box
    from pytui.components.text import Text

    renderer.set_background_color("#0f172a")
    _output_lines.clear()
    _output_lines.append("Key Input Demo — press any key combinations to see parsed output.")
    _output_lines.append("Ctrl+C to exit. Try: letters, Tab, Shift+Tab, arrows, Ctrl+A, Alt+c, etc.")
    _output_lines.append("")

    _parent_container = Box(
        renderer.context,
        {
            "id": "parent-container",
            "z_index": 10,
            "flex_direction": "column",
            "width": "auto",
            "height": "auto",
        },
    )
    renderer.root.add(_parent_container)

    hint = Text(
        renderer.context,
        {
            "id": "hint",
            "content": "Press any keys. Output below shows: name, char, sequence, mods (Ctrl/Shift/Meta), type, source.",
            "width": 80,
            "height": 1,
            "z_index": 50,
            "fg": "#94a3b8",
        },
    )
    _parent_container.add(hint)

    _output_display = Text(
        renderer.context,
        {
            "id": "key-output",
            "content": "\n".join(_output_lines),
            "width": 88,
            "height": _MAX_LINES + 2,
            "z_index": 50,
            "fg": "#e2e8f0",
        },
    )
    _parent_container.add(_output_display)

    renderer.events.on("keypress", _on_keypress)


def destroy(renderer: Any) -> None:
    global _output_display, _parent_container

    try:
        renderer.events.remove_listener("keypress", _on_keypress)
    except Exception:
        pass
    _output_display = None
    if _parent_container and renderer.root:
        renderer.root.remove(_parent_container.id)
    _parent_container = None
