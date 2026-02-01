# pytui.components.scrollbar - aligns with OpenTUI ScrollBarRenderable (ScrollBar.ts): all properties, scrollBy, value_to_row/row_to_value, orientation, change event.

from __future__ import annotations

from typing import Literal

from pytui.core.buffer import Cell, OptimizedBuffer
from pytui.core.renderable import Renderable
from pytui.lib import parse_color_to_tuple

ScrollUnit = Literal["absolute", "viewport", "content", "step"]


class ScrollBar(Renderable):
    """Scrollbar: scroll_size, scroll_position, viewport_size, orientation, scroll_by(delta, unit), value_to_row/row_to_value. Aligns with OpenTUI ScrollBarRenderable."""

    def __init__(self, ctx, options: dict | None = None) -> None:
        options = options or {}
        super().__init__(ctx, options)
        self.orientation: Literal["vertical", "horizontal"] = options.get(
            "orientation", options.get("orientation", "vertical")
        )
        self._scroll_size = max(0, int(options.get("scroll_size", options.get("scrollSize", options.get("scroll_max", 0)))))
        self._viewport_size = max(1, int(options.get("viewport_size", options.get("viewportSize", 1))))
        self._scroll_position = max(
            0,
            min(
                self._scroll_size - self._viewport_size,
                int(options.get("scroll_position", options.get("scrollPosition", options.get("scroll_value", 0)))),
            ),
        )
        self.scroll_max = self._scroll_size  # backward compat
        self._scroll_value = self._scroll_position  # backward compat
        self.fg = parse_color_to_tuple(options.get("fg", options.get("backgroundColor", "#555555")))
        self.bg = parse_color_to_tuple(options.get("bg", "transparent"))
        self.thumb_fg = parse_color_to_tuple(options.get("thumb_fg", options.get("foregroundColor", "#ffffff")))
        self.thumb_bg = parse_color_to_tuple(options.get("thumb_bg", "#888888"))
        self._on_change = options.get("on_change", options.get("onChange"))
        self._show_arrows = options.get("show_arrows", options.get("showArrows", False))

    @property
    def scroll_size(self) -> int:
        return self._scroll_size

    @scroll_size.setter
    def scroll_size(self, value: int) -> None:
        value = max(0, value)
        if value != self._scroll_size:
            self._scroll_size = value
            self.scroll_max = value
            self._scroll_position = max(0, min(self._scroll_position, self._scroll_size - self._viewport_size))
            self._scroll_value = self._scroll_position
            self.request_render()

    @property
    def scroll_position(self) -> int:
        return self._scroll_position

    @scroll_position.setter
    def scroll_position(self, value: int) -> None:
        max_pos = max(0, self._scroll_size - self._viewport_size)
        value = max(0, min(max_pos, int(value)))
        if value != self._scroll_position:
            self._scroll_position = value
            self._scroll_value = value
            if self._on_change:
                self._on_change(value)
            self.emit("change", {"position": value})
            self.emit("scroll", value)
            self.request_render()

    @property
    def viewport_size(self) -> int:
        return self._viewport_size

    @viewport_size.setter
    def viewport_size(self, value: int) -> None:
        value = max(1, int(value))
        if value != self._viewport_size:
            self._viewport_size = value
            self._scroll_position = max(0, min(self._scroll_position, self._scroll_size - self._viewport_size))
            self._scroll_value = self._scroll_position
            self.request_render()

    @property
    def scroll_value(self) -> int:
        return self._scroll_position

    def set_scroll_value(self, v: int) -> None:
        self.scroll_position = v

    def scroll_by(self, delta: float, unit: ScrollUnit = "absolute") -> None:
        """Align with OpenTUI scrollBy(delta, unit). unit: absolute | viewport | content | step."""
        if unit == "viewport":
            mult = self._viewport_size
        elif unit == "content":
            mult = self._scroll_size
        elif unit == "step":
            mult = 1
        else:
            mult = 1
        self.scroll_position = self._scroll_position + int(delta * mult)

    def value_to_row(self) -> int:
        """Align with OpenTUI (slider) value_to_row. Public API."""
        return self._value_to_row()

    def row_to_value(self, row: int) -> int:
        """Align with OpenTUI (slider) row_to_value. Public API."""
        return self._row_to_value(row)

    def _track_len(self) -> int:
        return (self.height if self.orientation == "vertical" else self.width) or 1

    def _value_to_row(self) -> int:
        track = self._track_len()
        if self._scroll_size <= self._viewport_size or track <= 0:
            return 0
        r = self._scroll_position / max(1, self._scroll_size - self._viewport_size)
        return int(r * (track - 1))

    def _row_to_value(self, row: int) -> int:
        track = self._track_len()
        if track <= 1:
            return 0
        r = max(0, min(1, row / (track - 1)))
        return int(r * max(0, self._scroll_size - self._viewport_size))

    def set_scroll_from_row(self, row: int) -> None:
        self.set_scroll_value(self._row_to_value(row))

    @property
    def show_arrows(self) -> bool:
        return self._show_arrows

    @show_arrows.setter
    def show_arrows(self, value: bool) -> None:
        self._show_arrows = value
        self.request_render()

    def render_self(self, buffer: OptimizedBuffer) -> None:
        track_char = "│" if self.orientation == "vertical" else "─"
        thumb_char = "█"
        if self.orientation == "vertical":
            for dy in range(self.height):
                buffer.set_cell(
                    self.x,
                    self.y + dy,
                    Cell(char=track_char, fg=self.fg, bg=self.bg),
                )
            if self._scroll_size > self._viewport_size and self.height > 0:
                row = self._value_to_row()
                if 0 <= row < self.height:
                    buffer.set_cell(
                        self.x,
                        self.y + row,
                        Cell(char=thumb_char, fg=self.thumb_fg, bg=self.thumb_bg),
                    )
        else:
            for dx in range(self.width):
                buffer.set_cell(
                    self.x + dx,
                    self.y,
                    Cell(char=track_char, fg=self.fg, bg=self.bg),
                )
            if self._scroll_size > self._viewport_size and self.width > 0:
                col = self._value_to_row()
                if 0 <= col < self.width:
                    buffer.set_cell(
                        self.x + col,
                        self.y,
                        Cell(char=thumb_char, fg=self.thumb_fg, bg=self.thumb_bg),
                    )
