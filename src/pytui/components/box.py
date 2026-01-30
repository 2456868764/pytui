# pytui.components.box

from typing import Literal

from pytui.core.buffer import Cell, OptimizedBuffer
from pytui.core.colors import parse_color
from pytui.core.renderable import Renderable

BorderStyle = Literal["single", "double", "rounded", "bold", "none"]


class Box(Renderable):
    """盒子组件（带边框）。"""

    BORDER_CHARS = {
        "single": {"tl": "┌", "tr": "┐", "bl": "└", "br": "┘", "h": "─", "v": "│"},
        "double": {"tl": "╔", "tr": "╗", "bl": "╚", "br": "╝", "h": "═", "v": "║"},
        "rounded": {"tl": "╭", "tr": "╮", "bl": "╰", "br": "╯", "h": "─", "v": "│"},
        "bold": {"tl": "┏", "tr": "┓", "bl": "┗", "br": "┛", "h": "━", "v": "┃"},
    }

    def __init__(self, ctx, options: dict | None = None):
        options = options or {}
        super().__init__(ctx, options)
        self.border = options.get("border", False)
        self.border_style: BorderStyle = options.get("border_style", "single")
        self.border_color = parse_color(options.get("border_color", "#ffffff"))
        self.background_color = parse_color(options.get("background_color", "transparent"))
        self.title = options.get("title")
        if self.border:
            self.layout_node.set_padding("all", 1)

    def render_self(self, buffer: OptimizedBuffer) -> None:
        if self.background_color[3] > 0:
            bg_cell = Cell(bg=self.background_color)
            for dy in range(self.height):
                for dx in range(self.width):
                    buffer.set_cell(self.x + dx, self.y + dy, bg_cell)
        if self.border and self.width >= 2 and self.height >= 2:
            self._draw_border(buffer)

    def _draw_border(self, buffer: OptimizedBuffer) -> None:
        chars = self.BORDER_CHARS.get(self.border_style, self.BORDER_CHARS["single"])
        buffer.set_cell(self.x, self.y, Cell(char=chars["tl"], fg=self.border_color))
        buffer.set_cell(
            self.x + self.width - 1, self.y, Cell(char=chars["tr"], fg=self.border_color)
        )
        buffer.set_cell(
            self.x,
            self.y + self.height - 1,
            Cell(char=chars["bl"], fg=self.border_color),
        )
        buffer.set_cell(
            self.x + self.width - 1,
            self.y + self.height - 1,
            Cell(char=chars["br"], fg=self.border_color),
        )
        for dx in range(1, self.width - 1):
            buffer.set_cell(
                self.x + dx, self.y, Cell(char=chars["h"], fg=self.border_color)
            )
            buffer.set_cell(
                self.x + dx,
                self.y + self.height - 1,
                Cell(char=chars["h"], fg=self.border_color),
            )
        for dy in range(1, self.height - 1):
            buffer.set_cell(
                self.x, self.y + dy, Cell(char=chars["v"], fg=self.border_color)
            )
            buffer.set_cell(
                self.x + self.width - 1,
                self.y + dy,
                Cell(char=chars["v"], fg=self.border_color),
            )
        if self.title:
            title = f" {self.title} "
            title_x = self.x + (self.width - len(title)) // 2
            if title_x >= self.x:
                for i, char in enumerate(title):
                    if title_x + i < self.x + self.width - 1:
                        buffer.set_cell(
                            title_x + i,
                            self.y,
                            Cell(char=char, fg=self.border_color),
                        )
