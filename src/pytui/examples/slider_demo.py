# slider_demo.py - Aligns OpenTUI packages/core/src/examples/slider-demo.ts
# Horizontal/vertical sliders with value display; mouse click & drag to change, F to switch focus.

from __future__ import annotations

from typing import Any

_slider_h: Any = None
_slider_v: Any = None
_value_display: Any = None
_key_legend: Any = None
_parent_container: Any = None


def _update_display() -> None:
    if not _value_display:
        return
    h_val = _slider_h.value if _slider_h else 0
    v_val = _slider_v.value if _slider_v else 0
    focus_h = _slider_h.focused if _slider_h else False
    focus_v = _slider_v.focused if _slider_v else False
    text = (
        f"Horizontal: {h_val:.0f} (min={_slider_h.min:.0f} max={_slider_h.max:.0f})\n"
        f"Vertical:   {v_val:.0f} (min={_slider_v.min:.0f} max={_slider_v.max:.0f})\n"
        f"Focus: H={'FOCUSED' if focus_h else 'blurred'}  V={'FOCUSED' if focus_v else 'blurred'}"
    )
    _value_display.set_content(text)


def _on_key(key_event: Any) -> None:
    """Only handle F to switch focus; Slider uses mouse to change value."""
    name = getattr(key_event, "name", None) or (key_event.get("name") if hasattr(key_event, "get") else None)
    if not name:
        return
    name = str(name).lower()
    if name != "f":
        return
    if _slider_h and _slider_h.focused:
        _slider_h.blur()
        if _slider_v:
            _slider_v.focus()
    elif _slider_v and _slider_v.focused:
        _slider_v.blur()
        if _slider_h:
            _slider_h.focus()
    elif _slider_h:
        _slider_h.focus()
    _update_display()


def run(renderer: Any) -> None:
    global _slider_h, _slider_v, _value_display, _key_legend, _parent_container

    from pytui.components.box import Box
    from pytui.components.text import Text
    from pytui.components.slider import Slider
    from pytui.core.renderable import FOCUSED, BLURRED

    renderer.use_mouse = True
    renderer.set_background_color("#0f172a")

    _parent_container = Box(
        renderer.context,
        {"id": "parent", "z_index": 10, "flex_direction": "column", "width": "auto", "height": "auto"},
    )
    renderer.root.add(_parent_container)

    top_row = Box(
        renderer.context,
        {"id": "top-row", "flex_direction": "row", "width": "auto", "height": "auto", "flex_grow": 0},
    )
    _parent_container.add(top_row)

    _slider_h = Slider(
        renderer.context,
        {
            "id": "slider-h",
            "width": 40,
            "height": 1,
            "orientation": "horizontal",
            "min": 0,
            "max": 100,
            "value": 50,
            "viewPortSize": 10,
            "z_index": 100,
        },
    )
    top_row.add(_slider_h)

    _slider_v = Slider(
        renderer.context,
        {
            "id": "slider-v",
            "width": 1,
            "height": 12,
            "orientation": "vertical",
            "min": 0,
            "max": 100,
            "value": 30,
            "viewPortSize": 10,
            "z_index": 100,
        },
    )
    top_row.add(_slider_v)

    _key_legend = Text(
        renderer.context,
        {
            "id": "key-legend",
            "content": "Mouse: click & drag sliders  F: switch focus",
            "width": 50,
            "height": 2,
            "z_index": 50,
            "fg": "#94a3b8",
        },
    )
    top_row.add(_key_legend)

    _value_display = Text(
        renderer.context,
        {
            "id": "value-display",
            "content": "",
            "width": 60,
            "height": 6,
            "z_index": 50,
            "fg": "#e2e8f0",
        },
    )
    _parent_container.add(_value_display)

    def _on_change_h(_v: float) -> None:
        _update_display()

    def _on_change_v(_v: float) -> None:
        _update_display()

    def _on_focus() -> None:
        _update_display()

    _slider_h.on("change", lambda e: _update_display())
    _slider_v.on("change", lambda e: _update_display())
    _slider_h.on(FOCUSED, _on_focus)
    _slider_h.on(BLURRED, _on_focus)
    _slider_v.on(FOCUSED, _on_focus)
    _slider_v.on(BLURRED, _on_focus)

    renderer.events.on("keypress", _on_key)
    _slider_h.focus()
    _update_display()


def destroy(renderer: Any) -> None:
    global _slider_h, _slider_v, _value_display, _key_legend, _parent_container

    try:
        renderer.events.remove_listener("keypress", _on_key)
    except Exception:
        pass
    if _slider_h:
        try:
            _slider_h.blur()
            _slider_h.remove_mouse_listener()
        except Exception:
            pass
        _slider_h = None
    if _slider_v:
        try:
            _slider_v.blur()
            _slider_v.remove_mouse_listener()
        except Exception:
            pass
        _slider_v = None
    if _parent_container and renderer.root:
        renderer.root.remove(_parent_container.id)
    _parent_container = None
    _value_display = None
    _key_legend = None
