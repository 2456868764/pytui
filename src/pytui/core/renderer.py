# pytui.core.renderer - Aligns with OpenTUI packages/core/src/renderer.ts
# CliRendererConfig, RendererControlState, DebugOverlayCorner, scheduleRender, renderFrame, destroy, etc.

import codecs
import os
import select
import sys
import time
from dataclasses import dataclass
from typing import Any, Callable

from pytui.core.buffer import OptimizedBuffer
from pytui.core.events import EventBus
from pytui.core.keyboard import KeyboardHandler
from pytui.core.renderable import Renderable
from pytui.core.terminal import Terminal
from pytui.core.types import CursorStyle, DebugOverlayCorner

try:
    from pytui_native import CliRenderer as NativeCliRenderer
except ImportError:
    NativeCliRenderer = None  # type: ignore[misc, assignment]

# --- Enums / constants (align OpenTUI RendererControlState, DebugOverlayCorner, CliRenderEvents) ---
class RendererControlState:
    IDLE = "idle"
    AUTO_STARTED = "auto_started"
    EXPLICIT_STARTED = "explicit_started"
    EXPLICIT_PAUSED = "explicit_paused"
    EXPLICIT_SUSPENDED = "explicit_suspended"
    EXPLICIT_STOPPED = "explicit_stopped"


class CliRenderEvents:
    DEBUG_OVERLAY_TOGGLE = "debugOverlay:toggle"
    DESTROY = "destroy"


@dataclass
class RenderContext:
    """渲染上下文。Aligns OpenTUI RenderContext."""

    renderer: "Renderer"


class RootRenderable(Renderable):
    """根渲染对象。"""

    def render_self(self, buffer: OptimizedBuffer) -> None:
        pass


class Renderer:
    """CLI 渲染器。Aligns OpenTUI CliRenderer (renderer.ts).

    Config: target_fps, max_fps, use_alternate_screen, use_mouse, exit_on_ctrl_c, exit_signals,
    debounce_delay, use_kitty_keyboard, gather_stats, max_stat_samples, memory_snapshot_interval,
    use_console, experimental_split_height, enable_mouse_movement, backgroundColor,
    open_console_on_error, on_destroy.
    Getters: control_state, is_destroyed, is_running, terminal_width, terminal_height, use_mouse,
    key_input, use_console, experimental_split_height, live_request_count, current_control_state,
    capabilities, resolution, current_focused_renderable, palette_detection_status.
    Methods: set_frame_callback, remove_frame_callback, clear_frame_callbacks, get_stats,
    reset_stats, set_gather_stats, add_input_handler, prepend_input_handler, remove_input_handler,
    set_background_color, toggle_debug_overlay, configure_debug_overlay, set_terminal_title,
    dump_hit_grid, dump_buffers, dump_stdout_buffer, set_cursor_position, set_cursor_style,
    set_cursor_color, get_cursor_state, add_post_process_fn, remove_post_process_fn,
    clear_post_process_fns, request_live, drop_live, auto, pause, suspend, resume, stop, destroy,
    intermediate_render, get_selection, has_selection, get_selection_container, clear_selection,
    start_selection, update_selection, request_selection_update, register_lifecycle_pass,
    unregister_lifecycle_pass, get_lifecycle_passes, focus_renderable, hit_test,
    set_memory_snapshot_interval, clear_palette_cache, idle, get_debug_inputs.
    Events: resize, keypress, keyrelease, paste, memory:snapshot, debugOverlay:toggle, destroy.
    """

    def __init__(
        self,
        width: int | None = None,
        height: int | None = None,
        target_fps: int = 60,
        max_fps: int = 60,
        use_alternate_screen: bool = True,
        use_mouse: bool = False,
        terminal: Terminal | None = None,
        exit_on_ctrl_c: bool = True,
        exit_signals: list | None = None,
        debounce_delay: int = 100,
        use_kitty_keyboard: bool = False,
        gather_stats: bool = False,
        max_stat_samples: int = 300,
        memory_snapshot_interval: int = 0,
        use_console: bool = True,
        experimental_split_height: int = 0,
        enable_mouse_movement: bool = False,
        backgroundColor: Any = None,
        open_console_on_error: bool = True,
        on_destroy: Callable[[], None] | None = None,
    ) -> None:
        self.terminal = terminal or Terminal()
        w, h = self.terminal.get_size()
        self._terminal_width = w
        self._terminal_height = h
        self.width = width if width is not None else w
        self.height = height if height is not None else (experimental_split_height if experimental_split_height > 0 else h)
        self.target_fps = target_fps
        self.max_fps = max_fps
        self.frame_time = 1.0 / target_fps if target_fps > 0 else 0.0
        self.min_frame_time = 1.0 / max_fps if max_fps > 0 else 0.0
        self.use_alternate_screen = use_alternate_screen
        self._use_mouse = use_mouse
        self.exit_on_ctrl_c = exit_on_ctrl_c
        self.exit_signals = exit_signals or []
        self.debounce_delay = debounce_delay
        self.use_kitty_keyboard = use_kitty_keyboard
        self.gather_stats = gather_stats
        self.max_stat_samples = max_stat_samples
        self.memory_snapshot_interval = memory_snapshot_interval
        self._use_console = use_console
        self._experimental_split_height = experimental_split_height
        self._render_offset = h - experimental_split_height if experimental_split_height > 0 else 0
        self.enable_mouse_movement = enable_mouse_movement
        self.open_console_on_error = open_console_on_error
        self._on_destroy = on_destroy
        self._control_state = RendererControlState.IDLE
        self._is_destroyed = False
        self._live_request_counter = 0
        self._debug_inputs: list[dict[str, str]] = []
        self._debug_mode_enabled = os.environ.get("OTUI_DEBUG", "").lower() in ("1", "true", "yes")
        self._input_handlers: list[Callable[[str], bool]] = []
        self._prepended_input_handlers: list[Callable[[str], bool]] = []
        self.post_process_fns: list[Callable[[OptimizedBuffer, float], None]] = []
        self.debug_overlay = {"enabled": False, "corner": DebugOverlayCorner.bottom_right}
        self._current_focused_renderable: Renderable | None = None
        self._lifecycle_passes: set = set()
        self._resolution: dict | None = None
        self._capabilities: Any = None
        self._backgroundColor = (0, 0, 0, 0)
        if backgroundColor is not None:
            try:
                from pytui.lib import parse_color_to_tuple
                self._backgroundColor = parse_color_to_tuple(backgroundColor)
            except Exception:
                pass
        self._current_selection = None
        self._cursor_state: dict = {}
        self._native_renderer = None
        if NativeCliRenderer is not None:
            try:
                self._native_renderer = NativeCliRenderer(self.width, self.height)
                self._native_renderer.set_background_color(*self._backgroundColor)
                self.front_buffer = OptimizedBuffer(0, 0, native_buffer=self._native_renderer.get_current_buffer())
                self.back_buffer = OptimizedBuffer(0, 0, native_buffer=self._native_renderer.get_next_buffer())
            except Exception:
                self._native_renderer = None
                self.front_buffer = OptimizedBuffer(self.width, self.height)
                self.back_buffer = OptimizedBuffer(self.width, self.height)
        else:
            self.front_buffer = OptimizedBuffer(self.width, self.height)
            self.back_buffer = OptimizedBuffer(self.width, self.height)
        self.context = RenderContext(renderer=self)
        self.root = RootRenderable(self.context, {"id": "root"})
        self.keyboard = KeyboardHandler(use_kitty_keyboard=use_kitty_keyboard, input_handlers_getter=lambda: self._input_handlers)
        self.keyboard.on("keypress", self._on_keypress)
        self.keyboard.on("keyrelease", self._on_keyrelease)
        self.keyboard.on("paste", self._on_paste)
        self.prepend_input_handler(self._debug_capture_input)
        self.events = EventBus()
        self.running = False
        self._render_scheduled = False
        self._frame_count = 0
        self._last_render_time = 0.0
        self._last_frame_time = 0.0
        self._utf8_decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
        self.stats = {"fps": 0, "frame_time": 0.0, "render_time": 0.0}
        self._frame_times: list[float] = []
        self._stats_frame_count = 0
        self._frame_callbacks: list = []
        self._memory_snapshot_last_emit = 0.0
        self._input_stream = None
        self._input_saved_attrs = None
        self._previous_control_state = RendererControlState.IDLE
        self._suspended_mouse_enabled = False

    def start(self) -> None:
        self._control_state = RendererControlState.EXPLICIT_STARTED
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
        if self._use_mouse:
            self.terminal.enable_mouse()
        try:
            self._run_loop()
        except KeyboardInterrupt:
            pass
        finally:
            self._cleanup()

    def stop(self) -> None:
        self._control_state = RendererControlState.EXPLICIT_STOPPED
        self.running = False

    def _run_loop(self) -> None:
        last_fps = time.time()
        fps_count = 0
        self._last_frame_time = time.time()
        while self.running:
            start = time.time()
            delta_ms = (start - self._last_frame_time) * 1000.0
            self.events.emit("frame", start)
            for cb in self._frame_callbacks:
                try:
                    cb(delta_ms)
                except Exception:
                    pass
            self._process_input()
            self._check_resize()
            if self._render_scheduled or self._should_render():
                t0 = time.time()
                self._render_frame()
                self.stats["render_time"] = (time.time() - t0) * 1000
                self._render_scheduled = False
                fps_count += 1
                if self.gather_stats:
                    frame_time_ms = (time.time() - start) * 1000.0
                    self._frame_times.append(frame_time_ms)
                    if len(self._frame_times) > self.max_stat_samples:
                        self._frame_times.pop(0)
                    self._stats_frame_count += 1
            now = time.time()
            if now - last_fps >= 1.0:
                self.stats["fps"] = fps_count
                fps_count = 0
                last_fps = now
            self.stats["frame_time"] = (time.time() - start) * 1000
            if self.memory_snapshot_interval > 0 and (now - self._memory_snapshot_last_emit) * 1000 >= self.memory_snapshot_interval:
                self._emit_memory_snapshot()
                self._memory_snapshot_last_emit = now
            self._last_frame_time = time.time()
            if self.frame_time > 0 and (time.time() - start) < self.frame_time:
                time.sleep(self.frame_time - (time.time() - start))

    def _render_frame(self) -> None:
        self.back_buffer.clear()
        self.root.calculate_layout()
        delta_time = time.time() - self._last_render_time if self._frame_count else 0.0
        self.root.render(self.back_buffer, delta_time)
        for fn in self.post_process_fns:
            try:
                fn(self.back_buffer, delta_time)
            except Exception:
                pass
        self._diff_and_output()
        self.front_buffer, self.back_buffer = self.back_buffer, self.front_buffer
        self._frame_count += 1
        self._last_render_time = time.time()

    def _diff_and_output(self) -> None:
        # 首帧全量重绘，确保终端显示完整内容
        full_repaint = self._frame_count == 0
        # 方案 B 阶段二：native CliRenderer 时由 render() 做 diff + swap + 输出
        if self._native_renderer is not None:
            try:
                out = self._native_renderer.render(full_repaint)
                if out:
                    sys.stdout.write(out)
                    sys.stdout.flush()
            except Exception:
                self._diff_and_output_python(full_repaint)
            return
        # 阶段一回退：无 CliRenderer 时用 buffer.diff_and_output_ansi
        front_native = getattr(self.front_buffer, "_native_buffer", None)
        back_native = getattr(self.back_buffer, "_native_buffer", None)
        if back_native is not None and front_native is not None:
            try:
                out = back_native.diff_and_output_ansi(front_native, full_repaint)
                if out:
                    sys.stdout.write(out)
                    sys.stdout.flush()
            except Exception:
                self._diff_and_output_python(full_repaint)
            return
        self._diff_and_output_python(full_repaint)

    def _diff_and_output_python(self, full_repaint: bool) -> None:
        from pytui.core.ansi import ANSI

        out = []
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
        self._terminal_width, self._terminal_height = w, h
        render_h = self._experimental_split_height if self._experimental_split_height > 0 else h
        if w != self.width or render_h != self.height:
            self.width, self.height = w, render_h
            self._render_offset = h - self._experimental_split_height if self._experimental_split_height > 0 else 0
            if self._native_renderer is not None:
                try:
                    self._native_renderer.resize(self.width, self.height)
                    self.front_buffer = OptimizedBuffer(0, 0, native_buffer=self._native_renderer.get_current_buffer())
                    self.back_buffer = OptimizedBuffer(0, 0, native_buffer=self._native_renderer.get_next_buffer())
                except Exception:
                    self._native_renderer = None
                    self.front_buffer = OptimizedBuffer(self.width, self.height)
                    self.back_buffer = OptimizedBuffer(self.width, self.height)
            else:
                self.front_buffer = OptimizedBuffer(self.width, self.height)
                self.back_buffer = OptimizedBuffer(self.width, self.height)
            self.events.emit("resize", self.width, self.height)
            self.schedule_render()

    def _on_keypress(self, key: dict) -> None:
        self.events.emit("keypress", key)
        if self.exit_on_ctrl_c and key.get("ctrl") and key.get("name") == "c":
            self.stop()

    def _on_keyrelease(self, key: dict) -> None:
        self.events.emit("keyrelease", key)

    def _on_paste(self, event: dict) -> None:
        self.events.emit("paste", event)

    def _debug_capture_input(self, sequence: str) -> bool:
        """Prepend input handler: capture sequence when debug mode; return False so key processing continues."""
        if self._debug_mode_enabled:
            import datetime
            self._debug_inputs.append({"timestamp": datetime.datetime.now().isoformat(), "sequence": sequence})
        return False

    def _should_render(self) -> bool:
        return self.root._dirty

    def schedule_render(self) -> None:
        self._render_scheduled = True

    def request_render(self) -> None:
        """Align with OpenTUI renderer.requestRender()."""
        self.schedule_render()

    def set_frame_callback(self, callback) -> None:
        """Align with OpenTUI setFrameCallback(callback). callback(delta_ms) called each frame."""
        self._frame_callbacks.append(callback)

    def get_stats(self) -> dict:
        """Align with OpenTUI getStats(): fps, frameCount, frameTimes, averageFrameTime, minFrameTime, maxFrameTime."""
        frame_times = list(self._frame_times)
        n = len(frame_times)
        avg = sum(frame_times) / n if n else 0.0
        return {
            "fps": self.stats["fps"],
            "frameCount": self._stats_frame_count,
            "frameTimes": frame_times,
            "averageFrameTime": avg,
            "minFrameTime": min(frame_times) if n else 0.0,
            "maxFrameTime": max(frame_times) if n else 0.0,
        }

    def reset_stats(self) -> None:
        """Align with OpenTUI resetStats(): clear frame times and stats frame count."""
        self._frame_times.clear()
        self._stats_frame_count = 0

    def pause(self) -> None:
        """Align with OpenTUI pause(): set control state and stop the render loop."""
        self._control_state = RendererControlState.EXPLICIT_PAUSED
        self.stop()

    # --- Getters / properties (align OpenTUI) ---
    @property
    def control_state(self) -> str:
        return self._control_state

    @property
    def is_destroyed(self) -> bool:
        return self._is_destroyed

    @property
    def is_running(self) -> bool:
        return self.running

    @property
    def terminal_width(self) -> int:
        return self._terminal_width

    @property
    def terminal_height(self) -> int:
        return self._terminal_height

    @property
    def use_mouse(self) -> bool:
        return self._use_mouse

    @use_mouse.setter
    def use_mouse(self, value: bool) -> None:
        if self._use_mouse == value:
            return
        self._use_mouse = value
        if value:
            self.terminal.enable_mouse()
        else:
            self.terminal.disable_mouse()

    @property
    def key_input(self) -> KeyboardHandler:
        """Align OpenTUI keyInput getter."""
        return self.keyboard

    @property
    def use_console(self) -> bool:
        return self._use_console

    @use_console.setter
    def use_console(self, value: bool) -> None:
        self._use_console = value

    @property
    def experimental_split_height(self) -> int:
        return self._experimental_split_height

    @property
    def live_request_count(self) -> int:
        return self._live_request_counter

    @property
    def current_control_state(self) -> str:
        return self._control_state

    @property
    def capabilities(self) -> Any:
        return self._capabilities

    @property
    def resolution(self) -> dict | None:
        return self._resolution

    @property
    def current_focused_renderable(self) -> Renderable | None:
        return self._current_focused_renderable

    @property
    def palette_detection_status(self) -> str:
        return "idle"

    def get_debug_inputs(self) -> list[dict[str, str]]:
        return list(self._debug_inputs)

    # --- Input handlers (align OpenTUI addInputHandler, prependInputHandler, removeInputHandler) ---
    def add_input_handler(self, handler: Callable[[str], bool]) -> None:
        self._input_handlers.append(handler)

    def prepend_input_handler(self, handler: Callable[[str], bool]) -> None:
        self._input_handlers.insert(0, handler)

    def remove_input_handler(self, handler: Callable[[str], bool]) -> None:
        self._input_handlers = [h for h in self._input_handlers if h != handler]

    # --- Frame callbacks (align OpenTUI removeFrameCallback, clearFrameCallbacks) ---
    def remove_frame_callback(self, callback: Callable) -> None:
        self._frame_callbacks = [cb for cb in self._frame_callbacks if cb != callback]

    def clear_frame_callbacks(self) -> None:
        self._frame_callbacks.clear()

    def set_gather_stats(self, enabled: bool) -> None:
        self.gather_stats = enabled
        if not enabled:
            self._frame_times.clear()

    # --- Background, debug overlay, cursor, terminal title (align OpenTUI) ---
    def set_background_color(self, color: Any) -> None:
        try:
            from pytui.lib import parse_color_to_tuple
            self._backgroundColor = parse_color_to_tuple(color)
            if self._native_renderer is not None:
                self._native_renderer.set_background_color(*self._backgroundColor)
        except Exception:
            pass
        self.request_render()

    def toggle_debug_overlay(self) -> None:
        self.debug_overlay["enabled"] = not self.debug_overlay["enabled"]
        if self.debug_overlay["enabled"] and not self.memory_snapshot_interval:
            self.memory_snapshot_interval = 3000
        self.events.emit(CliRenderEvents.DEBUG_OVERLAY_TOGGLE, self.debug_overlay["enabled"])
        self.request_render()

    def configure_debug_overlay(self, enabled: bool | None = None, corner: int | None = None) -> None:
        if enabled is not None:
            self.debug_overlay["enabled"] = enabled
        if corner is not None:
            self.debug_overlay["corner"] = corner
        self.request_render()

    def set_terminal_title(self, title: str) -> None:
        sys.stdout.write(f"\x1b]0;{title}\x07")
        sys.stdout.flush()

    def dump_hit_grid(self) -> None:
        pass

    def dump_buffers(self, timestamp: int | None = None) -> None:
        pass

    def dump_stdout_buffer(self, timestamp: int | None = None) -> None:
        pass

    def set_cursor_position(self, x: int, y: int, visible: bool = True) -> None:
        from pytui.core.ansi import ANSI
        sys.stdout.write(ANSI.cursor_to(x, y))
        sys.stdout.write(ANSI.CURSOR_SHOW if visible else ANSI.CURSOR_HIDE)
        sys.stdout.flush()

    def set_cursor_style(self, style: CursorStyle, blinking: bool = False, color: Any = None) -> None:
        self._cursor_state["style"] = style
        self._cursor_state["blinking"] = blinking
        if color is not None:
            self._cursor_state["color"] = color

    def set_cursor_color(self, color: Any) -> None:
        self._cursor_state["color"] = color

    def get_cursor_state(self) -> dict:
        return dict(self._cursor_state)

    # --- Post-process (align OpenTUI addPostProcessFn, removePostProcessFn, clearPostProcessFns) ---
    def add_post_process_fn(self, fn: Callable[[OptimizedBuffer, float], None]) -> None:
        self.post_process_fns.append(fn)

    def remove_post_process_fn(self, fn: Callable[[OptimizedBuffer, float], None]) -> None:
        self.post_process_fns = [f for f in self.post_process_fns if f != fn]

    def clear_post_process_fns(self) -> None:
        self.post_process_fns.clear()

    # --- Live / control (align OpenTUI requestLive, dropLive, auto, suspend, resume) ---
    def request_live(self) -> None:
        self._live_request_counter += 1
        if self._control_state == RendererControlState.IDLE and self._live_request_counter > 0:
            self._control_state = RendererControlState.AUTO_STARTED
            self.start()

    def drop_live(self) -> None:
        self._live_request_counter = max(0, self._live_request_counter - 1)

    def auto(self) -> None:
        self._control_state = RendererControlState.AUTO_STARTED if self.running else RendererControlState.IDLE

    def suspend(self) -> None:
        self._previous_control_state = self._control_state
        self._control_state = RendererControlState.EXPLICIT_SUSPENDED
        self._suspended_mouse_enabled = self._use_mouse
        self.stop()

    def resume(self) -> None:
        self._control_state = self._previous_control_state
        if self._previous_control_state in (RendererControlState.AUTO_STARTED, RendererControlState.EXPLICIT_STARTED):
            self.start()
        else:
            self.request_render()

    def destroy(self) -> None:
        if self._is_destroyed:
            return
        self._is_destroyed = True
        self.running = False
        self.events.emit(CliRenderEvents.DESTROY)
        try:
            if hasattr(self.root, "destroy_recursively"):
                self.root.destroy_recursively()
            else:
                self.root.remove_all()
        except Exception:
            pass
        if self._on_destroy:
            try:
                self._on_destroy()
            except Exception:
                pass

    def intermediate_render(self) -> None:
        """Align OpenTUI intermediateRender(): request immediate render."""
        self.request_render()

    # --- Selection (stubs; align OpenTUI getSelection, hasSelection, getSelectionContainer, clearSelection, startSelection, updateSelection, requestSelectionUpdate) ---
    def get_selection(self) -> Any:
        return self._current_selection

    @property
    def has_selection(self) -> bool:
        return self._current_selection is not None

    def get_selection_container(self) -> Renderable | None:
        return None

    def clear_selection(self) -> None:
        self._current_selection = None

    def start_selection(self, renderable: Renderable, x: int, y: int) -> None:
        self._current_selection = {"renderable": renderable, "x": x, "y": y}

    def update_selection(self, renderable: Renderable | None, x: int, y: int) -> None:
        if self._current_selection:
            self._current_selection["x"], self._current_selection["y"] = x, y

    def request_selection_update(self) -> None:
        pass

    # --- Lifecycle (align OpenTUI registerLifecyclePass, unregisterLifecyclePass, getLifecyclePasses) ---
    def register_lifecycle_pass(self, renderable: Renderable) -> None:
        self._lifecycle_passes.add(renderable)

    def unregister_lifecycle_pass(self, renderable: Renderable) -> None:
        self._lifecycle_passes.discard(renderable)

    def get_lifecycle_passes(self) -> set:
        return set(self._lifecycle_passes)

    def focus_renderable(self, renderable: Renderable) -> None:
        self._current_focused_renderable = renderable

    def hit_test(self, x: int, y: int) -> int:
        """Return renderable id at (x, y), or 0. 方案 B 阶段三：native 时转发到 check_hit。"""
        if self._native_renderer is not None:
            return self._native_renderer.check_hit(x, y)
        return 0

    def set_memory_snapshot_interval(self, interval: int) -> None:
        self.memory_snapshot_interval = interval

    def clear_palette_cache(self) -> None:
        pass

    def idle(self) -> Any:
        """Align OpenTUI idle(): return a resolved future (no-op in sync impl)."""
        return None

    def _emit_memory_snapshot(self) -> None:
        """Emit memory:snapshot event with heapUsed/heapTotal/arrayBuffers (align OpenTUI)."""
        try:
            import resource
            ru = resource.getrusage(resource.RUSAGE_SELF)
            heap_used = ru.ru_maxrss * 1024  # Linux/macOS: KB -> bytes
        except Exception:
            heap_used = 0
        self.events.emit("memory:snapshot", {"heapUsed": heap_used, "heapTotal": 0, "arrayBuffers": 0})

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
        if self._use_mouse:
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
