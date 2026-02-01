# tests/unit/core/test_text_buffer.py - Aligns with OpenTUI packages/core/src/text-buffer.test.ts
"""TextBuffer 单元测试。"""

import pytest

pytest.importorskip("pytui.core.text_buffer")


class TestTextBuffer:
    @pytest.fixture
    def buffer(self):
        from pytui.core.text_buffer import TextBuffer

        buf = TextBuffer.create("wcwidth")
        yield buf
        buf.destroy()

    def test_set_text_content(self, buffer):
        buffer.set_text("Hello World")
        assert buffer.length == 11
        assert buffer.byte_size > 0

    def test_set_styled_text(self, buffer):
        from pytui.lib.styled_text import string_to_styled_text

        styled = string_to_styled_text("Hello World")
        buffer.set_styled_text(styled)
        assert buffer.length == 11

    def test_empty_text(self, buffer):
        from pytui.lib.styled_text import string_to_styled_text

        empty = string_to_styled_text("")
        buffer.set_styled_text(empty)
        assert buffer.length == 0

    def test_text_with_newlines(self, buffer):
        buffer.set_text("Line 1\nLine 2\nLine 3")
        assert buffer.length == 20  # 6+1+6+1+6 chars including newlines

    def test_get_plain_text_empty(self, buffer):
        from pytui.lib.styled_text import string_to_styled_text

        buffer.set_styled_text(string_to_styled_text(""))
        assert buffer.get_plain_text() == ""

    def test_get_plain_text_no_styling(self, buffer):
        from pytui.lib.styled_text import string_to_styled_text

        buffer.set_styled_text(string_to_styled_text("Hello World"))
        assert buffer.get_plain_text() == "Hello World"

    def test_get_plain_text_with_newlines(self, buffer):
        from pytui.lib.styled_text import string_to_styled_text

        buffer.set_styled_text(string_to_styled_text("Line 1\nLine 2\nLine 3"))
        assert buffer.get_plain_text() == "Line 1\nLine 2\nLine 3"

    def test_get_plain_text_unicode(self, buffer):
        from pytui.lib.styled_text import string_to_styled_text

        buffer.set_styled_text(string_to_styled_text("Hello 世界 🌟"))
        assert buffer.get_plain_text() == "Hello 世界 🌟"

    def test_length_simple(self, buffer):
        from pytui.lib.styled_text import string_to_styled_text

        buffer.set_styled_text(string_to_styled_text("Hello World"))
        assert buffer.length == 11

    def test_length_empty(self, buffer):
        from pytui.lib.styled_text import string_to_styled_text

        buffer.set_styled_text(string_to_styled_text(""))
        assert buffer.length == 0

    def test_length_unicode(self, buffer):
        from pytui.lib.styled_text import string_to_styled_text

        s = "Hello 世界 🌟"
        buffer.set_styled_text(string_to_styled_text(s))
        assert buffer.length == len(s)  # Python len (codepoints); OpenTUI may use 13 (grapheme/display)

    def test_default_styles_no_error(self, buffer):
        from pytui.lib import RGBA

        buffer.set_default_fg(RGBA.from_values(1, 0, 0, 1))
        buffer.reset_defaults()
        buffer.set_default_bg(RGBA.from_values(0, 0, 1, 1))
        buffer.reset_defaults()
        buffer.set_default_attributes(1)
        buffer.reset_defaults()

    def test_clear_empties_buffer(self, buffer):
        buffer.set_text("First text")
        assert buffer.length == 10
        buffer.set_text("Second text")
        assert buffer.length == 11
        assert buffer.get_plain_text() == "Second text"
        buffer.clear()
        assert buffer.length == 0
        assert buffer.get_plain_text() == ""

    def test_reset_fully_resets(self, buffer):
        buffer.set_text("Some text")
        assert buffer.length == 9
        buffer.reset()
        assert buffer.length == 0
        assert buffer.get_plain_text() == ""
        buffer.set_text("New text")
        assert buffer.length == 8

    def test_append_to_empty(self, buffer):
        buffer.append("Hello")
        assert buffer.length == 5
        assert buffer.get_plain_text() == "Hello"

    def test_append_to_existing(self, buffer):
        buffer.set_text("Hello")
        buffer.append(" World")
        assert buffer.length == 11
        assert buffer.get_plain_text() == "Hello World"

    def test_append_with_newlines(self, buffer):
        buffer.set_text("Line 1")
        buffer.append("\nLine 2")
        assert buffer.get_plain_text() == "Line 1\nLine 2"

    def test_append_multiple_times(self, buffer):
        buffer.set_text("Start")
        buffer.append(" middle")
        buffer.append(" end")
        assert buffer.get_plain_text() == "Start middle end"

    def test_append_empty_string(self, buffer):
        buffer.set_text("Hello")
        before = buffer.length
        buffer.append("")
        assert buffer.length == before
        assert buffer.get_plain_text() == "Hello"

    def test_append_unicode(self, buffer):
        buffer.set_text("Hello ")
        buffer.append("世界 🌟")
        assert buffer.get_plain_text() == "Hello 世界 🌟"

    def test_append_crlf_normalized(self, buffer):
        buffer.append("Line1\r\n")
        buffer.append("Line2\r\n")
        buffer.append("Line3")
        assert buffer.get_plain_text() == "Line1\nLine2\nLine3"

    def test_clear_then_append(self, buffer):
        buffer.set_text("Initial")
        buffer.clear()
        buffer.append("After clear")
        assert buffer.get_plain_text() == "After clear"

    def test_reset_then_append(self, buffer):
        buffer.set_text("Initial")
        buffer.reset()
        buffer.append("After reset")
        assert buffer.get_plain_text() == "After reset"

    def test_get_text_range(self, buffer):
        buffer.set_text("Hello World")
        assert buffer.get_text_range(0, 5) == "Hello"
        assert buffer.get_text_range(6, 11) == "World"
        assert buffer.get_text_range(0, 0) == ""
        assert buffer.get_text_range(5, 3) == ""

    def test_destroy_twice_no_op(self, buffer):
        buffer.destroy()
        buffer.destroy()

    def test_after_destroy_raises(self):
        from pytui.core.text_buffer import TextBuffer

        buf = TextBuffer.create("wcwidth")
        buf.destroy()
        with pytest.raises(RuntimeError, match="destroyed"):
            buf.get_plain_text()
        with pytest.raises(RuntimeError, match="destroyed"):
            buf.set_text("x")
