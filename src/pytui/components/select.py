# pytui.components.select - fully aligned with OpenTUI SelectRenderable (Select.ts):
# SelectOption, options, selectedIndex, selectionChanged/itemSelected, all color options,
# showScrollIndicator, wrapSelection, showDescription, font, itemSpacing, fastScrollStep,
# moveUp/moveDown(steps), selectCurrent, setSelectedIndex, keyBindings (move-up, move-down, move-up-fast, move-down-fast, select-current).

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import Any

from pytui.core.buffer import Cell, OptimizedBuffer
from pytui.core.renderable import Renderable
from pytui.lib import parse_color_to_tuple

# Align with OpenTUI SelectRenderableEvents
SELECTION_CHANGED = "selection_changed"
ITEM_SELECTED = "item_selected"


@dataclass
class SelectOption:
    """Single option: name, description, optional value. Aligns with OpenTUI SelectOption."""
    name: str
    description: str
    value: Any = None


# Default keybindings align with OpenTUI defaultSelectKeybindings
DEFAULT_SELECT_KEY_BINDINGS = {
    "move-up": ["up", "k"],
    "move-down": ["down", "j"],
    "move-up-fast": ["shift+up"],
    "move-down-fast": ["shift+down"],
    "select-current": ["return", "linefeed"],
}


def _normalize_options(raw: list[Any]) -> list[SelectOption]:
    """Normalize to list[SelectOption]. Accepts str, dict, or SelectOption."""
    out: list[SelectOption] = []
    for o in raw:
        if isinstance(o, SelectOption):
            out.append(o)
        elif isinstance(o, str):
            out.append(SelectOption(name=o, description="", value=o))
        elif isinstance(o, dict):
            out.append(SelectOption(
                name=o.get("name", str(o.get("value", ""))),
                description=o.get("description", ""),
                value=o.get("value", o.get("name", "")),
            ))
        else:
            out.append(SelectOption(name=str(o), description="", value=o))
    return out


def _key_id(key: dict) -> str:
    parts = []
    if key.get("shift"):
        parts.append("shift")
    if key.get("ctrl"):
        parts.append("ctrl")
    if key.get("meta"):
        parts.append("meta")
    name = (key.get("name") or key.get("char") or "").strip().lower()
    if name:
        parts.append(name)
    return "+".join(sorted(parts)) if parts else ""


class Select(Renderable):
    """Select list. Fully aligned with OpenTUI SelectRenderable: options (SelectOption[]),
    selectedIndex, selectionChanged/itemSelected, moveUp/moveDown(steps), selectCurrent,
    setSelectedIndex, all color options, showScrollIndicator, wrapSelection, showDescription,
    itemSpacing, fastScrollStep, keyBindings (move-up, move-down, move-up-fast, move-down-fast, select-current)."""

    _default_options = {
        "backgroundColor": "transparent",
        "textColor": "#FFFFFF",
        "focusedBackgroundColor": "#1a1a1a",
        "focusedTextColor": "#FFFFFF",
        "selectedBackgroundColor": "#334455",
        "selectedTextColor": "#FFFF00",
        "descriptionColor": "#888888",
        "selectedDescriptionColor": "#CCCCCC",
        "showScrollIndicator": False,
        "wrapSelection": False,
        "showDescription": True,
        "itemSpacing": 0,
        "fastScrollStep": 5,
    }

    def __init__(self, ctx: Any, options: dict | None = None) -> None:
        options = options or {}
        super().__init__(ctx, options)
        raw_opts = list(options.get("options", []))
        self._options = _normalize_options(raw_opts)
        requested_index = options.get("selected_index", options.get("selectedIndex", options.get("selected", 0)))
        n = len(self._options)
        self._selected_index = max(0, min(requested_index, n - 1)) if n else 0
        self._scroll_offset = 0

        defs = self._default_options
        self._bg = parse_color_to_tuple(options.get("backgroundColor", options.get("bg", defs["backgroundColor"])))
        self._text_color = parse_color_to_tuple(options.get("textColor", options.get("fg", defs["textColor"])))
        self._focused_bg = parse_color_to_tuple(
            options.get("focusedBackgroundColor", options.get("focused_background_color")) or defs["focusedBackgroundColor"]
        )
        self._focused_text_color = parse_color_to_tuple(
            options.get("focusedTextColor", options.get("focused_text_color")) or defs["focusedTextColor"]
        )
        self._selected_bg = parse_color_to_tuple(
            options.get("selectedBackgroundColor", options.get("selected_bg")) or defs["selectedBackgroundColor"]
        )
        self._selected_text_color = parse_color_to_tuple(
            options.get("selectedTextColor", options.get("selected_fg")) or defs["selectedTextColor"]
        )
        self._description_color = parse_color_to_tuple(
            options.get("descriptionColor", options.get("description_color")) or defs["descriptionColor"]
        )
        self._selected_description_color = parse_color_to_tuple(
            options.get("selectedDescriptionColor", options.get("selected_description_color")) or defs["selectedDescriptionColor"]
        )

        self._show_scroll_indicator = options.get("show_scroll_indicator", options.get("showScrollIndicator", defs["showScrollIndicator"]))
        self._wrap_selection = options.get("wrap_selection", options.get("wrapSelection", defs["wrapSelection"]))
        self._show_description = options.get("show_description", options.get("showDescription", defs["showDescription"]))
        self._item_spacing = max(0, int(options.get("item_spacing", options.get("itemSpacing", defs["itemSpacing"]))))
        self._fast_scroll_step = max(1, int(options.get("fast_scroll_step", options.get("fastScrollStep", defs["fastScrollStep"]))))
        self._font = options.get("font") or options.get("font_dict")

        self._lines_per_item = (2 if self._show_description else 1) + self._item_spacing
        self._max_visible_items = max(1, self.height // self._lines_per_item) if self.height else 1
        self._update_scroll_offset()

        kb = options.get("key_bindings", options.get("keyBindings")) or {}
        if isinstance(kb, dict):
            self._key_bindings = {**DEFAULT_SELECT_KEY_BINDINGS, **kb}
        else:
            self._key_bindings = dict(DEFAULT_SELECT_KEY_BINDINGS)
        self._rebuild_key_map()

    def _rebuild_key_map(self) -> None:
        self._key_map: dict[str, str] = {}
        for action, keys in self._key_bindings.items():
            for k in keys if isinstance(keys, list) else [keys]:
                kstr = (k if isinstance(k, str) else str(k)).strip().lower()
                kstr = "+".join(sorted(s for s in kstr.replace(" ", "+").split("+") if s))
                self._key_map[kstr] = action

    def _action_for_key(self, key: dict) -> str | None:
        kid = _key_id(key)
        return self._key_map.get(kid)

    def _update_scroll_offset(self) -> None:
        if not self._options:
            return
        half = self._max_visible_items // 2
        new_offset = max(
            0,
            min(
                self._selected_index - half,
                len(self._options) - self._max_visible_items,
            ),
        )
        if new_offset != self._scroll_offset:
            self._scroll_offset = new_offset
            self.request_render()

    # --- Properties (align with OpenTUI) ---
    @property
    def options(self) -> list[SelectOption]:
        return list(self._options)

    @options.setter
    def options(self, value: list[SelectOption] | list[dict] | list[str]) -> None:
        self._options = _normalize_options(list(value))
        self._selected_index = max(0, min(self._selected_index, len(self._options) - 1))
        self._update_scroll_offset()
        self.request_render()

    @property
    def selected_index(self) -> int:
        return self._selected_index

    @selected_index.setter
    def selected_index(self, value: int) -> None:
        n = len(self._options)
        new_index = max(0, min(value, n - 1)) if n else 0
        if self._selected_index != new_index:
            self._selected_index = new_index
            self._update_scroll_offset()
            self.request_render()
            opt = self.get_selected_option()
            self.emit(SELECTION_CHANGED, self._selected_index, opt)
            self.emit("select", self._selected_index, opt.name if opt else "", opt.value if opt else None)

    def get_selected_option(self) -> SelectOption | None:
        if 0 <= self._selected_index < len(self._options):
            return self._options[self._selected_index]
        return None

    def get_selected_index(self) -> int:
        return self._selected_index

    def move_up(self, steps: int = 1) -> None:
        new_index = self._selected_index - steps
        if new_index >= 0:
            self._selected_index = new_index
        elif self._wrap_selection and self._options:
            self._selected_index = len(self._options) - 1
        else:
            self._selected_index = 0
        self._update_scroll_offset()
        self.request_render()
        opt = self.get_selected_option()
        self.emit(SELECTION_CHANGED, self._selected_index, opt)
        self.emit("select", self._selected_index, opt.name if opt else "", opt.value if opt else None)

    def move_down(self, steps: int = 1) -> None:
        new_index = self._selected_index + steps
        if new_index < len(self._options):
            self._selected_index = new_index
        elif self._wrap_selection and self._options:
            self._selected_index = 0
        else:
            self._selected_index = len(self._options) - 1
        self._update_scroll_offset()
        self.request_render()
        opt = self.get_selected_option()
        self.emit(SELECTION_CHANGED, self._selected_index, opt)
        self.emit("select", self._selected_index, opt.name if opt else "", opt.value if opt else None)

    def select_current(self) -> None:
        opt = self.get_selected_option()
        if opt is not None:
            self.emit(ITEM_SELECTED, self._selected_index, opt)
            self.emit("select", self._selected_index, opt.name, opt.value)

    def set_selected_index(self, index: int) -> None:
        self.selected_index = index

    # Backward compat
    def select_next(self, step: int = 1) -> None:
        self.move_down(step)

    def select_prev(self, step: int = 1) -> None:
        self.move_up(step)

    @property
    def selected(self) -> str | None:
        opt = self.get_selected_option()
        return opt.name if opt else None

    @property
    def selected_value(self) -> Any:
        opt = self.get_selected_option()
        return opt.value if opt else None

    # Color / option property setters (align with OpenTUI)
    @property
    def show_scroll_indicator(self) -> bool:
        return self._show_scroll_indicator

    @show_scroll_indicator.setter
    def show_scroll_indicator(self, value: bool) -> None:
        self._show_scroll_indicator = value
        self.request_render()

    @property
    def show_description(self) -> bool:
        return self._show_description

    @show_description.setter
    def show_description(self, value: bool) -> None:
        if self._show_description != value:
            self._show_description = value
            self._lines_per_item = (2 if self._show_description else 1) + self._item_spacing
            self._max_visible_items = max(1, self.height // self._lines_per_item) if self.height else 1
            self._update_scroll_offset()
            self.request_render()

    @property
    def wrap_selection(self) -> bool:
        return self._wrap_selection

    @wrap_selection.setter
    def wrap_selection(self, value: bool) -> None:
        self._wrap_selection = value

    @property
    def fast_scroll_step(self) -> int:
        return self._fast_scroll_step

    @fast_scroll_step.setter
    def fast_scroll_step(self, value: int) -> None:
        self._fast_scroll_step = max(1, int(value))

    @property
    def item_spacing(self) -> int:
        return self._item_spacing

    @item_spacing.setter
    def item_spacing(self, value: int) -> None:
        self._item_spacing = max(0, int(value))
        self._lines_per_item = (2 if self._show_description else 1) + self._item_spacing
        self._max_visible_items = max(1, self.height // self._lines_per_item) if self.height else 1
        self._update_scroll_offset()
        self.request_render()

    # Color property setters (align with OpenTUI)
    @property
    def backgroundColor(self):
        return self._bg

    @backgroundColor.setter
    def backgroundColor(self, value) -> None:
        self._bg = parse_color_to_tuple(value) if value is not None else parse_color_to_tuple(self._default_options["backgroundColor"])
        self.request_render()

    @property
    def textColor(self):
        return self._text_color

    @textColor.setter
    def textColor(self, value) -> None:
        self._text_color = parse_color_to_tuple(value) if value is not None else parse_color_to_tuple(self._default_options["textColor"])
        self.request_render()

    @property
    def focusedBackgroundColor(self):
        return self._focused_bg

    @focusedBackgroundColor.setter
    def focusedBackgroundColor(self, value) -> None:
        self._focused_bg = parse_color_to_tuple(value) if value is not None else parse_color_to_tuple(self._default_options["focusedBackgroundColor"])
        self.request_render()

    @property
    def focusedTextColor(self):
        return self._focused_text_color

    @focusedTextColor.setter
    def focusedTextColor(self, value) -> None:
        self._focused_text_color = parse_color_to_tuple(value) if value is not None else parse_color_to_tuple(self._default_options["focusedTextColor"])
        self.request_render()

    @property
    def selectedBackgroundColor(self):
        return self._selected_bg

    @selectedBackgroundColor.setter
    def selectedBackgroundColor(self, value) -> None:
        self._selected_bg = parse_color_to_tuple(value) if value is not None else parse_color_to_tuple(self._default_options["selectedBackgroundColor"])
        self.request_render()

    @property
    def selectedTextColor(self):
        return self._selected_text_color

    @selectedTextColor.setter
    def selectedTextColor(self, value) -> None:
        self._selected_text_color = parse_color_to_tuple(value) if value is not None else parse_color_to_tuple(self._default_options["selectedTextColor"])
        self.request_render()

    @property
    def descriptionColor(self):
        return self._description_color

    @descriptionColor.setter
    def descriptionColor(self, value) -> None:
        self._description_color = parse_color_to_tuple(value) if value is not None else parse_color_to_tuple(self._default_options["descriptionColor"])
        self.request_render()

    @property
    def selectedDescriptionColor(self):
        return self._selected_description_color

    @selectedDescriptionColor.setter
    def selectedDescriptionColor(self, value) -> None:
        self._selected_description_color = parse_color_to_tuple(value) if value is not None else parse_color_to_tuple(self._default_options["selectedDescriptionColor"])
        self.request_render()

    def on_resize(self, width: int, height: int) -> None:
        self._max_visible_items = max(1, height // self._lines_per_item) if height else 1
        self._update_scroll_offset()
        self.request_render()

    def focus(self) -> None:
        super().focus()
        if hasattr(self.ctx, "renderer") and self.ctx.renderer:
            self.ctx.renderer.keyboard.on("keypress", self._on_keypress)

    def blur(self) -> None:
        if hasattr(self.ctx, "renderer") and self.ctx.renderer:
            self.ctx.renderer.keyboard.remove_listener("keypress", self._on_keypress)
        super().blur()

    def _on_keypress(self, key: dict) -> None:
        if os.environ.get("PYTUI_DEBUG"):
            print(f"[pytui:select] _on_keypress focused={self.focused} key={key}", file=sys.stderr, flush=True)
        if not self.focused:
            return
        action = self._action_for_key(key)
        if action == "move-up":
            self.move_up(1)
            return
        if action == "move-down":
            self.move_down(1)
            return
        if action == "move-up-fast":
            self.move_up(self._fast_scroll_step)
            return
        if action == "move-down-fast":
            self.move_down(self._fast_scroll_step)
            return
        if action == "select-current":
            self.select_current()
            return
        name = (key.get("name") or key.get("char") or "").lower()
        if name in ("up", "k"):
            self.move_up(1)
            return
        if name in ("down", "j"):
            self.move_down(1)
            return
        if name in ("return", "linefeed", "enter"):
            self.select_current()
            return

    def render_self(self, buffer: OptimizedBuffer) -> None:
        if not self.visible or not self._options or self.height <= 0 or self.width <= 0:
            return
        bg_color = self._focused_bg if self.focused else self._bg
        content_x, content_y = 0, 0
        content_width, content_height = self.width, self.height
        max_visible = max(1, self.height // self._lines_per_item)
        visible = self._options[self._scroll_offset : self._scroll_offset + max_visible]
        font_height = 1

        for i, option in enumerate(visible):
            actual_index = self._scroll_offset + i
            is_selected = actual_index == self._selected_index
            item_y = content_y + i * self._lines_per_item
            if item_y + self._lines_per_item > content_y + content_height:
                break
            content_height_line = self._lines_per_item - self._item_spacing
            if is_selected:
                for dy in range(content_height_line):
                    for dx in range(content_width):
                        buffer.set_cell(
                            self.x + dx,
                            self.y + item_y + dy,
                            Cell(bg=self._selected_bg),
                        )
            prefix = "▶ " if is_selected else "  "
            name_content = prefix + option.name
            base_text = self._focused_text_color if self.focused else self._text_color
            name_color = self._selected_text_color if is_selected else base_text
            for dx, ch in enumerate(name_content):
                if dx < content_width and item_y < self.y + self.height:
                    buffer.set_cell(
                        self.x + dx,
                        self.y + item_y,
                        Cell(char=ch, fg=name_color, bg=self._selected_bg if is_selected else bg_color),
                    )
            if self._show_description and item_y + font_height < self.y + self.height:
                desc_color = self._selected_description_color if is_selected else self._description_color
                desc_text = (option.description or "")[: content_width - 2]
                for dx, ch in enumerate(desc_text):
                    if dx < content_width:
                        buffer.set_cell(
                            self.x + 2 + dx,
                            self.y + item_y + 1,
                            Cell(char=ch, fg=desc_color, bg=self._selected_bg if is_selected else bg_color),
                        )

        if self._show_scroll_indicator and len(self._options) > self._max_visible_items and content_width > 0:
            scroll_percent = self._selected_index / max(1, len(self._options) - 1)
            indicator_height = max(1, content_height - 2)
            indicator_y = content_y + 1 + int(scroll_percent * indicator_height)
            indicator_x = content_x + content_width - 1
            if indicator_y < self.height:
                buffer.set_cell(
                    self.x + indicator_x,
                    self.y + indicator_y,
                    Cell(char="█", fg=parse_color_to_tuple("#666666")),
                )
