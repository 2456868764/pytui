# relative_positioning_demo.py - Aligns OpenTUI packages/core/src/examples/relative-positioning-demo.ts (simplified)
# Child positions relative to parent: parent Box with absolute-positioned children.

from __future__ import annotations

from typing import Any

_parent_container: Any = None


def run(renderer: Any) -> None:
    global _parent_container

    from pytui.components.box import Box
    from pytui.components.text import Text

    renderer.set_background_color("#001122")

    _parent_container = Box(
        renderer.context,
        {
            "id": "root-container",
            "position": "relative",
            "z_index": 10,
        },
    )
    renderer.root.add(_parent_container)

    title = Text(
        renderer.context,
        {
            "id": "main-title",
            "content": "Relative Positioning Demo - Child positions are relative to parent",
            "position": "absolute",
            "left": 5,
            "top": 1,
            "fg": "#FFFF00",
            "bold": True,
            "underline": True,
            "z_index": 1000,
        },
    )
    _parent_container.add(title)

    parent_a = Box(
        renderer.context,
        {
            "id": "parent-container-a",
            "position": "absolute",
            "left": 10,
            "top": 5,
            "z_index": 50,
        },
    )
    _parent_container.add(parent_a)

    parent_box_a = Box(
        renderer.context,
        {
            "id": "parent-box-a",
            "left": 0,
            "top": 0,
            "width": 40,
            "height": 12,
            "backgroundColor": "#220044",
            "z_index": 1,
            "border_style": "double",
            "border": True,
            "title": "Parent A",
            "title_alignment": "center",
            "flex_direction": "row",
        },
    )
    parent_a.add(parent_box_a)

    for i in range(3):
        child = Box(
            renderer.context,
            {
                "id": f"child-a{i+1}",
                "width": 10,
                "height": 6,
                "backgroundColor": ["#440066", "#660044", "#440044"][i],
                "z_index": 2,
                "border_style": "single",
                "border": True,
                "title": f"Child {i+1}",
                "title_alignment": "center",
                "flex_grow": 1,
                "min_width": 8,
            },
        )
        parent_box_a.add(child)

    parent_b = Box(
        renderer.context,
        {
            "id": "parent-container-b",
            "position": "absolute",
            "left": 55,
            "top": 8,
            "z_index": 50,
        },
    )
    _parent_container.add(parent_b)

    parent_box_b = Box(
        renderer.context,
        {
            "id": "parent-box-b",
            "width": 25,
            "height": 10,
            "backgroundColor": "#004422",
            "border_style": "double",
            "border": True,
            "title": "Parent B (right)",
            "title_alignment": "center",
        },
    )
    parent_b.add(parent_box_b)
    parent_box_b.add(
        Text(
            renderer.context,
            {"id": "text-b", "content": "Children use left/top relative to parent.", "fg": "#44FF44"},
        )
    )

    _parent_container.add(
        Text(
            renderer.context,
            {
                "id": "explanation",
                "content": "Key: position absolute + left/top place children relative to parent. Ctrl+C to exit.",
                "position": "absolute",
                "left": 10,
                "top": 22,
                "fg": "#AAAAAA",
                "z_index": 1000,
            },
        )
    )


def destroy(renderer: Any) -> None:
    global _parent_container
    if _parent_container and renderer.root:
        try:
            renderer.root.remove(_parent_container.id)
        except Exception:
            pass
    _parent_container = None
