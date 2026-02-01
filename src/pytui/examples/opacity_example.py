# opacity_example.py - Aligns OpenTUI packages/core/src/examples/opacity-example.ts
# Box opacity: 4 boxes with different opacities; 1-4 toggle, A animate.

from __future__ import annotations

import math
import time
from typing import Any

_parent_container: Any = None
_header: Any = None
_info_text: Any = None
_boxes: list[Any] = []
_animating: bool = False
_frame_cb: Any = None

_OPACITY_VALUES = [1.0, 0.8, 0.5, 0.3]
_COLORS = ["#e94560", "#0f3460", "#533483", "#16a085"]
_LABELS = ["Box 1", "Box 2", "Box 3", "Box 4"]


def _update_opacity_labels() -> None:
    for i, box in enumerate(_boxes):
        if box is None:
            continue
        child = getattr(box, "find_by_id", lambda _: None)(f"opacity-{i}")
        if child is not None and hasattr(child, "set_content"):
            child.set_content(f"Opacity: {box.opacity:.1f}")


def _on_key(key_event: Any) -> None:
    global _animating
    name = getattr(key_event, "name", None) or (key_event.get("name") if isinstance(key_event, dict) else None)
    if not name:
        return
    name = str(name).lower()
    if name == "a":
        _animating = not _animating
        if _info_text:
            _info_text.set_content(
                "OPACITY DEMO | Animating... | A: Stop | Ctrl+C: Exit"
                if _animating
                else "OPACITY DEMO | 1-4: Toggle opacity | A: Animate | Ctrl+C: Exit"
            )
        return
    if name in ("1", "2", "3", "4"):
        idx = int(name) - 1
        if 0 <= idx < len(_boxes) and _boxes[idx]:
            b = _boxes[idx]
            b.opacity = 0.3 if b.opacity >= 1.0 else 1.0
            _update_opacity_labels()


def _frame_callback(_delta_ms: float) -> None:
    if not _animating or not _boxes:
        return
    t = time.time()
    for i, box in enumerate(_boxes):
        if box is None:
            continue
        phase = t + i * 0.5
        box.opacity = 0.3 + 0.7 * abs(math.sin(phase))
    _update_opacity_labels()


def run(renderer: Any) -> None:
    global _parent_container, _header, _info_text, _boxes, _frame_cb

    from pytui.components.box import Box
    from pytui.components.text import Text

    renderer.set_background_color("#1a1a2e")

    _header = Box(
        renderer.context,
        {
            "id": "opacity-demo-header",
            "width": "auto",
            "height": 3,
            "backgroundColor": "#16213e",
            "border": True,
            "align_items": "center",
            "justify_content": "center",
        },
    )
    _info_text = Text(
        renderer.context,
        {
            "id": "info",
            "content": "OPACITY DEMO | 1-4: Toggle opacity | A: Animate | Ctrl+C: Exit",
            "fg": "#e94560",
        },
    )
    _header.add(_info_text)

    _parent_container = Box(
        renderer.context,
        {
            "id": "opacity-demo-container",
            "flex_direction": "row",
            "align_items": "center",
            "justify_content": "center",
            "padding": 2,
            "flex_grow": 1,
        },
    )

    for i in range(4):
        box = Box(
            renderer.context,
            {
                "id": f"box-{i}",
                "width": 20,
                "height": 8,
                "backgroundColor": _COLORS[i],
                "border": True,
                "border_style": "double",
                "position": "absolute",
                "left": 10 + i * 8,
                "top": 5 + i * 2,
                "opacity": _OPACITY_VALUES[i],
                "align_items": "center",
                "justify_content": "center",
                "flex_direction": "column",
            },
        )
        label = Text(
            renderer.context,
            {"id": f"label-{i}", "content": _LABELS[i], "fg": "#ffffff"},
        )
        opacity_label = Text(
            renderer.context,
            {"id": f"opacity-{i}", "content": f"Opacity: {_OPACITY_VALUES[i]:.1f}", "fg": "#ffffff"},
        )
        box.add(label)
        box.add(opacity_label)
        _boxes.append(box)
        _parent_container.add(box)

    renderer.root.add(_header)
    renderer.root.add(_parent_container)

    _frame_cb = _frame_callback
    renderer.set_frame_callback(_frame_cb)
    renderer.events.on("keypress", _on_key)


def destroy(renderer: Any) -> None:
    global _parent_container, _header, _info_text, _boxes, _frame_cb
    try:
        renderer.events.remove_listener("keypress", _on_key)
    except Exception:
        pass
    if _frame_cb is not None and hasattr(renderer, "remove_frame_callback"):
        try:
            renderer.remove_frame_callback(_frame_cb)
        except Exception:
            pass
    if _parent_container and renderer.root:
        try:
            renderer.root.remove(_header.id)
            renderer.root.remove(_parent_container.id)
        except Exception:
            pass
    _parent_container = None
    _header = None
    _info_text = None
    _boxes = []
    _frame_cb = None
