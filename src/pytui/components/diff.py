# pytui.components.diff


from pytui.core.buffer import Cell, OptimizedBuffer
from pytui.core.colors import parse_color
from pytui.core.renderable import Renderable
from pytui.utils.diff import diff_lines


class Diff(Renderable):
    """Diff 视图：显示两段文本的增删改。"""

    def __init__(self, ctx, options: dict | None = None):
        options = options or {}
        super().__init__(ctx, options)
        self.old_text = options.get("old_text", "")
        self.new_text = options.get("new_text", "")
        self.add_fg = parse_color(options.get("add_fg", "#00ff00"))
        self.del_fg = parse_color(options.get("del_fg", "#ff0000"))
        self.ctx_fg = parse_color(options.get("context_fg", "#ffffff"))
        self.bg = parse_color(options.get("bg", "transparent"))
        self._diff: list[tuple[str, str]] = []

    def set_texts(self, old_text: str, new_text: str) -> None:
        if self.old_text != old_text or self.new_text != new_text:
            self.old_text = old_text
            self.new_text = new_text
            self.request_render()

    def render_self(self, buffer: OptimizedBuffer) -> None:
        self._diff = diff_lines(self.old_text, self.new_text)
        row = 0
        for tag, line in self._diff:
            if row >= self.height:
                break
            if tag == "+":
                fg = self.add_fg
                prefix = "+"
            elif tag == "-":
                fg = self.del_fg
                prefix = "-"
            else:
                fg = self.ctx_fg
                prefix = " "
            display = (prefix + " " + line)[: self.width]
            for dx, ch in enumerate(display):
                if dx >= self.width:
                    break
                buffer.set_cell(
                    self.x + dx,
                    self.y + row,
                    Cell(char=ch, fg=fg, bg=self.bg),
                )
            for dx in range(len(display), self.width):
                buffer.set_cell(
                    self.x + dx,
                    self.y + row,
                    Cell(char=" ", fg=fg, bg=self.bg),
                )
            row += 1
