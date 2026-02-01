# link_demo.py - Aligns OpenTUI packages/core/src/examples/link-demo.ts (minimal)
# OSC 8 hyperlinks: Text with link Span; terminal may support clickable links.

from __future__ import annotations

from typing import Any

from pytui.components.text_node import Span, link, bold

_parent_container: Any = None


def run(renderer: Any) -> None:
    global _parent_container

    from pytui.components.box import Box
    from pytui.components.text import Text

    renderer.set_background_color("#0f172a")

    _parent_container = Box(
        renderer.context,
        {
            "id": "parent",
            "flex_direction": "column",
            "width": "auto",
            "height": "auto",
            "z_index": 10,
        },
    )
    renderer.root.add(_parent_container)

    title = Text(
        renderer.context,
        {
            "id": "title",
            "content": "Link Demo (OSC 8)",
            "width": 60,
            "height": 1,
            "fg": "#e2e8f0",
            "bold": True,
        },
    )
    _parent_container.add(title)

    # Link spans: href is stored; terminal that supports OSC 8 may render them clickable
    link_content: list[Span | str] = [
        Span(text="PyTUI ", fg="#94a3b8"),
        link("GitHub", "https://github.com", "#38bdf8"),
        Span(text="  |  ", fg="#64748b"),
        link("OpenTUI", "https://github.com/opentui/opentui", "#a78bfa"),
        Span(text="  |  ", fg="#64748b"),
        link("Docs", "https://pytui.readthedocs.io", "#34d399"),
    ]
    link_text = Text(
        renderer.context,
        {
            "id": "links",
            "content": link_content,
            "width": 70,
            "height": 2,
            "fg": "#cbd5e1",
        },
    )
    _parent_container.add(link_text)

    hint = Text(
        renderer.context,
        {
            "id": "hint",
            "content": [
                bold("Note:", "#fbbf24"),
                Span(text=" OSC 8 links may be clickable in supported terminals (e.g. iTerm2, Kitty). Ctrl+C to exit.", fg="#94a3b8"),
            ],
            "width": 72,
            "height": 3,
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
