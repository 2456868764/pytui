# tests/unit/core/test_terminal.py - terminal capability detection

import pytest

pytest.importorskip("pytui.core.terminal")


class TestTerminalCapabilityDetection:
    def test_is_capability_response_decrpm(self):
        from pytui.core.terminal import is_capability_response

        assert is_capability_response("\x1b[?6;0$y") is True
        assert is_capability_response("x") is False

    def test_is_capability_response_cpr(self):
        from pytui.core.terminal import is_capability_response

        assert is_capability_response("\x1b[1;2R") is True
        assert is_capability_response("\x1b[1;1R") is False  # column 1 = no width support

    def test_is_pixel_resolution_response(self):
        from pytui.core.terminal import is_pixel_resolution_response

        assert is_pixel_resolution_response("\x1b[4;600;800t") is True
        assert is_pixel_resolution_response("\x1b[1;2R") is False

    def test_parse_pixel_resolution(self):
        from pytui.core.terminal import parse_pixel_resolution

        assert parse_pixel_resolution("\x1b[4;600;800t") == (800, 600)
        assert parse_pixel_resolution("x") is None

    def test_terminal_get_size(self):
        from pytui.core.terminal import Terminal

        t = Terminal()
        w, h = t.get_size()
        assert isinstance(w, int) and w >= 1
        assert isinstance(h, int) and h >= 1
