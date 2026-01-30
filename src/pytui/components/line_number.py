# pytui.components.line_number


from pytui.core.buffer import Cell, OptimizedBuffer
from pytui.core.colors import parse_color
from pytui.core.renderable import Renderable


class LineNumber(Renderable):
    """行号区：左侧固定宽度的行号列（可配 scroll_offset），与内容区配合使用。"""

    def __init__(self, ctx, options: dict | None = None) -> None:
        options = options or {}
        super().__init__(ctx, options)
        self.line_count = max(0, int(options.get("line_count", 1)))
        self.scroll_offset = max(0, int(options.get("scroll_offset", 0)))
        self.line_number_width = max(1, int(options.get("line_number_width", 4)))
        self.fg = parse_color(options.get("fg", "#666666"))
        self.bg = parse_color(options.get("bg", "transparent"))

    def set_scroll_offset(self, offset: int) -> None:
        offset = max(0, offset)
        if offset != self.scroll_offset:
            self.scroll_offset = offset
            self.request_render()

    def render_self(self, buffer: OptimizedBuffer) -> None:
        w = min(self.line_number_width, self.width)
        for dy in range(self.height):
            line_num = self.scroll_offset + dy + 1
            num_str = str(line_num).rjust(w)
            if line_num > self.line_count:
                num_str = "".ljust(w)
            for dx, ch in enumerate(num_str):
                if dx < self.width:
                    buffer.set_cell(
                        self.x + dx,
                        self.y + dy,
                        Cell(char=ch, fg=self.fg, bg=self.bg),
                    )
            for dx in range(len(num_str), w):
                if dx < self.width:
                    buffer.set_cell(
                        self.x + dx,
                        self.y + dy,
                        Cell(char=" ", fg=self.fg, bg=self.bg),
                    )
