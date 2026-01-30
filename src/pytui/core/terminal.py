# pytui.core.terminal - terminal I/O

import os
import sys

from pytui.core.ansi import ANSI


class Terminal:
    """终端控制（尺寸、alternate screen、光标、raw、鼠标）。"""

    def __init__(self) -> None:
        self._raw = False
        self._alternate = False
        self._mouse = False

    def get_size(self) -> tuple[int, int]:
        """返回 (width, height)。"""
        try:
            size = os.get_terminal_size(sys.stderr.fileno())
            return (size.columns, size.lines)
        except Exception:
            return (80, 24)

    @property
    def width(self) -> int:
        w, _ = self.get_size()
        return w

    @property
    def height(self) -> int:
        _, h = self.get_size()
        return h

    def enter_alternate_screen(self) -> None:
        sys.stdout.write(ANSI.ALTERNATE_SCREEN_ON)
        sys.stdout.flush()
        self._alternate = True

    def exit_alternate_screen(self) -> None:
        sys.stdout.write(ANSI.ALTERNATE_SCREEN_OFF)
        sys.stdout.flush()
        self._alternate = False

    def hide_cursor(self) -> None:
        sys.stdout.write(ANSI.CURSOR_HIDE)
        sys.stdout.flush()

    def show_cursor(self) -> None:
        sys.stdout.write(ANSI.CURSOR_SHOW)
        sys.stdout.flush()

    def set_raw_mode(self) -> None:
        if hasattr(sys.stdin, "fileno"):
            try:
                import termios
                import tty

                fd = sys.stdin.fileno()
                self._saved_attrs = termios.tcgetattr(fd)
                tty.setraw(fd)
                self._raw = True
            except Exception:
                pass

    def restore_mode(self) -> None:
        if self._raw and hasattr(sys.stdin, "fileno") and hasattr(self, "_saved_attrs"):
            try:
                import termios

                termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self._saved_attrs)
            except Exception:
                pass
            self._raw = False

    def enable_mouse(self) -> None:
        sys.stdout.write(ANSI.MOUSE_ON)
        sys.stdout.flush()
        self._mouse = True

    def disable_mouse(self) -> None:
        sys.stdout.write(ANSI.MOUSE_OFF)
        sys.stdout.flush()
        self._mouse = False
