# pytui.components.text


from pytui.core.buffer import Cell, OptimizedBuffer
from pytui.core.colors import parse_color
from pytui.core.renderable import Renderable


class Text(Renderable):
    """文本组件。"""

    def __init__(self, ctx, options: dict | None = None):
        options = options or {}
        super().__init__(ctx, options)
        self.content = options.get("content", "")
        self.fg = parse_color(options.get("fg", "#ffffff"))
        self.bg = parse_color(options.get("bg", "transparent"))
        self.bold = options.get("bold", False)
        self.italic = options.get("italic", False)
        self.underline = options.get("underline", False)

    def set_content(self, content: str) -> None:
        if self.content != content:
            self.content = content
            self.request_render()

    def render_self(self, buffer: OptimizedBuffer) -> None:
        lines = self.content.split("\n")
        for dy, line in enumerate(lines):
            if dy >= self.height:
                break
            for dx, char in enumerate(line):
                if dx >= self.width:
                    break
                buffer.set_cell(
                    self.x + dx,
                    self.y + dy,
                    Cell(
                        char=char,
                        fg=self.fg,
                        bg=self.bg,
                        bold=self.bold,
                        italic=self.italic,
                        underline=self.underline,
                    ),
                )
