# pytui.core.console - 控制台便捷入口与 Console Overlay（捕获 stdout/stderr 显示）


import sys
from typing import Any

from pytui.core.buffer import Cell, OptimizedBuffer
from pytui.core.colors import parse_color
from pytui.core.renderable import Renderable
from pytui.core.renderer import Renderer
from pytui.core.terminal import Terminal


class ConsoleBuffer:
    """控制台输出缓冲：供 ConsoleOverlay 显示，可由 capture_stdout 写入。"""

    def __init__(self, max_lines: int = 500) -> None:
        self._lines: list[str] = []
        self.max_lines = max_lines

    @property
    def lines(self) -> list[str]:
        return self._lines

    def append(self, text: str) -> None:
        for line in text.splitlines():
            self._lines.append(line)
            if len(self._lines) > self.max_lines:
                self._lines.pop(0)

    def clear(self) -> None:
        self._lines.clear()


class ConsoleOverlay(Renderable):
    """Console overlay：显示 ConsoleBuffer 内容，可定位 BOTTOM/TOP、可滚动。"""

    def __init__(self, ctx: Any, options: dict | None = None) -> None:
        options = options or {}
        super().__init__(ctx, options)
        self.buffer: ConsoleBuffer = options.get("buffer") or ConsoleBuffer()
        self.scroll_y = 0
        self.position = options.get("position", "bottom")  # "bottom" | "top"
        self.fg = parse_color(options.get("fg", "#cccccc"))
        self.bg = parse_color(options.get("bg", "#1a1a1a"))

    def set_scroll(self, y: int) -> None:
        self.scroll_y = max(0, min(y, max(0, len(self.buffer.lines) - self.height)))
        self.request_render()

    def scroll_up(self) -> None:
        self.set_scroll(self.scroll_y - 1)

    def scroll_down(self) -> None:
        self.set_scroll(self.scroll_y + 1)

    def render_self(self, buffer: OptimizedBuffer) -> None:
        lines = self.buffer.lines
        start = self.scroll_y
        for dy in range(self.height):
            line_idx = start + dy
            line = (lines[line_idx][: self.width] if line_idx < len(lines) else "").ljust(self.width)
            for dx, ch in enumerate(line):
                if dx < self.width:
                    buffer.set_cell(
                        self.x + dx,
                        self.y + dy,
                        Cell(char=ch, fg=self.fg, bg=self.bg),
                    )


def capture_stdout(buffer: ConsoleBuffer, also_stdout: bool = True):
    """上下文管理器：将 sys.stdout 写入 buffer，可选同时写回原 stdout。"""

    class Tee:
        def __init__(self, buffer: ConsoleBuffer, original: Any, also: bool) -> None:
            self.buffer = buffer
            self.original = original
            self.also = also

        def write(self, data: str) -> int:
            if data:
                self.buffer.append(data)
            if self.also:
                self.original.write(data)
            return len(data)

        def flush(self) -> None:
            self.original.flush()

    original = sys.stdout
    tee = Tee(buffer, original, also_stdout)

    class Ctx:
        def __enter__(self) -> None:
            sys.stdout = tee  # type: ignore[assignment]

        def __exit__(self, *args: Any) -> None:
            sys.stdout = original

    return Ctx()


class Console:
    """控制台便捷封装：终端尺寸 + 渲染器，可 run(app) 启动。"""

    def __init__(
        self,
        width: int | None = None,
        height: int | None = None,
        target_fps: int = 30,
        use_alternate_screen: bool = True,
        use_mouse: bool = False,
    ) -> None:
        self._terminal = Terminal()
        self._renderer = Renderer(
            width=width or self._terminal.width,
            height=height or self._terminal.height,
            target_fps=target_fps,
            use_alternate_screen=use_alternate_screen,
            use_mouse=use_mouse,
        )

    @property
    def renderer(self) -> Renderer:
        return self._renderer

    @property
    def root(self) -> Renderable:
        return self._renderer.root

    @property
    def context(self) -> object:
        return self._renderer.context

    def run(self, mount: Renderable | None = None) -> None:
        """若传入 mount 则挂到 root，然后 start()。"""
        if mount is not None:
            self._renderer.root.add(mount)
        self._renderer.start()
