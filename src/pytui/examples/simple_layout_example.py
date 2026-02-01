# simple_layout_example.py - Aligns OpenTUI packages/core/src/examples/simple-layout-example.ts
# Flex layout demo: Horizontal / Vertical / Centered / Three-column; Space to cycle, R restart, P autoplay.

from __future__ import annotations

from typing import Any

# Module state (cleared in destroy)
_header: Any = None
_header_text: Any = None
_content_area: Any = None
_sidebar: Any = None
_sidebar_text: Any = None
_main_content: Any = None
_main_content_text: Any = None
_right_sidebar: Any = None
_right_sidebar_text: Any = None
_footer: Any = None
_footer_text: Any = None
_current_demo_index = 0
_autoplay_enabled = True
_renderer_ref: Any = None
# Accumulated ms since last autoplay advance; list so frame callback can mutate
_autoplay_accum_ms: list[float] = [0.0]
_autoplay_frame_cb: Any = None


def _reset_element_layout(box: Any) -> None:
    box.layout_node.set_flex_basis("auto")
    box.layout_node.set_flex_grow(0)
    box.layout_node.set_width("auto")
    box.layout_node.set_height("auto")


def _setup_horizontal(renderer: Any) -> None:
    global _content_area, _sidebar, _main_content, _right_sidebar, _sidebar_text, _main_content_text
    if not _content_area or not _sidebar or not _main_content or not _right_sidebar:
        return
    _sidebar.visible = True
    _main_content.visible = True
    _right_sidebar.visible = False
    _reset_element_layout(_sidebar)
    _reset_element_layout(_main_content)
    _content_area.layout_node.set_flex_direction("row")
    _content_area.layout_node.set_align_items("stretch")
    tw = renderer.terminal_width
    sidebar_w = max(15, int(tw * 0.2))
    _sidebar.layout_node.set_flex_basis(sidebar_w)
    _sidebar.layout_node.set_flex_grow(0)
    _sidebar.layout_node.set_width(sidebar_w)
    _sidebar.layout_node.set_height("auto")
    if _sidebar_text:
        _sidebar_text.set_content("LEFT SIDEBAR")
    _sidebar.backgroundColor = "#64748b"
    _main_content.layout_node.set_flex_basis("auto")
    _main_content.layout_node.set_flex_grow(1)
    _main_content.layout_node.set_width("auto")
    _main_content.layout_node.set_height("auto")
    if _main_content_text:
        _main_content_text.set_content("MAIN CONTENT")
    _main_content.backgroundColor = "#eab308"


def _setup_vertical(renderer: Any) -> None:
    global _content_area, _sidebar, _main_content, _right_sidebar, _sidebar_text, _main_content_text
    if not _content_area or not _sidebar or not _main_content or not _right_sidebar:
        return
    _sidebar.visible = True
    _main_content.visible = True
    _right_sidebar.visible = False
    _reset_element_layout(_sidebar)
    _reset_element_layout(_main_content)
    _content_area.layout_node.set_flex_direction("column")
    _content_area.layout_node.set_align_items("stretch")
    th = renderer.terminal_height - 6
    top_h = max(3, int(th * 0.2))
    _sidebar.layout_node.set_flex_basis(top_h)
    _sidebar.layout_node.set_flex_grow(0)
    _sidebar.layout_node.set_height(top_h)
    _sidebar.layout_node.set_width("auto")
    if _sidebar_text:
        _sidebar_text.set_content("TOP BAR")
    _sidebar.backgroundColor = "#059669"
    _main_content.layout_node.set_flex_basis("auto")
    _main_content.layout_node.set_flex_grow(1)
    _main_content.layout_node.set_height("auto")
    _main_content.layout_node.set_width("auto")
    if _main_content_text:
        _main_content_text.set_content("MAIN CONTENT")
    _main_content.backgroundColor = "#eab308"


def _setup_centered(renderer: Any) -> None:
    global _content_area, _sidebar, _main_content, _right_sidebar, _main_content_text
    if not _content_area or not _sidebar or not _main_content or not _right_sidebar:
        return
    _sidebar.visible = False
    _main_content.visible = True
    _right_sidebar.visible = False
    _reset_element_layout(_main_content)
    _content_area.layout_node.set_flex_direction("row")
    _content_area.layout_node.set_align_items("stretch")
    _content_area.layout_node.set_justify_content("center")
    tw = renderer.terminal_width
    center_w = max(30, int(tw * 0.6))
    _main_content.layout_node.set_flex_basis(center_w)
    _main_content.layout_node.set_flex_grow(0)
    _main_content.layout_node.set_width(center_w)
    _main_content.layout_node.set_height("auto")
    if _main_content_text:
        _main_content_text.set_content("CENTERED CONTENT")
    _main_content.backgroundColor = "#7c3aed"


def _setup_three_column(renderer: Any) -> None:
    global _content_area, _sidebar, _main_content, _right_sidebar, _sidebar_text, _main_content_text, _right_sidebar_text
    if not _content_area or not _sidebar or not _main_content or not _right_sidebar:
        return
    _sidebar.visible = True
    _main_content.visible = True
    _right_sidebar.visible = True
    _reset_element_layout(_sidebar)
    _reset_element_layout(_main_content)
    _reset_element_layout(_right_sidebar)
    _content_area.layout_node.set_flex_direction("row")
    _content_area.layout_node.set_align_items("stretch")
    tw = renderer.terminal_width
    side_w = max(12, int(tw * 0.15))
    _sidebar.layout_node.set_flex_basis(side_w)
    _sidebar.layout_node.set_flex_grow(0)
    _sidebar.layout_node.set_width(side_w)
    _sidebar.layout_node.set_height("auto")
    if _sidebar_text:
        _sidebar_text.set_content("LEFT")
    _sidebar.backgroundColor = "#dc2626"
    _main_content.layout_node.set_flex_basis("auto")
    _main_content.layout_node.set_flex_grow(1)
    _main_content.layout_node.set_width("auto")
    _main_content.layout_node.set_height("auto")
    if _main_content_text:
        _main_content_text.set_content("CENTER")
    _main_content.backgroundColor = "#059669"
    _right_sidebar.layout_node.set_flex_basis(side_w)
    _right_sidebar.layout_node.set_flex_grow(0)
    _right_sidebar.layout_node.set_width(side_w)
    _right_sidebar.layout_node.set_height("auto")
    if _right_sidebar_text:
        _right_sidebar_text.set_content("RIGHT")
    _right_sidebar.backgroundColor = "#7c3aed"


LAYOUT_DEMOS = [
    ("Horizontal Layout", "Sidebar left, main right", _setup_horizontal),
    ("Vertical Layout", "Sidebar top, main below", _setup_vertical),
    ("Centered Layout", "Content centered", _setup_centered),
    ("Three Column", "Left, center, right", _setup_three_column),
]


def _next_demo() -> None:
    global _current_demo_index
    _current_demo_index = (_current_demo_index + 1) % len(LAYOUT_DEMOS)
    _apply_current_demo()


def _apply_current_demo() -> None:
    global _header_text, _current_demo_index, _autoplay_enabled, _renderer_ref
    if not _renderer_ref or not _header_text:
        return
    demo = LAYOUT_DEMOS[_current_demo_index]
    _header_text.set_content(
        f"{demo[0]} ({_current_demo_index + 1}/{len(LAYOUT_DEMOS)}) - {'AUTO' if _autoplay_enabled else 'MANUAL'}"
    )
    demo[2](_renderer_ref)
    _update_footer_text()


def _toggle_autoplay() -> None:
    global _autoplay_enabled
    _autoplay_enabled = not _autoplay_enabled
    if _autoplay_accum_ms:
        _autoplay_accum_ms[0] = 0.0  # reset timer when toggling
    _update_footer_text()


def _update_footer_text() -> None:
    global _footer_text, _autoplay_enabled
    if not _footer_text:
        return
    ap = "ON" if _autoplay_enabled else "OFF"
    _footer_text.set_content(f"SPACE: next | R: restart | P: autoplay ({ap}) | Ctrl+C: exit")


def _on_key(key_event: Any) -> None:
    global _autoplay_enabled, _current_demo_index
    # KeyEvent has .name / .char; dict has ["name"]/["char"]. Normalize single-char to lowercase.
    name = getattr(key_event, "name", None) or (key_event.get("name") if hasattr(key_event, "get") else None)
    if not name:
        name = getattr(key_event, "char", None) or (key_event.get("char") if hasattr(key_event, "get") else None)
    if name is not None and len(str(name)) == 1:
        name = str(name).lower()
    if name == "space":
        _next_demo()
    elif name == "r":
        _autoplay_enabled = False  # restart to first page and stop autoplay
        _current_demo_index = 0
        _apply_current_demo()
    elif name == "p":
        _toggle_autoplay()
        if _renderer_ref and hasattr(_renderer_ref, "schedule_render"):
            _renderer_ref.schedule_render()


def run(renderer: Any) -> None:
    global _header, _header_text, _content_area, _sidebar, _sidebar_text
    global _main_content, _main_content_text, _right_sidebar, _right_sidebar_text
    global _footer, _footer_text, _current_demo_index, _autoplay_enabled, _renderer_ref, _autoplay_frame_cb

    from pytui.components.box import Box
    from pytui.components.text import Text

    _renderer_ref = renderer
    renderer.set_background_color("#001122")

    _header = Box(renderer.context, {
        "id": "header",
        "z_index": 0,
        "width": "auto",
        "height": 3,
        "backgroundColor": "#3b82f6",
        "borderStyle": "single",
        "align_items": "center",
        "border": True,
    })
    _header_text = Text(renderer.context, {"id": "header-text", "content": "LAYOUT DEMO", "fg": "#ffffff", "bg": "transparent", "z_index": 1})
    _header.add(_header_text)

    _content_area = Box(renderer.context, {
        "id": "content-area",
        "z_index": 0,
        "width": "auto",
        "height": "auto",
        "flex_direction": "row",
        "flex_grow": 1,
        "flex_shrink": 1,
    })

    _sidebar = Box(renderer.context, {
        "id": "sidebar",
        "z_index": 0,
        "width": "auto",
        "height": "auto",
        "backgroundColor": "#64748b",
        "borderStyle": "single",
        "flex_grow": 0,
        "flex_shrink": 0,
        "flex_direction": "row",
        "align_items": "center",
        "justify_content": "center",
        "border": True,
    })
    _sidebar_text = Text(renderer.context, {"id": "sidebar-text", "content": "SIDEBAR", "fg": "#ffffff", "bg": "transparent", "z_index": 1})
    _sidebar.add(_sidebar_text)

    _main_content = Box(renderer.context, {
        "id": "main-content",
        "z_index": 0,
        "width": "auto",
        "height": "auto",
        "backgroundColor": "#919599",
        "borderStyle": "single",
        "flex_grow": 1,
        "flex_shrink": 1,
        "flex_direction": "row",
        "align_items": "center",
        "justify_content": "center",
        "border": True,
    })
    _main_content_text = Text(renderer.context, {"id": "main-content-text", "content": "MAIN CONTENT", "fg": "#1e293b", "bg": "transparent", "z_index": 1})
    _main_content.add(_main_content_text)

    _right_sidebar = Box(renderer.context, {
        "id": "right-sidebar",
        "z_index": 0,
        "width": "auto",
        "height": "auto",
        "backgroundColor": "#7c3aed",
        "borderStyle": "single",
        "flex_grow": 0,
        "flex_shrink": 0,
        "flex_direction": "row",
        "align_items": "center",
        "justify_content": "center",
        "border": True,
    })
    _right_sidebar_text = Text(renderer.context, {"id": "right-sidebar-text", "content": "RIGHT", "fg": "#ffffff", "bg": "transparent", "z_index": 1})
    _right_sidebar.add(_right_sidebar_text)

    _content_area.add(_sidebar)
    _content_area.add(_main_content)
    _content_area.add(_right_sidebar)
    _right_sidebar.visible = False

    _footer = Box(renderer.context, {
        "id": "footer",
        "z_index": 0,
        "height": 3,
        "backgroundColor": "#1e40af",
        "borderStyle": "single",
        "flex_grow": 0,
        "flex_shrink": 0,
        "flex_direction": "row",
        "align_items": "center",
        "justify_content": "center",
        "border": True,
    })
    _footer_text = Text(renderer.context, {"id": "footer-text", "content": "", "fg": "#ffffff", "bg": "transparent", "z_index": 1})
    _footer.add(_footer_text)

    renderer.root.add(_header)
    renderer.root.add(_content_area)
    renderer.root.add(_footer)

    _current_demo_index = 0
    _autoplay_enabled = False
    _autoplay_accum_ms[0] = 0.0
    _apply_current_demo()
    # Listen on renderer.events so we get the same keypress stream as the renderer (after _on_keypress)
    renderer.events.on("keypress", _on_key)
    # Autoplay: every 4s advance layout when autoplay is ON
    def _on_frame(delta_ms: float) -> None:
        if not _autoplay_enabled or not _autoplay_accum_ms:
            return
        _autoplay_accum_ms[0] += delta_ms
        if _autoplay_accum_ms[0] >= 4000.0:
            _autoplay_accum_ms[0] = 0.0
            _next_demo()
    _autoplay_frame_cb = _on_frame
    renderer.set_frame_callback(_on_frame)


def destroy(renderer: Any) -> None:
    global _header, _header_text, _content_area, _sidebar, _sidebar_text
    global _main_content, _main_content_text, _right_sidebar, _right_sidebar_text
    global _footer, _footer_text, _renderer_ref, _autoplay_frame_cb

    try:
        renderer.events.remove_listener("keypress", _on_key)
    except Exception:
        pass
    if _autoplay_frame_cb is not None and hasattr(renderer, "remove_frame_callback"):
        try:
            renderer.remove_frame_callback(_autoplay_frame_cb)
        except Exception:
            pass
    _autoplay_frame_cb = None

    root = renderer.root
    if _header:
        root.remove(_header.id)
    if _content_area:
        root.remove(_content_area.id)
    if _footer:
        root.remove(_footer.id)

    _header = None
    _header_text = None
    _content_area = None
    _sidebar = None
    _sidebar_text = None
    _main_content = None
    _main_content_text = None
    _right_sidebar = None
    _right_sidebar_text = None
    _footer = None
    _footer_text = None
    _renderer_ref = None
