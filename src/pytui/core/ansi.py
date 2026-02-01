# pytui.core.ansi - ANSI escape sequences. Aligns with OpenTUI packages/core/src/ansi.ts
# Keys: switchToAlternateScreen, switchToMainScreen, reset, scrollDown/Up, moveCursor, moveCursorAndClear,
# setRgbBackground, resetBackground, bracketedPasteStart/End. Python API uses snake_case for methods.

from __future__ import annotations


class ANSI:
    """ANSI 转义序列工具。对齐 OpenTUI ansi.ts。"""

    # 光标控制
    CURSOR_UP = "\x1b[A"
    CURSOR_DOWN = "\x1b[B"
    CURSOR_RIGHT = "\x1b[C"
    CURSOR_LEFT = "\x1b[D"
    CURSOR_HOME = "\x1b[H"
    CURSOR_SAVE = "\x1b[s"
    CURSOR_RESTORE = "\x1b[u"
    CURSOR_HIDE = "\x1b[?25l"
    CURSOR_SHOW = "\x1b[?25h"

    # 屏幕控制（OpenTUI 命名）
    switchToAlternateScreen = "\x1b[?1049h"
    switchToMainScreen = "\x1b[?1049l"
    ALTERNATE_SCREEN_ON = switchToAlternateScreen
    ALTERNATE_SCREEN_OFF = switchToMainScreen

    resetBackground = "\x1b[49m"

    @staticmethod
    def reset() -> str:
        """重置样式。OpenTUI reset。"""
        return "\x1b[0m"

    # Bracketed paste（OpenTUI）
    bracketedPasteStart = "\x1b[200~"
    bracketedPasteEnd = "\x1b[201~"

    CLEAR_SCREEN = "\x1b[2J"
    CLEAR_LINE = "\x1b[2K"

    MOUSE_ON = "\x1b[?1000h\x1b[?1002h\x1b[?1015h\x1b[?1006h"
    MOUSE_OFF = "\x1b[?1000l\x1b[?1002l\x1b[?1015l\x1b[?1006l"

    @staticmethod
    def cursor_to(x: int, y: int) -> str:
        """移动光标到指定位置 (ANSI 为 1-based: row;col)。对齐 OpenTUI moveCursor(row,col)。"""
        return f"\x1b[{y + 1};{x + 1}H"

    @staticmethod
    def move_cursor(row: int, col: int) -> str:
        """OpenTUI moveCursor(row, col) 1-based。"""
        return f"\x1b[{row};{col}H"

    @staticmethod
    def move_cursor_and_clear(row: int, col: int) -> str:
        """OpenTUI moveCursorAndClear(row, col)。"""
        return f"\x1b[{row};{col}H\x1b[J"

    @staticmethod
    def scroll_down(lines: int) -> str:
        """OpenTUI scrollDown(lines)。"""
        return f"\x1b[{lines}T"

    @staticmethod
    def scroll_up(lines: int) -> str:
        """OpenTUI scrollUp(lines)。"""
        return f"\x1b[{lines}S"

    @staticmethod
    def rgb_fg(r: int, g: int, b: int) -> str:
        """设置前景色 (RGB)。"""
        return f"\x1b[38;2;{r};{g};{b}m"

    @staticmethod
    def rgb_bg(r: int, g: int, b: int) -> str:
        """设置背景色 (RGB)。"""
        return f"\x1b[48;2;{r};{g};{b}m"

    @staticmethod
    def set_rgb_background(r: int, g: int, b: int) -> str:
        """OpenTUI setRgbBackground(r,g,b)。"""
        return f"\x1b[48;2;{r};{g};{b}m"
