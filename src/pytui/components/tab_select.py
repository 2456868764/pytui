# pytui.components.tab_select


from pytui.core.buffer import Cell, OptimizedBuffer
from pytui.core.colors import parse_color
from pytui.core.renderable import Renderable


class TabSelect(Renderable):
    """多 tab 切换：水平排列，选中项高亮，支持 selection_changed 事件。"""

    def __init__(self, ctx, options: dict | None = None) -> None:
        options = options or {}
        super().__init__(ctx, options)
        self.tabs: list[str] = list(options.get("tabs", []))
        self.selected_index = max(0, min(options.get("selected", 0), len(self.tabs) - 1))
        self.fg = parse_color(options.get("fg", "#ffffff"))
        self.bg = parse_color(options.get("bg", "transparent"))
        self.selected_fg = parse_color(options.get("selected_fg", "#000000"))
        self.selected_bg = parse_color(options.get("selected_bg", "#ffffff"))
        self.separator = options.get("separator", "  ")

    @property
    def selected(self) -> str | None:
        if 0 <= self.selected_index < len(self.tabs):
            return self.tabs[self.selected_index]
        return None

    def select_index(self, index: int) -> None:
        if 0 <= index < len(self.tabs) and index != self.selected_index:
            self.selected_index = index
            self.emit("selection_changed", self.selected_index, self.selected)
            self.request_render()

    def select_next(self) -> None:
        if self.tabs:
            self.select_index((self.selected_index + 1) % len(self.tabs))

    def select_prev(self) -> None:
        if self.tabs:
            self.select_index((self.selected_index - 1 + len(self.tabs)) % len(self.tabs))

    def render_self(self, buffer: OptimizedBuffer) -> None:
        if self.height < 1:
            return
        x_off = 0
        for i, label in enumerate(self.tabs):
            if x_off >= self.width:
                break
            is_selected = i == self.selected_index
            fg = self.selected_fg if is_selected else self.fg
            bg = self.selected_bg if is_selected else self.bg
            text = f"[{label}]" if is_selected else label
            seg_len = min(len(text), self.width - x_off)
            for dx in range(seg_len):
                if x_off + dx < self.width:
                    ch = text[dx] if dx < len(text) else " "
                    buffer.set_cell(
                        self.x + x_off + dx,
                        self.y,
                        Cell(char=ch, fg=fg, bg=bg),
                    )
            x_off += len(text)
            if i < len(self.tabs) - 1:
                for _, s in enumerate(self.separator):
                    if x_off < self.width:
                        buffer.set_cell(self.x + x_off, self.y, Cell(char=s, fg=self.fg, bg=self.bg))
                        x_off += 1
