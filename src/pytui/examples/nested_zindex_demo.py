# nested_zindex_demo.py - Aligns OpenTUI packages/core/src/examples/nested-zindex-demo.ts
# Nested z-index: 3 parent groups A/B/C; frame callback cycles 4 phases; +/- speed.

from __future__ import annotations

import time
from typing import Any

_parent_container: Any = None
_group_a: Any = None
_group_b: Any = None
_group_c: Any = None
_box_a1: Any = None
_box_b1: Any = None
_box_c1: Any = None
_phase_indicator: Any = None
_zindex_display: Any = None
_animation_speed_ms: float = 2000.0
_frame_cb: Any = None
_key_handler: Any = None
_renderer: Any = None

_PHASES = [
    "Original Hierarchy",
    "C Group on Top",
    "B Group on Top",
    "Equal Parents (Child z-index matters)",
]


def _frame_callback(_delta_ms: float) -> None:
    global _group_a, _group_b, _group_c, _box_a1, _box_b1, _box_c1, _phase_indicator, _zindex_display
    if not _group_a or not _group_b or not _group_c:
        return
    t_ms = time.time() * 1000
    phase_duration = _animation_speed_ms
    new_phase = int((t_ms % (phase_duration * 4)) / phase_duration) % 4

    # Phase 0: A=100, B=50, C=20
    # Phase 1: C=100, A=50, B=20
    # Phase 2: B=100, A=20, C=50
    # Phase 3: A=B=C=60
    if new_phase == 0:
        _group_a.z_index = 100
        _group_b.z_index = 50
        _group_c.z_index = 20
        if _box_a1:
            _box_a1.title = "Parent A (z=100)"
        if _box_b1:
            _box_b1.title = "Parent B (z=50)"
        if _box_c1:
            _box_c1.title = "Parent C (z=20)"
    elif new_phase == 1:
        _group_a.z_index = 50
        _group_b.z_index = 20
        _group_c.z_index = 100
        if _box_a1:
            _box_a1.title = "Parent A (z=50)"
        if _box_b1:
            _box_b1.title = "Parent B (z=20)"
        if _box_c1:
            _box_c1.title = "Parent C (z=100)"
    elif new_phase == 2:
        _group_a.z_index = 20
        _group_b.z_index = 100
        _group_c.z_index = 50
        if _box_a1:
            _box_a1.title = "Parent A (z=20)"
        if _box_b1:
            _box_b1.title = "Parent B (z=100)"
        if _box_c1:
            _box_c1.title = "Parent C (z=50)"
    else:
        _group_a.z_index = 60
        _group_b.z_index = 60
        _group_c.z_index = 60
        if _box_a1:
            _box_a1.title = "Parent A (z=60)"
        if _box_b1:
            _box_b1.title = "Parent B (z=60)"
        if _box_c1:
            _box_c1.title = "Parent C (z=60)"

    if _phase_indicator:
        _phase_indicator.set_content(f"Animation Phase: {new_phase + 1}/4 - {_PHASES[new_phase]}")
    if _zindex_display:
        _zindex_display.set_content(
            f"Current Z-Indices - A:{_group_a.z_index}, B:{_group_b.z_index}, C:{_group_c.z_index}"
        )


def _on_key(key_event: Any) -> None:
    global _animation_speed_ms
    name = getattr(key_event, "name", None) or (key_event.get("name") if isinstance(key_event, dict) else None)
    if not name:
        return
    if name in ("escape", "esc"):
        if _renderer and hasattr(_renderer, "stop"):
            _renderer.stop()
        return
    if name in ("+", "="):
        _animation_speed_ms = max(500, _animation_speed_ms - 200)
    elif name in ("-", "_"):
        _animation_speed_ms = min(5000, _animation_speed_ms + 200)


def run(renderer: Any) -> None:
    global _parent_container, _group_a, _group_b, _group_c, _box_a1, _box_b1, _box_c1
    global _phase_indicator, _zindex_display, _frame_cb, _key_handler, _renderer

    _renderer = renderer
    from pytui.components.box import Box
    from pytui.components.text import Text

    renderer.set_background_color("#001122")

    _parent_container = Box(
        renderer.context,
        {"id": "parent-container", "z_index": 10},
    )
    renderer.root.add(_parent_container)

    title = Text(
        renderer.context,
        {
            "id": "main-title",
            "content": "Nested Render Objects & Z-Index Demo",
            "position": "absolute",
            "left": 10,
            "top": 2,
            "fg": "#FFFF00",
            "bold": True,
            "underline": True,
            "z_index": 1000,
        },
    )
    _parent_container.add(title)

    _group_a = Box(
        renderer.context,
        {"id": "parent-group-a", "position": "absolute", "z_index": 100},
    )
    _parent_container.add(_group_a)

    _group_b = Box(
        renderer.context,
        {"id": "parent-group-b", "position": "absolute", "z_index": 50},
    )
    _parent_container.add(_group_b)

    _group_c = Box(
        renderer.context,
        {"id": "parent-group-c", "position": "absolute", "z_index": 20},
    )
    _parent_container.add(_group_c)

    _box_a1 = Box(
        renderer.context,
        {
            "id": "box-a1",
            "position": "absolute",
            "left": 15,
            "top": 8,
            "width": 25,
            "height": 6,
            "backgroundColor": "#220044",
            "z_index": 10,
            "border_style": "single",
            "border": True,
            "title": "Parent A (z=100)",
            "title_alignment": "center",
        },
    )
    _group_a.add(_box_a1)
    _group_a.add(
        Text(
            renderer.context,
            {"id": "text-a1", "content": "Child A1 (z=10)", "position": "absolute", "left": 17, "top": 10, "fg": "#FF44FF", "bold": True, "z_index": 10},
        )
    )

    _box_b1 = Box(
        renderer.context,
        {
            "id": "box-b1",
            "position": "absolute",
            "left": 30,
            "top": 12,
            "width": 25,
            "height": 6,
            "backgroundColor": "#004422",
            "z_index": 20,
            "border_style": "double",
            "border": True,
            "title": "Parent B (z=50)",
            "title_alignment": "center",
        },
    )
    _group_b.add(_box_b1)
    _group_b.add(
        Text(
            renderer.context,
            {"id": "text-b1", "content": "Child B1 (z=20)", "position": "absolute", "left": 32, "top": 14, "fg": "#44FF44", "bold": True, "z_index": 20},
        )
    )

    _box_c1 = Box(
        renderer.context,
        {
            "id": "box-c1",
            "position": "absolute",
            "left": 45,
            "top": 16,
            "width": 25,
            "height": 6,
            "backgroundColor": "#442200",
            "z_index": 30,
            "border_style": "rounded",
            "border": True,
            "title": "Parent C (z=20)",
            "title_alignment": "center",
        },
    )
    _group_c.add(_box_c1)
    _group_c.add(
        Text(
            renderer.context,
            {"id": "text-c1", "content": "Child C1 (z=30)", "position": "absolute", "left": 47, "top": 18, "fg": "#FFFF44", "bold": True, "z_index": 30},
        )
    )

    _parent_container.add(
        Text(
            renderer.context,
            {
                "id": "explanation1",
                "content": "Key: Parent z-index determines group layering. +/- speed. ESC exit.",
                "position": "absolute",
                "left": 10,
                "top": 25,
                "fg": "#AAAAAA",
                "z_index": 1000,
            },
        )
    )
    _phase_indicator = Text(
        renderer.context,
        {"id": "phase-indicator", "content": "Animation Phase: 1/4", "position": "absolute", "left": 10, "top": 27, "fg": "#FFFFFF", "bold": True, "z_index": 1000},
    )
    _parent_container.add(_phase_indicator)
    _zindex_display = Text(
        renderer.context,
        {"id": "zindex-display", "content": "Current Z-Indices - A:100, B:50, C:20", "position": "absolute", "left": 10, "top": 28, "fg": "#FFFFFF", "z_index": 1000},
    )
    _parent_container.add(_zindex_display)

    _frame_cb = _frame_callback
    renderer.set_frame_callback(_frame_cb)
    _key_handler = _on_key
    renderer.events.on("keypress", _key_handler)


def destroy(renderer: Any) -> None:
    global _parent_container, _group_a, _group_b, _group_c, _box_a1, _box_b1, _box_c1
    global _phase_indicator, _zindex_display, _frame_cb, _key_handler, _renderer
    try:
        if _key_handler:
            renderer.events.remove_listener("keypress", _key_handler)
    except Exception:
        pass
    if _frame_cb and hasattr(renderer, "remove_frame_callback"):
        try:
            renderer.remove_frame_callback(_frame_cb)
        except Exception:
            pass
    if _parent_container and renderer.root:
        try:
            renderer.root.remove(_parent_container.id)
        except Exception:
            pass
    _parent_container = None
    _group_a = _group_b = _group_c = None
    _box_a1 = _box_b1 = _box_c1 = None
    _phase_indicator = _zindex_display = None
    _frame_cb = _key_handler = _renderer = None
