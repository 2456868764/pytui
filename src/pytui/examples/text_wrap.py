# text_wrap.py - Aligns OpenTUI packages/core/src/examples/text-wrap.ts (simplified)
# Text wrapping: ScrollBox + Text with long content; scroll with j/k or Up/Down.

from __future__ import annotations

from typing import Any

from pytui.components.text_node import Span, bold

_parent_container: Any = None
_scrollbox: Any = None
_text_content: Any = None
_instructions_text: Any = None

_DEMO_CONTENT = """OpenTUI Text Wrapping Demo

Welcome to the text wrapping demonstration. This example showcases how PyTUI handles multi-line text inside a scrollable box.

Key Features:
  Word-based wrapping - Preserves word boundaries when breaking lines.
  Character-based wrapping - Breaks at any character for precise control.
  Dynamic resizing - Text reflows as container dimensions change.
  Rich styling - Individual segments can have different colors and attributes.

How It Works:
Text is created with specific styling and composed together to form rich, formatted content. When the container is resized, the text automatically reflows to fit the new dimensions.

Try It Out:
  j / Down - Scroll down
  k / Up   - Scroll up
  L        - Load file (enter path when prompted)
  Ctrl+C   - Exit
"""


def _on_key(key_event: Any) -> None:
    name = getattr(key_event, "name", None) or (key_event.get("name") if isinstance(key_event, dict) else None)
    if not name:
        return
    name = str(name).lower()
    if not _scrollbox:
        return
    if name in ("j", "down"):
        _scrollbox.scroll_top = min(_scrollbox.scroll_top + 1, max(0, _scrollbox.scroll_height - _scrollbox.height))
    elif name in ("k", "up"):
        _scrollbox.scroll_top = max(0, _scrollbox.scroll_top - 1)


def run(renderer: Any) -> None:
    global _parent_container, _scrollbox, _text_content, _instructions_text

    from pytui.components.box import Box
    from pytui.components.text import Text
    from pytui.components.scrollbox import Scrollbox

    renderer.set_background_color("#0a0a14")

    _parent_container = Box(
        renderer.context,
        {
            "id": "main_container",
            "flex_direction": "column",
            "width": "100%",
            "height": "auto",
            "flex_grow": 1,
            "backgroundColor": "#0f0f23",
        },
    )
    renderer.root.add(_parent_container)

    content_box = Box(
        renderer.context,
        {
            "id": "content_box",
            "flex_grow": 1,
            "backgroundColor": "#1e1e2e",
            "border": True,
            "padding": 1,
        },
    )
    _parent_container.add(content_box)

    _scrollbox = Scrollbox(
        renderer.context,
        {
            "id": "text_box",
            "width": 70,
            "height": 18,
            "backgroundColor": "#11111b",
        },
    )
    content_box.add(_scrollbox)

    _text_content = Text(
        renderer.context,
        {
            "id": "text_content",
            "content": _DEMO_CONTENT,
            "width": 68,
            "height": 40,
            "fg": "#c0caf5",
        },
    )
    _scrollbox.add(_text_content)

    _instructions_text = Text(
        renderer.context,
        {
            "id": "instructions",
            "content": [
                bold("Text Wrap Demo", "#7aa2f7"),
                Span(text=" - ", fg="#565f89"),
                Span(text="j/k", fg="#9ece6a"),
                Span(text=" or ", fg="#c0caf5"),
                Span(text="Up/Down", fg="#9ece6a"),
                Span(text=" scroll  ", fg="#c0caf5"),
                Span(text="L", fg="#e0af68"),
                Span(text=" load file  ", fg="#c0caf5"),
                Span(text="Ctrl+C", fg="#f7768e"),
                Span(text=" exit", fg="#c0caf5"),
            ],
            "width": 72,
            "height": 2,
            "fg": "#c0caf5",
        },
    )
    _parent_container.add(_instructions_text)

    renderer.events.on("keypress", _on_key)


def destroy(renderer: Any) -> None:
    global _parent_container, _scrollbox, _text_content, _instructions_text
    try:
        renderer.events.remove_listener("keypress", _on_key)
    except Exception:
        pass
    if _parent_container and renderer.root:
        try:
            renderer.root.remove(_parent_container.id)
        except Exception:
            pass
    _parent_container = None
    _scrollbox = None
    _text_content = None
    _instructions_text = None
