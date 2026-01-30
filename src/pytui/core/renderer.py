# pytui.core.renderer - CLI renderer

import codecs
import os
import select
import sys
import time
from dataclasses import dataclass

from pytui.core.buffer import OptimizedBuffer
from pytui.core.events import EventBus
from pytui.core.keyboard import KeyboardHandler
from pytui.core.renderable import Renderable
from pytui.core.terminal import Terminal


@dataclass
class RenderContext:
    """渲染上下文。"""
    renderer: "Renderer"


class RootRenderable(Renderable):
    """根渲染对象。"""

    def render_self(self, buffer: OptimizedBuffer) -> None:
        pass


class Renderer:
    """CLI 渲染器。"""

    def __init__(
        self,
        width: int | None = None,
        height: int | None = None,
        target_fps: int = 60,
        use_alternate_screen: bool = True,
        use_mouse: bool = False,
        terminal: Terminal | None = None,
    ) -> None:
        self.terminal = terminal or Terminal()
        self.width = width if width is not None else self.terminal.width
        self.height = height if height is not None else self.terminal.height
        self.target_fps = target_fps
        self.frame_time = 1.0 / target_fps if target_fps > 0 else 0.0
        self.use_alternate_screen = use_alternate_screen
        self.use_mouse = use_mouse
        self.front_buffer = OptimizedBuffer(self.width, self.height)
        self.back_buffer = OptimizedBuffer(self.width, self.height)
        self.context = RenderContext(renderer=self)
        self.root = RootRenderable(self.context, {"id": "root"})
        self.keyboard = KeyboardHandler()
        self.keyboard.on("keypress", self._on_keypress)
        self.events = EventBus()
        self.running = False
        self._render_scheduled = False
        self._frame_count = 0
        self._last_render_time = 0.0
        self._utf8_decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
        self.stats = {"fps": 0, "frame_time": 0.0, "render_time": 0.0}
        self._input_stream = None  # 非 TTY 时从 /dev/tty 读
        self._input_saved_attrs = None

    def start(self) -> None:
        self.running = True
        if self.use_alternate_screen:
            self.terminal.enter_alternate_screen()
        self.terminal.hide_cursor()
        self.terminal.set_raw_mode()
        # stdin 被重定向时（如 IDE 运行）从控制终端读，否则收不到方向键
        if not sys.stdin.isatty() and os.name == "posix":
            try:
                self._input_stream = open("/dev/tty", "rb")
                import termios
                import tty
                fd = self._input_stream.fileno()
                self._input_saved_attrs = termios.tcgetattr(fd)
                tty.setraw(fd)
            except Exception:
                self._input_stream = None
                self._input_saved_attrs = None
        if self.use_mouse:
            self.terminal.enable_mouse()
        try:
            self._run_loop()
        except KeyboardInterrupt:
            pass
        finally:
            self._cleanup()

    def stop(self) -> None:
        self.running = False

    def _run_loop(self) -> None:
        last_fps = time.time()
        fps_count = 0
        while self.running:
            start = time.time()
            self.events.emit("frame", start)
            self._process_input()
            self._check_resize()
            if self._render_scheduled or self._should_render():
                t0 = time.time()
                self._render_frame()
                self.stats["render_time"] = (time.time() - t0) * 1000
                self._render_scheduled = False
                fps_count += 1
            now = time.time()
            if now - last_fps >= 1.0:
                self.stats["fps"] = fps_count
                fps_count = 0
                last_fps = now
            self.stats["frame_time"] = (time.time() - start) * 1000
            if self.frame_time > 0 and (time.time() - start) < self.frame_time:
                time.sleep(self.frame_time - (time.time() - start))

    def _render_frame(self) -> None:
        self.back_buffer.clear()
        self.root.calculate_layout()
        self.root.render(self.back_buffer)
        self._diff_and_output()
        self.front_buffer, self.back_buffer = self.back_buffer, self.front_buffer
        self._frame_count += 1
        self._last_render_time = time.time()

    def _diff_and_output(self) -> None:
        from pytui.core.ansi import ANSI

        out = []
        # 首帧全量重绘，确保终端显示完整内容
        full_repaint = self._frame_count == 0
        if full_repaint:
            out.append(ANSI.CURSOR_HOME)
            out.append(ANSI.CLEAR_SCREEN)
        for y in range(self.height):
            for x in range(self.width):
                fc = self.front_buffer.get_cell(x, y)
                bc = self.back_buffer.get_cell(x, y)
                if full_repaint or (fc != bc and bc is not None):
                    if bc is not None:
                        out.append(ANSI.cursor_to(x, y))
                        out.append(self.back_buffer._cell_to_ansi(bc))
        if out:
            sys.stdout.write("".join(out))
            sys.stdout.flush()

    def _process_input(self) -> None:
        # 非 TTY 时从 /dev/tty 读，否则从 stdin；逐字节读 + 增量 UTF-8 解码
        stream = self._input_stream if self._input_stream is not None else getattr(sys.stdin, "buffer", sys.stdin)
        max_reads = 256
        try:
            ready = select.select([stream], [], [], 0)[0]
        except (ValueError, OSError) as e:
            if os.environ.get("PYTUI_DEBUG"):
                print(f"[pytui:renderer] select error: {e}", file=sys.stderr, flush=True)
            ready = []
        if os.environ.get("PYTUI_DEBUG") and ready:
            print("[pytui:renderer] select ready, reading...", file=sys.stderr, flush=True)
        while max_reads > 0 and ready:
            data = stream.read(1)
            if not data:
                break
            if os.environ.get("PYTUI_DEBUG"):
                print(f"[pytui:renderer] read bytes: {data!r}", file=sys.stderr, flush=True)
            if isinstance(data, bytes):
                decoded = self._utf8_decoder.decode(data)
                if decoded:
                    if os.environ.get("PYTUI_DEBUG"):
                        print(f"[pytui:renderer] feed decoded: {decoded!r}", file=sys.stderr, flush=True)
                    self.keyboard.feed(decoded)
            else:
                self.keyboard.feed(data)
            max_reads -= 1
            try:
                ready = select.select([stream], [], [], 0)[0]
            except (ValueError, OSError):
                ready = []

    def _check_resize(self) -> None:
        w, h = self.terminal.get_size()
        if w != self.width or h != self.height:
            self.width, self.height = w, h
            self.front_buffer = OptimizedBuffer(self.width, self.height)
            self.back_buffer = OptimizedBuffer(self.width, self.height)
            self.events.emit("resize", self.width, self.height)
            self.schedule_render()

    def _on_keypress(self, key: dict) -> None:
        self.events.emit("keypress", key)
        if key.get("ctrl") and key.get("name") == "c":
            self.stop()

    def _should_render(self) -> bool:
        return self.root._dirty

    def schedule_render(self) -> None:
        self._render_scheduled = True

    def _cleanup(self) -> None:
        if self._input_stream is not None and self._input_saved_attrs is not None:
            try:
                import termios
                termios.tcsetattr(self._input_stream.fileno(), termios.TCSADRAIN, self._input_saved_attrs)
            except Exception:
                pass
            try:
                self._input_stream.close()
            except Exception:
                pass
            self._input_stream = None
            self._input_saved_attrs = None
        if self.use_mouse:
            self.terminal.disable_mouse()
        self.terminal.show_cursor()
        self.terminal.restore_mode()
        if self.use_alternate_screen:
            self.terminal.exit_alternate_screen()

    def render_once(self) -> None:
        """执行一次布局与渲染（不读输入、不写终端）。用于无 TTY 测试。"""
        self._check_resize()
        self.back_buffer.clear()
        self.root.calculate_layout()
        self.root.render(self.back_buffer)
        self.front_buffer, self.back_buffer = self.back_buffer, self.front_buffer
        self._frame_count += 1
