# pytui.core.ansi - ANSI escape sequences

class ANSI:
    """ANSI 转义序列工具"""

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

    # 屏幕控制
    CLEAR_SCREEN = "\x1b[2J"
    CLEAR_LINE = "\x1b[2K"
    ALTERNATE_SCREEN_ON = "\x1b[?1049h"
    ALTERNATE_SCREEN_OFF = "\x1b[?1049l"

    # 鼠标支持
    MOUSE_ON = "\x1b[?1000h\x1b[?1002h\x1b[?1015h\x1b[?1006h"
    MOUSE_OFF = "\x1b[?1000l\x1b[?1002l\x1b[?1015l\x1b[?1006l"

    @staticmethod
    def cursor_to(x: int, y: int) -> str:
        """移动光标到指定位置 (ANSI 为 1-based: row;col)"""
        return f"\x1b[{y + 1};{x + 1}H"

    @staticmethod
    def rgb_fg(r: int, g: int, b: int) -> str:
        """设置前景色 (RGB)"""
        return f"\x1b[38;2;{r};{g};{b}m"

    @staticmethod
    def rgb_bg(r: int, g: int, b: int) -> str:
        """设置背景色 (RGB)"""
        return f"\x1b[48;2;{r};{g};{b}m"

    @staticmethod
    def reset() -> str:
        """重置样式"""
        return "\x1b[0m"
