# pytui.components.text_buffer_renderable - Aligns with OpenTUI packages/core/src/renderables/TextBufferRenderable.ts
# TextBufferRenderable base: TextBuffer + TextBufferView, LineInfoProvider, scrollY/scrollX, fg/bg, wrapMode,
# selection, getSelectedText, hasSelection, getSelection, renderSelf (draw text buffer content).

from __future__ import annotations

from typing import Any

from pytui.core.buffer import OptimizedBuffer
from pytui.core.renderable import Renderable
from pytui.core.syntax_style import SyntaxStyle
from pytui.core.text_buffer import TextBuffer
from pytui.core.text_buffer_view import TextBufferView
from pytui.core.types import LineInfo
from pytui.lib import parse_color_to_tuple


class TextBufferRenderable(Renderable):
    """Base renderable that displays a TextBuffer via TextBufferView. Aligns OpenTUI TextBufferRenderable (API)."""

    def __init__(self, ctx: Any, options: dict[str, Any] | None = None) -> None:
        options = options or {}
        super().__init__(ctx, options)
        self.selectable = options.get("selectable", True)
        self._default_fg = parse_color_to_tuple(options.get("fg", "#ffffff"))
        self._default_bg = parse_color_to_tuple(options.get("bg", "transparent"))
        self._default_attributes = options.get("attributes", 0)
        self._selection_bg = (
            parse_color_to_tuple(options["selection_bg"]) if options.get("selection_bg") is not None else None
        )
        self._selection_fg = (
            parse_color_to_tuple(options["selection_fg"]) if options.get("selection_fg") is not None else None
        )
        self._wrap_mode = options.get("wrap_mode", "word")
        self._scroll_x = 0
        self._scroll_y = 0
        self._tab_indicator = options.get("tab_indicator", options.get("tabIndicator"))
        self._tab_indicator_color = (
            parse_color_to_tuple(options["tab_indicator_color"])
            if options.get("tab_indicator_color") is not None
            else (parse_color_to_tuple(options["tabIndicatorColor"]) if options.get("tabIndicatorColor") is not None else None)
        )
        self._truncate = options.get("truncate", False)
        self._width_method = options.get("width_method", "unicode")

        self.text_buffer = TextBuffer.create(self._width_method)
        self.text_buffer_view = TextBufferView.create(self.text_buffer)
        self.text_buffer.set_default_fg(self._default_fg)
        self.text_buffer.set_default_bg(self._default_bg)
        self.text_buffer.set_default_attributes(self._default_attributes)
        self.text_buffer_view.set_wrap_mode(self._wrap_mode)
        if self._tab_indicator is not None:
            self.text_buffer_view.set_wrap_width(0)  # placeholder
        w = max(1, options.get("width", 80) if isinstance(options.get("width"), (int, float)) else 80)
        h = max(1, options.get("height", 24) if isinstance(options.get("height"), (int, float)) else 24)
        self.text_buffer_view.set_viewport_size(w, h)

    @property
    def line_info(self) -> LineInfo:
        return self.text_buffer_view.line_info

    @property
    def line_count(self) -> int:
        return self.text_buffer.get_line_count()

    @property
    def virtual_line_count(self) -> int:
        return self.text_buffer_view.get_virtual_line_count()

    @property
    def scroll_y(self) -> int:
        return self._scroll_y

    @scroll_y.setter
    def scroll_y(self, value: int) -> None:
        max_sy = max(0, self.scroll_height - self.height)
        clamped = max(0, min(value, max_sy))
        if self._scroll_y != clamped:
            self._scroll_y = clamped
            self._update_viewport()
            self.request_render()

    @property
    def scroll_x(self) -> int:
        return self._scroll_x

    @scroll_x.setter
    def scroll_x(self, value: int) -> None:
        max_sx = max(0, self.scroll_width - self.width)
        clamped = max(0, min(value, max_sx))
        if self._scroll_x != clamped:
            self._scroll_x = clamped
            self._update_viewport()
            self.request_render()

    @property
    def scroll_width(self) -> int:
        return self.line_info.get("max_line_width", 0)

    @property
    def scroll_height(self) -> int:
        return len(self.line_info.get("line_starts", []))

    @property
    def plain_text(self) -> str:
        return self.text_buffer.get_plain_text()

    @property
    def text_length(self) -> int:
        return self.text_buffer.length

    def _update_viewport(self) -> None:
        self.text_buffer_view.set_viewport(
            self._scroll_x, self._scroll_y, max(1, self.width), max(1, self.height)
        )

    def get_selected_text(self) -> str:
        return self.text_buffer_view.get_selected_text()

    def has_selection(self) -> bool:
        return self.text_buffer_view.has_selection()

    def get_selection(self) -> tuple[int, int] | None:
        return self.text_buffer_view.get_selection()

    def render_self(self, buffer: OptimizedBuffer) -> None:
        """Draw text buffer content line by line (no native drawTextBuffer in Python)."""
        lines = self.text_buffer.get_plain_text().split("\n")
        if not lines:
            return
        info = self.line_info
        starts = info.get("line_starts", [])
        fg = self._default_fg
        h = max(1, self.height)
        start_row = self._scroll_y
        for i in range(min(h, len(lines) - start_row)):
            row = start_row + i
            if row >= len(lines):
                break
            line = lines[row]
            if self._scroll_x > 0:
                line = line[self._scroll_x : self._scroll_x + self.width]
            else:
                line = line[: self.width]
            buffer.draw_text(line, self.x, self.y + i, fg)

    def destroy(self) -> None:
        self.text_buffer_view.destroy()
        self.text_buffer.destroy()
