# tests.unit.core.test_console - ConsoleBuffer, ConsoleOverlay, capture_stdout

import io
import sys

import pytest

pytest.importorskip("pytui.core.console")


class TestConsoleBuffer:
    def test_append_single_line(self):
        from pytui.core.console import ConsoleBuffer

        buf = ConsoleBuffer()
        buf.append("hello")
        assert buf.lines == ["hello"]

    def test_append_multiple_lines(self):
        from pytui.core.console import ConsoleBuffer

        buf = ConsoleBuffer()
        buf.append("a\nb\nc")
        assert buf.lines == ["a", "b", "c"]

    def test_append_empty_no_line(self):
        from pytui.core.console import ConsoleBuffer

        buf = ConsoleBuffer()
        buf.append("")
        assert buf.lines == []

    def test_max_lines_caps(self):
        from pytui.core.console import ConsoleBuffer

        buf = ConsoleBuffer(max_lines=3)
        buf.append("1")
        buf.append("2")
        buf.append("3")
        assert buf.lines == ["1", "2", "3"]
        buf.append("4")
        assert buf.lines == ["2", "3", "4"]

    def test_clear(self):
        from pytui.core.console import ConsoleBuffer

        buf = ConsoleBuffer()
        buf.append("a\nb")
        buf.clear()
        assert buf.lines == []


class TestConsoleOverlay:
    def test_render_self_shows_buffer_lines(self, buffer_10x5):
        from pytui.core.console import ConsoleBuffer, ConsoleOverlay

        buf = ConsoleBuffer()
        buf.append("Hi\nWorld")
        ctx = _mock_ctx(10, 5)
        overlay = ConsoleOverlay(ctx, {"buffer": buf, "width": 10, "height": 5})
        overlay.x, overlay.y = 0, 0
        overlay.width, overlay.height = 10, 5
        overlay.render_self(buffer_10x5)
        c0 = buffer_10x5.get_cell(0, 0)
        assert c0 and c0.char == "H"
        c1 = buffer_10x5.get_cell(0, 1)
        assert c1 and c1.char == "W"

    def test_scroll_y_offset(self, buffer_10x5):
        from pytui.core.console import ConsoleBuffer, ConsoleOverlay

        buf = ConsoleBuffer()
        buf.append("line0\nline1\nline2")
        ctx = _mock_ctx(10, 5)
        overlay = ConsoleOverlay(ctx, {"buffer": buf, "width": 10, "height": 5})
        overlay.x, overlay.y = 0, 0
        overlay.width, overlay.height = 10, 5
        overlay.set_scroll(1)
        overlay.render_self(buffer_10x5)
        c0 = buffer_10x5.get_cell(0, 0)
        assert c0 and c0.char == "l"  # first char of "line1"

    def test_scroll_up_down(self):
        from pytui.core.console import ConsoleBuffer, ConsoleOverlay

        buf = ConsoleBuffer()
        buf.append("\n".join(["line"] * 10))
        ctx = _mock_ctx(10, 5)
        overlay = ConsoleOverlay(ctx, {"buffer": buf})
        overlay.width, overlay.height = 10, 5
        overlay.set_scroll(3)
        overlay.scroll_up()
        assert overlay.scroll_y == 2
        overlay.scroll_down()
        assert overlay.scroll_y == 3

    def test_set_scroll_clamps(self):
        from pytui.core.console import ConsoleBuffer, ConsoleOverlay

        buf = ConsoleBuffer()
        buf.append("a\nb")
        ctx = _mock_ctx(10, 5)
        overlay = ConsoleOverlay(ctx, {"buffer": buf})
        overlay.width, overlay.height = 10, 5
        overlay.set_scroll(-1)
        assert overlay.scroll_y == 0
        overlay.set_scroll(100)
        assert overlay.scroll_y == max(0, len(buf.lines) - overlay.height)  # 0 when lines <= height


class TestCaptureStdout:
    def test_capture_stdout_writes_to_buffer(self):
        from pytui.core.console import ConsoleBuffer, capture_stdout

        buf = ConsoleBuffer()
        with capture_stdout(buf, also_stdout=False):
            print("hello", end="")
        assert buf.lines == ["hello"]

    def test_capture_stdout_also_stdout(self):
        from pytui.core.console import ConsoleBuffer, capture_stdout

        buf = ConsoleBuffer()
        out = io.StringIO()
        old = sys.stdout
        try:
            sys.stdout = out
            with capture_stdout(buf, also_stdout=True):
                print("x", end="")
            assert buf.lines == ["x"]
            assert out.getvalue() == "x"
        finally:
            sys.stdout = old


def _mock_ctx(width: int, height: int):
    from unittest.mock import MagicMock

    m = MagicMock()
    m.renderer = MagicMock()
    m.renderer.width = width
    m.renderer.height = height
    return m
