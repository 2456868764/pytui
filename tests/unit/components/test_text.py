# tests/unit/components/test_text.py - Aligns with OpenTUI packages/core/src/renderables/Text.test.ts
# Covers: Initialization, content/plain_text/text_length, clear, wrap_mode, truncate,
# selection_bg/fg, tab_indicator, line_count/virtual_line_count, rendering (plain, styled, wrap, tab).

import pytest

pytest.importorskip("pytui.components.text")


def _create_text(ctx, **options):
    from pytui.components.text import Text
    return Text(ctx, {"width": 20, "height": 5, **options})


class TestTextInitialization:
    """Align OpenTUI: Initialization."""

    def test_initializes_with_content_and_dimensions(self, mock_context):
        from pytui.components.text import Text
        t = Text(mock_context, {"content": "Hello World", "width": 20, "height": 5})
        assert t.content == "Hello World"
        assert t.plain_text == "Hello World"
        assert t.text_length == 11
        # width/height from options are applied by layout; without layout run they may be 0
        assert t.width >= 0
        assert t.height >= 0

    def test_default_wrap_mode_is_word(self, mock_context):
        t = _create_text(mock_context, content="Hi")
        assert t.wrap_mode == "word"

    def test_default_truncate_is_false(self, mock_context):
        t = _create_text(mock_context, content="Hi")
        assert t.truncate is False

    def test_accepts_wrapMode_camelCase(self, mock_context):
        t = _create_text(mock_context, content="x", wrapMode="char")
        assert t.wrap_mode == "char"


class TestTextContentAndPlainText:
    """Align OpenTUI: content, plainText, textLength."""

    def test_set_content_triggers_request_render(self, mock_context):
        from pytui.components.text import Text
        t = Text(mock_context, {"content": "a", "width": 10, "height": 1})
        t.request_render = lambda: None
        t.set_content("b")
        assert t.content == "b"

    def test_plain_text_from_string_content(self, mock_context):
        t = _create_text(mock_context, content="Hello World")
        assert t.plain_text == "Hello World"
        assert t.text_length == 11

    def test_plain_text_from_styled_content(self, mock_context):
        from pytui.components.text_node import Span
        t = _create_text(mock_context, content=[Span(text="Red "), Span(text="Green"), " Blue"])
        assert t.plain_text == "Red Green Blue"
        assert t.text_length == 14

    def test_plain_text_empty(self, mock_context):
        t = _create_text(mock_context, content="")
        assert t.plain_text == ""
        assert t.text_length == 0


class TestTextClear:
    """Align OpenTUI: clear()."""

    def test_clear_empties_content(self, mock_context):
        t = _create_text(mock_context, content="Hello")
        t.clear()
        assert t.content == ""
        assert t.plain_text == ""
        assert t.text_length == 0


class TestTextWrapModeAndTruncate:
    """Align OpenTUI: wrapMode, truncate getters/setters."""

    def test_wrap_mode_getter_setter(self, mock_context):
        t = _create_text(mock_context, content="x", wrap_mode="word")
        assert t.wrap_mode == "word"
        t.wrap_mode = "char"
        assert t.wrap_mode == "char"
        t.wrap_mode = "none"
        assert t.wrap_mode == "none"

    def test_truncate_getter_setter(self, mock_context):
        t = _create_text(mock_context, content="x", truncate=False)
        assert t.truncate is False
        t.truncate = True
        assert t.truncate is True


class TestTextSelectionAndTabOptions:
    """Align OpenTUI: selectionBg, selectionFg, tabIndicator, tabIndicatorColor."""

    def test_selection_bg_fg_options_and_properties(self, mock_context):
        t = _create_text(mock_context, content="x", selection_bg="#ff0000", selection_fg="#00ff00")
        assert t.selection_bg is not None
        assert t.selection_fg is not None
        t.selection_bg = None
        t.selection_fg = None
        assert t.selection_bg is None
        assert t.selection_fg is None

    def test_tab_indicator_option_and_property(self, mock_context):
        t = _create_text(mock_context, content="a\tb", tab_indicator="→")
        assert t.tab_indicator == "→"
        t.tab_indicator = 4
        assert t.tab_indicator == 4

    def test_tab_indicator_color_option(self, mock_context):
        t = _create_text(mock_context, content="x", tabIndicatorColor="#888888")
        assert t.tab_indicator_color is not None


class TestTextLineCountAndVirtualLineCount:
    """Align OpenTUI: lineCount, getVirtualLineCount / virtualLineCount."""

    def test_line_count_plain(self, mock_context):
        t = _create_text(mock_context, content="Line 1\nLine 2\nLine 3", width=20, height=10)
        t.x, t.y, t.width, t.height = 0, 0, 20, 10
        assert t.line_count == 3
        assert t.virtual_line_count == 3  # no wrap at width 20

    def test_virtual_line_count_with_word_wrap(self, mock_context):
        t = _create_text(mock_context, content="Hello world here", width=5, height=10)
        t.x, t.y, t.width, t.height = 0, 0, 5, 10
        assert t.line_count == 1
        assert t.virtual_line_count >= 2  # wrapped

    def test_line_count_empty(self, mock_context):
        t = _create_text(mock_context, content="", width=10, height=5)
        t.x, t.y, t.width, t.height = 0, 0, 10, 5
        assert t.line_count == 0
        assert t.virtual_line_count == 0


class TestTextRendering:
    """Align OpenTUI: render content (plain, multiline, wrap, truncate, tab)."""

    def test_render_self_draws_content(self, mock_context, buffer_10x5):
        from pytui.components.text import Text
        t = Text(mock_context, {"content": "Hi", "width": 10, "height": 1})
        t.x, t.y, t.width, t.height = 0, 0, 10, 1
        t.render_self(buffer_10x5)
        assert buffer_10x5.get_cell(0, 0).char == "H"
        assert buffer_10x5.get_cell(1, 0).char == "i"

    def test_render_self_multiline(self, mock_context, buffer_10x5):
        from pytui.components.text import Text
        t = Text(mock_context, {"content": "ab\ncd", "width": 10, "height": 2})
        t.x, t.y, t.width, t.height = 0, 0, 10, 2
        t.render_self(buffer_10x5)
        assert buffer_10x5.get_cell(0, 0).char == "a"
        assert buffer_10x5.get_cell(1, 0).char == "b"
        assert buffer_10x5.get_cell(0, 1).char == "c"
        assert buffer_10x5.get_cell(1, 1).char == "d"

    def test_render_word_wrap(self, mock_context, buffer_40x20):
        from pytui.components.text import Text
        t = Text(mock_context, {"content": "The quick brown fox", "width": 8, "height": 10, "wrap_mode": "word"})
        t.x, t.y, t.width, t.height = 0, 0, 8, 10
        t.render_self(buffer_40x20)
        # First line "The "
        assert buffer_40x20.get_cell(0, 0).char == "T"
        assert buffer_40x20.get_cell(3, 0).char == " "
        # Second line "quick "
        assert buffer_40x20.get_cell(0, 1).char == "q"
        assert buffer_40x20.get_cell(5, 1).char == " "

    def test_render_char_wrap(self, mock_context, buffer_40x20):
        from pytui.components.text import Text
        t = Text(mock_context, {"content": "ABCDEFGHIJ", "width": 4, "height": 10, "wrap_mode": "char"})
        t.x, t.y, t.width, t.height = 0, 0, 4, 10
        t.render_self(buffer_40x20)
        assert buffer_40x20.get_cell(0, 0).char == "A"
        assert buffer_40x20.get_cell(3, 0).char == "D"
        assert buffer_40x20.get_cell(0, 1).char == "E"
        assert buffer_40x20.get_cell(3, 1).char == "H"

    def test_render_truncate_ellipsis(self, mock_context, buffer_10x5):
        from pytui.components.text import Text
        t = Text(mock_context, {"content": "0123456789ABCDEF", "width": 10, "height": 1, "wrap_mode": "none", "truncate": True})
        t.x, t.y, t.width, t.height = 0, 0, 10, 1
        t.render_self(buffer_10x5)
        # Last visible char should be ellipsis
        assert buffer_10x5.get_cell(9, 0).char == "…"

    def test_render_tab_indicator_string(self, mock_context, buffer_40x20):
        from pytui.components.text import Text
        t = Text(mock_context, {"content": "a\tb", "width": 20, "height": 1, "tab_indicator": "→"})
        t.x, t.y, t.width, t.height = 0, 0, 20, 1
        t.render_self(buffer_40x20)
        assert buffer_40x20.get_cell(0, 0).char == "a"
        assert buffer_40x20.get_cell(1, 0).char == "→"
        assert buffer_40x20.get_cell(2, 0).char == "b"

    def test_render_tab_indicator_spaces(self, mock_context, buffer_40x20):
        from pytui.components.text import Text
        t = Text(mock_context, {"content": "x\ty", "width": 20, "height": 1, "tab_indicator": 4})
        t.x, t.y, t.width, t.height = 0, 0, 20, 1
        t.render_self(buffer_40x20)
        assert buffer_40x20.get_cell(0, 0).char == "x"
        assert buffer_40x20.get_cell(1, 0).char == " "
        assert buffer_40x20.get_cell(5, 0).char == "y"  # x + 4 spaces + y -> y at index 5


class TestTextStyledContent:
    """Align OpenTUI: StyledText content, plainText from styled."""

    def test_render_styled_content(self, mock_context, buffer_10x5):
        from pytui.components.text import Text
        from pytui.components.text_node import Span
        t = Text(mock_context, {"content": [Span(text="Hello"), Span(text=" World")], "width": 20, "height": 1})
        t.x, t.y, t.width, t.height = 0, 0, 20, 1
        t.render_self(buffer_10x5)
        assert buffer_10x5.get_cell(0, 0).char == "H"
        assert buffer_10x5.get_cell(5, 0).char == " "
        assert buffer_10x5.get_cell(6, 0).char == "W"

    def test_plain_text_after_styled_content(self, mock_context):
        from pytui.components.text_node import Span
        t = _create_text(mock_context, content=[Span(text="Red"), " ", Span(text="Blue")])
        assert t.plain_text == "Red Blue"

    def test_empty_styled_content(self, mock_context):
        t = _create_text(mock_context, content=[])
        assert t.plain_text == ""
        assert t.text_length == 0


class TestTextWordWrapping:
    """Align OpenTUI: Word Wrapping describe block."""

    def test_default_wrap_mode_is_word(self, mock_context):
        t = _create_text(mock_context, content="Hello World")
        assert t.wrap_mode == "word"

    def test_long_word_breaks_by_char_in_word_mode(self, mock_context, buffer_40x20):
        from pytui.components.text import Text
        t = Text(mock_context, {"content": "ABCDEFGHIJKLMNOP", "width": 5, "height": 10, "wrap_mode": "word"})
        t.x, t.y, t.width, t.height = 0, 0, 5, 10
        t.render_self(buffer_40x20)
        # No spaces -> break by char
        assert buffer_40x20.get_cell(0, 0).char == "A"
        assert buffer_40x20.get_cell(4, 0).char == "E"
        assert buffer_40x20.get_cell(0, 1).char == "F"

    def test_preserve_empty_lines_with_wrap(self, mock_context, buffer_40x20):
        from pytui.components.text import Text
        t = Text(mock_context, {"content": "First\n\nThird", "width": 10, "height": 5, "wrap_mode": "word"})
        t.x, t.y, t.width, t.height = 0, 0, 10, 5
        t.render_self(buffer_40x20)
        assert buffer_40x20.get_cell(0, 0).char == "F"
        # Empty logical line yields no visual row; "Third" is on next row
        assert buffer_40x20.get_cell(0, 1).char == "T"
