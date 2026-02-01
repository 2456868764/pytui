# pytui.core.console - Aligns with OpenTUI packages/core/src/console.ts
# ConsolePosition, ConsoleAction, ConsoleOptions, TerminalConsole, capture, visible, bounds, resize, set_debug_mode, get_cached_logs.

import os
import sys
from typing import Any, Literal, TypedDict

from pytui.core.buffer import Cell, OptimizedBuffer
from pytui.core.renderable import Renderable
from pytui.lib import parse_color_to_tuple
from pytui.core.renderer import Renderer
from pytui.core.terminal import Terminal

ConsoleLevel = str  # "log" | "info" | "warn" | "error" | "debug"

# Align with OpenTUI ConsolePosition
ConsolePosition = Literal["top", "bottom", "left", "right"]

# Align with OpenTUI ConsoleAction
ConsoleAction = Literal[
    "scroll-up",
    "scroll-down",
    "scroll-to-top",
    "scroll-to-bottom",
    "position-previous",
    "position-next",
    "size-increase",
    "size-decrease",
    "save-logs",
    "copy-selection",
]


class ConsoleOptions(TypedDict, total=False):
    """Options for console overlay; aligns with OpenTUI ConsoleOptions."""

    position: ConsolePosition
    size_percent: int
    sizePercent: int
    z_index: int
    zIndex: int
    color_info: str
    colorInfo: str
    color_warn: str
    colorWarn: str
    color_error: str
    colorError: str
    color_debug: str
    colorDebug: str
    color_default: str
    colorDefault: str
    backgroundColor: str
    background_color: str
    start_in_debug_mode: bool
    startInDebugMode: bool
    title: str
    titleBarColor: str
    title_bar_color: str
    titleBarTextColor: str
    title_bar_text_color: str
    cursorColor: str
    cursor_color: str
    max_stored_logs: int
    maxStoredLogs: int
    max_display_lines: int
    maxDisplayLines: int
    on_copy_selection: object
    onCopySelection: object
    selection_color: str
    selectionColor: str
    copy_button_color: str
    copyButtonColor: str


class ConsoleBuffer:
    """Output buffer for ConsoleOverlay; capture_stdout/capture_stderr write here. Lines are (text, level)."""

    def __init__(self, max_lines: int = 500, max_stored_logs: int | None = None) -> None:
        self._lines: list[tuple[str, ConsoleLevel]] = []
        self.max_lines = max_stored_logs if max_stored_logs is not None else max_lines
        self._collect_caller_info = False

    @property
    def lines(self) -> list[tuple[str, ConsoleLevel]]:
        return self._lines

    def set_collect_caller_info(self, enabled: bool) -> None:
        """Align with OpenTUI TerminalConsoleCache.setCollectCallerInfo."""
        self._collect_caller_info = enabled

    def append(self, text: str, level: ConsoleLevel = "log") -> None:
        for line in text.splitlines():
            self._lines.append((line, level))
            if len(self._lines) > self.max_lines:
                self._lines.pop(0)

    def clear(self) -> None:
        self._lines.clear()

    def get_cached_logs(self) -> str:
        """Return all buffered lines as a single string (align with OpenTUI getCachedLogs)."""
        return "\n".join(line for line, _ in self._lines)


class ConsoleOverlay(Renderable):
    """Console overlay: shows ConsoleBuffer; position top/bottom/left/right; scroll when focused; color by level."""

    def __init__(self, ctx: Any, options: dict | None = None) -> None:
        options = options or {}
        super().__init__(ctx, options)
        self.buffer: ConsoleBuffer = options.get("buffer") or ConsoleBuffer(
            max_stored_logs=options.get("max_stored_logs", options.get("maxStoredLogs")) or 500
        )
        self.scroll_y = 0
        self.position = options.get("position", "bottom")  # ConsolePosition
        self._visible = True
        self._debug_mode_enabled = bool(
            options.get("start_in_debug_mode", options.get("startInDebugMode", False))
        )
        self.buffer.set_collect_caller_info(self._debug_mode_enabled)
        self.fg = parse_color_to_tuple(options.get("fg", options.get("color_default", options.get("colorDefault")) or "#cccccc"))
        self.bg = parse_color_to_tuple(options.get("bg", options.get("backgroundColor", options.get("background_color")) or "#1a1a1a"))
        self.color_info = parse_color_to_tuple(options.get("color_info", options.get("colorInfo")) or "#00ffff")
        self.color_warn = parse_color_to_tuple(options.get("color_warn", options.get("colorWarn")) or "#ffff00")
        self.color_error = parse_color_to_tuple(options.get("color_error", options.get("colorError")) or "#ff0000")
        self.color_debug = parse_color_to_tuple(options.get("color_debug", options.get("colorDebug")) or "#808080")

    @property
    def visible(self) -> bool:
        """Align with OpenTUI TerminalConsole.visible."""
        return self._visible

    @visible.setter
    def visible(self, value: bool) -> None:
        """Allow base Renderable to set visible from options."""
        self._visible = value

    @property
    def bounds(self) -> dict[str, int]:
        """Align with OpenTUI TerminalConsole.bounds: { x, y, width, height }."""
        return {"x": self.x, "y": self.y, "width": self.width, "height": self.height}

    def resize(self, width: int, height: int) -> None:
        """Align with OpenTUI TerminalConsole.resize(width, height)."""
        self.width = max(1, width)
        self.height = max(1, height)
        self.request_render()

    def set_debug_mode(self, enabled: bool) -> None:
        """Align with OpenTUI TerminalConsole.setDebugMode."""
        self._debug_mode_enabled = enabled
        self.buffer.set_collect_caller_info(enabled)
        self.request_render()

    def toggle_debug_mode(self) -> None:
        """Align with OpenTUI TerminalConsole.toggleDebugMode."""
        self.set_debug_mode(not self._debug_mode_enabled)

    def get_cached_logs(self) -> str:
        """Align with OpenTUI TerminalConsole.getCachedLogs."""
        return self.buffer.get_cached_logs()

    def show(self) -> None:
        """Align with OpenTUI TerminalConsole.show."""
        self._visible = True
        self.request_render()

    def hide(self) -> None:
        """Align with OpenTUI TerminalConsole.hide."""
        self._visible = False
        self.request_render()

    def clear(self) -> None:
        """Align with OpenTUI TerminalConsole.clear."""
        self.buffer.clear()
        self.request_render()

    def focus(self) -> None:
        super().focus()
        if hasattr(self.ctx, "renderer") and self.ctx.renderer:
            self.ctx.renderer.keyboard.on("keypress", self._on_keypress)

    def blur(self) -> None:
        if hasattr(self.ctx, "renderer") and self.ctx.renderer:
            self.ctx.renderer.keyboard.remove_listener("keypress", self._on_keypress)
        super().blur()

    def _on_keypress(self, key: dict) -> None:
        if not self.focused:
            return
        name = key.get("name") or key.get("char")
        if name == "up":
            self.scroll_up()
        elif name == "down":
            self.scroll_down()

    def set_scroll(self, y: int) -> None:
        max_scroll = max(0, len(self.buffer.lines) - self.height)
        self.scroll_y = max(0, min(y, max_scroll))
        self.request_render()

    def scroll_up(self) -> None:
        self.set_scroll(self.scroll_y - 1)

    def scroll_down(self) -> None:
        self.set_scroll(self.scroll_y + 1)

    def _fg_for_level(self, level: ConsoleLevel) -> tuple[float, float, float, float]:
        if level == "info":
            return self.color_info
        if level == "warn":
            return self.color_warn
        if level == "error":
            return self.color_error
        if level == "debug":
            return self.color_debug
        return self.fg

    def render_self(self, buffer: OptimizedBuffer) -> None:
        if not self._visible:
            return
        lines = self.buffer.lines
        start = self.scroll_y
        for dy in range(self.height):
            line_idx = start + dy
            if line_idx < len(lines):
                text, level = lines[line_idx]
                line = (text[: self.width]).ljust(self.width)
                fg = self._fg_for_level(level)
            else:
                line = "".ljust(self.width)
                fg = self.fg
            for dx, ch in enumerate(line):
                if dx < self.width:
                    buffer.set_cell(
                        self.x + dx,
                        self.y + dy,
                        Cell(char=ch, fg=fg, bg=self.bg),
                    )


def capture_stdout(
    buffer: ConsoleBuffer,
    also_stdout: bool = True,
    stderr_to_buffer: bool = False,
    stderr_level: ConsoleLevel = "error",
) -> Any:
    """Context manager: write sys.stdout to buffer (level log); optionally also sys.stderr (level error)."""

    class Tee:
        def __init__(self, buf: ConsoleBuffer, original: Any, also: bool, level: ConsoleLevel) -> None:
            self.buffer = buf
            self.original = original
            self.also = also
            self.level = level

        def write(self, data: str) -> int:
            if data:
                self.buffer.append(data, level=self.level)
            if self.also:
                self.original.write(data)
            return len(data)

        def flush(self) -> None:
            self.original.flush()

    original_stdout = sys.stdout
    tee_stdout = Tee(buffer, original_stdout, also_stdout, "log")

    class Ctx:
        _stderr_patched = False

        def __enter__(self) -> None:
            sys.stdout = tee_stdout  # type: ignore[assignment]
            if stderr_to_buffer:
                self._original_stderr = sys.stderr  # type: ignore[attr-defined]
                self._tee_stderr = Tee(buffer, self._original_stderr, True, stderr_level)
                sys.stderr = self._tee_stderr  # type: ignore[assignment]
                self._stderr_patched = True

        def __exit__(self, *args: Any) -> None:
            sys.stdout = original_stdout
            if getattr(self, "_stderr_patched", False):
                sys.stderr = self._original_stderr  # type: ignore[attr-defined]

    return Ctx()


class ConsoleController:
    """Controller for console overlay: toggle() focuses or blurs overlay (aligns with OpenTUI renderer.console.toggle())."""

    def __init__(self, overlay: ConsoleOverlay, renderer: Renderer) -> None:
        self.overlay = overlay
        self.renderer = renderer

    def toggle(self) -> None:
        """When overlay is focused, blur; otherwise focus. When open but not focused, focus; when focused, close (blur)."""
        if self.overlay.focused:
            self.overlay.blur()
        else:
            self.overlay.focus()
        self.renderer.schedule_render()


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
