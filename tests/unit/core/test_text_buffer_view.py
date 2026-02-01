# tests/unit/core/test_text_buffer_view.py - Aligns with OpenTUI packages/core/src/text-buffer-view.test.ts
"""TextBufferView 单元测试。"""

import pytest

pytest.importorskip("pytui.core.text_buffer_view")


class TestTextBufferView:
    @pytest.fixture
    def buffer(self):
        from pytui.core.text_buffer import TextBuffer

        buf = TextBuffer.create("wcwidth")
        yield buf
        buf.destroy()

    @pytest.fixture
    def view(self, buffer):
        from pytui.core.text_buffer_view import TextBufferView

        v = TextBufferView.create(buffer)
        yield v
        v.destroy()

    def test_line_info_empty(self, buffer, view):
        from pytui.lib.styled_text import string_to_styled_text

        buffer.set_styled_text(string_to_styled_text(""))
        info = view.line_info
        assert info["line_starts"] == [0]
        assert info["line_widths"] == [0]

    def test_line_info_single_line(self, buffer, view):
        from pytui.lib.styled_text import string_to_styled_text

        buffer.set_styled_text(string_to_styled_text("Hello World"))
        info = view.line_info
        assert info["line_starts"] == [0]
        assert len(info["line_widths"]) == 1
        assert info["line_widths"][0] == 11

    def test_line_info_two_lines(self, buffer, view):
        from pytui.lib.styled_text import string_to_styled_text

        buffer.set_styled_text(string_to_styled_text("Hello\nWorld"))
        info = view.line_info
        assert info["line_starts"] == [0, 6]
        assert len(info["line_widths"]) == 2
        assert info["line_widths"][0] == 5
        assert info["line_widths"][1] == 5

    def test_set_get_selection(self, buffer, view):
        buffer.set_text("Hello World")
        view.set_selection(0, 5)
        sel = view.get_selection()
        assert sel == (0, 5)
        assert view.has_selection() is True
        assert view.get_selected_text() == "Hello"

    def test_reset_selection(self, buffer, view):
        buffer.set_text("Hi")
        view.set_selection(0, 2)
        view.reset_selection()
        assert view.get_selection() is None
        assert view.has_selection() is False
        assert view.get_selected_text() == ""

    def test_get_plain_text(self, buffer, view):
        buffer.set_text("abc")
        assert view.get_plain_text() == "abc"

    def test_get_virtual_line_count(self, buffer, view):
        buffer.set_text("a\nb\nc")
        assert view.get_virtual_line_count() == 3

    def test_destroy_twice_no_op(self, buffer, view):
        view.destroy()
        view.destroy()

    def test_after_destroy_raises(self, buffer):
        from pytui.core.text_buffer_view import TextBufferView

        v = TextBufferView.create(buffer)
        v.destroy()
        with pytest.raises(RuntimeError, match="destroyed"):
            v.line_info
        with pytest.raises(RuntimeError, match="destroyed"):
            v.get_plain_text()
