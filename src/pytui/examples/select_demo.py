# select_demo.py - Aligns OpenTUI packages/core/src/examples/select-demo.ts
# Select list with keyboard nav, descriptions, scroll indicator, wrap; F/D/S/W toggles, status display.

from __future__ import annotations

from typing import Any

_select_element: Any = None
_key_legend_display: Any = None
_status_display: Any = None
_parent_container: Any = None
_last_action_text = "Welcome to Select demo! Use the controls to test features."
_last_action_color = "#FFCC00"
_keyboard_handler_ref: Any = None

SELECT_OPTIONS = [
    {"name": "Home", "description": "Navigate to the home page", "value": "home"},
    {"name": "Profile", "description": "View and edit your user profile", "value": "profile"},
    {"name": "Settings", "description": "Configure application preferences", "value": "settings"},
    {"name": "Dashboard", "description": "View analytics and key metrics", "value": "dashboard"},
    {"name": "Projects", "description": "Manage your active projects", "value": "projects"},
    {"name": "Reports", "description": "Generate and view detailed reports", "value": "reports"},
    {"name": "Users", "description": "Manage user accounts and permissions", "value": "users"},
    {"name": "Analytics", "description": "Deep dive into usage analytics", "value": "analytics"},
    {"name": "Tools", "description": "Access various utility tools", "value": "tools"},
    {"name": "API Documentation", "description": "Browse API endpoints and examples", "value": "api"},
    {"name": "Help Center", "description": "Find answers to common questions", "value": "help"},
    {"name": "Support", "description": "Contact our support team", "value": "support"},
    {"name": "Billing", "description": "Manage your subscription and billing", "value": "billing"},
    {"name": "Integrations", "description": "Connect with third-party services", "value": "integrations"},
    {"name": "Security", "description": "Configure security settings", "value": "security"},
    {"name": "Notifications", "description": "Manage your notification preferences", "value": "notifications"},
    {"name": "Backup", "description": "Backup and restore your data", "value": "backup"},
    {"name": "Import/Export", "description": "Import or export your data", "value": "import-export"},
    {"name": "Advanced Settings", "description": "Configure advanced options", "value": "advanced"},
    {"name": "About", "description": "Learn more about this application", "value": "about"},
]


def _update_displays() -> None:
    global _last_action_text, _last_action_color
    if not _select_element:
        return
    scroll_ind = "on" if _select_element.show_scroll_indicator else "off"
    desc = "on" if _select_element.show_description else "off"
    wrap = "on" if _select_element.wrap_selection else "off"

    key_legend_text = (
        "Key Controls:\n"
        "↑/↓ or j/k: Navigate items\n"
        "Shift+↑/↓: Fast scroll\n"
        "Enter: Select item\n"
        "F: Toggle focus\n"
        "D: Toggle descriptions\n"
        "S: Toggle scroll indicator\n"
        "W: Toggle wrap selection"
    )
    if _key_legend_display:
        _key_legend_display.set_content(key_legend_text)

    current = _select_element.get_selected_option()
    selection_text = (
        f"Selection: {current.name} ({current.value}) - Index: {_select_element.get_selected_index()}"
        if current
        else "No selection"
    )
    focus_text = "Select element is FOCUSED" if _select_element.focused else "Select element is BLURRED"
    focus_color = "#00FF00" if _select_element.focused else "#FF0000"

    status_text = (
        f"{selection_text}\n\n"
        f"{focus_text}\n\n"
        f"Scroll indicator: {scroll_ind} | Description: {desc} | Wrap: {wrap}\n\n"
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
    if not _select_element:
        return
    if name == "f":
        if _select_element.focused:
            _select_element.blur()
            _last_action_text = "Focus removed from select element"
        else:
            _select_element.focus()
            _last_action_text = "Select element focused"
        _last_action_color = "#FFCC00"
        _update_displays()
    elif name == "d":
        new_state = not _select_element.show_description
        _select_element.show_description = new_state
        _select_element.request_render()
        _last_action_text = f"Descriptions {'enabled' if new_state else 'disabled'}"
        _last_action_color = "#FFCC00"
        _update_displays()
    elif name == "s":
        new_state = not _select_element.show_scroll_indicator
        _select_element.show_scroll_indicator = new_state
        _select_element.request_render()
        _last_action_text = f"Scroll indicator {'enabled' if new_state else 'disabled'}"
        _last_action_color = "#FFCC00"
        _update_displays()
    elif name == "w":
        new_state = not _select_element.wrap_selection
        _select_element.wrap_selection = new_state
        _select_element.request_render()
        _last_action_text = f"Wrap selection {'enabled' if new_state else 'disabled'}"
        _last_action_color = "#FFCC00"
        _update_displays()


def run(renderer: Any) -> None:
    global _select_element, _key_legend_display, _status_display, _parent_container, _keyboard_handler_ref

    from pytui.components.box import Box
    from pytui.components.text import Text
    from pytui.components.select import Select, SELECTION_CHANGED, ITEM_SELECTED
    from pytui.core.renderable import FOCUSED, BLURRED

    renderer.set_background_color("#001122")

    _parent_container = Box(renderer.context, {"id": "parent-container", "z_index": 10, "flex_direction": "column", "width": "auto", "height": "auto"})
    renderer.root.add(_parent_container)

    top_row = Box(renderer.context, {"id": "top-row", "flex_direction": "row", "width": "auto", "height": "auto", "flex_grow": 0})
    _parent_container.add(top_row)

    _select_element = Select(renderer.context, {
        "id": "demo-select",
        "width": 50,
        "height": 20,
        "options": SELECT_OPTIONS,
        "z_index": 100,
        "backgroundColor": "#1e293b",
        "focusedBackgroundColor": "#2d3748",
        "textColor": "#e2e8f0",
        "focusedTextColor": "#f7fafc",
        "selectedBackgroundColor": "#3b82f6",
        "selectedTextColor": "#ffffff",
        "descriptionColor": "#94a3b8",
        "selectedDescriptionColor": "#cbd5e1",
        "show_description": True,
        "show_scroll_indicator": True,
        "wrap_selection": False,
        "fast_scroll_step": 5,
    })
    top_row.add(_select_element)

    _key_legend_display = Text(renderer.context, {
        "id": "key-legend",
        "content": "",
        "width": 40,
        "height": 9,
        "z_index": 50,
        "fg": "#AAAAAA",
    })
    top_row.add(_key_legend_display)

    _status_display = Text(renderer.context, {
        "id": "status-display",
        "content": "",
        "width": 80,
        "height": 10,
        "z_index": 50,
        "fg": "#CCCCCC",
    })
    _parent_container.add(_status_display)

    def _on_selection_changed(_index: int, option: Any) -> None:
        global _last_action_text, _last_action_color
        _last_action_text = f'Navigation: Moved to "{option.name}"'
        _last_action_color = "#FFCC00"
        _update_displays()

    def _on_item_selected(_index: int, option: Any) -> None:
        global _last_action_text, _last_action_color
        _last_action_text = f"*** ACTIVATED: {option.name} ({option.value}) ***"
        _last_action_color = "#FF00FF"
        _update_displays()

    def _on_focused() -> None:
        _update_displays()

    def _on_blurred() -> None:
        _update_displays()

    _select_element.on(SELECTION_CHANGED, _on_selection_changed)
    _select_element.on(ITEM_SELECTED, _on_item_selected)
    _select_element.on(FOCUSED, _on_focused)
    _select_element.on(BLURRED, _on_blurred)

    renderer.events.on("keypress", _on_key)
    _select_element.focus()
    _update_displays()


def destroy(renderer: Any) -> None:
    global _select_element, _key_legend_display, _status_display, _parent_container, _keyboard_handler_ref

    try:
        renderer.events.remove_listener("keypress", _on_key)
    except Exception:
        pass
    if _select_element:
        try:
            _select_element.blur()
        except Exception:
            pass
        _select_element = None
    if _parent_container and renderer.root:
        renderer.root.remove(_parent_container.id)
    _parent_container = None
    _key_legend_display = None
    _status_display = None
    _keyboard_handler_ref = None
