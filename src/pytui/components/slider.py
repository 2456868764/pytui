# pytui.components.slider

from typing import Optional

from pytui.core.buffer import Cell, OptimizedBuffer
from pytui.core.colors import parse_color
from pytui.core.renderable import Renderable


class Slider(Renderable):
    """数值滑块：min/max/step，水平条与拇指，支持 change 事件。"""

    def __init__(self, ctx, options: Optional[dict] = None) -> None:
        options = options or {}
        super().__init__(ctx, options)
        self._min = float(options.get("min", 0))
        self._max = float(options.get("max", 100))
        self._step = float(options.get("step", 1))
        if self._step <= 0:
            self._step = 1
        self._value = max(
            self._min,
            min(self._max, float(options.get("value", self._min))),
        )
        self.fg = parse_color(options.get("fg", "#ffffff"))
        self.bg = parse_color(options.get("bg", "transparent"))
        self.thumb_fg = parse_color(options.get("thumb_fg", "#ffffff"))
        self.thumb_bg = parse_color(options.get("thumb_bg", "#444444"))

    @property
    def value(self) -> float:
        return self._value

    def set_value(self, v: float) -> None:
        v = max(self._min, min(self._max, v))
        if v != self._value:
            self._value = v
            self.emit("change", self._value)
            self.request_render()

    def _value_to_pos(self) -> int:
        if self._max <= self._min or self.width <= 0:
            return 0
        r = (self._value - self._min) / (self._max - self._min)
        return int(r * (self.width - 1))

    def _pos_to_value(self, pos: int) -> float:
        if self.width <= 1:
            return self._min
        r = max(0, min(1, pos / (self.width - 1)))
        v = self._min + r * (self._max - self._min)
        if self._step > 0:
            v = round((v - self._min) / self._step) * self._step + self._min
        return max(self._min, min(self._max, v))

    def set_value_from_pos(self, pos: int) -> None:
        self.set_value(self._pos_to_value(pos))

    def render_self(self, buffer: OptimizedBuffer) -> None:
        track_char = "─"
        thumb_char = "●"
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
