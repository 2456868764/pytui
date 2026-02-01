# tests/unit/core/test_terminal_palette.py

import pytest

pytest.importorskip("pytui.lib")


class TestTerminalPalette:
    def test_get_palette_color(self):
        from pytui.lib import get_palette_color

        c = get_palette_color(0)
        assert len(c) == 4
        assert c[0] >= 0 and c[1] >= 0 and c[2] >= 0 and c[3] == 255
        c1 = get_palette_color(255)
        assert c1[0] == c1[1] == c1[2]

    def test_detect_capability(self):
        from pytui.lib import detect_capability

        cap = detect_capability()
        assert cap in ("truecolor", "256", "16", "mono")

    def test_terminal_palette_class_cleanup(self):
        from pytui.lib import TerminalPalette

        p = TerminalPalette()
        p.cleanup()
        assert p._active_listeners == [] and p._active_timers == []

    def test_terminal_palette_detect_osc_support_no_tty(self):
        from pytui.lib import TerminalPalette

        p = TerminalPalette()
        assert p.detect_osc_support(100) is False

    def test_terminal_palette_detect_returns_static_palette(self):
        from pytui.lib import TerminalPalette

        p = TerminalPalette()
        result = p.detect({"size": 16})
        assert "palette" in result
        assert len(result["palette"]) == 16
        assert result["palette"][0] is not None
        assert result["defaultForeground"] is None

    def test_create_terminal_palette(self):
        from pytui.lib import create_terminal_palette

        detector = create_terminal_palette()
        assert hasattr(detector, "detect") and hasattr(detector, "cleanup")
