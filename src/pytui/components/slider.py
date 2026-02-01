# pytui.components.slider - aligns with OpenTUI SliderRenderable (Slider.ts): value, min, max, viewPortSize, orientation, value_to_row/row_to_value, value_to_pos/pos_to_value, change event.

from __future__ import annotations

from typing import Literal

from pytui.core.buffer import Cell, OptimizedBuffer
from pytui.core.renderable import Renderable
from pytui.lib import parse_color_to_tuple


class Slider(Renderable):
    """Slider: value, min, max, view_port_size, orientation, value_to_row/row_to_value (vertical), value_to_pos/pos_to_value (horizontal). Aligns with OpenTUI SliderRenderable."""

    def __init__(self, ctx, options: dict | None = None) -> None:
        options = options or {}
        super().__init__(ctx, options)
        self.orientation: Literal["vertical", "horizontal"] = options.get(
            "orientation", options.get("orientation", "horizontal")
        )
        self._min = float(options.get("min", 0))
        self._max = float(options.get("max", 100))
        self._step = float(options.get("step", 1))
        if self._step <= 0:
            self._step = 1
        self._view_port_size = float(options.get("view_port_size", options.get("viewPortSize", max(1, (self._max - self._min) * 0.1))))
        self._value = max(
            self._min,
            min(self._max, float(options.get("value", self._min))),
        )
        self.fg = parse_color_to_tuple(options.get("fg", options.get("backgroundColor", "#252527")))
        self.bg = parse_color_to_tuple(options.get("bg", "transparent"))
        self.thumb_fg = parse_color_to_tuple(options.get("thumb_fg", options.get("foregroundColor", "#9a9ea3")))
        self.thumb_bg = parse_color_to_tuple(options.get("thumb_bg", "#444444"))
        self._on_change = options.get("on_change", options.get("onChange"))

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, v: float) -> None:
        v = max(self._min, min(self._max, v))
        if v != self._value:
            self._value = v
            if self._on_change:
                self._on_change(v)
            self.emit("change", {"value": v})
            self.request_render()

    @property
    def min(self) -> float:
        return self._min

    @min.setter
    def min(self, v: float) -> None:
        if v != self._min:
            self._min = v
            if self._value < v:
                self.value = v
            self.request_render()

    @property
    def max(self) -> float:
        return self._max

    @max.setter
    def max(self, v: float) -> None:
        if v != self._max:
            self._max = v
            if self._value > v:
                self.value = v
            self.request_render()

    @property
    def view_port_size(self) -> float:
        return self._view_port_size

    @view_port_size.setter
    def view_port_size(self, v: float) -> None:
        v = max(0.01, min(v, self._max - self._min))
        if v != self._view_port_size:
            self._view_port_size = v
            self.request_render()

    @property
    def backgroundColor(self):
        return self.fg

    @backgroundColor.setter
    def backgroundColor(self, value) -> None:
        self.fg = parse_color_to_tuple(value) if isinstance(value, str) else value
        self.request_render()

    @property
    def foregroundColor(self):
        return self.thumb_fg

    @foregroundColor.setter
    def foregroundColor(self, value) -> None:
        self.thumb_fg = parse_color_to_tuple(value) if isinstance(value, str) else value
        self.request_render()

    def set_value(self, v: float) -> None:
        self.value = v

    def value_to_row(self) -> int:
        """Vertical: value maps to row index. Align with OpenTUI value_to_row."""
        if self._max <= self._min or self.height <= 0:
            return 0
        r = (self._value - self._min) / (self._max - self._min)
        return int(r * (self.height - 1))

    def row_to_value(self, row: int) -> float:
        """Vertical: row index to value. Align with OpenTUI row_to_value."""
        if self.height <= 1:
            return self._min
        r = max(0, min(1, row / (self.height - 1)))
        v = self._min + r * (self._max - self._min)
        if self._step > 0:
            v = round((v - self._min) / self._step) * self._step + self._min
        return max(self._min, min(self._max, v))

    def value_to_pos(self) -> int:
        """Horizontal: value maps to position. Align with OpenTUI value_to_pos."""
        if self._max <= self._min or self.width <= 0:
            return 0
        r = (self._value - self._min) / (self._max - self._min)
        return int(r * (self.width - 1))

    def pos_to_value(self, pos: int) -> float:
        """Horizontal: position to value. Align with OpenTUI pos_to_value."""
        if self.width <= 1:
            return self._min
        r = max(0, min(1, pos / (self.width - 1)))
        v = self._min + r * (self._max - self._min)
        if self._step > 0:
            v = round((v - self._min) / self._step) * self._step + self._min
        return max(self._min, min(self._max, v))

    def _value_to_pos(self) -> int:
        if self.orientation == "vertical":
            return self.value_to_row()
        return self.value_to_pos()

    def _pos_to_value(self, pos: int) -> float:
        if self.orientation == "vertical":
            return self.row_to_value(pos)
        return self.pos_to_value(pos)

    def set_value_from_pos(self, pos: int) -> None:
        self.value = self._pos_to_value(pos)

    def render_self(self, buffer: OptimizedBuffer) -> None:
        track_char = "─" if self.orientation == "horizontal" else "│"
        thumb_char = "●"
        if self.orientation == "horizontal":
            for dy in range(self.height):
                for dx in range(self.width):
                    buffer.set_cell(
                        self.x + dx,
                        self.y + dy,
                        Cell(char=track_char, fg=self.fg, bg=self.bg),
                    )
            pos = self._value_to_pos()
            if 0 <= pos < self.width:
                for dy in range(self.height):
                    buffer.set_cell(
                        self.x + pos,
                        self.y + dy,
                        Cell(char=thumb_char, fg=self.thumb_fg, bg=self.thumb_bg),
                    )
        else:
            for dy in range(self.height):
                buffer.set_cell(
                    self.x,
                    self.y + dy,
                    Cell(char=track_char, fg=self.fg, bg=self.bg),
                )
            pos = self._value_to_pos()
            if 0 <= pos < self.height:
                buffer.set_cell(
                    self.x,
                    self.y + pos,
                    Cell(char=thumb_char, fg=self.thumb_fg, bg=self.thumb_bg),
                )
