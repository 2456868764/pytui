# tests/unit/core/test_ansi.py
"""ANSI 工具单元测试。"""

import pytest

pytest.importorskip("pytui.core.ansi")


class TestANSI:
    """ANSI 常量与静态方法。"""

    def test_cursor_to_format(self):
        from pytui.core.ansi import ANSI

        # 1-based in ANSI
        s = ANSI.cursor_to(0, 0)
        assert "\x1b[" in s
        assert "1;1H" in s

        s = ANSI.cursor_to(5, 10)
        assert "11;6H" in s  # y+1=11, x+1=6

    def test_rgb_fg_bg(self):
        from pytui.core.ansi import ANSI

        fg = ANSI.rgb_fg(100, 150, 200)
        assert "\x1b[38;2;100;150;200m" == fg

        bg = ANSI.rgb_bg(1, 2, 3)
        assert "\x1b[48;2;1;2;3m" == bg

    def test_reset(self):
        from pytui.core.ansi import ANSI

        assert ANSI.reset() == "\x1b[0m"

    def test_constants_exist(self):
        from pytui.core.ansi import ANSI

        assert ANSI.CURSOR_UP == "\x1b[A"
        assert ANSI.CLEAR_SCREEN == "\x1b[2J"
        assert ANSI.CURSOR_HIDE == "\x1b[?25l"
        assert ANSI.CURSOR_SHOW == "\x1b[?25h"
