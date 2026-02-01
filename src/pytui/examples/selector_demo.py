# selector_demo.py - Example selector menu (Phase 0.4). Box + Text list, Enter run, Esc exit.

from __future__ import annotations

from typing import Any

_container: Any = None
_title_text: Any = None
_lines: list[Any] = []
_selected_index = 0
_implemented_names: list[str] = []
_all_names: list[str] = []


def _on_key(key_event: Any) -> None:
    global _selected_index
    name = getattr(key_event, "name", None) or (key_event.get("name") if isinstance(key_event, dict) else None)
    renderer = getattr(_container, "ctx", None) and getattr(_container.ctx, "renderer", None) if _container else None
    if not renderer:
        return
    if name == "up":
        _selected_index = max(0, _selected_index - 1)
        _update_highlight()
    elif name == "down":
        _selected_index = min(len(_implemented_names) - 1, _selected_index + 1)
        _update_highlight()
    elif name == "enter" or name == "return":
        if _implemented_names and 0 <= _selected_index < len(_implemented_names):
            setattr(renderer, "_example_to_run", _implemented_names[_selected_index])
        renderer.stop()
    elif name == "escape" or name == "q":
        setattr(renderer, "_example_to_run", None)
        renderer.stop()


def _update_highlight() -> None:
    global _lines, _selected_index, _implemented_names
    for i, line in enumerate(_lines):
        if i < len(_implemented_names):
            name = _implemented_names[i]
            prefix = "> " if i == _selected_index else "  "
            line.set_content(prefix + name)


def run_selector(renderer: Any) -> None:
    global _container, _title_text, _lines, _selected_index, _implemented_names, _all_names
    from pytui.examples.registry import EXAMPLES, get_example_names

    _all_names = get_example_names()
    _implemented_names = [n for n in _all_names if EXAMPLES.get(n) and EXAMPLES[n][0] is not None]
    if not _implemented_names:
        _implemented_names = ["simple-layout"]
    _selected_index = 0

    from pytui.components.box import Box
    from pytui.components.text import Text

    _container = Box(renderer.context, {"id": "selector", "width": "auto", "height": "auto", "flex_direction": "column", "padding": 1, "border": True, "backgroundColor": "#1a1a2e"})
    _title_text = Text(renderer.context, {"id": "selector-title", "content": "PyTUI Examples (Enter=run, Esc=exit)", "fg": "#eeeeff", "bg": "transparent"})
    _container.add(_title_text)
    _lines = []
    for i, ex_name in enumerate(_implemented_names):
        prefix = "> " if i == 0 else "  "
        t = Text(renderer.context, {"id": f"selector-line-{i}", "content": prefix + ex_name, "fg": "#aaccff" if i == 0 else "#8899aa", "bg": "transparent"})
        _container.add(t)
        _lines.append(t)
    renderer.root.add(_container)
    renderer.keyboard.on("keypress", _on_key)


def destroy_selector(renderer: Any) -> None:
    global _container, _title_text, _lines
    try:
        renderer.keyboard.remove_listener("keypress", _on_key)
    except Exception:
        pass
    if _container and renderer.root:
        renderer.root.remove(_container.id)
    _container = None
    _title_text = None
    _lines = []
