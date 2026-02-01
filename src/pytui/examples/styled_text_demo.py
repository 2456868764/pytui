# styled_text_demo.py - Aligns OpenTUI packages/core/src/examples/styled-text-demo.ts
# Styled text with colors, bold, underline; Text content as list of Span.

from __future__ import annotations

from typing import Any

_parent_container: Any = None


def run(renderer: Any) -> None:
    global _parent_container

    from pytui.components.box import Box
    from pytui.components.text import Text
    from pytui.components.text_node import Span, bold, italic, underline

    renderer.set_background_color("#0f172a")

    _parent_container = Box(
        renderer.context,
        {"id": "parent", "z_index": 10, "flex_direction": "column", "width": "auto", "height": "auto"},
    )
    renderer.root.add(_parent_container)

    # Plain string
    plain_text = Text(
        renderer.context,
        {"id": "plain", "content": "Plain text (default fg/bg)", "width": 50, "height": 1, "fg": "#e2e8f0"},
    )
    _parent_container.add(plain_text)

    # Styled: color + bold
    styled_content: list[Span | str] = [
        Span(text="Red ", fg="#ef4444"),
        Span(text="Green ", fg="#22c55e"),
        Span(text="Blue ", fg="#3b82f6"),
        bold("Bold yellow ", "#eab308"),
        italic("Italic cyan ", "#06b6d4"),
        underline("Underline magenta ", "#d946ef"),
        Span(text="Mixed ", fg="#f97316", bold=True),
        Span(text="dim ", fg="#94a3b8", bold=False),
    ]
    text_styled = Text(
        renderer.context,
        {
            "id": "styled",
            "content": styled_content,
            "width": 60,
            "height": 4,
            "fg": "#e2e8f0",
        },
    )
    _parent_container.add(text_styled)

    hint = Text(
        renderer.context,
        {
            "id": "hint",
            "content": "Styled text demo: Span colors, bold(), italic(), underline(). Ctrl+C to exit.",
            "width": 70,
            "height": 2,
            "fg": "#94a3b8",
        },
    )
    _parent_container.add(hint)


def destroy(renderer: Any) -> None:
    global _parent_container
    if _parent_container and renderer.root:
        try:
            renderer.root.remove(_parent_container.id)
        except Exception:
            pass
    _parent_container = None
