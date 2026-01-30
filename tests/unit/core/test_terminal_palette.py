# tests/unit/core/test_terminal_palette.py

import pytest

pytest.importorskip("pytui.core.terminal_palette")


class TestTerminalPalette:
    def test_get_palette_color(self):
        from pytui.core.terminal_palette import get_palette_color

        c = get_palette_color(0)
        assert len(c) == 4
        assert c[0] >= 0 and c[1] >= 0 and c[2] >= 0 and c[3] == 255
        c1 = get_palette_color(255)
        assert c1[0] == c1[1] == c1[2]

    def test_detect_capability(self):
        from pytui.core.terminal_palette import detect_capability

        cap = detect_capability()
        assert cap in ("truecolor", "256", "16", "mono")
