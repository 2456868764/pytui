# pytui.components.input - Aligns OpenTUI packages/core/src/renderables/Input.ts
# Single-line input: value, maxLength, placeholder, insertText (strip newlines), focus/blur (CHANGE),
# submit (ENTER), deleteCharBackward/deleteChar, deleteCharacter, handlePaste, keyBindings, keyAliasMap,
# onKeyDown, onPaste, preventDefault, focusable; events INPUT, CHANGE, ENTER.

from __future__ import annotations

import re
from typing import Any, Callable

from pytui.core.buffer import Cell, OptimizedBuffer
from pytui.core.renderable import Renderable
from pytui.lib import parse_color_to_tuple
from pytui.lib.keymapping import (
    KeyAliasMap,
    KeyBinding,
    build_key_bindings_map,
    default_key_aliases,
    get_key_binding_key,
    merge_key_aliases,
    merge_key_bindings,
)

# Align with OpenTUI InputRenderableEvents
INPUT_EVENT = "input"
CHANGE_EVENT = "change"
ENTER_EVENT = "enter"

# Default key bindings: return/linefeed -> submit; align OpenTUI Input (overrides Textarea newline)
DEFAULT_INPUT_KEY_BINDINGS: list[KeyBinding] = [
    {"name": "return", "action": "submit"},
    {"name": "linefeed", "action": "submit"},
    {"name": "left", "action": "move-left"},
    {"name": "right", "action": "move-right"},
    {"name": "home", "action": "move-home"},
    {"name": "end", "action": "move-end"},
    {"name": "backspace", "action": "delete-backward"},
    {"name": "delete", "action": "delete-forward"},
]

_DEFAULT_OPTIONS = {
    "placeholder": "",
    "maxLength": 1000,
    "value": "",
}


def _key_id_from_event(key: Any) -> str:
    """Build key binding key from key event (name:ctrl:shift:meta:super)."""
    name = getattr(key, "name", None) or (key.get("name") if hasattr(key, "get") else None) or ""
    ctrl = getattr(key, "ctrl", None) or (key.get("ctrl") if hasattr(key, "get") else False)
    shift = getattr(key, "shift", None) or (key.get("shift") if hasattr(key, "get") else False)
    meta = getattr(key, "meta", None) or (key.get("meta") if hasattr(key, "get") else False)
    super_k = getattr(key, "super_key", None) or getattr(key, "super", None) or (key.get("super") if hasattr(key, "get") else False)
    return get_key_binding_key({
        "name": (name or "").lower(),
        "ctrl": bool(ctrl),
        "shift": bool(shift),
        "meta": bool(meta),
        "super": bool(super_k),
    })


class Input(Renderable):
    """Single-line input. Aligns OpenTUI InputRenderable: extends Textarea semantics with
    single-line (value, maxLength, placeholder, newLine() false, handlePaste strip newlines),
    value/plainText, cursorOffset, insertText, setText, submit, deleteCharBackward/deleteChar,
    deleteCharacter, keyBindings, keyAliasMap, onKeyDown, onPaste, focusable; events INPUT, CHANGE, ENTER.
    """

    def __init__(self, ctx: Any, options: dict[str, Any] | None = None) -> None:
        options = options or {}
        super().__init__(ctx, options)
        defaults = _DEFAULT_OPTIONS
        max_len = options.get("maxLength", options.get("max_length", defaults["maxLength"]))
        raw_value = options.get("value", defaults["value"])
        initial_value = re.sub(r"[\n\r]", "", str(raw_value))[:max_len]

        self._value = initial_value
        self._max_length = max_len
        self._cursor_pos = len(initial_value)
        self._last_committed_value = initial_value
        self._destroyed = False

        self._placeholder = options.get("placeholder", defaults["placeholder"])
        if not isinstance(self._placeholder, str):
            self._placeholder = str(self._placeholder) if self._placeholder else ""

        self.fg = parse_color_to_tuple(options.get("fg", options.get("textColor", "#ffffff")))
        self.bg = parse_color_to_tuple(options.get("bg", options.get("backgroundColor", "transparent")))
        foc_bg = options.get("focused_background_color", options.get("focusedBackgroundColor"))
        self._focused_bg = parse_color_to_tuple(foc_bg) if isinstance(foc_bg, str) else (foc_bg if foc_bg is not None else self.bg)
        foc_fg = options.get("focused_text_color", options.get("focusedTextColor"))
        self._focused_fg = parse_color_to_tuple(foc_fg) if isinstance(foc_fg, str) else (foc_fg if foc_fg is not None else self.fg)
        self.placeholder_color = parse_color_to_tuple(
            options.get("placeholder_color", options.get("placeholderColor")) or "#666666"
        )
        self._cursor_color = parse_color_to_tuple(
            options.get("cursor_color", options.get("cursorColor")) or "#ffffff"
        )
        cs = options.get("cursor_style", options.get("cursorStyle", "block"))
        self.cursor_style = cs.get("style", "block") if isinstance(cs, dict) else (cs if isinstance(cs, str) else "block")

        custom_bindings = options.get("keyBindings", options.get("key_bindings")) or []
        bindings_list = merge_key_bindings(
            DEFAULT_INPUT_KEY_BINDINGS,
            custom_bindings if isinstance(custom_bindings, list) else [],
        )
        alias_map = merge_key_aliases(
            default_key_aliases,
            options.get("keyAliasMap", options.get("key_alias_map")) or {},
        )
        self._key_map = build_key_bindings_map(bindings_list, alias_map)
        self._key_alias_map = alias_map
        self._on_key_down: Callable[[Any], None] | None = options.get("onKeyDown", options.get("on_key_down"))
        self._on_paste_cb: Callable[[Any], None] | None = options.get("onPaste", options.get("on_paste"))

        self._focusable = True

    @property
    def focusable(self) -> bool:
        return self._focusable

    @focusable.setter
    def focusable(self, value: bool) -> None:
        self._focusable = bool(value)

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, v: str) -> None:
        new_val = re.sub(r"[\n\r]", "", str(v))[: self._max_length]
        if self._value != new_val:
            self._value = new_val
            self._cursor_pos = len(self._value)
            self.request_render()
            self.emit(INPUT_EVENT, self._value)

    @property
    def plain_text(self) -> str:
        """Align OpenTUI plainText (same as value)."""
        return self._value

    @property
    def cursor_offset(self) -> int:
        """Align OpenTUI cursorOffset."""
        return self._cursor_pos

    @cursor_offset.setter
    def cursor_offset(self, pos: int) -> None:
        pos = max(0, min(pos, len(self._value)))
        if self._cursor_pos != pos:
            self._cursor_pos = pos
            self.request_render()

    @property
    def cursor_position(self) -> int:
        """Alias for cursor_offset."""
        return self._cursor_pos

    @cursor_position.setter
    def cursor_position(self, pos: int) -> None:
        self.cursor_offset = pos

    @property
    def cursor_pos(self) -> int:
        return self._cursor_pos

    @cursor_pos.setter
    def cursor_pos(self, pos: int) -> None:
        self.cursor_offset = pos

    def set_value(self, value: str) -> None:
        """Set value and move cursor to end. Backward compat / convenience."""
        self.value = value
        self._cursor_pos = len(self._value)

    @property
    def placeholder(self) -> str:
        return self._placeholder

    @placeholder.setter
    def placeholder(self, v: str) -> None:
        if self._placeholder != v:
            self._placeholder = str(v) if v is not None else ""
            self.request_render()

    @property
    def max_length(self) -> int:
        return self._max_length

    @max_length.setter
    def max_length(self, v: int) -> None:
        self._max_length = max(0, int(v))
        if len(self._value) > self._max_length:
            self._value = self._value[: self._max_length]
            self._cursor_pos = min(self._cursor_pos, len(self._value))
            self.request_render()
            self.emit(INPUT_EVENT, self._value)

    maxLength = max_length

    def new_line(self) -> bool:
        """Prevent newlines in single-line input. Align OpenTUI newLine() -> false."""
        return False

    def set_text(self, text: str) -> None:
        """Set full text; strip newlines, enforce maxLength. Align OpenTUI setText()."""
        self.value = text

    def insert_char(self, ch: str) -> None:
        """Insert single character. Convenience / align OpenTUI insertChar."""
        self.insert_text(ch)

    def insert_text(self, text: str) -> None:
        """Insert at cursor; strip newlines, enforce maxLength. Align OpenTUI insertText()."""
        sanitized = re.sub(r"[\n\r]", "", str(text))
        if not sanitized:
            return
        remaining = self._max_length - len(self._value)
        if remaining <= 0:
            return
        to_insert = sanitized[:remaining]
        self._value = self._value[: self._cursor_pos] + to_insert + self._value[self._cursor_pos :]
        self._cursor_pos += len(to_insert)
        self.request_render()
        self.emit(INPUT_EVENT, self._value)

    def delete_char_backward(self) -> bool:
        """Align OpenTUI deleteCharBackward(). Returns True if a char was deleted."""
        if self._cursor_pos <= 0:
            return False
        self._value = self._value[: self._cursor_pos - 1] + self._value[self._cursor_pos :]
        self._cursor_pos -= 1
        self.request_render()
        self.emit(INPUT_EVENT, self._value)
        return True

    def delete_char(self) -> bool:
        """Align OpenTUI deleteChar(). Returns True if a char was deleted."""
        if self._cursor_pos >= len(self._value):
            return False
        self._value = self._value[: self._cursor_pos] + self._value[self._cursor_pos + 1 :]
        self.request_render()
        self.emit(INPUT_EVENT, self._value)
        return True

    def delete_character(self, direction: str) -> None:
        """Align OpenTUI deleteCharacter('backward'|'forward')."""
        if direction == "backward":
            self.delete_char_backward()
        else:
            self.delete_char()

    def backspace(self) -> None:
        """Convenience; same as delete_char_backward."""
        self.delete_char_backward()

    def delete_forward(self) -> None:
        """Convenience; same as delete_char."""
        self.delete_char()

    def submit(self) -> bool:
        """Emit CHANGE if value changed, then ENTER. Align OpenTUI submit() -> true."""
        if self._value != self._last_committed_value:
            self._last_committed_value = self._value
            self.emit(CHANGE_EVENT, self._value)
        self.emit(ENTER_EVENT, self._value)
        return True

    def handle_paste(self, event: Any) -> None:
        """Strip newlines and insert. Align OpenTUI handlePaste()."""
        text = getattr(event, "text", None) or (event.get("text") if hasattr(event, "get") else "")
        sanitized = re.sub(r"[\n\r]", "", str(text))
        if sanitized:
            self.insert_text(sanitized)

    def focus(self) -> None:
        if not self.focused:
            r = getattr(self.ctx, "renderer", None)
            if r and getattr(r, "current_focused_renderable", None) is not None:
                prev = r.current_focused_renderable
                if prev is not self and getattr(prev, "focused", False):
                    prev.blur()
            if r and hasattr(r, "focus_renderable"):
                r.focus_renderable(self)
            super().focus()
            self._last_committed_value = self._value
            if r and getattr(r, "events", None):
                r.events.on("keypress", self._on_keypress)
                r.events.on("paste", self._on_paste)
            self.request_render()

    def blur(self) -> None:
        r = getattr(self.ctx, "renderer", None)
        if r and getattr(r, "events", None):
            try:
                r.events.remove_listener("keypress", self._on_keypress)
            except KeyError:
                pass
            try:
                r.events.remove_listener("paste", self._on_paste)
            except KeyError:
                pass
        if not self._destroyed and self._value != self._last_committed_value:
            self._last_committed_value = self._value
            self.emit(CHANGE_EVENT, self._value)
        super().blur()
        self.request_render()

    def _on_paste(self, event: Any) -> None:
        if not self.focused:
            return
        self.handle_paste(event)
        if self._on_paste_cb:
            self._on_paste_cb(event)

    def _action_for_key(self, key: Any) -> str | None:
        name = (getattr(key, "name", None) or (key.get("name") if hasattr(key, "get") else None) or "").strip().lower()
        if not name:
            return None
        resolved = self._key_alias_map.get(name, name)
        key_binding = {"name": resolved, "ctrl": getattr(key, "ctrl", False) or key.get("ctrl", False),
                      "shift": getattr(key, "shift", False) or key.get("shift", False),
                      "meta": getattr(key, "meta", False) or key.get("meta", False),
                      "super": getattr(key, "super_key", False) or getattr(key, "super", False) or key.get("super", False)}
        kid = get_key_binding_key(key_binding)
        return self._key_map.get(kid)

    def _on_keypress(self, key: Any) -> None:
        if not self.focused:
            return
        default_prevented = getattr(key, "default_prevented", False) or (key.get("default_prevented") if hasattr(key, "get") else False)
        if default_prevented:
            return
        if self._on_key_down:
            try:
                self._on_key_down(key)
            except Exception:
                pass
            if getattr(key, "default_prevented", False) or (key.get("default_prevented") if hasattr(key, "get") else False):
                return
        action = self._action_for_key(key)
        name = (getattr(key, "name", None) or key.get("name") if hasattr(key, "get") else None) or ""
        char = (getattr(key, "char", None) or key.get("char") if hasattr(key, "get") else None) or ""
        ctrl = getattr(key, "ctrl", False) or (key.get("ctrl") if hasattr(key, "get") else False)
        meta = getattr(key, "meta", False) or (key.get("meta") if hasattr(key, "get") else False)

        if action == "submit" or name in ("enter", "return", "linefeed") or char in ("\r", "\n"):
            self.submit()
            return
        if action == "delete-backward" or name == "backspace" or char in ("\x08", "\x7f"):
            self.delete_char_backward()
            return
        if action == "delete-forward" or name == "delete":
            self.delete_char()
            return
        if action == "move-left" or name == "left":
            self.cursor_offset = self._cursor_pos - 1
            return
        if action == "move-right" or name == "right":
            self.cursor_offset = self._cursor_pos + 1
            return
        if action == "move-home" or name == "home":
            self.cursor_offset = 0
            return
        if action == "move-end" or name == "end":
            self.cursor_offset = len(self._value)
            return
        if name == "space":
            self.insert_text(" ")
            return
        if name and len(name) == 1 and name.isprintable() and not ctrl and not meta:
            self.insert_text(name)

    @property
    def backgroundColor(self) -> tuple[int, int, int, int]:
        return self.bg

    @backgroundColor.setter
    def backgroundColor(self, value: Any) -> None:
        self.bg = parse_color_to_tuple(value)
        self.request_render()

    @property
    def textColor(self) -> tuple[int, int, int, int]:
        return self.fg

    @textColor.setter
    def textColor(self, value: Any) -> None:
        self.fg = parse_color_to_tuple(value)
        self.request_render()

    @property
    def focusedBackgroundColor(self) -> tuple[int, int, int, int]:
        return self._focused_bg

    @focusedBackgroundColor.setter
    def focusedBackgroundColor(self, value: Any) -> None:
        self._focused_bg = parse_color_to_tuple(value)
        self.request_render()

    @property
    def focusedTextColor(self) -> tuple[int, int, int, int]:
        return self._focused_fg

    @focusedTextColor.setter
    def focusedTextColor(self, value: Any) -> None:
        self._focused_fg = parse_color_to_tuple(value)
        self.request_render()

    @property
    def placeholderColor(self) -> tuple[int, int, int, int]:
        return self.placeholder_color

    @placeholderColor.setter
    def placeholderColor(self, value: Any) -> None:
        self.placeholder_color = parse_color_to_tuple(value)
        self.request_render()

    @property
    def cursorColor(self) -> tuple[int, int, int, int]:
        return self._cursor_color

    @cursorColor.setter
    def cursorColor(self, value: Any) -> None:
        self._cursor_color = parse_color_to_tuple(value)
        self.request_render()

    def render_self(self, buffer: OptimizedBuffer) -> None:
        if self.width <= 0 or self.height <= 0:
            return
        bg = self._focused_bg if self.focused else self.bg
        fg = self._focused_fg if self.focused else self.fg
        text = self._value if self._value else self._placeholder
        text_fg = fg if self._value else self.placeholder_color
        for dx, char in enumerate(text):
            if dx >= self.width:
                break
            buffer.set_cell(self.x + dx, self.y, Cell(char=char, fg=text_fg, bg=bg))
        for dx in range(len(text), self.width):
            buffer.set_cell(self.x + dx, self.y, Cell(char=" ", fg=fg, bg=bg))
        if self.focused and 0 <= self._cursor_pos < self.width:
            cx = min(self._cursor_pos, self.width - 1)
            if cx < 0:
                cx = 0
            cell = buffer.get_cell(self.x + cx, self.y)
            if cell:
                if self.cursor_style == "line":
                    buffer.set_cell(self.x + cx, self.y, Cell(char="\u258c", fg=self._cursor_color, bg=cell.bg))
                else:
                    buffer.set_cell(
                        self.x + cx, self.y,
                        Cell(char=cell.char, fg=cell.fg, bg=self._cursor_color, underline=True),
                    )

    def destroy(self) -> None:
        if self._destroyed:
            return
        self._destroyed = True
        self.blur()
