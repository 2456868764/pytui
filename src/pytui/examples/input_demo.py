# input_demo.py - Aligns OpenTUI packages/core/src/examples/input-demo.ts
# Multiple inputs (name, email, password, comment), Tab/Shift+Tab to navigate, validation, status display.

from __future__ import annotations

import re
from typing import Any

_container: Any = None
_header_text: Any = None
_name_input: Any = None
_email_input: Any = None
_password_input: Any = None
_comment_input: Any = None
_inputs: list[Any] = []
_key_legend: Any = None
_status_display: Any = None
_active_index = 0
_last_action = "Welcome! Use Tab to navigate between fields."
_renderer_ref: Any = None


def _get_active_input():
    if not _inputs or _active_index < 0 or _active_index >= len(_inputs):
        return None
    return _inputs[_active_index]


def _get_input_name(inp: Any) -> str:
    if inp is _name_input:
        return "Name"
    if inp is _email_input:
        return "Email"
    if inp is _password_input:
        return "Password"
    if inp is _comment_input:
        return "Comment"
    return "Unknown"


def _validate_name(value: str) -> bool:
    return len(value) >= 2


def _validate_email(value: str) -> bool:
    return bool(re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", value))


def _validate_password(value: str) -> bool:
    return len(value) >= 6


def _update_displays() -> None:
    global _last_action
    if not _key_legend or not _status_display:
        return
    _key_legend.set_content(
        "Key: Tab/Shift+Tab navigate | Enter submit | Ctrl+R reset all"
    )
    name_val = (_name_input.value if _name_input else "") or ""
    email_val = (_email_input.value if _email_input else "") or ""
    pass_val = (_password_input.value if _password_input else "") or ""
    comment_val = (_comment_input.value if _comment_input else "") or ""
    active = _get_active_input()
    active_name = _get_input_name(active) if active else ""
    n_st = "FOCUSED" if _name_input and _name_input.focused else "blurred"
    e_st = "FOCUSED" if _email_input and _email_input.focused else "blurred"
    p_st = "FOCUSED" if _password_input and _password_input.focused else "blurred"
    c_st = "FOCUSED" if _comment_input and _comment_input.focused else "blurred"
    n_ok = "Valid" if _validate_name(name_val) else "Invalid (min 2)"
    e_ok = "Valid" if _validate_email(email_val) else "Invalid format"
    p_ok = "Valid" if _validate_password(pass_val) else "Invalid (min 6)"
    pass_mask = "*" * len(pass_val) if pass_val else ""
    status = (
        f"Name: \"{name_val}\" ({n_st})\n"
        f"Email: \"{email_val}\" ({e_st})\n"
        f"Password: \"{pass_mask}\" ({p_st})\n"
        f"Comment: \"{comment_val}\" ({c_st})\n"
        f"Active: {active_name}\n"
        f"Name {n_ok} | Email {e_ok} | Password {p_ok}\n"
        f"{_last_action}"
    )
    _status_display.set_content(status)


def _navigate_to(index: int) -> None:
    global _active_index, _last_action
    cur = _get_active_input()
    if cur:
        cur.blur()
    _active_index = max(0, min(index, len(_inputs) - 1))
    nxt = _get_active_input()
    if nxt:
        nxt.focus()
    _last_action = f"Switched to {_get_input_name(nxt)} input"
    _update_displays()


def _reset_inputs() -> None:
    global _last_action
    if _name_input:
        _name_input.value = ""
    if _email_input:
        _email_input.value = ""
    if _password_input:
        _password_input.value = ""
    if _comment_input:
        _comment_input.value = ""
    _last_action = "All inputs reset to empty"
    _update_displays()


def _on_key(key_event: Any) -> None:
    global _active_index
    name = getattr(key_event, "name", None) or (key_event.get("name") if hasattr(key_event, "get") else None)
    if not name:
        name = getattr(key_event, "char", None) or (key_event.get("char") if hasattr(key_event, "get") else None)
    if name is not None and len(str(name)) == 1:
        name = str(name).lower()
    shift = getattr(key_event, "shift", False) or (key_event.get("shift") if hasattr(key_event, "get") else False)
    ctrl = getattr(key_event, "ctrl", False) or (key_event.get("ctrl") if hasattr(key_event, "get") else False)
    seq = getattr(key_event, "sequence", None) or (key_event.get("sequence") if hasattr(key_event, "get") else None)
    is_backtab = (name == "backtab" or shift and name == "tab" or seq == "\x1b[Z")
    if name == "tab" or name == "backtab" or (seq == "\x1b[Z"):
        if is_backtab:
            _navigate_to(_active_index - 1)
        else:
            _navigate_to(_active_index + 1)
        return
    if ctrl and name == "r":
        _reset_inputs()
        return
    if name in ("enter", "return"):
        global _last_action
        name_val = (_name_input.value if _name_input else "") or ""
        email_val = (_email_input.value if _email_input else "") or ""
        pass_val = (_password_input.value if _password_input else "") or ""
        n_ok = _validate_name(name_val)
        e_ok = _validate_email(email_val)
        p_ok = _validate_password(pass_val)
        if n_ok and e_ok and p_ok:
            _last_action = "Form submitted (all valid)."
        else:
            _last_action = "Form validation failed (fix Name/Email/Password and try again)."
        _update_displays()
        return


def _on_input_change(_value: Any) -> None:
    _update_displays()


def run(renderer: Any) -> None:
    global _container, _header_text, _name_input, _email_input, _password_input, _comment_input
    global _inputs, _key_legend, _status_display, _active_index, _last_action, _renderer_ref

    from pytui.components.box import Box
    from pytui.components.text import Text
    from pytui.components.input import Input

    _renderer_ref = renderer
    renderer.set_background_color("#001122")

    _container = Box(renderer.context, {"id": "input-demo-container", "width": "auto", "height": "auto", "flex_direction": "column"})
    _header_text = Text(renderer.context, {"id": "header", "content": "Input Demo", "fg": "#ffffff", "width": 60, "height": 1})
    _container.add(_header_text)

    _name_input = Input(renderer.context, {
        "id": "name-input", "width": 40, "height": 1, "placeholder": "Enter your name...",
        "value": "", "max_length": 50, "fg": "#ffffff", "bg": "#001122",
    })
    _email_input = Input(renderer.context, {
        "id": "email-input", "width": 40, "height": 1, "placeholder": "Enter your email...",
        "value": "", "max_length": 100, "fg": "#ffffff", "bg": "#001122",
    })
    _password_input = Input(renderer.context, {
        "id": "password-input", "width": 40, "height": 1, "placeholder": "Enter password...",
        "value": "", "max_length": 50, "fg": "#ffffff", "bg": "#001122",
    })
    _comment_input = Input(renderer.context, {
        "id": "comment-input", "width": 60, "height": 1, "placeholder": "Enter a comment...",
        "value": "", "max_length": 200, "fg": "#ffffff", "bg": "#001122",
    })
    _inputs = [_name_input, _email_input, _password_input, _comment_input]

    for inp in _inputs:
        inp.on("input", _on_input_change)
    _container.add(_name_input)
    _container.add(_email_input)
    _container.add(_password_input)
    _container.add(_comment_input)

    _key_legend = Text(renderer.context, {"id": "key-legend", "content": "", "fg": "#aaaaaa", "width": 50, "height": 4})
    _container.add(_key_legend)
    _status_display = Text(renderer.context, {"id": "status", "content": "", "fg": "#cccccc", "width": 70, "height": 12})
    _container.add(_status_display)

    renderer.root.add(_container)
    _active_index = 0
    renderer.events.on("keypress", _on_key)  # register before focus so demo handles Tab before Input
    _inputs[0].focus()
    _update_displays()


def destroy(renderer: Any) -> None:
    global _container, _header_text, _name_input, _email_input, _password_input, _comment_input
    global _inputs, _key_legend, _status_display, _renderer_ref

    try:
        renderer.events.remove_listener("keypress", _on_key)
    except Exception:
        pass
    for inp in _inputs:
        try:
            inp.blur()
            inp.remove_all_listeners("input")
        except Exception:
            pass
    if _container and renderer.root:
        renderer.root.remove(_container.id)
    _container = None
    _header_text = None
    _name_input = None
    _email_input = None
    _password_input = None
    _comment_input = None
    _inputs.clear()
    _key_legend = None
    _status_display = None
    _renderer_ref = None
