# pytui.components.code


from pytui.core.buffer import Cell, OptimizedBuffer
from pytui.core.colors import parse_color
from pytui.core.renderable import Renderable
from pytui.syntax.highlighter import highlight
from pytui.syntax.themes import get_theme


class Code(Renderable):
    """代码块：可选语法高亮 + 行号 + show_diff（左侧 +/- 列）+ show_diagnostics（左侧诊断标记）。"""

    def __init__(self, ctx, options: dict | None = None):
        options = options or {}
        super().__init__(ctx, options)
        self.content = options.get("content", "")
        self.language = options.get("language", "python")
        self.show_line_numbers = options.get("show_line_numbers", True)
        self.show_diff = options.get("show_diff", False)
        self.show_diagnostics = options.get("show_diagnostics", False)
        # diagnostics: list of (line_0based, severity) e.g. [(1, "error"), (4, "warning")]
        self.diagnostics = list(options.get("diagnostics", []))
        self.theme_name = options.get("theme", "default")
        self.theme = get_theme(self.theme_name)
        self.fg = parse_color(options.get("fg", "#cccccc"))
        self.bg = parse_color(options.get("bg", "transparent"))
        self.line_num_fg = parse_color(options.get("line_num_fg", "#666666"))
        self._diff_add_fg = parse_color(options.get("diff_add_fg", "#22aa22"))
        self._diff_remove_fg = parse_color(options.get("diff_remove_fg", "#aa2222"))
        self._diag_error_fg = parse_color(options.get("diag_error_fg", "#ff6666"))
        self._diag_warning_fg = parse_color(options.get("diag_warning_fg", "#ddaa00"))

    def set_content(self, content: str) -> None:
        if self.content != content:
            self.content = content
            self.request_render()

    def set_show_diff(self, value: bool) -> None:
        if self.show_diff != value:
            self.show_diff = value
            self.request_render()

    def set_show_diagnostics(self, value: bool) -> None:
        if self.show_diagnostics != value:
            self.show_diagnostics = value
            self.request_render()

    def render_self(self, buffer: OptimizedBuffer) -> None:
        lines = self.content.split("\n")
        col_start = 0
        diff_w = 1 if self.show_diff else 0
        diag_w = 1 if self.show_diagnostics else 0
        col_start += diff_w + diag_w
        line_w = 0
        if self.show_line_numbers and lines:
            line_w = min(len(str(len(lines))) + 1, (self.width - col_start) // 4)
        col_start += line_w

        for dy, line in enumerate(lines):
            if dy >= self.height:
                break
            x_off = 0
            # Diff 列：+ 绿 / - 红
            if self.show_diff and diff_w > 0:
                ch = "+" if dy % 2 == 0 else "-"
                fg = self._diff_add_fg if ch == "+" else self._diff_remove_fg
                buffer.set_cell(self.x + x_off, self.y + dy, Cell(char=ch, fg=fg, bg=self.bg))
                x_off += 1
            # 诊断列：! 错误 / ⚠ 警告
            if self.show_diagnostics and diag_w > 0:
                mark = " "
                for d_line, severity in self.diagnostics:
                    if d_line == dy:
                        mark = "!" if severity == "error" else "⚠"
                        break
                fg = self._diag_error_fg if mark == "!" else self._diag_warning_fg if mark == "⚠" else self.line_num_fg
                buffer.set_cell(self.x + x_off, self.y + dy, Cell(char=mark, fg=fg, bg=self.bg))
                x_off += 1
            # 行号
            if self.show_line_numbers and line_w > 0:
                num_str = (str(dy + 1) + " ").rjust(line_w)[:line_w]
                for dx, ch in enumerate(num_str):
                    if x_off + dx >= self.width:
                        break
                    buffer.set_cell(
                        self.x + x_off + dx,
                        self.y + dy,
                        Cell(char=ch, fg=self.line_num_fg, bg=self.bg),
                    )
                x_off += line_w

            # 代码（可选高亮）
            spans = highlight(line, self.language)
            col = x_off
            for text, token_type in spans:
                color = self.theme.get(token_type, self.theme["plain"])
                for ch in text:
                    if col >= self.width:
                        break
                    buffer.set_cell(
                        self.x + col,
                        self.y + dy,
                        Cell(char=ch, fg=color, bg=self.bg),
                    )
                    col += 1
            for col in range(col, self.width):
                buffer.set_cell(
                    self.x + col,
                    self.y + dy,
                    Cell(char=" ", fg=self.fg, bg=self.bg),
                )
