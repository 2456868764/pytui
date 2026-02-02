# scroll_example.py - Aligns OpenTUI packages/core/src/examples/scroll-example.ts
# ScrollBox with Box/Text children; j/k or Up/Down to scroll.

from __future__ import annotations

from typing import Any

_main_container: Any = None
_scrollbox: Any = None
_instructions_text: Any = None
_renderer_ref: Any = None

_COLORS = ("#292e42", "#2f3449")
_PALETTE = ("#7aa2f7", "#9ece6a", "#f7768e", "#7dcfff", "#bb9af7", "#e0af68")


def _make_box_content(i: int) -> str:
    bar_len = 10 + (i % 30)
    bar_fill = int(bar_len * 0.6)
    bar = "█" * bar_fill + "░" * (bar_len - bar_fill)
    tag = "INFO" if i % 3 == 0 else ("WARN" if i % 3 == 1 else "ERROR")
    detail = "data " * ((i % 4) + 2)
    return (
        f"[{(i+1):04d}] Box {i+1} | {tag}\n"
        f"Multiline content with mixed styles for stress testing.\n"
        f"• Title: Lorem ipsum {i}\n"
        f"• Detail A: {detail.strip()}\n"
        f"• Detail B: The quick brown fox jumps over the lazy dog.\n"
        f"• Progress: {bar} {bar_len}\n"
        "— end of box —"
    )


def _on_key(key_event: Any) -> None:
    if not _scrollbox:
        return
    name = getattr(key_event, "name", None) or (key_event.get("name") if isinstance(key_event, dict) else None)
    name = (name or "").lower()
    if name in ("j", "down"):
        _scrollbox.scroll_top = min(
            _scrollbox.scroll_top + 1,
            max(0, _scrollbox.scroll_height - _scrollbox.height),
        )
    elif name in ("k", "up"):
        _scrollbox.scroll_top = max(0, _scrollbox.scroll_top - 1)


def run(renderer: Any) -> None:
    global _main_container, _scrollbox, _instructions_text, _renderer_ref
    from pytui.components.box import Box
    from pytui.components.text import Text
    from pytui.components.scrollbox import Scrollbox

    _renderer_ref = renderer
    renderer.set_background_color("#1a1b26")

    _main_container = Box(
        renderer.context,
        {
            "id": "scroll_example_main",
            "flex_direction": "column",
            "flex_grow": 1,
            "max_height": "100%",
            "max_width": "100%",
            "backgroundColor": "#1a1b26",
        },
    )
    renderer.root.add(_main_container)

    content_box = Box(
        renderer.context,
        {
            "id": "scroll_content_box",
            "flex_grow": 1,
            "backgroundColor": "#24283b",
            "border": True,
            "padding": 1,
        },
    )
    _main_container.add(content_box)

    _scrollbox = Scrollbox(
        renderer.context,
        {
            "id": "scroll-box",
            "width": "100%",
            "height": "100%",
            "backgroundColor": "#1f2335",
        },
    )
    content_box.add(_scrollbox)

    for i in range(20):
        box = Box(
            renderer.context,
            {
                "id": f"box-{i+1}",
                "width": "auto",
                "padding": 1,
                "backgroundColor": _COLORS[i % 2],
            },
        )
        text = Text(
            renderer.context,
            {
                "id": f"box-text-{i+1}",
                "content": _make_box_content(i),
                "fg": _PALETTE[i % len(_PALETTE)],
            },
        )
        box.add(text)
        _scrollbox.add(box)

    _instructions_text = Text(
        renderer.context,
        {
            "id": "scroll_instructions",
            "content": "Scroll Example — j/k or Up/Down to scroll · Ctrl+C exit",
            "width": "100%",
            "height": 2,
            "fg": "#c0caf5",
        },
    )
    _main_container.add(_instructions_text)

    renderer.events.on("keypress", _on_key)


def destroy(renderer: Any) -> None:
    global _main_container, _scrollbox, _instructions_text, _renderer_ref
    try:
        renderer.events.remove_listener("keypress", _on_key)
    except Exception:
        pass
    if _main_container and renderer.root:
        try:
            renderer.root.remove(_main_container.id)
        except Exception:
            pass
    _main_container = None
    _scrollbox = None
    _instructions_text = None
    _renderer_ref = None
