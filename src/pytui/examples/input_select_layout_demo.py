# input_select_layout_demo.py - Aligns OpenTUI packages/core/src/examples/input-select-layout-demo.ts
# Input + Select layout: two Selects (Color, Size) and one Input; Tab/Shift+Tab to cycle focus.

from __future__ import annotations

from typing import Any

_header_box: Any = None
_header_text: Any = None
_select_container_box: Any = None
_select_container: Any = None
_left_select_box: Any = None
_left_select: Any = None
_right_select_box: Any = None
_right_select: Any = None
_input_container_box: Any = None
_input_container: Any = None
_input_label: Any = None
_text_input_box: Any = None
_text_input: Any = None
_footer_box: Any = None
_footer_text: Any = None
_current_focus_index = 0
_focusable_elements: list[Any] = []
_focusable_boxes: list[Any] = []

COLOR_OPTIONS = [
    {"name": "Red", "description": "A warm primary color", "value": "#ff0000"},
    {"name": "Blue", "description": "A cool primary color", "value": "#0066ff"},
    {"name": "Green", "description": "A natural color", "value": "#00aa00"},
    {"name": "Purple", "description": "A regal color", "value": "#8a2be2"},
    {"name": "Orange", "description": "A vibrant color", "value": "#ff8c00"},
    {"name": "Teal", "description": "A calming color", "value": "#008080"},
]

SIZE_OPTIONS = [
    {"name": "Small", "description": "Compact size (8px)", "value": 8},
    {"name": "Medium", "description": "Standard size (12px)", "value": 12},
    {"name": "Large", "description": "Big size (16px)", "value": 16},
    {"name": "Extra Large", "description": "Huge size (20px)", "value": 20},
]


def _update_display() -> None:
    if not _left_select or not _right_select or not _text_input or not _input_label:
        return
    color_opt = _left_select.get_selected_option()
    size_opt = _right_select.get_selected_option()
    input_val = (_text_input.value if _text_input else "") or ""
    display = "Enter your text:"
    if input_val:
        display += f' "{input_val}"'
    if color_opt:
        display += f" in {color_opt.name}"
    if size_opt:
        display += f" ({size_opt.name})"
    _input_label.set_content(display)


def _update_focus() -> None:
    for el in _focusable_elements:
        if el:
            el.blur()
    for box in _focusable_boxes:
        if box:
            box.blur()
    if _current_focus_index < len(_focusable_elements) and _focusable_elements[_current_focus_index]:
        _focusable_elements[_current_focus_index].focus()
    if _current_focus_index < len(_focusable_boxes) and _focusable_boxes[_current_focus_index]:
        _focusable_boxes[_current_focus_index].focus()


def _on_key(key_event: Any) -> None:
    global _current_focus_index
    name = getattr(key_event, "name", None) or (key_event.get("name") if hasattr(key_event, "get") else None)
    shift = getattr(key_event, "shift", False) or (key_event.get("shift") if hasattr(key_event, "get") else False)
    if name == "tab" or name == "backtab":
        n = len(_focusable_elements)
        if name == "backtab" or shift:
            _current_focus_index = (_current_focus_index - 1 + n) % n
        else:
            _current_focus_index = (_current_focus_index + 1) % n
        _update_focus()
        return


def run(renderer: Any) -> None:
    global _header_box, _header_text, _select_container_box, _select_container
    global _left_select_box, _left_select, _right_select_box, _right_select
    global _input_container_box, _input_container, _input_label, _text_input_box, _text_input
    global _footer_box, _footer_text, _current_focus_index, _focusable_elements, _focusable_boxes

    from pytui.components.box import Box
    from pytui.components.text import Text
    from pytui.components.input import Input, INPUT_EVENT, CHANGE_EVENT
    from pytui.components.select import Select, SELECTION_CHANGED, ITEM_SELECTED

    renderer.set_background_color("#001122")

    _header_box = Box(renderer.context, {
        "id": "header-box", "z_index": 0, "width": "auto", "height": 3,
        "backgroundColor": "#3b82f6", "border_style": "single", "border_color": "#2563eb",
        "flex_grow": 0, "flex_shrink": 0, "border": True,
    })
    _header_text = Text(renderer.context, {
        "id": "header", "content": "INPUT & SELECT LAYOUT DEMO",
        "fg": "#ffffff", "bg": "transparent", "z_index": 1, "flex_grow": 1, "flex_shrink": 1,
    })
    _header_box.add(_header_text)

    _select_container_box = Box(renderer.context, {
        "id": "select-container-box", "z_index": 0, "width": "auto", "height": "auto",
        "flex_grow": 1, "flex_shrink": 1, "min_height": 10,
        "backgroundColor": "#1e293b", "border_style": "single", "border_color": "#475569", "border": True,
    })
    _select_container = Box(renderer.context, {
        "id": "select-container", "z_index": 1, "width": "auto", "height": "auto",
        "flex_direction": "row", "flex_grow": 1, "flex_shrink": 1,
    })
    _select_container_box.add(_select_container)

    _left_select_box = Box(renderer.context, {
        "id": "color-select-box", "z_index": 0, "width": "auto", "height": "auto", "min_height": 8,
        "border_style": "single", "border_color": "#475569", "focused_border_color": "#3b82f6",
        "title": "Color Selection", "title_alignment": "center",
        "flex_grow": 1, "flex_shrink": 1, "backgroundColor": "transparent", "border": True,
    })
    _left_select = Select(renderer.context, {
        "id": "color-select", "z_index": 1, "width": "auto", "height": "auto", "min_height": 6,
        "options": COLOR_OPTIONS,
        "backgroundColor": "#1e293b", "focusedBackgroundColor": "#2d3748",
        "textColor": "#e2e8f0", "focusedTextColor": "#f7fafc",
        "selectedBackgroundColor": "#3b82f6", "selectedTextColor": "#ffffff",
        "descriptionColor": "#94a3b8", "selectedDescriptionColor": "#cbd5e1",
        "show_scroll_indicator": True, "wrap_selection": True, "show_description": True,
        "flex_grow": 1, "flex_shrink": 1,
    })
    _left_select_box.add(_left_select)

    _right_select_box = Box(renderer.context, {
        "id": "size-select-box", "z_index": 0, "width": "auto", "height": "auto", "min_height": 8,
        "border_style": "single", "border_color": "#475569", "focused_border_color": "#059669",
        "title": "Size Selection", "title_alignment": "center",
        "flex_grow": 1, "flex_shrink": 1, "backgroundColor": "transparent", "border": True,
    })
    _right_select = Select(renderer.context, {
        "id": "size-select", "z_index": 1, "width": "auto", "height": "auto", "min_height": 6,
        "options": SIZE_OPTIONS,
        "backgroundColor": "#1e293b", "focusedBackgroundColor": "#2d3748",
        "textColor": "#e2e8f0", "focusedTextColor": "#f7fafc",
        "selectedBackgroundColor": "#059669", "selectedTextColor": "#ffffff",
        "descriptionColor": "#94a3b8", "selectedDescriptionColor": "#cbd5e1",
        "show_scroll_indicator": True, "wrap_selection": True, "show_description": True,
        "flex_grow": 1, "flex_shrink": 1,
    })
    _right_select_box.add(_right_select)

    _input_container_box = Box(renderer.context, {
        "id": "input-container-box", "z_index": 0, "width": "auto", "height": 7,
        "flex_grow": 0, "flex_shrink": 0,
        "backgroundColor": "#0f172a", "border_style": "single", "border_color": "#334155", "border": True,
    })
    _input_container = Box(renderer.context, {
        "id": "input-container", "z_index": 1, "width": "auto", "height": "auto",
        "flex_direction": "column", "flex_grow": 1, "flex_shrink": 1,
    })
    _input_container_box.add(_input_container)

    _input_label = Text(renderer.context, {
        "id": "input-label", "content": "Enter your text:",
        "fg": "#f1f5f9", "bg": "#0f172a", "z_index": 0, "flex_grow": 0, "flex_shrink": 0,
    })
    _text_input_box = Box(renderer.context, {
        "id": "text-input-box", "z_index": 0, "width": "auto", "height": 3,
        "border_style": "single", "border_color": "#475569", "focused_border_color": "#eab308",
        "flex_grow": 0, "flex_shrink": 0, "margin_top": 1, "backgroundColor": "transparent", "border": True,
    })
    _text_input = Input(renderer.context, {
        "id": "text-input", "z_index": 1, "width": "auto", "height": 1,
        "placeholder": "Type something here...",
        "backgroundColor": "#1e293b", "focusedBackgroundColor": "#334155",
        "textColor": "#f1f5f9", "focusedTextColor": "#ffffff",
        "placeholderColor": "#64748b", "cursorColor": "#f1f5f9",
        "max_length": 100, "flex_grow": 1, "flex_shrink": 1,
    })
    _text_input_box.add(_text_input)
    _input_container.add(_input_label)
    _input_container.add(_text_input_box)

    _footer_box = Box(renderer.context, {
        "id": "footer-box", "z_index": 0, "width": "auto", "height": 3,
        "backgroundColor": "#1e40af", "border_style": "single", "border_color": "#1d4ed8",
        "flex_grow": 0, "flex_shrink": 0, "border": True,
    })
    _footer_text = Text(renderer.context, {
        "id": "footer",
        "content": "TAB: focus next | SHIFT+TAB: focus prev | ARROWS/JK: navigate | ESC: quit",
        "fg": "#dbeafe", "bg": "transparent", "z_index": 1, "flex_grow": 1, "flex_shrink": 1,
    })
    _footer_box.add(_footer_text)

    _select_container.add(_left_select_box)
    _select_container.add(_right_select_box)

    renderer.root.add(_header_box)
    renderer.root.add(_select_container_box)
    renderer.root.add(_input_container_box)
    renderer.root.add(_footer_box)

    _focusable_elements = [_left_select, _right_select, _text_input]
    _focusable_boxes = [_left_select_box, _right_select_box, _text_input_box]

    def _on_selection_changed(*_args: Any) -> None:
        _update_display()

    def _on_item_selected(*_args: Any) -> None:
        _update_display()

    def _on_input_change(_val: Any) -> None:
        _update_display()

    _left_select.on(SELECTION_CHANGED, _on_selection_changed)
    _left_select.on(ITEM_SELECTED, _on_item_selected)
    _right_select.on(SELECTION_CHANGED, _on_selection_changed)
    _right_select.on(ITEM_SELECTED, _on_item_selected)
    _text_input.on(INPUT_EVENT, _on_input_change)
    _text_input.on(CHANGE_EVENT, _on_input_change)

    renderer.events.on("keypress", _on_key)
    _update_focus()
    _update_display()


def destroy(renderer: Any) -> None:
    global _header_box, _header_text, _select_container_box, _select_container
    global _left_select_box, _left_select, _right_select_box, _right_select
    global _input_container_box, _input_container, _input_label, _text_input_box, _text_input
    global _footer_box, _footer_text, _current_focus_index, _focusable_elements, _focusable_boxes

    try:
        renderer.events.remove_listener("keypress", _on_key)
    except Exception:
        pass
    for el in _focusable_elements:
        try:
            if el:
                el.blur()
        except Exception:
            pass
    root = renderer.root
    if _header_box:
        root.remove(_header_box.id)
    if _select_container_box:
        root.remove(_select_container_box.id)
    if _input_container_box:
        root.remove(_input_container_box.id)
    if _footer_box:
        root.remove(_footer_box.id)
    _header_box = None
    _header_text = None
    _select_container_box = None
    _select_container = None
    _left_select_box = None
    _left_select = None
    _right_select_box = None
    _right_select = None
    _input_container_box = None
    _input_container = None
    _input_label = None
    _text_input_box = None
    _text_input = None
    _footer_box = None
    _footer_text = None
    _current_focus_index = 0
    _focusable_elements = []
    _focusable_boxes = []
