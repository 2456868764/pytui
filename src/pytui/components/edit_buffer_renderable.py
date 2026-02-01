# pytui.components.edit_buffer_renderable - Aligns with OpenTUI packages/core/src/renderables/EditBufferRenderable.ts
# 与 OpenTUI EditBufferRenderable.ts 对齐：属性、功能、行为

from __future__ import annotations

from typing import Any, Callable

from pytui.core.buffer import Cell, OptimizedBuffer
from pytui.core.edit_buffer import EditBuffer
from pytui.lib import parse_color_to_tuple
from pytui.core.editor_view import EditorView
from pytui.core.renderable import Renderable


# 默认选项对齐 OpenTUI _defaultOptions
_DEFAULT_OPTIONS = {
    "text_color": "#ffffff",
    "background_color": "transparent",
    "selection_bg": None,
    "selection_fg": None,
    "selectable": True,
    "attributes": 0,
    "wrap_mode": "word",
    "scroll_margin": 0.2,
    "scroll_speed": 16,
    "show_cursor": True,
    "cursor_color": "#ffffff",
    "cursor_style": {"style": "block", "blinking": True},
    "tab_indicator": None,
    "tab_indicator_color": None,
}

CursorChangeEvent = dict  # { "line": int, "visualColumn": int }
ContentChangeEvent = dict  # {}


class EditBufferRenderable(Renderable):
    """编辑缓冲组件：与 OpenTUI EditBufferRenderable 对齐。拥有 edit_buffer 与 editor_view，支持光标、选区、undo/redo。"""

    def __init__(self, ctx: Any, options: dict[str, Any] | None = None) -> None:
        options = options or {}
        opts = dict(options)
        for camel, snake in [
            ("textColor", "text_color"),
            ("backgroundColor", "background_color"),
            ("selectionBg", "selection_bg"),
            ("selectionFg", "selection_fg"),
            ("wrapMode", "wrap_mode"),
            ("scrollMargin", "scroll_margin"),
            ("scrollSpeed", "scroll_speed"),
            ("showCursor", "show_cursor"),
            ("cursorColor", "cursor_color"),
            ("cursorStyle", "cursor_style"),
            ("tabIndicator", "tab_indicator"),
            ("tabIndicatorColor", "tab_indicator_color"),
            ("onCursorChange", "on_cursor_change"),
            ("onContentChange", "on_content_change"),
            ("syntaxStyle", "syntax_style"),
        ]:
            if camel in opts and snake not in opts:
                opts[snake] = opts[camel]
        super().__init__(ctx, opts)

        self._focusable = True
        self.selectable = opts.get("selectable", _DEFAULT_OPTIONS["selectable"])
        self._text_color = parse_color_to_tuple(opts.get("text_color", _DEFAULT_OPTIONS["text_color"]))
        self._background_color = parse_color_to_tuple(
            opts.get("background_color", _DEFAULT_OPTIONS["background_color"])
        )
        self._default_attributes = opts.get("attributes", _DEFAULT_OPTIONS["attributes"])
        self._selection_bg = (
            parse_color_to_tuple(opts["selection_bg"]) if opts.get("selection_bg") is not None else None
        )
        self._selection_fg = (
            parse_color_to_tuple(opts["selection_fg"]) if opts.get("selection_fg") is not None else None
        )
        self._wrap_mode = opts.get("wrap_mode", _DEFAULT_OPTIONS["wrap_mode"])
        self._scroll_margin = opts.get("scroll_margin", _DEFAULT_OPTIONS["scroll_margin"])
        self._scroll_speed = max(0, opts.get("scroll_speed", _DEFAULT_OPTIONS["scroll_speed"]))
        self._show_cursor = opts.get("show_cursor", _DEFAULT_OPTIONS["show_cursor"])
        self._cursor_color = parse_color_to_tuple(
            opts.get("cursor_color", _DEFAULT_OPTIONS["cursor_color"])
        )
        cs = opts.get("cursor_style", _DEFAULT_OPTIONS["cursor_style"])
        self._cursor_style = (
            dict(cs) if isinstance(cs, dict) else {"style": "block", "blinking": True}
        )
        self._tab_indicator = opts.get("tab_indicator", _DEFAULT_OPTIONS["tab_indicator"])
        self._tab_indicator_color = (
            parse_color_to_tuple(opts["tab_indicator_color"])
            if opts.get("tab_indicator_color") is not None
            else None
        )
        self._on_cursor_change: Callable[[CursorChangeEvent], None] | None = opts.get(
            "on_cursor_change"
        )
        self._on_content_change: Callable[[ContentChangeEvent], None] | None = opts.get(
            "on_content_change"
        )
        self._syntax_style: Any = opts.get("syntax_style")
        self._last_local_selection: tuple[int, int, int, int] | None = None  # anchor_x,y focus_x,y
        self._auto_scroll_velocity = 0.0
        self._auto_scroll_accumulator = 0.0

        width = opts.get("width") or 80
        height = opts.get("height") or 24
        self.edit_buffer = EditBuffer()
        self.editor_view = EditorView(self.edit_buffer, view_width=max(1, width), view_height=max(1, height))
        self.editor_view.set_wrap_mode(self._wrap_mode)
        self.editor_view.set_scroll_margin(self._scroll_margin)
        if self._tab_indicator is not None:
            self.editor_view.set_tab_indicator(self._tab_indicator)
        if self._tab_indicator_color is not None:
            self.editor_view.set_tab_indicator_color(self._tab_indicator_color)

        initial_text = opts.get("text", opts.get("content", ""))
        if initial_text:
            self.edit_buffer.set_text(initial_text)

    @property
    def line_info(self) -> dict[str, Any]:
        return self.editor_view.get_logical_line_info()

    @property
    def line_count(self) -> int:
        return self.edit_buffer.line_count

    @property
    def virtual_line_count(self) -> int:
        return self.editor_view.virtual_line_count

    @property
    def scroll_y(self) -> int:
        return self.editor_view.scroll_y

    @scroll_y.setter
    def scroll_y(self, value: int) -> None:
        self.editor_view.scroll_y = value
        self.request_render()

    @property
    def plain_text(self) -> str:
        return self.edit_buffer.text

    @property
    def logical_cursor(self) -> tuple[int, int]:
        """(row, col) 0-based. Aligns OpenTUI logicalCursor."""
        return self.edit_buffer.pos_to_line_col(self.editor_view.cursor_pos)

    @property
    def visual_cursor(self) -> tuple[int, int]:
        """(visual_row, visual_col) in viewport. Aligns OpenTUI visualCursor."""
        return self.editor_view.get_visual_cursor()

    @property
    def cursor_offset(self) -> int:
        return self.editor_view.cursor_offset

    @cursor_offset.setter
    def cursor_offset(self, value: int) -> None:
        self.editor_view.set_cursor_by_offset(value)
        self.request_render()

    @property
    def text_color(self) -> tuple[int, int, int, int]:
        return self._text_color

    @text_color.setter
    def text_color(self, value: Any) -> None:
        c = parse_color_to_tuple(value)
        if self._text_color != c:
            self._text_color = c
            self.request_render()

    @property
    def selection_bg(self) -> tuple[int, int, int, int] | None:
        return self._selection_bg

    @selection_bg.setter
    def selection_bg(self, value: Any) -> None:
        c = parse_color_to_tuple(value) if value is not None else None
        if self._selection_bg != c:
            self._selection_bg = c
            self.request_render()

    @property
    def selection_fg(self) -> tuple[int, int, int, int] | None:
        return self._selection_fg

    @selection_fg.setter
    def selection_fg(self, value: Any) -> None:
        c = parse_color_to_tuple(value) if value is not None else None
        if self._selection_fg != c:
            self._selection_fg = c
            self.request_render()

    @property
    def background_color(self) -> tuple[int, int, int, int]:
        return self._background_color

    @background_color.setter
    def background_color(self, value: Any) -> None:
        c = parse_color_to_tuple(value)
        if self._background_color != c:
            self._background_color = c
            self.request_render()

    @property
    def attributes(self) -> int:
        return self._default_attributes

    @attributes.setter
    def attributes(self, value: int) -> None:
        if self._default_attributes != value:
            self._default_attributes = value
            self.request_render()

    @property
    def wrap_mode(self) -> str:
        return self._wrap_mode

    @wrap_mode.setter
    def wrap_mode(self, value: str) -> None:
        if self._wrap_mode != value:
            self._wrap_mode = value
            self.editor_view.set_wrap_mode(value)
            self.request_render()

    @property
    def show_cursor(self) -> bool:
        return self._show_cursor

    @show_cursor.setter
    def show_cursor(self, value: bool) -> None:
        if self._show_cursor != value:
            self._show_cursor = value
            if not value and self.focused and hasattr(self.ctx, "set_cursor_position"):
                self.ctx.set_cursor_position(0, 0, False)
            self.request_render()

    @property
    def cursor_color(self) -> tuple[int, int, int, int]:
        return self._cursor_color

    @cursor_color.setter
    def cursor_color(self, value: Any) -> None:
        c = parse_color_to_tuple(value)
        if self._cursor_color != c:
            self._cursor_color = c
            if self.focused:
                self.request_render()

    @property
    def cursor_style(self) -> dict[str, Any]:
        return dict(self._cursor_style)

    @cursor_style.setter
    def cursor_style(self, value: dict[str, Any]) -> None:
        v = dict(value)
        if self._cursor_style.get("style") != v.get("style") or self._cursor_style.get("blinking") != v.get("blinking"):
            self._cursor_style = v
            if self.focused:
                self.request_render()

    @property
    def tab_indicator(self) -> str | int | None:
        return self._tab_indicator

    @tab_indicator.setter
    def tab_indicator(self, value: str | int | None) -> None:
        if self._tab_indicator != value:
            self._tab_indicator = value
            if value is not None:
                self.editor_view.set_tab_indicator(value)
            self.request_render()

    @property
    def tab_indicator_color(self) -> tuple[int, int, int, int] | None:
        return self._tab_indicator_color

    @tab_indicator_color.setter
    def tab_indicator_color(self, value: Any) -> None:
        c = parse_color_to_tuple(value) if value is not None else None
        if self._tab_indicator_color != c:
            self._tab_indicator_color = c
            if c is not None:
                self.editor_view.set_tab_indicator_color(c)
            self.request_render()

    @property
    def scroll_speed(self) -> int:
        return self._scroll_speed

    @scroll_speed.setter
    def scroll_speed(self, value: int) -> None:
        self._scroll_speed = max(0, value)

    @property
    def on_cursor_change(self) -> Callable[[CursorChangeEvent], None] | None:
        return self._on_cursor_change

    @on_cursor_change.setter
    def on_cursor_change(self, handler: Callable[[CursorChangeEvent], None] | None) -> None:
        self._on_cursor_change = handler

    @property
    def on_content_change(self) -> Callable[[ContentChangeEvent], None] | None:
        return self._on_content_change

    @on_content_change.setter
    def on_content_change(self, handler: Callable[[ContentChangeEvent], None] | None) -> None:
        self._on_content_change = handler

    @property
    def syntax_style(self) -> Any:
        return self._syntax_style

    @syntax_style.setter
    def syntax_style(self, value: Any) -> None:
        if self._syntax_style != value:
            self._syntax_style = value
            self.request_render()

    def _emit_cursor_change(self) -> None:
        if self._on_cursor_change:
            row, col = self.logical_cursor
            self._on_cursor_change({"line": row, "visualColumn": col})

    def _emit_content_change(self) -> None:
        if self._on_content_change:
            self._on_content_change({})
        self.emit("line-info-change")

    def set_text(self, text: str) -> None:
        """Set text and reset buffer state. Aligns OpenTUI setText()."""
        self.edit_buffer.set_text(text)
        self.request_render()
        self._emit_content_change()

    def replace_text(self, text: str) -> None:
        """Replace text preserving undo. Aligns OpenTUI replaceText()."""
        self.edit_buffer.replace_text(text)
        self.request_render()
        self._emit_content_change()

    def clear(self) -> None:
        self.edit_buffer.clear()
        self.edit_buffer.clear_all_highlights()
        self.request_render()
        self._emit_content_change()

    def delete_range(self, start_line: int, start_col: int, end_line: int, end_col: int) -> None:
        self.edit_buffer.delete_range(start_line, start_col, end_line, end_col)
        self.request_render()
        self._emit_content_change()

    def insert_text(self, text: str) -> None:
        """Insert at cursor. Aligns OpenTUI insertText()."""
        self.editor_view.insert(text)
        self.request_render()
        self._emit_content_change()
        self._emit_cursor_change()

    def get_text_range(self, start_offset: int, end_offset: int) -> str:
        return self.edit_buffer.get_text_range(start_offset, end_offset)

    def get_text_range_by_coords(
        self, start_row: int, start_col: int, end_row: int, end_col: int
    ) -> str:
        return self.edit_buffer.get_text_range_by_coords(
            start_row, start_col, end_row, end_col
        )

    def add_highlight(self, line_idx: int, highlight: dict[str, Any]) -> None:
        self.edit_buffer.add_highlight(line_idx, highlight)
        self.request_render()

    def add_highlight_by_char_range(self, highlight: dict[str, Any]) -> None:
        self.edit_buffer.add_highlight_by_char_range(highlight)
        self.request_render()

    def remove_highlights_by_ref(self, hl_ref: int) -> None:
        self.edit_buffer.remove_highlights_by_ref(hl_ref)
        self.request_render()

    def clear_line_highlights(self, line_idx: int) -> None:
        self.edit_buffer.clear_line_highlights(line_idx)
        self.request_render()

    def clear_all_highlights(self) -> None:
        self.edit_buffer.clear_all_highlights()
        self.request_render()

    def get_line_highlights(self, line_idx: int) -> list[dict[str, Any]]:
        return self.edit_buffer.get_line_highlights(line_idx)

    def should_start_selection(self, x: int, y: int) -> bool:
        if not self.selectable:
            return False
        local_x = x - self.x
        local_y = y - self.y
        return 0 <= local_x < self.width and 0 <= local_y < self.height

    def on_selection_changed(self, selection: Any) -> bool:
        """Update local selection from global. Aligns OpenTUI onSelectionChanged(). Returns hasSelection()."""
        if selection is None or not getattr(selection, "is_active", True):
            self.editor_view.clear_selection()
            self._last_local_selection = None
            self.request_render()
            return False
        anchor_x = getattr(selection, "anchor_x", 0) - self.x
        anchor_y = getattr(selection, "anchor_y", 0) - self.y
        focus_x = getattr(selection, "focus_x", 0) - self.x
        focus_y = getattr(selection, "focus_y", 0) - self.y
        anchor_pos = self.editor_view.buffer.line_col_to_pos(
            max(0, min(anchor_y, self.editor_view.buffer.line_count - 1)),
            max(0, anchor_x),
        )
        focus_pos = self.editor_view.buffer.line_col_to_pos(
            max(0, min(focus_y, self.editor_view.buffer.line_count - 1)),
            max(0, focus_x),
        )
        self.editor_view.set_selection(anchor_pos, focus_pos)
        self._last_local_selection = (anchor_x, anchor_y, focus_x, focus_y)
        self.request_render()
        return self.has_selection()

    def get_selected_text(self) -> str:
        return self.editor_view.get_selected_text()

    def has_selection(self) -> bool:
        return self.editor_view.has_selection()

    def get_selection(self) -> tuple[int, int] | None:
        return self.editor_view.get_selection()

    def focus(self) -> None:
        super().focus()
        if hasattr(self.ctx, "set_cursor_style"):
            self.ctx.set_cursor_style(
                self._cursor_style.get("style", "block"),
                self._cursor_style.get("blinking", True),
            )
        if hasattr(self.ctx, "set_cursor_color"):
            self.ctx.set_cursor_color(self._cursor_color)
        self.request_render()

    def blur(self) -> None:
        if hasattr(self.ctx, "set_cursor_position"):
            self.ctx.set_cursor_position(0, 0, False)
        super().blur()
        self.request_render()

    def destroy(self) -> None:
        """Aligns OpenTUI destroy(): blur, clear buffer/highlights, release refs."""
        if getattr(self, "_destroyed", False):
            return
        if self.focused and hasattr(self.ctx, "set_cursor_position"):
            self.ctx.set_cursor_position(0, 0, False)
        self.blur()
        self._destroyed = True
        self.edit_buffer.clear_all_highlights()
        self.edit_buffer.clear()

    def _handle_scroll(self, direction: str, delta: int) -> None:
        ev = self.editor_view
        if direction == "up":
            ev.scroll_y = max(0, ev.scroll_y - delta)
        elif direction == "down":
            ev.scroll_y = min(
                max(0, ev.buffer.line_count - ev.view_height),
                ev.scroll_y + delta,
            )
        self.request_render()

    def on_resize(self, width: int, height: int) -> None:
        self.editor_view.set_viewport_size(width, height)

    def render_self(self, buffer: OptimizedBuffer) -> None:
        if self.width <= 0 or self.height <= 0:
            return
        self.editor_view.view_width = self.width
        self.editor_view.view_height = self.height
        lines = self.editor_view.get_visible_lines()
        start_line = self.editor_view.scroll_y
        sel = self.editor_view.get_selection_range()
        vrow, vcol = self.editor_view.get_visual_cursor()
        fg = self._text_color
        bg = self._background_color
        sel_bg = self._selection_bg or (64, 64, 170, 255)
        cursor_fg = self._cursor_color
        cursor_bg = self._background_color

        for dy in range(self.height):
            line_idx = start_line + dy
            if dy >= len(lines):
                line = ""
            else:
                line = lines[dy]
            for dx in range(self.width):
                ch = line[dx] if dx < len(line) else " "
                cell_fg, cell_bg = fg, bg
                pos = (
                    self.editor_view.buffer.line_col_to_pos(line_idx, dx)
                    if line_idx < self.editor_view.buffer.line_count
                    else None
                )
                if sel is not None and pos is not None and sel[0] <= pos < sel[1]:
                    cell_bg = sel_bg
                if self._show_cursor and self.focused and vrow == dy and vcol == dx:
                    cell_fg, cell_bg = cursor_fg, cursor_bg
                buffer.set_cell(
                    self.x + dx,
                    self.y + dy,
                    Cell(char=ch, fg=cell_fg, bg=cell_bg),
                )
        if self._show_cursor and self.focused and hasattr(self.ctx, "set_cursor_position"):
            self.ctx.set_cursor_position(
                self.x + vcol + 1,
                self.y + vrow + 1,
                True,
            )
            if hasattr(self.ctx, "set_cursor_color"):
                self.ctx.set_cursor_color(self._cursor_color)
            if hasattr(self.ctx, "set_cursor_style"):
                self.ctx.set_cursor_style(
                    self._cursor_style.get("style", "block"),
                    self._cursor_style.get("blinking", True),
                )
