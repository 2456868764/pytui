# pytui.components.scrollbar


from pytui.core.buffer import Cell, OptimizedBuffer
from pytui.core.colors import parse_color
from pytui.core.renderable import Renderable


class ScrollBar(Renderable):
    """独立垂直滚动条：scroll_max、scroll_value，可组合 Scrollbox 使用，支持 scroll 事件。"""

    def __init__(self, ctx, options: dict | None = None) -> None:
        options = options or {}
        super().__init__(ctx, options)
        self.scroll_max = max(0, int(options.get("scroll_max", 0)))
        self._scroll_value = max(
            0,
            min(self.scroll_max, int(options.get("scroll_value", 0))),
        )
        self.fg = parse_color(options.get("fg", "#555555"))
        self.bg = parse_color(options.get("bg", "transparent"))
        self.thumb_fg = parse_color(options.get("thumb_fg", "#ffffff"))
        self.thumb_bg = parse_color(options.get("thumb_bg", "#888888"))

    @property
    def scroll_value(self) -> int:
        return self._scroll_value

    def set_scroll_value(self, v: int) -> None:
        v = max(0, min(self.scroll_max, v))
        if v != self._scroll_value:
            self._scroll_value = v
            self.emit("scroll", self._scroll_value)
            self.request_render()

    def _value_to_row(self) -> int:
        if self.scroll_max <= 0 or self.height <= 1:
            return 0
        r = self._scroll_value / self.scroll_max
        return int(r * (self.height - 1))

    def _row_to_value(self, row: int) -> int:
        if self.height <= 1:
            return 0
        r = max(0, min(1, row / (self.height - 1)))
        return int(r * self.scroll_max)

    def set_scroll_from_row(self, row: int) -> None:
        self.set_scroll_value(self._row_to_value(row))

    def render_self(self, buffer: OptimizedBuffer) -> None:
        track_char = "│"
        thumb_char = "█"
        for dy in range(self.height):
            buffer.set_cell(
                self.x,
                self.y + dy,
                Cell(char=track_char, fg=self.fg, bg=self.bg),
            )
        if self.scroll_max > 0 and self.height > 0:
            row = self._value_to_row()
            if 0 <= row < self.height:
                buffer.set_cell(
                    self.x,
                    self.y + row,
                    Cell(char=thumb_char, fg=self.thumb_fg, bg=self.thumb_bg),
                )
