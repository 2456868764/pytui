# pytui.components.tab_select - aligns with OpenTUI TabSelectRenderable (TabSelect.ts):
# TabSelectOption, options, selected_index, selection_changed/item_selected, tab_width,
# show_scroll_arrows, show_description, show_underline, wrap_selection, color options, keybindings.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pytui.core.buffer import Cell, OptimizedBuffer
from pytui.core.renderable import Renderable
from pytui.lib import parse_color_to_tuple

# Align with OpenTUI TabSelectRenderableEvents
SELECTION_CHANGED = "selection_changed"
ITEM_SELECTED = "item_selected"


@dataclass
class TabSelectOption:
    """Single tab option: name, description, optional value. Aligns with OpenTUI TabSelectOption."""
    name: str
    description: str
    value: Any = None


def _dynamic_height(show_underline: bool, show_description: bool) -> int:
    h = 1
    if show_underline:
        h += 1
    if show_description:
        h += 1
    return h


# Default keybindings align with OpenTUI defaultTabSelectKeybindings
DEFAULT_TAB_SELECT_KEY_BINDINGS = {
    "move-left": ["left", "["],
    "move-right": ["right", "]"],
    "select-current": ["return", "linefeed"],
}


def _normalize_key(key: str) -> str:
    return (key or "").lower().strip()


def _match_key(event_key: str, bound_keys: list[str]) -> bool:
    k = _normalize_key(event_key)
    return any(_normalize_key(b) == k for b in bound_keys)


class TabSelect(Renderable):
    """Tab select. Aligns with OpenTUI TabSelectRenderable: options (TabSelectOption[]), selected_index,
    move_left/move_right/select_current, selection_changed/item_selected, tab_width, show_scroll_arrows,
    show_description, show_underline, wrap_selection, color options, keybindings.
    """

    def __init__(self, ctx: Any, options: dict | None = None) -> None:
        options = options or {}
        show_underline = options.get("show_underline", options.get("showUnderline", True))
        show_description = options.get("show_description", options.get("showDescription", True))
        height = options.get("height")
        if height is None:
            height = _dynamic_height(show_underline, show_description)
        opts = dict(options)
        opts["height"] = height
        super().__init__(ctx, opts)

        raw_opts = options.get("options", options.get("tabs"))
        if isinstance(raw_opts, list):
            self._options: list[TabSelectOption] = []
            for o in raw_opts:
                if isinstance(o, TabSelectOption):
                    self._options.append(o)
                elif isinstance(o, dict):
                    self._options.append(TabSelectOption(
                        name=o.get("name", ""),
                        description=o.get("description", ""),
                        value=o.get("value"),
                    ))
                else:
                    self._options.append(TabSelectOption(name=str(o), description=""))
        else:
            self._options = []

        self._selected_index = max(0, min(
            options.get("selected_index", options.get("selectedIndex", options.get("selected", 0))),
            max(0, len(self._options) - 1),
        ))
        self._scroll_offset = 0
        self._tab_width = max(1, int(options.get("tab_width", options.get("tabWidth", 20))))
        self._max_visible_tabs = max(1, (self.width or 80) // self._tab_width)

        self._bg = parse_color_to_tuple(options.get("backgroundColor", options.get("bg", "transparent")))
        self._text_color = parse_color_to_tuple(options.get("textColor", options.get("fg", "#FFFFFF")))
        self._focused_bg = parse_color_to_tuple(
            options.get("focusedBackgroundColor", options.get("focused_background_color")) or "#1a1a1a"
        )
        self._focused_text_color = parse_color_to_tuple(
            options.get("focusedTextColor", options.get("focused_text_color")) or "#FFFFFF"
        )
        self._selected_bg = parse_color_to_tuple(
            options.get("selectedBackgroundColor", options.get("selected_background_color")) or "#334455"
        )
        self._selected_text_color = parse_color_to_tuple(
            options.get("selectedTextColor", options.get("selected_text_color")) or "#FFFF00"
        )
        self._selected_description_color = parse_color_to_tuple(
            options.get("selectedDescriptionColor", options.get("selected_description_color")) or "#CCCCCC"
        )

        self._show_scroll_arrows = options.get("show_scroll_arrows", options.get("showScrollArrows", True))
        self._show_description = show_description
        self._show_underline = show_underline
        self._wrap_selection = options.get("wrap_selection", options.get("wrapSelection", False))

        kb = options.get("key_bindings", options.get("keyBindings")) or {}
        if isinstance(kb, dict):
            self._key_bindings = {**DEFAULT_TAB_SELECT_KEY_BINDINGS, **kb}
        else:
            self._key_bindings = dict(DEFAULT_TAB_SELECT_KEY_BINDINGS)
        self._update_scroll_offset()

    def _update_scroll_offset(self) -> None:
        half = self._max_visible_tabs // 2
        new_offset = max(
            0,
            min(
                self._selected_index - half,
                len(self._options) - self._max_visible_tabs,
            ),
        )
        if new_offset != self._scroll_offset:
            self._scroll_offset = new_offset
            self.request_render()

    def _get_action_for_key(self, key: str) -> str | None:
        for action, bound in self._key_bindings.items():
            keys = bound if isinstance(bound, list) else [bound]
            if _match_key(key, keys):
                return action
        return None

    # --- Properties (align with OpenTUI) ---
    @property
    def options(self) -> list[TabSelectOption]:
        return self._options

    @options.setter
    def options(self, value: list[TabSelectOption] | list[dict]) -> None:
        if isinstance(value, list):
            out: list[TabSelectOption] = []
            for o in value:
                if isinstance(o, TabSelectOption):
                    out.append(o)
                elif isinstance(o, dict):
                    out.append(TabSelectOption(
                        name=o.get("name", ""),
                        description=o.get("description", ""),
                        value=o.get("value"),
                    ))
                else:
                    out.append(TabSelectOption(name=str(o), description=""))
            self._options = out
            self._selected_index = max(0, min(self._selected_index, len(self._options) - 1))
            self._update_scroll_offset()
            self.request_render()

    @property
    def selected_index(self) -> int:
        return self._selected_index

    @selected_index.setter
    def selected_index(self, index: int) -> None:
        if 0 <= index < len(self._options) and index != self._selected_index:
            self._selected_index = index
            self._update_scroll_offset()
            self.request_render()
            opt = self.get_selected_option()
            self.emit(SELECTION_CHANGED, self._selected_index, opt)

    @property
    def tab_width(self) -> int:
        return self._tab_width

    @tab_width.setter
    def tab_width(self, value: int) -> None:
        if value != self._tab_width:
            self._tab_width = max(1, value)
            self._max_visible_tabs = max(1, self.width // self._tab_width) if self.width else 1
            self._update_scroll_offset()
            self.request_render()

    @property
    def show_scroll_arrows(self) -> bool:
        return self._show_scroll_arrows

    @show_scroll_arrows.setter
    def show_scroll_arrows(self, value: bool) -> None:
        if self._show_scroll_arrows != value:
            self._show_scroll_arrows = value
            self.request_render()

    @property
    def show_description(self) -> bool:
        return self._show_description

    @show_description.setter
    def show_description(self, value: bool) -> None:
        if self._show_description != value:
            self._show_description = value
            self.height = _dynamic_height(self._show_underline, self._show_description)
            self.request_render()

    @property
    def show_underline(self) -> bool:
        return self._show_underline

    @show_underline.setter
    def show_underline(self, value: bool) -> None:
        if self._show_underline != value:
            self._show_underline = value
            self.height = _dynamic_height(self._show_underline, self._show_description)
            self.request_render()

    @property
    def wrap_selection(self) -> bool:
        return self._wrap_selection

    @wrap_selection.setter
    def wrap_selection(self, value: bool) -> None:
        self._wrap_selection = value

    # Backward compat: selected returns option; for list-of-strings API, selected_name returns name
    @property
    def selected(self) -> TabSelectOption | None:
        return self.get_selected_option()

    @property
    def selected_name(self) -> str | None:
        opt = self.get_selected_option()
        return opt.name if opt else None

    def select_next(self) -> None:
        self.move_right()

    def select_prev(self) -> None:
        self.move_left()

    def select_index(self, index: int) -> None:
        self.set_selected_index(index)

    def get_selected_option(self) -> TabSelectOption | None:
        if 0 <= self._selected_index < len(self._options):
            return self._options[self._selected_index]
        return None

    def get_selected_index(self) -> int:
        return self._selected_index

    def set_options(self, opts: list[TabSelectOption] | list[dict]) -> None:
        self.options = opts

    def set_selected_index(self, index: int) -> None:
        self.selected_index = index

    def move_left(self) -> None:
        if self._selected_index > 0:
            self._selected_index -= 1
        elif self._wrap_selection and self._options:
            self._selected_index = len(self._options) - 1
        else:
            return
        self._update_scroll_offset()
        self.request_render()
        self.emit(SELECTION_CHANGED, self._selected_index, self.get_selected_option())

    def move_right(self) -> None:
        if self._selected_index < len(self._options) - 1:
            self._selected_index += 1
        elif self._wrap_selection and self._options:
            self._selected_index = 0
        else:
            return
        self._update_scroll_offset()
        self.request_render()
        self.emit(SELECTION_CHANGED, self._selected_index, self.get_selected_option())

    def select_current(self) -> None:
        opt = self.get_selected_option()
        if opt is not None:
            self.emit(ITEM_SELECTED, self._selected_index, opt)

    def set_tab_width(self, w: int) -> None:
        self.tab_width = w

    def _truncate(self, text: str, max_width: int) -> str:
        if len(text) <= max_width:
            return text
        return text[: max(0, max_width - 1)] + "…"

    def focus(self) -> None:
        super().focus()
        if hasattr(self.ctx, "renderer") and self.ctx.renderer:
            self.ctx.renderer.events.on("keypress", self._on_keypress)

    def blur(self) -> None:
        if hasattr(self.ctx, "renderer") and self.ctx.renderer:
            self.ctx.renderer.events.remove_listener("keypress", self._on_keypress)
        super().blur()

    def _on_keypress(self, key: dict) -> None:
        if not self.focused:
            return
        name = (key.get("name") or key.get("char") or "").lower()
        action = self._get_action_for_key(name)
        if action == "move-left":
            self.move_left()
        elif action == "move-right":
            self.move_right()
        elif action == "select-current":
            self.select_current()

    def on_resize(self, width: int, height: int) -> None:
        self._max_visible_tabs = max(1, width // self._tab_width) if width else 1
        self._update_scroll_offset()
        self.request_render()

    # Color property setters (align with OpenTUI)
    @property
    def backgroundColor(self):
        return self._bg

    @backgroundColor.setter
    def backgroundColor(self, value) -> None:
        self._bg = parse_color_to_tuple(value)
        self.request_render()

    @property
    def textColor(self):
        return self._text_color

    @textColor.setter
    def textColor(self, value) -> None:
        self._text_color = parse_color_to_tuple(value)
        self.request_render()

    @property
    def focusedBackgroundColor(self):
        return self._focused_bg

    @focusedBackgroundColor.setter
    def focusedBackgroundColor(self, value) -> None:
        self._focused_bg = parse_color_to_tuple(value)
        self.request_render()

    @property
    def focusedTextColor(self):
        return self._focused_text_color

    @focusedTextColor.setter
    def focusedTextColor(self, value) -> None:
        self._focused_text_color = parse_color_to_tuple(value)
        self.request_render()

    @property
    def selectedBackgroundColor(self):
        return self._selected_bg

    @selectedBackgroundColor.setter
    def selectedBackgroundColor(self, value) -> None:
        self._selected_bg = parse_color_to_tuple(value)
        self.request_render()

    @property
    def selectedTextColor(self):
        return self._selected_text_color

    @selectedTextColor.setter
    def selectedTextColor(self, value) -> None:
        self._selected_text_color = parse_color_to_tuple(value)
        self.request_render()

    @property
    def selectedDescriptionColor(self):
        return self._selected_description_color

    @selectedDescriptionColor.setter
    def selectedDescriptionColor(self, value) -> None:
        self._selected_description_color = parse_color_to_tuple(value)
        self.request_render()

    def render_self(self, buffer: OptimizedBuffer) -> None:
        if not self.visible or self.height < 1:
            return
        bg = self._focused_bg if self.focused else self._bg
        for dy in range(self.height):
            for dx in range(self.width):
                buffer.set_cell(self.x + dx, self.y + dy, Cell(bg=bg))

        if not self._options:
            return

        content_x, content_y = 0, 0
        content_width, content_height = self.width, self.height
        visible = self._options[self._scroll_offset : self._scroll_offset + self._max_visible_tabs]

        for i, option in enumerate(visible):
            actual_index = self._scroll_offset + i
            is_selected = actual_index == self._selected_index
            tab_x = content_x + i * self._tab_width
            if tab_x >= content_width:
                break
            actual_tab_width = min(self._tab_width, content_width - i * self._tab_width)

            if is_selected:
                for dx in range(actual_tab_width):
                    buffer.set_cell(
                        self.x + tab_x + dx,
                        self.y + content_y,
                        Cell(bg=self._selected_bg),
                    )

            base_text = self._focused_text_color if self.focused else self._text_color
            name_color = self._selected_text_color if is_selected else base_text
            name_content = self._truncate(option.name, actual_tab_width - 2)
            for j, ch in enumerate(name_content):
                if tab_x + 1 + j < self.x + self.width:
                    buffer.set_cell(
                        self.x + tab_x + 1 + j,
                        self.y + content_y,
                        Cell(char=ch, fg=name_color, bg=self._selected_bg if is_selected else bg),
                    )

            if is_selected and self._show_underline and content_height >= 2:
                underline_y = content_y + 1
                ul_bg = self._selected_bg if is_selected else bg
                for dx in range(actual_tab_width):
                    if self.y + underline_y < self.y + self.height:
                        buffer.set_cell(
                            self.x + tab_x + dx,
                            self.y + underline_y,
                            Cell(char="▬", fg=name_color, bg=ul_bg),
                        )

        if self._show_description and content_height >= (2 if self._show_underline else 1):
            opt = self.get_selected_option()
            if opt:
                desc_y = content_y + (2 if self._show_underline else 1)
                desc_content = self._truncate(opt.description, content_width - 2)
                for j, ch in enumerate(desc_content):
                    if self.x + content_x + 1 + j < self.x + self.width and desc_y < self.height:
                        buffer.set_cell(
                            self.x + content_x + 1 + j,
                            self.y + desc_y,
                            Cell(char=ch, fg=self._selected_description_color),
                        )

        if self._show_scroll_arrows and len(self._options) > self._max_visible_tabs:
            has_left = self._scroll_offset > 0
            has_right = self._scroll_offset + self._max_visible_tabs < len(self._options)
            arrow_fg = parse_color_to_tuple("#AAAAAA")
            if has_left:
                buffer.set_cell(self.x + content_x, self.y + content_y, Cell(char="‹", fg=arrow_fg))
            if has_right:
                buffer.set_cell(
                    self.x + content_x + content_width - 1,
                    self.y + content_y,
                    Cell(char="›", fg=arrow_fg),
                )
