# tab_select_demo.py - Aligns OpenTUI packages/core/src/examples/tab-select-demo.ts
# Tab selection with left/right arrows, descriptions, underline; F/D/U/W toggles, status display.

from __future__ import annotations

from typing import Any

_tab_element: Any = None
_key_legend_display: Any = None
_status_display: Any = None
_parent_container: Any = None
_last_action_text = "Welcome to TabSelect demo! Use Left/Right or [/] to move, Enter to select."
_last_action_color = "#FFCC00"

TAB_OPTIONS = [
    {"name": "Overview", "description": "Dashboard and summary", "value": "overview"},
    {"name": "Settings", "description": "Configure preferences", "value": "settings"},
    {"name": "Profile", "description": "User profile and account", "value": "profile"},
    {"name": "Security", "description": "Security and privacy", "value": "security"},
    {"name": "Billing", "description": "Subscription and payments", "value": "billing"},
    {"name": "Integrations", "description": "Connected services", "value": "integrations"},
    {"name": "API", "description": "API keys and docs", "value": "api"},
    {"name": "Help", "description": "Documentation and support", "value": "help"},
]


def _update_displays() -> None:
    if not _tab_element:
        return
    desc = "on" if _tab_element.show_description else "off"
    underline = "on" if _tab_element.show_underline else "off"
    wrap = "on" if _tab_element.wrap_selection else "off"

    key_legend_text = (
        "Key Controls:\n"
        "Left/Right or [/]: Move between tabs\n"
        "Enter: Select (activate) current tab\n"
        "F: Toggle focus\n"
        "D: Toggle descriptions\n"
        "U: Toggle underline\n"
        "W: Toggle wrap selection"
    )
    if _key_legend_display:
        _key_legend_display.set_content(key_legend_text)

    opt = _tab_element.get_selected_option()
    selection_text = (
        f"Tab: {opt.name} ({opt.value}) - Index: {_tab_element.get_selected_index()}"
        if opt
        else "No selection"
    )
    focus_text = "TabSelect is FOCUSED" if _tab_element.focused else "TabSelect is BLURRED"
    focus_color = "#00FF00" if _tab_element.focused else "#FF0000"

    status_text = (
        f"{selection_text}\n\n"
        f"{focus_text}\n\n"
        f"Description: {desc} | Underline: {underline} | Wrap: {wrap}\n\n"
        f"{_last_action_text}"
    )
    if _status_display:
        _status_display.set_content(status_text)


def _on_key(key_event: Any) -> None:
    global _last_action_text, _last_action_color
    name = getattr(key_event, "name", None) or (key_event.get("name") if hasattr(key_event, "get") else None)
    if not name:
        return
    name = str(name).lower()
    if not _tab_element:
        return
    if name == "f":
        if _tab_element.focused:
            _tab_element.blur()
            _last_action_text = "Focus removed from TabSelect"
        else:
            _tab_element.focus()
            _last_action_text = "TabSelect focused"
        _last_action_color = "#FFCC00"
        _update_displays()
    elif name == "d":
        new_state = not _tab_element.show_description
        _tab_element.show_description = new_state
        _tab_element.request_render()
        _last_action_text = f"Descriptions {'enabled' if new_state else 'disabled'}"
        _last_action_color = "#FFCC00"
        _update_displays()
    elif name == "u":
        new_state = not _tab_element.show_underline
        _tab_element.show_underline = new_state
        _tab_element.request_render()
        _last_action_text = f"Underline {'enabled' if new_state else 'disabled'}"
        _last_action_color = "#FFCC00"
        _update_displays()
    elif name == "w":
        new_state = not _tab_element.wrap_selection
        _tab_element.wrap_selection = new_state
        _tab_element.request_render()
        _last_action_text = f"Wrap selection {'enabled' if new_state else 'disabled'}"
        _last_action_color = "#FFCC00"
        _update_displays()


def run(renderer: Any) -> None:
    global _tab_element, _key_legend_display, _status_display, _parent_container

    from pytui.components.box import Box
    from pytui.components.text import Text
    from pytui.components.tab_select import TabSelect, SELECTION_CHANGED, ITEM_SELECTED
    from pytui.core.renderable import FOCUSED, BLURRED

    renderer.set_background_color("#0f172a")

    _parent_container = Box(
        renderer.context,
        {
            "id": "parent-container",
            "z_index": 10,
            "flex_direction": "column",
            "width": "auto",
            "height": "auto",
        },
    )
    renderer.root.add(_parent_container)

    top_row = Box(
        renderer.context,
        {
            "id": "top-row",
            "flex_direction": "row",
            "width": "auto",
            "height": "auto",
            "flex_grow": 0,
        },
    )
    _parent_container.add(top_row)

    _tab_element = TabSelect(
        renderer.context,
        {
            "id": "demo-tab-select",
            "width": 80,
            "tab_width": 14,
            "options": TAB_OPTIONS,
            "z_index": 100,
            "backgroundColor": "#1e293b",
            "focusedBackgroundColor": "#334155",
            "textColor": "#e2e8f0",
            "focusedTextColor": "#f8fafc",
            "selectedBackgroundColor": "#3b82f6",
            "selectedTextColor": "#ffffff",
            "selectedDescriptionColor": "#cbd5e1",
            "show_description": True,
            "show_underline": True,
            "show_scroll_arrows": True,
            "wrap_selection": False,
        },
    )
    top_row.add(_tab_element)

    _key_legend_display = Text(
        renderer.context,
        {
            "id": "key-legend",
            "content": "",
            "width": 36,
            "height": 10,
            "z_index": 50,
            "fg": "#94a3b8",
        },
    )
    top_row.add(_key_legend_display)

    _status_display = Text(
        renderer.context,
        {
            "id": "status-display",
            "content": "",
            "width": 80,
            "height": 10,
            "z_index": 50,
            "fg": "#cbd5e1",
        },
    )
    _parent_container.add(_status_display)

    def _on_selection_changed(_index: int, option: Any) -> None:
        global _last_action_text, _last_action_color
        _last_action_text = f'Navigated to tab "{option.name}"'
        _last_action_color = "#FFCC00"
        _update_displays()

    def _on_item_selected(_index: int, option: Any) -> None:
        global _last_action_text, _last_action_color
        _last_action_text = f"*** ACTIVATED: {option.name} ({option.value}) ***"
        _last_action_color = "#a78bfa"
        _update_displays()

    def _on_focused() -> None:
        _update_displays()

    def _on_blurred() -> None:
        _update_displays()

    _tab_element.on(SELECTION_CHANGED, _on_selection_changed)
    _tab_element.on(ITEM_SELECTED, _on_item_selected)
    _tab_element.on(FOCUSED, _on_focused)
    _tab_element.on(BLURRED, _on_blurred)

    renderer.events.on("keypress", _on_key)
    _tab_element.focus()
    _update_displays()


def destroy(renderer: Any) -> None:
    global _tab_element, _key_legend_display, _status_display, _parent_container

    try:
        renderer.events.remove_listener("keypress", _on_key)
    except Exception:
        pass
    if _tab_element:
        try:
            _tab_element.blur()
        except Exception:
            pass
        _tab_element = None
    if _parent_container and renderer.root:
        renderer.root.remove(_parent_container.id)
    _parent_container = None
    _key_legend_display = None
    _status_display = None
